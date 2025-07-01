
from colorama import init, Fore, Style
import humanize
from config import Config

init(autoreset=True)

config = Config()
primary_color_name = config.get('colors', {}).get('primary', 'green').upper()
PRIMARY_COLOR = getattr(Fore, primary_color_name, Fore.GREEN)
RESET = Style.RESET_ALL

def print_help():
    print(f"""
{PRIMARY_COLOR}Usage:{RESET}
  - Enter a path to scan for large files.
  - Type 'q' or 'quit' to exit the application at any prompt.
  - Type 'help' to display this help message again.
""")

def get_input(prompt):
    response = input(prompt).strip().lower()
    if response in ['help']:
        print_help()
        return get_input(prompt)
    if response in ['q', 'quit']:
        raise SystemExit("Exiting application.")
    return response

def print_welcome_message():
    print(f"{PRIMARY_COLOR}👋 Hi there! I'm miniBot and I'm here to help you scan and delete big files in your system!{RESET}\n")
    print_help()

def get_folder_path():
    default_path = config.get('default_path', '.')
    return get_input(f"{PRIMARY_COLOR}🗂️  Please enter the path you'd like me to scan (default: '{default_path}'): {RESET}")

def print_scan_message(folder):
    print(f"\n{PRIMARY_COLOR}🔎 Scanning {folder}, please hold on...{RESET}\n")

def print_scan_complete():
    print("\n\n✅ Scan complete!\n")

def print_no_files_found():
    print("😔 I couldn't find any files in that location. Maybe try another folder?\n")

def print_goodbye_message():
    print("\n👋 Thanks for using miniBot! Goodbye!")

def ask_to_delete_files():
    return get_input("\n🧹 Would you like me to help you delete any of these files? (y/n): ")

def ask_for_file_to_delete():
    return get_input("\nEnter the number of the file you want to delete (or 'q' to quit deleting): ")

def ask_to_scan_another_folder():
    return get_input("\n🔄 Would you like to scan another folder? (y/n): ")

def print_updated_list_message():
    print(f"\n{PRIMARY_COLOR}📋 Updated list of biggest files:{RESET}")

def print_all_files_processed():
    print(f"\n{PRIMARY_COLOR}✨ All files have been processed!{RESET}")

def print_table(file_list, top_n=20):
    if not file_list:
        return

    max_no_width = len(str(min(top_n, len(file_list))))
    max_size_width = max([len(humanize.naturalsize(size)) for _, size in file_list[:top_n]], default=4)
    max_path_width = min(80, max([len(path) for path, _ in file_list[:top_n]], default=9))

    max_no_width = max(max_no_width, 3)
    max_size_width = max(max_size_width, 4)
    max_path_width = max(max_path_width, 9)

    print(f"\n{PRIMARY_COLOR}{'┌' + '─' * (max_no_width + 2) + '┬' + '─' * (max_size_width + 2) + '┬' + '─' * (max_path_width + 2) + '┐'}{RESET}")
    print(f"{PRIMARY_COLOR}│{RESET} {'No.':^{max_no_width}} {PRIMARY_COLOR}│{RESET} {'Size':^{max_size_width}} {PRIMARY_COLOR}│{RESET} {'File Path':^{max_path_width}} {PRIMARY_COLOR}│{RESET}")
    print(f"{PRIMARY_COLOR}{'├' + '─' * (max_no_width + 2) + '┼' + '─' * (max_size_width + 2) + '┼' + '─' * (max_path_width + 2) + '┤'}{RESET}")

    for idx, (path, size) in enumerate(file_list[:top_n], 1):
        display_path = path if len(path) <= max_path_width else f"...{path[-(max_path_width-3):]}"
        size_str = humanize.naturalsize(size)
        print(f"{PRIMARY_COLOR}│{RESET} {str(idx):>{max_no_width}} {PRIMARY_COLOR}│{RESET} {size_str:>{max_size_width}} {PRIMARY_COLOR}│{RESET} {display_path:<{max_path_width}} {PRIMARY_COLOR}│{RESET}")

    print(f"{PRIMARY_COLOR}{'└' + '─' * (max_no_width + 2) + '┴' + '─' * (max_size_width + 2) + '┴' + '─' * (max_path_width + 2) + '┘'}{RESET}")

def print_progress_bar(progress_tracker):
    bar_length = 30
    completed, total = progress_tracker["done"], progress_tracker["total"]
    percentage = (completed / total) * 100 if total else 0
    filled_length = int(bar_length * completed // total) if total else 0
    bar = f"{PRIMARY_COLOR}{'█' * filled_length}{RESET}{'░' * (bar_length - filled_length)}"
    print(f"\r[{bar}] {percentage:.2f}% complete...", end="", flush=True)

