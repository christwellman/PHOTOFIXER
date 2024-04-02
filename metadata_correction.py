import os
import piexif
import logging
import exifread
from datetime import datetime

logging.basicConfig( encoding='utf-8', level=logging.INFO, format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def correct_metadata_and_rename(file_path):
    # Extract EXIF data
    exif_dict = piexif.load(file_path)
    if not exif_dict['Exif']:
        return

    datetime_original = exif_dict['Exif'][36867]
    datetime_original = datetime.strptime(datetime_original.decode('utf-8'), "%Y:%m:%d %H:%M:%S")

    # Update 'Create Date'
    exif_dict['Exif'][36868] = datetime_original.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)

    # Rename file
    new_name = f"{datetime_original.strftime('%Y%m%d_%H%M%S')}_photo"
    new_file_path = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
    os.rename(file_path, new_file_path)

# Prompt for the path to the directory
directory_path = input('Enter the path to the directory containing the image files: ')

# Iterate over each subdirectory, directory, and file in the directory
for subdir, dirs, files in os.walk(directory_path):
    for file_name in files:
        # Skip over any files that start with a dot
        if file_name.startswith('.'):
            continue
        # Check if the file is an image (.jpg or .jpeg)
        if file_name.lower().endswith(('.jpg', '.jpeg')):
            # Construct the full file path
            file_path = os.path.join(subdir, file_name)
            # Call the function to correct the metadata and rename the file
            correct_metadata_and_rename(file_path)
