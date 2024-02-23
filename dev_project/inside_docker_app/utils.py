import os
import shutil

try:
    from .logger import get_module_logger
except:
    from logger import get_module_logger

_logger = get_module_logger(__name__)

def delete_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            _logger.warning(f"Failed to delete {file_path}. Reason: {e}")
            exit()