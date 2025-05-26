import os
from settings import EXPORTS_PATH

""" Check if the model already exists in the specified format and with the given parameters.
    Args:
        weights (str): Path to the model weights file.
        format (str): The format to export the model to.
        export_args (dict): Dictionary of export arguments.
    Returns:
        bool: True if the model exists, False otherwise.
        str: The path to the existing model if it exists, None otherwise.
"""

# We don't want to export the model everytime when we do tests
# https://docs.ultralytics.com/modes/export/#export-formats

def check_if_model_exists(weights, format, export_args):

    model_basename = os.path.basename(weights).split('.')[0]
    
    filtered_export_args = {}
    if format == 'torchscript':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'optimize', 'batch']}
    elif format == 'onnx':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'dynamic', 'simplify', 'opset', 'batch']}
    elif format == 'openvino':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'engine':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'dynamic', 'simplify', 'workspace', 'int8', 'batch']}
    elif format == 'coreml':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'nms', 'batch']}
    elif format == 'saved_model':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'keras', 'int8', 'batch']}
    elif format == 'pb':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'batch']}
    elif format == 'tflite':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'edgetpu':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz']}
    elif format == 'tfjs':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'int8', 'batch']}
    elif format == 'paddle':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'batch']}
    elif format == 'ncnn':
        filtered_export_args = {k: v for k, v in export_args.items() if k in ['imgsz', 'half', 'batch']}
    else:
        filtered_export_args = export_args
    
    # Generate parameter suffix based on the filtered export arguments
    param_suffix = '_' + '_'.join([f"{key}_{value}" for key, value in filtered_export_args.items() 
                                if key in ['imgsz', 'half', 'int8', 'dynamic', 'simplify', 'opset', 'workspace', 'nms', 'batch'] and value])
    
    # Different formats have different directory structures
    if format == 'torchscript':
        expected_filename = f"{model_basename}.torchscript"
    elif format == 'onnx':
        expected_filename = f"{model_basename}.onnx"
    elif format == 'openvino':
        dirname = f"{model_basename}_openvino_model"
        if filtered_export_args.get('int8'):
            dirname = f"{model_basename}_int8_openvino_model"
        expected_filename = dirname
    elif format == 'engine':
        expected_filename = f"{model_basename}.engine"
    elif format == 'coreml':
        expected_filename = f"{model_basename}.mlpackage"
    elif format == 'saved_model':
        expected_filename = f"{model_basename}_saved_model"
    elif format == 'pb':
        expected_filename = f"{model_basename}_saved_model/{model_basename}.pb"
    elif format == 'tflite':
        base = f"{model_basename}_saved_model/{model_basename}"
        if filtered_export_args.get('int8'):
            expected_filename = f"{base}_int8.tflite"
        elif filtered_export_args.get('half'):
            expected_filename = f"{base}_float16.tflite"
        else:
            expected_filename = f"{base}_float32.tflite"
    elif format == 'edgetpu':
        expected_filename = f"{model_basename}_saved_model/{model_basename}_full_integer_quant_edgetpu.tflite"
    elif format == 'tfjs':
        expected_filename = f"{model_basename}_web_model"
    elif format == 'paddle':
        expected_filename = f"{model_basename}_paddle_model"
    elif format == 'ncnn':
        expected_filename = f"{model_basename}_ncnn_model"
    else:
        expected_filename = f"{model_basename}.{format}"


    # Two options to try - first the directory format:
    dir_path = os.path.join(EXPORTS_PATH, f"{expected_filename}{param_suffix}")
    file_in_dir_path = os.path.join(dir_path, os.path.basename(expected_filename))
    
    
    # Check if either path exists
    if os.path.exists(file_in_dir_path):
        return True, file_in_dir_path
    
    # For directory-based formats
    directory_formats = ['openvino', 'saved_model', 'tfjs', 'paddle', 'ncnn', 'coreml']
    if format in directory_formats and os.path.exists(dir_path):
        return True, dir_path

    return False, None

