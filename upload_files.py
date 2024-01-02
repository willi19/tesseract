import os
import shutil

def copy_directory_with_ignore_existing(source_path, destination_path):
    """
    Copy the contents of the source directory to the destination directory.
    If a file or directory already exists in the destination, it will be ignored.

    :param source_path: Path to the source directory.
    :param destination_path: Path to the destination directory.
    """
    for item in os.listdir(source_path):
        print(item)
        s = os.path.join(source_path, item)
        d = os.path.join(destination_path, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                shutil.copytree(s, d)
            else:
                copy_directory_with_ignore_existing(s, d)
        else:
            if not os.path.exists(d):
                shutil.copy2(s, d)

# Example usage
source_directory = "data"
destination_directory = "shared_data"
copy_directory_with_ignore_existing(source_directory, destination_directory)
