# library imports
import sys
import time
import logging
from os import getcwd, listdir, mkdir, remove, walk
from os import path
from datetime import datetime
from posixpath import join
from zipfile import BadZipFile, ZipFile
from shutil import make_archive, move, rmtree
from watchdog.observers import Observer

# local imports
from processed_file import is_file_processed, add_processed_file
from file_watcher import FileWatcher

# constants
CURRENT_DIR = getcwd()
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")


def remove_txt_files():
    """
	Remove all the .txt files in the current directory
	"""
    for root, _, files in walk(CURRENT_DIR):
        for file in files:
            if file.endswith(".txt") and file != "processed_files.txt":
                remove(path.join(root, file))
                print(f"Removed {file} from {root}")


def zip_files_and_folders():
    for item in listdir(CURRENT_DIR):
        if path.isfile(item) and not item.endswith(tuple([".txt", ".zip"])):
            zip_file_name = f"{CURRENT_DATE}_{item.split('.')[0]}.zip"
            zip_file = ZipFile(zip_file_name, "w")
            zip_file.write(item)
            remove(item)
            zip_file.close()
            print(f"Zipped {item} to {zip_file.filename}")
            add_processed_file(join(CURRENT_DIR, zip_file_name))
        elif path.isdir(item) and item.endswith("database"):
            make_archive(f"{CURRENT_DATE}_{item}", "zip", join(CURRENT_DIR, item))
            print(f"Zipped {item} to {item}.zip")
            rmtree(join(CURRENT_DIR, item))
            if not path.exists(join(CURRENT_DIR, item)):
                mkdir(join(CURRENT_DIR, item))
            move(f"{CURRENT_DATE}_{item}.zip", join(CURRENT_DIR, item))
            print(f"Moved {item}.zip to {item}")
            add_processed_file(join(CURRENT_DIR, f"{CURRENT_DATE}_{item}.zip"))


def extract_zip_file(file_path: str):
    try:
        with ZipFile(file_path) as zip_file:
            # extract all the content inside the zip file into the root directory
            zip_file.extractall()
        remove_txt_files()
        zip_files_and_folders()
    except BadZipFile as e:
        print(e)


def process_zip_files():
    for file in listdir(CURRENT_DIR):
        # if the file ends with .zip and is not already processed, process it
        if file.endswith(".zip") and not is_file_processed(file):
            extract_zip_file(path.join(CURRENT_DIR, file))
            add_processed_file(join(CURRENT_DIR, file))
        # to avoid checking src and other non-related folders
        elif is_file_processed(file):
            print(f"{file} is already processed.Skipping file....")


if __name__ == "__main__":
    # check if processed_files.txt exists in the root directory
    # if the file does not exist, create it
    if not path.exists(join(CURRENT_DIR, "processed_files.txt")):
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
    print(f"Starting to watch {path} for changes...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
