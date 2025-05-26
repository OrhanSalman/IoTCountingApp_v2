import time
import cv2
import os
from src.utils.logger import Logger
from picamera2 import Picamera2
from src.core.stream.ffmpeg import convert_video
from settings import (
    LOG_PATH,
    IMG_PATH,
    VID_PATH,
)

logger = Logger("PiCameraStream", LOG_PATH + "/stream.log")

img_path = IMG_PATH
vid_path = VID_PATH


class CameraStream:
    def __init__(self, source, main_resolution, fps, stream_channel):
        self.resolution = main_resolution
        self.fps = fps
        self.source = source
        self.frame_times = []
        self.current_frame_time = 0
        self.frame_counter = 0
        self.stream_channel = stream_channel
        self.is_capturing = False
        
        try:
            self.stream = Picamera2()
            if self.stream:
                
                if not self.stream_channel == "greyscale":
                    preview_config = self.stream.create_preview_configuration(
                    main={"size": self.resolution, "format": self.stream_channel},
                )
                else:
                    preview_config = self.stream.create_preview_configuration(
                    main={"size": self.resolution},
                    )
                    self.stream.set_controls({"Saturation": 0.0}) # Does not work ?
                self.stream.set_controls({"FrameRate": self.fps})
                self.stream.configure(preview_config)
                self.stream.start()
        except Exception as e:
            error = f"Error initializing camera: {e}"
            logger.error(error)
            self.stream = None

    def __del__(self):
        if self.stream:
            self.stop_camera()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stop_camera()

    #def isOpened(self):
    #    return self.stream is not None and self.stream.is_open()

    def isOpened(self):
        #return self.stream is not None and self.stream.is_open
        return self.stream is not None


    def get_details(self):
        return {
            "resolution": self.resolution,
            "fps": self.fps,
            "source": self.source
        }
    
    def read(self):
        if self.stream:
            try:
                start_time = time.time()
                frame = self.stream.capture_array()
                end_time = time.time()

                if frame is not None:
                    self.frame_counter += 1
                    frame_time = (end_time - start_time) * 1000
                    self.current_frame_time = frame_time
                    self.frame_times.append(frame_time)
                    return True, frame
                else:
                    error = "Failed to capture frame."
                    logger.error(error)
                    return False, error
            except Exception as e:
                error = f"Error capturing frame: {e}"
                logger.error(error)
                return False, error
        return False, "Camera stream is not initialized."

    
    def start_camera(self):
        if self.stream:
            self.stream.start()

    def stop_camera(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def capture_image(self):
        if self.stream:
            try:
                frame = self.stream.capture_array()
                if frame is not None:
                    # Save image
                    cv2.imwrite(os.path.join(img_path, "capture.jpg"), frame)
                    return True, frame
                else:
                    logger.error("Failed to capture image.")
                    return False, None
            except Exception as e:
                error = f"Error capturing image: {e}"
                logger.error(error)
                return False, error
        else:
            error = "Camera is not open."
            logger.error(error)
            return False, error


    def capturing(self):
        return self.is_capturing
    
    def capture_video(self, duration):
        if self.stream:
            self.is_capturing = True
            try:
                frame_width, frame_height = self.resolution
                size = (frame_width, frame_height)

                temp_video_path = os.path.join(vid_path, 'capture_temp.mp4')
                final_video_path = os.path.join(vid_path, 'capture.mp4')
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_video_path, fourcc, self.fps, size)

                expected_frames = int(duration * self.fps)
                frame_count = 0
                
                #start_time = time.time()
                #while time.time() - start_time < duration:
                while frame_count < expected_frames:
                    frame = self.stream.capture_array()
                    if frame is not None:
                        out.write(frame)
                        frame_count += 1
                    else:
                        error = "Failed to capture frame."
                        logger.error(error)
                        out.release()
                        return False, error

                out.release()

                convert_video(temp_video_path, final_video_path)

                self.is_capturing = False
                return True, "Video finished. You Can now run a simulation on the video."
            except Exception as e:
                self.is_capturing = False
                error = f"Error capturing video: {e}"
                logger.error(error)
                return False, error
        else:
            self.is_capturing = False
            error = "Camera is not open."
            logger.error(error)
            return False, error


    # Get the current frame position in milliseconds
    def get_CAP_PROP_POS_MSEC(self):
        return self.current_frame_time

    # Returns the number of frames
    def get_CAP_PROP_POS_FRAMES(self):
        return self.frame_counter