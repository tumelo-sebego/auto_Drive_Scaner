
import os
import humanize
import csv

class FileManager:
    def __init__(self, files):
        self.files = files

    def get_biggest_files(self, top_n=20, file_type=None):
        filtered_files = self.files
        if file_type:
            filtered_files = [f for f in self.files if f[0].endswith(file_type)]
        
        filtered_files.sort(key=lambda x: x[1], reverse=True)
        return filtered_files[:top_n]

    def delete_file(self, index):
        if 0 <= index < len(self.files):
            path_to_delete = self.files[index][0]
            file_size = self.files[index][1]
            try:
                os.remove(path_to_delete)
                self.files.pop(index)
                return True, f"Deleted successfully: {humanize.naturalsize(file_size)} - {os.path.basename(path_to_delete)}"
            except Exception as e:
                return False, f"Failed to delete: {e}"
        return False, "Invalid index."

    def export_to_csv(self, file_list, filename="largest_files.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Size (bytes)", "Size (human readable)"])
            for path, size in file_list:
                writer.writerow([path, size, humanize.naturalsize(size)])

