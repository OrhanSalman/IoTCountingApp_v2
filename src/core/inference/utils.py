import cv2
import json
import os
import datetime
from settings import LOG_PATH
from src.utils.logger import Logger


logger = Logger("Inference", LOG_PATH + "/inference.log")


def build_regions(data):
    regions = []
    for region in data:
        lines = []
        points = region["points"]
        isFormationClosed = region["isFormationClosed"]

        for i in range(len(points) - 1):
            line = {
                "start_coord": [points[i]["x"], points[i]["y"]],
                "end_coord": [points[i + 1]["x"], points[i + 1]["y"]],
                "direction": points[i]["direction"],
                "counts": {"in": 0, "out": 0},
                "id": f"{region['id']}-{i}"
            }
            lines.append(line)

        if isFormationClosed and len(points) > 1:
            line = {
                "start_coord": [points[-1]["x"], points[-1]["y"]],
                "end_coord": [points[0]["x"], points[0]["y"]],
                "direction": points[-1]["direction"],
                "counts": {"in": 0, "out": 0},
                "id": f"{region['id']}-{len(points) - 1}"
            }
            lines.append(line)

        regions.append({
            "name": region["roiName"],
            "lines": lines,
            "region_color": tuple(int(region["region_color"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)),
            "text_color": (255, 255, 255),
            "line_thickness": region.get("line_thickness", 2),
            "tagsInThisRegion": list(map(int, region["tagsInThisRegion"]))
        })

    return regions


def draw_regions(frame, regions):
    for region in regions:
        for line in region["lines"]:
            # Zeichne die Linie
            start_point = tuple(line["start_coord"])
            end_point = tuple(line["end_coord"])
            color = region["region_color"]
            thickness = region["line_thickness"]
            cv2.line(frame, start_point, end_point, color, thickness)
            
            # Zeichne die Start- und Endpunkte
            cv2.circle(frame, start_point, 5, color, -1)
            cv2.circle(frame, end_point, 5, color, -1)
            
            # Berechne die Mitte der Linie
            mid_point = (
                (start_point[0] + end_point[0]) // 2,
                (start_point[1] + end_point[1]) // 2
            )
            
            # Zeichne die Richtung und die Zähler an der Mittellinie
            text = f"{line['direction']} in: {line['counts']['in']} out: {line['counts']['out']}"
            cv2.putText(frame, text, mid_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, region["text_color"], 1, cv2.LINE_AA)
        
    return frame


def format_check(format):
    match format:

        case "engine":
            format = "TensorRT"
        case "pt":
            format = "PyTorch"
        case "onnx":
            format = "ONNX"
        case "tflite":
            format = "TensorFlow Lite"
        case "openvino":
            format = "OpenVINO"
        case "edgetpu":
            format = "TFLite Edge TPU"
        case "tfjs":
            format = "TensorFlow.js"
        case "paddle":
            format = "Paddle"
        case "coreml":
            format = "CoreML"
        case "ncnn":
            format = "NCNN"
        case "saved_model":
            format = "TensorFlow SavedModel"
        case "pb":
            format = "TensorFlow GraphDef"
        case "torchscript":
            format = "TorchScript"
        case _:
            logger.error(f"Unknown model format: {format}")
            raise ValueError(f"Unknown model format: {format}")

    return format