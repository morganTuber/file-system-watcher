# library imports
import sys
import time
import logging
import coloredlogs
from os import getcwd, listdir, mkdir, remove, walk
from os.path import join, exists, isfile, isdir
from datetime import datetime
from zipfile import BadZipFile, ZipFile
from shutil import make_archive, move, rmtree
from watchdog.observers import Observer

# initialize the logger
coloredlogs.install(level="DEBUG")

# local imports
from processed_file import is_file_processed, add_processed_file
from file_watcher import FileWatcher

# constants
CURRENT_DIR = getcwd()
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
# valid extensions to be zipped in a separate folder
VALID_EXTENSIONS = tuple([".csv"])
# txt file to not delete
VALID_TXT_FILES = ["processed_files.txt", "requirements.txt"]


def remove_txt_files():
    """
	Remove all the .txt files in the current directory
	"""
    for root, _, files in walk(CURRENT_DIR):
        for file in files:
            if file.endswith(".txt") and file not in VALID_TXT_FILES:
                remove(join(root, file))
                logging.info(f"Removed {file} from {root}")


def zip_files_and_folders():
    for item in listdir(CURRENT_DIR):
        if isfile(item) and item.endswith(VALID_EXTENSIONS):
            try:
                zip_file_name = f"{CURRENT_DATE}_{item.split('.')[0]}.zip"
                zip_file = ZipFile(zip_file_name, "w")
                zip_file.write(item)
                remove(item)
                zip_file.close()
                logging.info(f"Zipped {item} to {zip_file.filename}")
                add_processed_file(join(CURRENT_DIR, zip_file_name))
            except Exception as e:
                logging.critical(e)
        elif isdir(item) and item.endswith("database"):
            try:
                make_archive(f"{CURRENT_DATE}_{item}", "zip", join(CURRENT_DIR, item))
                logging.info(f"Zipped {item} to {item}.zip")
                rmtree(join(CURRENT_DIR, item))
                if not exists(join(CURRENT_DIR, item)):
                    mkdir(join(CURRENT_DIR, item))
                move(f"{CURRENT_DATE}_{item}.zip", join(CURRENT_DIR, item))
                logging.info(f"Moved {item}.zip to {item}")
                add_processed_file(join(CURRENT_DIR, f"{CURRENT_DATE}_{item}.zip"))
            except Exception as e:
                logging.error(e)


def extract_zip_file(file_path: str):
    try:
        with ZipFile(file_path) as zip_file:
            # extract all the content inside the zip file into the root directory
            zip_file.extractall()
        remove_txt_files()
        zip_files_and_folders()
    except BadZipFile as e:
        logging.error(e)


def process_zip_files():
    for file in listdir(CURRENT_DIR):
        # if the file ends with .zip and is not already processed, process it
        if file.endswith(".zip") and not is_file_processed(join(CURRENT_DIR, file)):
            extract_zip_file(join(CURRENT_DIR, file))
            add_processed_file(join(CURRENT_DIR, file))
        else:
            logging.warning(
                f"{file} is already processed or not valid.Skipping file...."
            )


if __name__ == "__main__":
    try:
        # check if processed_files.txt exists in the root directory
        # if the file does not exist, create it
        if not exists(join(CURRENT_DIR, "processed_files.txt")):
            with open(join(CURRENT_DIR, "processed_files.txt"), "w") as f:
                f.write("")
        # process the zip files when the script is run for the first time
        process_zip_files()
        # create a file watcher to monitor the current directory for any changes
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        path = sys.argv[1] if len(sys.argv) > 1 else "."
        event_handler = FileWatcher(process_zip_files)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        logging.info(f"Starting to watch {path} for changes...")
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
    except Exception as e:
        logging.error(e)

