import os
import piexif
import datetime
import subprocess

def get_video_duration(file_path):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        return float(result.stdout)
    except subprocess.CalledProcessError:
        print(f"Error: Failed to read video file '{file_path}'")
        return None


def rename_short_videos(directory):
    for file_name in os.listdir(directory):
        if file_name.startswith('.'):
            continue
        if file_name.lower().endswith(('.mp4', '.mov')) and not file_name.startswith('z_DELETE_'):
            file_path = os.path.join(directory, file_name)
            duration = get_video_duration(file_path)
            if duration is not None and duration < 4:
                created_datetime = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                new_name = f"z_DELETE_{created_datetime.strftime('%Y%m%d%H%M%S')}.{file_name.split('.')[-1]}"
                new_path = os.path.join(directory, new_name)
                os.rename(file_path, new_path)
                print(f"Renamed short video: {file_name} -> {new_name}")


directory = input("Enter the path to the directory containing the video files: ")
rename_short_videos(directory)