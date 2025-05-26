import glob
import sys
import os

from src.utils.exists_helper import check_queue_manager_exists

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import threading
import cv2
import json
import time
import numpy as np
from datetime import date
from collections import defaultdict
from datetime import datetime
from shapely.geometry import LineString
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from src.utils.logger import Logger
from src.core.inference.names import names
from src.core.stream.ffmpeg import convert_video
from src.utils.tools import load_config, convert_to_seconds
from src.core.inference.utils import build_regions, draw_regions, format_check
from src.core.inference.entities import create_session_entity
from settings import (
    LOG_PATH,
    VID_PATH,
    CONFIG_PATH,
    SYSTEM_SETTINGS_PATH,
    DEVICE_ID,
    CUDA_AVAILABLE,
    MPS_AVAILABLE,
    TMP_PATH,
)

logger = Logger("Inference", LOG_PATH + "/inference.log")

names = names

class Inference:
    def __init__(self, stream, model_str, only_simulation):
        # PROPS
        self.only_simulation = only_simulation
        self.model_str = model_str
        self.stream = stream
        self.last_frame = None
        self.annotate = True # False, check control.py get_last_inference_frame
        self.show_regions = True # False, check control.py get_last_inference_frame
        self.frame_count = self.stream.get_total_frames() if self.only_simulation else None
        self.save_sim = True

        if self.only_simulation:
            self.annotate = True
            self.show_regions = True
        
        # BASIC
        self.inference_started_event = threading.Event()
        self.temp_dir = os.path.join(TMP_PATH, f"simframes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.frame_count_sim = 0

        # If it's a simulation, create a temporary directory for frames
        if self.only_simulation:
            self.temp_dir = os.path.join(TMP_PATH, f"simframes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(self.temp_dir, exist_ok=True)
            self.frame_count_sim = 0
        
        self.frame_width = int(self.stream.get_details()['resolution'][0])
        self.frame_height = int(self.stream.get_details()['resolution'][1])
        self.fps = int(self.stream.get_details()['fps'])

        self.last_track_id = 0

        # DATA
        self.init_time = None
        self.frame_count = 0
        self.avg_performance = {
            "avg_fps": 0,
            "avg_fps_model": 0,
            "avg_time_preprocess": 0,
            "avg_time_inference": 0,
            "avg_time_postprocess": 0,
            "avg_time_total": 0
        }
        
        # Erfassung der Zählungen
        self.counts = defaultdict(lambda: defaultdict(lambda: {
            "IN": defaultdict(lambda: {"count": 0, "total_conf": 0}),
            "OUT": defaultdict(lambda: {"count": 0, "total_conf": 0})
        }))

        self.track_history = defaultdict(list)  # tracking history for each track ID
        
        # Set Config
        DATA = load_config(CONFIG_PATH)
        CONFIG = next(config for config in DATA["deviceConfigs"])
        self.deviceConfigId = CONFIG['id']
        self.deviceId = DEVICE_ID
        self.format = CONFIG['modelFormat']
        self.imgsz = CONFIG['imgsz']
        self.iou = CONFIG['iou']
        self.conf = CONFIG['conf']
        self.tracker = CONFIG['tracker']
        self.persist = CONFIG['persist']
        self.quantization = CONFIG['quantization']
        self.device = CONFIG['deviceType']
        self.vid_stride = CONFIG['vid_stride']
        self.hasRegions = True if "deviceRois" in DATA and len(DATA["deviceRois"]) > 0 else False
        self.obj_clss = list(map(int, DATA["deviceTags"][0]["tags"])) if "deviceTags" in DATA else None
        self.regions = build_regions(DATA["deviceRois"]) if self.hasRegions else None

        # VALIDATION
        self.validate_regions()

        # Load system settings
        SYSTEM_SETTINGS = load_config(SYSTEM_SETTINGS_PATH)
        self.blur_humans = SYSTEM_SETTINGS['blur_humans']
        self.detect_count_timespan = SYSTEM_SETTINGS['detect_count_timespan']
        counts_save_intervall_tmp = SYSTEM_SETTINGS['counts_save_intervall']
        self.counts_save_intervall = convert_to_seconds(counts_save_intervall_tmp, SYSTEM_SETTINGS['counts_save_intervall_format'])

        # Init Functions
        self.set_device() if self.device != "cpu" else None
        self.queue_manager = check_queue_manager_exists()
        self.active = True

        # Create session
        self.session_day = date.today()
        create_session_entity(self.session_day, self.deviceId, self.deviceConfigId, self.init_time)


    def validate_regions(self):
        if not self.hasRegions or not self.regions:
            warning = "You need to define regions with at least one tag."
            logger.warning(warning)
            raise Exception(warning)

        if any(not roi["tagsInThisRegion"] for roi in self.regions):
            warning = "You need to select at least one tag for your regions."
            logger.warning(warning)
            raise Exception(warning)

    def activate(self):
        self.inference_started_event.set()
        self.active = True

    def deactivate(self):
        self.inference_started_event.clear()
        self.active = False
        self.save_sim = False
        import gc
        gc.collect()

    def set_device(self):
        if CUDA_AVAILABLE:
            self.device = "cuda"
        elif MPS_AVAILABLE:
            self.device = "mps"
        else:
            error = "No GPU Device available."
            logger.error(error)
            raise Exception(error)

    def get_last_frame(self):
        return self.last_frame
    
    def change_vars(self, annotate, show_regions):
        self.annotate = annotate
        self.show_regions = show_regions

    def is_simulation(self):
        return self.only_simulation

    def performance_metrics(self, preprocess, inference, postprocess):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        avg_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

        total_time = preprocess + inference + postprocess

        self.avg_performance["avg_fps"] = avg_fps
        avg_time_total = (self.avg_performance["avg_time_total"] * (self.frame_count - 1) + total_time) / self.frame_count
        self.avg_performance["avg_fps_model"] = 1000 / avg_time_total if avg_time_total > 0 else 0
        self.avg_performance["avg_time_preprocess"] = (self.avg_performance["avg_time_preprocess"] * (self.frame_count - 1) + preprocess) / self.frame_count
        self.avg_performance["avg_time_inference"] = (self.avg_performance["avg_time_inference"] * (self.frame_count - 1) + inference) / self.frame_count
        self.avg_performance["avg_time_postprocess"] = (self.avg_performance["avg_time_postprocess"] * (self.frame_count - 1) + postprocess) / self.frame_count
        self.avg_performance["avg_time_total"] = avg_time_total

    def get_performance_metrics(self):
        inference_performance = {
            'init_time': self.init_time,
            "avg_fps": self.avg_performance["avg_fps"],
            "avg_fps_model": self.avg_performance["avg_fps_model"],
            "frames_processed": self.frame_count,
        }
        return inference_performance

    def blur_objects(self, frame, boxes, blur_factor=55):
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            roi = frame[y1:y2, x1:x2]
            roi = cv2.GaussianBlur(roi, (blur_factor, blur_factor), 0)
            frame[y1:y2, x1:x2] = roi
        return frame
    
    # https://github.com/ultralytics/ultralytics/blob/main/examples/YOLOv8-Region-Counter/yolov8_region_counter.py
    def count(self, track_id, cls, cls_name, region_name, line, previous_position, current_position, conf, current_time):
        line_geom = LineString([line["start_coord"], line["end_coord"]])
        
        if line_geom.crosses(LineString([previous_position, current_position])):
            cross_product = (current_position[0] - line["start_coord"][0]) * (line["end_coord"][1] - line["start_coord"][1]) - \
                               (current_position[1] - line["start_coord"][1]) * (line["end_coord"][0] - line["start_coord"][0])
                
            direction = line["direction"]
                
            if cross_product < 0:  # OUT
                line["counts"]["out"] += 1
                self.counts[region_name][direction]["OUT"][cls_name]["count"] += 1
                self.counts[region_name][direction]["OUT"][cls_name]["total_conf"] += conf
            else:  # IN
                line["counts"]["in"] += 1
                self.counts[region_name][direction]["IN"][cls_name]["count"] += 1
                self.counts[region_name][direction]["IN"][cls_name]["total_conf"] += conf
                
            self.last_track_id = track_id


    def run(self):
        try:
            model = YOLO(self.model_str)
            self.start_time = time.time()
            self.init_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_save_time = time.time()
            self.frame_count += 1
            
            while self.active:
                ret, frame = self.stream.read()
                if not ret and self.only_simulation:
                    info = "Simulation Video has ended."
                    logger.info(info)
                    return info
                if not ret:
                    from src.control import yt_live
                    isExpired = yt_live.get_expiration()
                    if isExpired < datetime.now():
                        info = "Stream expired!"
                        logger.info(info)
                        # this needs to be handled in another way
                        raise Exception(info)

                    error = "Could not read image from camera."
                    logger.error(error)
                    raise Exception(error)
                    
                    
                # vid_stride issue: https://github.com/ultralytics/ultralytics/issues/5770
                # https://github.com/ultralytics/ultralytics/issues/11723
                # officially vid_stride is not supported in tracking mode
                # https://docs.ultralytics.com/usage/cfg/#predict-settings
                if self.frame_count % (self.vid_stride) == 0:
                    # TRACKING
                    results = model.track(frame, imgsz=self.imgsz, device=self.device, iou=self.iou, conf=self.conf, persist=True, tracker=self.tracker, classes=self.obj_clss, verbose=False)
                    # DRAW REGIONS (VISUALIZATION)
                    frame = draw_regions(frame, self.regions) if (self.show_regions and self.hasRegions) else frame

                    # FROM HERE AT THE LATEST WE KNOW THAT THE INFERENCE HAS BEEN STARTED, SO WE INFORM IN CONTROL.PY
                    if self.active and not self.inference_started_event.is_set():
                        self.inference_started_event.set()

                    current_time = datetime.now().timestamp() * 1000

                    """ PROCESS DETECTION """
                    if results[0].boxes.id is not None and len(results[0].boxes.id) > 0:
                        boxes = results[0].boxes.xyxy.cpu()
                        track_ids = results[0].boxes.id.int().cpu().tolist()
                        clss = results[0].boxes.cls.cpu().tolist()      
                        confs = results[0].boxes.conf.cpu().tolist()

                        annotator = Annotator(frame, line_width=2, example=str(names)) if self.annotate else None
                        blur_boxes = []

                        for box, track_id, cls, conf in zip(boxes, track_ids, clss, confs):
                            cls = int(cls)
                            cls_name = names.get(cls, str(cls))
                            
                            blur_boxes.append(box) if self.annotate and cls == 0 else None
                            annotator.box_label(box, f"{str(names[cls])} ID:{track_id} Conf:{conf:.2f}", color=colors(cls, True)) if self.annotate else None
                            
                            # Tracking-Points
                            bbox_center = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

                            # Add the current position to the track history
                            self.track_history[track_id].append((float(bbox_center[0]), float(bbox_center[1])))
                            
                            # Visualize
                            points = np.array(self.track_history[track_id]).reshape((-1, 1, 2)).astype(np.int32)
                            cv2.polylines(frame, [points], isClosed=False, color=colors(cls, True), thickness=2)
                            
                            # Überprüfe Linienüberquerungen
                            track = self.track_history[track_id]
                            
                            if len(track) > 1:
                                previous_position, current_position = track[-2], track[-1]
                                
                                for region in self.regions:
                                    if cls not in region["tagsInThisRegion"]:
                                        continue
                                        
                                    region_name = region["name"]
                                    
                                    for line in region["lines"]:
                                        self.count(track_id, cls, cls_name, region_name, line, previous_position, current_position, conf, current_time)
                        
                        # Blur objects
                        if self.blur_humans and blur_boxes:
                            frame = self.blur_objects(frame, blur_boxes)
                                                
                    # Save and reset counts
                    if not self.only_simulation:
                        if time.time() - last_save_time >= self.counts_save_intervall:
                            self.queue_manager.save_counts(self.counts) if not self.only_simulation and self.counts else None
                            last_save_time = time.time()
                            
                            # Reset
                            self.counts = defaultdict(lambda: defaultdict(lambda: {
                                "IN": defaultdict(lambda: {"count": 0, "total_conf": 0}), 
                                "OUT": defaultdict(lambda: {"count": 0, "total_conf": 0})
                            }))
                            self.track_history = defaultdict(list)
                            #self.crossed_lines = defaultdict(set)
                    
                    preprocess = results[0].speed['preprocess']
                    inference = results[0].speed['inference']
                    postprocess = results[0].speed['postprocess']
                    self.performance_metrics(preprocess, inference, postprocess)

                    if self.only_simulation:
                        frame_path = os.path.join(self.temp_dir, f"frame_{self.frame_count_sim:06d}.jpg")
                        cv2.imwrite(frame_path, frame)
                        self.frame_count_sim += 1

                    try:
                        self.last_frame = frame.copy()
                    except Exception as e:
                        logger.error("Could not copy frame: " + str(e))
                        self.last_frame = None
                    
                self.frame_count += 1

            logger.info("Inference peacefully stopped.")
        except Exception as e:
            error = "Error in inference: " + str(e)
            logger.error(error)
            self.deactivate()
            raise Exception(error)
        finally:
            if 'model' in locals():
                del model
            
            if self.device != "cpu":
                import torch
                torch.cuda.empty_cache()

            if self.only_simulation and self.save_sim:
                self.save_simulation()
            
            self.deactivate()

    def save_simulation(self):
        video_writer = None
        try:
            datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            frame_paths = sorted(glob.glob(os.path.join(self.temp_dir, "*.jpg")))
            cover_image = cv2.imread(frame_paths[-1])
            cover_image_filename = f"simvid_{self.deviceConfigId}_{datetime_str}.jpg"
            cover_image_path = os.path.join(VID_PATH, cover_image_filename)
            cv2.imwrite(cover_image_path, cover_image)
            
            video_filename = f"simvid_{self.deviceConfigId}_{datetime_str}.mp4"
            video_filename_temp = f"simvid_{self.deviceConfigId}_{datetime_str}_temp.mp4"
            output_file = os.path.join(VID_PATH, video_filename_temp)
            final_output_file = os.path.join(VID_PATH, video_filename)
            
            video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), 
                                          self.fps, (self.frame_width, self.frame_height))
            
            # Get Frames and write to video
            for frame_path in frame_paths:
                frame = cv2.imread(frame_path)
                video_writer.write(frame)
                os.remove(frame_path)
                
            video_writer.release()
            
            try:
                convert_video(output_file, final_output_file)
                logger.info(f"Video successfully converted")
            except RuntimeError as e:
                logger.error(str(e))
                raise Exception(str(e))

            if os.path.exists(output_file):
                os.remove(output_file)

            total_in = 0
            total_out = 0
            total_in_conf = 0
            total_out_conf = 0
            
            for region_name, directions in self.counts.items():
                for direction, counts in directions.items():
                    for direction_type, classes in counts.items():
                        if direction_type == "IN":
                            for cls_name, data in classes.items():
                                total_in += data["count"]
                                total_in_conf += data["total_conf"]

                        elif direction_type == "OUT":
                            for cls_name, data in classes.items():
                                total_out += data["count"]
                                total_out_conf += data["total_conf"]
            
            avg_counts = (total_in + total_out) / 2 if (total_in + total_out) > 0 else 1
            detection_ratio = self.last_track_id / avg_counts if avg_counts > 0 else 0

            self.model_type = self.model_str.split(".")[0].split("/")[-1].split("_")[0]
            

            self.format = format_check(self.format)

            json_data = {
                "datetime": datetime_str,
                "deviceConfigId": self.deviceConfigId,
                "model": self.model_type,
                "imgsz": self.imgsz,
                "format": self.format,
                "iou": self.iou,
                "conf": self.conf,
                "tracker": self.tracker,
                "quantization": self.quantization,
                "device": self.device,
                "vid_stride": self.vid_stride,
                "resolution": (self.frame_width, self.frame_height),
                "fps": self.fps,
                "performance": self.get_performance_metrics(),
                "counts": self.counts,
                "last_track_id": self.last_track_id,
                "detection_ratio": detection_ratio,
                "total_in": total_in,
                "total_out": total_out,
                "total_in_conf":  total_in_conf / total_in if total_in and total_in_conf > 0 else 0,
                "total_out_conf": total_out_conf / total_out if total_out and total_out_conf > 0 else 0,
            }

            json_filename = f"simvid_{self.deviceConfigId}_{datetime_str}.json"
            json_file_path = os.path.join(VID_PATH, json_filename)

            with open(json_file_path, 'w') as f:
                json.dump(json_data, f, indent=4)

            logger.info(f"JSON file saved successfully: {json_file_path}")

        except Exception as e:
            logger.error(f"Error saving video or JSON file: {str(e)}")
        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None

            from src.control import stop_stream
            stop_stream()

            if self.stream is not None:
                self.stream = None

            import gc
            gc.collect()
            return True, "Simulation abgeschlossen"