import os
import humanize  # pip install humanize
import threading
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def scan_folder(path, progress_callback=None):
    file_list = []
    all_dirs = []

    # First, collect all directories to estimate progress
    for root, dirs, files in os.walk(path):
        all_dirs.append(root)

    total_dirs = len(all_dirs)

    for idx, root in enumerate(all_dirs):
        for name in os.listdir(root):
            try:
                full_path = os.path.join(root, name)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    file_list.append((full_path, size))
            except (PermissionError, FileNotFoundError):
                pass  # Skip inaccessible files

        if progress_callback:
            progress_callback(idx + 1, total_dirs)

    return file_list

def show_biggest_files(file_list, top_n=20):
    file_list.sort(key=lambda x: x[1], reverse=True)
    print("\nHere are the biggest files I found:\n")
    for idx, (path, size) in enumerate(file_list[:top_n], 1):
        print(f"{idx}. {humanize.naturalsize(size)} - {path}")

def progress_bar_task(stop_event, progress_tracker):
    bar_length = 30
    while not stop_event.is_set():
        completed, total = progress_tracker["done"], progress_tracker["total"]
        percentage = (completed / total) * 100 if total else 0

        filled_length = int(bar_length * completed // total) if total else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        colored_bar = f"{Fore.GREEN}{'█' * filled_length}{Style.RESET_ALL}{'░' * (bar_length - filled_length)}"

        print(f"\r[{colored_bar}] {percentage:.2f}% complete...", end="", flush=True)
        time.sleep(0.1)

def mini_robot():
    print("👋 Hi there! I'm miniRobot and I'm here to help you scan and delete big files in your system!\n")

    while True:
        folder = input("🗂️  Please enter the path you'd like me to scan (example: C:/Users/YourName): ").strip()

        if not os.path.exists(folder):
            print("⚠️  Oops! That path doesn't seem to exist. Let's try again!\n")
            continue

        print("\n🔎 Scanning your files, please hold on...\n")

        stop_event = threading.Event()
        progress_tracker = {"done": 0, "total": 1}

        spinner_thread = threading.Thread(target=progress_bar_task, args=(stop_event, progress_tracker))
        spinner_thread.start()

        def update_progress(done, total):
            progress_tracker["done"] = done
            progress_tracker["total"] = total

        files = scan_folder(folder, progress_callback=update_progress)

        stop_event.set()
        spinner_thread.join()
        print("\n\n✅ Scan complete!\n")

        if not files:
            print("😔 I couldn't find any files in that location. Maybe try another folder?\n")
            continue

        show_biggest_files(files)

        delete_choice = input("\n🧹 Would you like me to help you delete any of these files? (y/n): ").lower()
        
        if delete_choice == 'y':
            while True:
                num = input("\nEnter the number of the file you want to delete (or 'q' to quit deleting): ")
                if num.lower() == 'q':
                    print("\n🛑 Done deleting files. If you want, you can scan another folder next!")
                    break
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(files):
                        path_to_delete = files[idx][0]
                        confirm = input(f"⚠️  Are you sure you want to delete '{path_to_delete}'? (y/n): ")
                        if confirm.lower() == 'y':
                            os.remove(path_to_delete)
                            print("🗑️  Deleted successfully!")
                        else:
                            print("👍 No worries, I skipped that file.")
                    else:
                        print("❌ Invalid number. Please pick a number from the list.")
                except Exception as e:
                    print(f"⚠️ Error: {e}")
        else:
            print("\n👍 No problem! Let's scan another location!\n")

if __name__ == "__main__":
    mini_robot()
