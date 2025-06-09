#!/usr/bin/env python3
import os
import sys
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
    
    # Define colors
    GREEN = '\033[38;2;49;112;57m'  # #317039
    RESET = '\033[0m'
    
    # Calculate column widths
    max_no_width = len(str(min(top_n, len(file_list))))
    max_size_width = max([len(humanize.naturalsize(size)) for _, size in file_list[:top_n]], default=4)
    max_path_width = min(80, max([len(path) for path, _ in file_list[:top_n]], default=9))  # Limit path width
    
    # Ensure minimum widths
    max_no_width = max(max_no_width, 3)
    max_size_width = max(max_size_width, 4)
    max_path_width = max(max_path_width, 9)
    
    total_width = max_no_width + max_size_width + max_path_width + 8  # +8 for borders and spaces
    
    # Print top border
    print(f"\n{GREEN}{'┌' + '─' * (max_no_width + 2) + '┬' + '─' * (max_size_width + 2) + '┬' + '─' * (max_path_width + 2) + '┐'}{RESET}")
    
    # Print header
    print(f"{GREEN}│{RESET} {'No.':^{max_no_width}} {GREEN}│{RESET} {'Size':^{max_size_width}} {GREEN}│{RESET} {'File Path':^{max_path_width}} {GREEN}│{RESET}")
    
    # Print header separator
    print(f"{GREEN}{'├' + '─' * (max_no_width + 2) + '┼' + '─' * (max_size_width + 2) + '┼' + '─' * (max_path_width + 2) + '┤'}{RESET}")
    
    # Print data rows
    for idx, (path, size) in enumerate(file_list[:top_n], 1):
        # Truncate path if too long
        display_path = path if len(path) <= max_path_width else f"...{path[-(max_path_width-3):]}"
        size_str = humanize.naturalsize(size)
        
        print(f"{GREEN}│{RESET} {str(idx):>{max_no_width}} {GREEN}│{RESET} {size_str:>{max_size_width}} {GREEN}│{RESET} {display_path:<{max_path_width}} {GREEN}│{RESET}")
    
    # Print bottom border
    print(f"{GREEN}{'└' + '─' * (max_no_width + 2) + '┴' + '─' * (max_size_width + 2) + '┴' + '─' * (max_path_width + 2) + '┘'}{RESET}")

def progress_bar_task(stop_event, progress_tracker):
    GREEN = '\033[38;2;49;112;57m'  # #317039
    RESET = '\033[0m'
    bar_length = 30
    while not stop_event.is_set():
        completed, total = progress_tracker["done"], progress_tracker["total"]
        percentage = (completed / total) * 100 if total else 0

        filled_length = int(bar_length * completed // total) if total else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        colored_bar = f"{GREEN}{'█' * filled_length}{RESET}{'░' * (bar_length - filled_length)}"

        print(f"\r[{colored_bar}] {percentage:.2f}% complete...", end="", flush=True)
        time.sleep(0.1)

def mini_robot():
    GREEN = '\033[38;2;49;112;57m'  # #317039
    RESET = '\033[0m'
    
    print(f"{GREEN}👋 Hi there! I'm miniBot and I'm here to help you scan and delete big files in your system!{RESET}\n")

    while True:
        folder = input(f"{GREEN}🗂️  Please enter the path you'd like me to scan (use '.' for current directory): {RESET}").strip()

        # Handle current directory shortcut
        if folder == '.':
            folder = os.getcwd()
            print(f"{GREEN}📁 Scanning current directory: {folder}{RESET}")
        elif folder == '':
            folder = os.getcwd()
            print(f"{GREEN}📁 No path provided, scanning current directory: {folder}{RESET}")

        # Expand user home directory if needed
        folder = os.path.expanduser(folder)
        
        # Convert to absolute path
        folder = os.path.abspath(folder)

        if not os.path.exists(folder):
            print(f"{GREEN}⚠️  Oops! That path doesn't seem to exist. Let's try again!{RESET}\n")
            continue

        if not os.path.isdir(folder):
            print(f"{GREEN}⚠️  That's not a directory. Please enter a folder path!{RESET}\n")
            continue

        print(f"\n{GREEN}🔎 Scanning {folder}, please hold on...{RESET}\n")

        stop_event = threading.Event()
        progress_tracker = {"done": 0, "total": 1}

        spinner_thread = threading.Thread(target=progress_bar_task, args=(stop_event, progress_tracker))
        spinner_thread.start()

        def update_progress(done, total):
            progress_tracker["done"] = done
            progress_tracker["total"] = total

        try:
            files = scan_folder(folder, progress_callback=update_progress)
        except KeyboardInterrupt:
            print("\n\n⏹️  Scan interrupted by user.")
            stop_event.set()
            spinner_thread.join()
            sys.exit(0)

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
                            try:
                                file_size = files[idx][1]  # Get size before deletion
                                os.remove(path_to_delete)
                                print(f"🗑️  Deleted successfully: {humanize.naturalsize(file_size)} - {os.path.basename(path_to_delete)}")
                                # Remove from list so numbering stays consistent
                                files.pop(idx)
                                
                                # Show updated list if there are still files
                                if files:
                                    print(f"\n{GREEN}📋 Updated list of biggest files:{RESET}")
                                    show_biggest_files(files)
                                else:
                                    print(f"\n{GREEN}✨ All files have been processed!{RESET}")
                                    break
                            except Exception as e:
                                print(f"❌ Failed to delete: {e}")
                        else:
                            print("👍 No worries, I skipped that file.")
                    else:
                        print("❌ Invalid number. Please pick a number from the list.")
                except ValueError:
                    print("❌ Please enter a valid number or 'q' to quit.")
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    sys.exit(0)
        else:
            print("\n👍 No problem! Let's scan another location!\n")

        # Ask if user wants to continue
        continue_choice = input("\n🔄 Would you like to scan another folder? (y/n): ").lower()
        if continue_choice != 'y':
            print("\n👋 Thanks for using miniBot! Goodbye!")
            break

def main():
    try:
        mini_robot()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()