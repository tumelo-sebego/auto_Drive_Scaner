
import os
import threading
from multiprocessing import Pool, cpu_count

def _scan_directory(directory):
    files = []
    try:
        for name in os.listdir(directory):
            try:
                full_path = os.path.join(directory, name)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    files.append((full_path, size))
            except (PermissionError, FileNotFoundError):
                pass
    except (PermissionError, FileNotFoundError):
        pass
    return files

class Scanner:
    def __init__(self, path):
        self.path = path
        self.file_list = []
        self.progress_tracker = {"done": 0, "total": 1}
        self.stop_event = threading.Event()

    def scan_folder(self, progress_callback=None):
        all_dirs = [root for root, _, _ in os.walk(self.path)]
        total_dirs = len(all_dirs)
        self.progress_tracker["total"] = total_dirs

        with Pool(processes=cpu_count()) as pool:
            results = pool.imap_unordered(_scan_directory, all_dirs)
            for i, files in enumerate(results):
                if self.stop_event.is_set():
                    pool.terminate()
                    break
                self.file_list.extend(files)
                if progress_callback:
                    progress_callback(i + 1, total_dirs)
        
        return self.file_list

    def start_scan(self):
        scan_thread = threading.Thread(target=self.scan_folder, args=(self.update_progress,))
        scan_thread.start()
        return scan_thread

    def update_progress(self, done, total):
        self.progress_tracker["done"] = done
        self.progress_tracker["total"] = total

    def stop_scan(self):
        self.stop_event.set()

