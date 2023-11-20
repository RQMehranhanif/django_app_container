import os


def create_folder_if_not_exist( folder_name ):
    # Create the log folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)