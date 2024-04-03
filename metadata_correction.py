import os
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime
from itertools import chain

# Set up argument parsing
parser = argparse.ArgumentParser(description='Correct metadata and rename image files.')
parser.add_argument('directory', type=str, help='The path to the directory containing the image files.')
parser.add_argument('--recursive', action='store_true', help='Process files recursively in subdirectories.')
args = parser.parse_args()

directory_path = Path(args.directory)

# Set up logging
log_directory = os.path.expanduser('~/logs')
os.makedirs(log_directory, exist_ok=True)
file_name = os.path.basename(__file__).replace(" ", "_")
log_filename = Path(log_directory) / f"{file_name}_{datetime.now().strftime('%a')}.log"

# log to file
logging.basicConfig(filename=log_filename, encoding='utf-8', level=logging.INFO, format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def correct_metadata_and_rename(file_path):
    logging.info(f"Processing file: {file_path}")

    # Read DateTimeOriginal using exiftool
    try:
        output = subprocess.check_output(['exiftool', '-DateTimeOriginal', '-s3', str(file_path)], universal_newlines=True, stderr=subprocess.STDOUT)
        datetime_original = output.strip()
        logging.debug(f"exiftool output: {output.strip()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error reading EXIF data using exiftool: {file_path}. Error: {str(e)}")
        logging.error(f"exiftool output: {e.output}")
        return

    if not datetime_original:
        logging.warning(f"Skipping image file with no DateTimeOriginal attribute: {file_path}")
        return

    logging.debug(f"DateTimeOriginal: {datetime_original}")

    # Update DateTimeDigitized using exiftool
    try:
        subprocess.run(['exiftool', '-DateTimeDigitized=' + datetime_original, '-overwrite_original', str(file_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error updating EXIF data using exiftool: {file_path}. Error: {str(e)}")
        logging.error(f"exiftool output: {e.output.decode('utf-8')}")
        return

    # Rename file
    new_name = f"{datetime_original.replace(':', '').replace(' ', '_')}_photo"
    new_file_path = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
    os.rename(file_path, new_file_path)
    logging.info(f"Renamed file: {file_path} -> {new_file_path}")

logging.info(f"Processing files in directory {directory_path}")

# Determine the file iteration method based on the 'recursive' argument
if args.recursive:
    file_iterator = directory_path.rglob("*.[jJ][pP][gG]")
    file_iterator = chain(file_iterator, directory_path.rglob("*.[cC][rR][2]"))
else:
    file_iterator = directory_path.glob("*.[jJ][pP][gG]")
    file_iterator = chain(file_iterator, directory_path.glob("*.[cC][rR][2]"))

# Iterate over each file
for file_path in file_iterator:
    # Skip over any files that start with a dot
    if file_path.name.startswith('.'):
        logging.debug(f"Skipping file {file_path} which starts with '.'")
        continue
    # Call the function to correct the metadata and rename the file
    correct_metadata_and_rename(file_path)