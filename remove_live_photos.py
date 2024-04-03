import os
import piexif
import datetime
import subprocess
import logging
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='Rename short videos and delete empty directories.')
parser.add_argument('directory', type=str, help='The path to the directory containing the video files.')
parser.add_argument('--threshold', type=float, default=3, help='The duration threshold for short videos (in seconds).')
parser.add_argument('--delete', action='store_true', help='Delete all files and directories that start with "z_DELETE_".')
args = parser.parse_args()

directory = Path(args.directory)
duration_threshold = args.threshold

# Set up logging
log_directory = os.path.expanduser('~/logs')
os.makedirs(log_directory, exist_ok=True)
file_name = os.path.basename(__file__).replace(" ", "_")
log_filename = Path(log_directory) / f"{file_name}_{datetime.datetime.now().strftime('%a')}.log"

# log to file
logging.basicConfig(filename=log_filename, encoding='utf-8', level=logging.INFO, format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def delete_empty_directories(directory):
    for dir_path, dir_names, file_names in os.walk(directory, topdown=False):
        if not file_names and not dir_names:
            try:
                os.rmdir(dir_path)
                logging.info(f"Deleted empty directory: {dir_path}")
            except OSError as e:
                logging.error(f"Error: Failed to delete empty directory '{dir_path}': {e}")

def get_video_duration(file_path):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        return float(result.stdout)
    except subprocess.CalledProcessError:
        logging.error(f"Error: Failed to read video file '{file_path}'")
        return None

def rename_short_videos(directory, duration_threshold):
    video_files = list(directory.glob('**/*.[mM][pP]4')) + list(directory.glob('**/*.[mM][oO][vV]'))

    for file_path in video_files:
        if not file_path.name.startswith('z_DELETE_'):
            duration = get_video_duration(file_path)
            if duration is not None and duration < duration_threshold:
                created_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
                new_name = f"z_DELETE_{created_datetime.strftime('%Y%m%d%H%M%S')}{file_path.suffix}"
                new_path = file_path.with_name(new_name)
                file_path.rename(new_path)
                logging.info(f"Renamed short video: {file_path.name} -> {new_name}")

if args.delete:
    for dir_path, dir_names, file_names in os.walk(directory):
        for file_name in file_names:
            if file_name.startswith('z_DELETE_'):
                file_path = os.path.join(dir_path, file_name)
                os.remove(file_path)
                logging.info(f"Deleted file: {file_path}")
        for dir_name in dir_names:
            if dir_name.startswith('z_DELETE_'):
                dir_path = os.path.join(dir_path, dir_name)
                os.rmdir(dir_path)
                logging.info(f"Deleted directory: {dir_path}")
    delete_empty_directories(directory)

logging.info(f"Processing files in directory {directory}")
rename_short_videos(directory, duration_threshold)