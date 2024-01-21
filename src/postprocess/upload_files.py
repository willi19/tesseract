import os
import shutil
import argparse

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
    print("upload done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required = True, help='root')
    args = parser.parse_args()
    
    source = os.path.join("data", args.root)
    dest = os.path.join("shared_data", args.root)
    copy_directory_with_ignore_existing(source, dest)
