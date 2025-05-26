from ultralytics import YOLO
import shutil
import os
from settings import EXPORTS_PATH
from src.utils.logger import Logger
from settings import LOG_PATH


logger = Logger("Exporter", LOG_PATH + "/exporter.log")

def move_to_exports(model_path, finalized_export_path):
    destination_path = os.path.join(EXPORTS_PATH, finalized_export_path)

    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)
        
    os.makedirs(destination_path, exist_ok=True)
    
    try:
        if os.path.exists(model_path):
            # Check if model_path is a file or directory
            if os.path.isdir(model_path):
                
                for item in os.listdir(model_path):
                    source_item = os.path.join(model_path, item)
                    dest_item = os.path.join(destination_path, item)
                    
                    if os.path.isdir(source_item):
                        shutil.copytree(source_item, dest_item)
                    else:
                        shutil.copy2(source_item, dest_item)
                        
                return destination_path
                
            else:
                # For single files
                dest_file = os.path.join(destination_path, os.path.basename(model_path))
                logger.info(f"Moving file from {model_path} to {dest_file}")
                shutil.copy2(model_path, dest_file)
                return dest_file
        else:
            logger.warning(f"Model path not found at {model_path}")
            return None
    except Exception as e:
        logger.error(f"Error moving model: {e}")
        return None

def export(weights, format, imgsz, keras, optimize, half, int8, dynamic, simplify, opset, workspace, nms, batch):

    model = YOLO(weights)

    export_args = {
        "imgsz": imgsz,
        "half": half,
        "int8": int8,
        "dynamic": dynamic,
        "simplify": simplify,
        "opset": opset,
        "workspace": workspace,
        "nms": nms,
        "batch": batch,
        "keras": keras,
        "optimize": optimize,
    }
    
    # https://docs.ultralytics.com/de/modes/export/#arguments
    if format == 'torchscript':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'optimize', 'batch']}
    elif format == 'onnx':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'dynamic', 'simplify', 'opset', 'batch']}
    elif format == 'openvino':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'engine':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'dynamic', 'simplify', 'workspace', 'int8', 'batch']}
    elif format == 'coreml':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'nms', 'batch']}
    elif format == 'saved_model':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'keras', 'int8', 'batch']}
    elif format == 'pb':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'batch']}
    elif format == 'tflite':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'edgetpu':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz']}
    elif format == 'tfjs':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'paddle':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'batch']}
    elif format == 'ncnn':
        export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'batch']}


    try:
        # Store the export path returned by model.export()
        export_path = model.export(format=format, **export_args)

        finalized_export_path = export_path + '_' + '_'.join([f"{key}_{value}" for key, value in export_args.items() if key in ['imgsz', 'half', 'int8', 'dynamic', 'simplify', 'opset', 'workspace', 'nms', 'batch'] and value])
        # Move the exported model to the exports directory
        if export_path:
            final_path = move_to_exports(str(export_path), finalized_export_path)
            return final_path
        else:
            error = logger.warning("Export succeeded but no path was returned")
            raise Exception(error)

    except Exception as e:
        error = logger.error(f"Error exporting model: {e}")
        raise Exception(error)
