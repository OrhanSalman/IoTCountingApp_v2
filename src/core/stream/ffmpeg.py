import subprocess
import os

# Global variable to track conversion status
conversion_in_progress = False

# Function to convert video simulations, to be playable in the frontend
def convert_video(input_path, output_path):
    global conversion_in_progress
    conversion_in_progress = True
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path, '-vcodec', 'libx264', output_path
        ], check=True)
        conversion_in_progress = False
        return True
    except subprocess.CalledProcessError as e:
        conversion_in_progress = False
        raise RuntimeError(f"Error occurred during video conversion: {e}")

# Get method
def is_conversion_in_progress():
    return conversion_in_progress