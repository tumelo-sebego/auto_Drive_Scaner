
import os

def get_valid_folder_path(path):
    if path == '.':
        path = os.getcwd()
    elif path == '':
        path = os.getcwd()
    
    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return None, "Path does not exist."
    
    if not os.path.isdir(path):
        return None, "Path is not a directory."
        
    return path, None
