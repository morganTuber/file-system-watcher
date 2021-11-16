from typing import List
from os import path, getcwd

# path where processed_files.txt is located
# processed files should never be deleted for performance reasons
PROCESSED_FILE_PATH = path.join(getcwd(), "processed_files.txt")


def get_processed_files() -> List[str]:
    """
    Return all the processed files from processed_files.txt as an array
    """
    processed_files: List[str] = []

    with open(PROCESSED_FILE_PATH, "r") as f:
        processed_files = f.read().splitlines()
    return processed_files


def set_processed_files(files: List[str]):
    """
    Set processed files in processed_files.txt
    """
    with open(PROCESSED_FILE_PATH, "w") as f:
        f.write("\n".join(files))


def add_processed_file(file_name: str):
    """
    Add newly processed file to processed_files.txt
    """
    processed_files = set([*get_processed_files(), file_name])
    print(f"Adding {file_name} to processed_files.txt")
    set_processed_files(list(processed_files))


def remove_processed_file(file_name: str):
    """
    Remove processed file from processed_files.txt
    """
    processed_files = [file for file in get_processed_files() if file != file_name]
    set_processed_files(processed_files)


def is_file_processed(file_name: str) -> bool:
    """
    Check whether a file is already processed or not
    """
    return file_name in get_processed_files()
