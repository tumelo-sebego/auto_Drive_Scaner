import sys
import time
import threading
from scanner import Scanner
from file_manager import FileManager
from config import Config
import ui
import utils

def main():
    config = Config()
    top_n = config.get('top_n', 20)
    default_path = config.get('default_path', '.')

    ui.print_welcome_message()

    while True:
        try:
            folder_path = ui.get_folder_path()
            if not folder_path:
                folder_path = default_path
                
            folder_path, error = utils.get_valid_folder_path(folder_path)

            if error:
                print(error)
                continue

            ui.print_scan_message(folder_path)
            
            scanner = Scanner(folder_path)
            scan_thread = scanner.start_scan()

            while scan_thread.is_alive():
                ui.print_progress_bar(scanner.progress_tracker)
                time.sleep(0.1)
            
            ui.print_progress_bar(scanner.progress_tracker)
            ui.print_scan_complete()

            files = scanner.file_list
            if not files:
                ui.print_no_files_found()
                continue

            file_manager = FileManager(files)
            
            file_type_filter = ui.get_input("Enter file type to filter (e.g., .pdf, .jpg), or press Enter to skip: ")
            biggest_files = file_manager.get_biggest_files(top_n, file_type_filter)
            ui.print_table(biggest_files, top_n)

            export_choice = ui.get_input("Export this list to a CSV file? (y/n): ")
            if export_choice == 'y':
                file_manager.export_to_csv(biggest_files)
                print("List exported to largest_files.csv")

            if ui.ask_to_delete_files() == 'y':
                while True:
                    choice = ui.ask_for_file_to_delete()
                    if choice.lower() == 'q':
                        break
                    
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(biggest_files):
                            file_to_delete = biggest_files[idx]
                            confirm = ui.get_input(f"Are you sure you want to delete '{file_to_delete[0]}'? (y/n): ")
                            if confirm == 'y':
                                success, message = file_manager.delete_file(idx)
                                print(message)
                                if success:
                                    biggest_files = file_manager.get_biggest_files(top_n, file_type_filter)
                                    if biggest_files:
                                        ui.print_updated_list_message()
                                        ui.print_table(biggest_files, top_n)
                                    else:
                                        ui.print_all_files_processed()
                                        break
                            else:
                                print("Deletion cancelled.")
                        else:
                            print("Invalid number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            if ui.ask_to_scan_another_folder() != 'y':
                ui.print_goodbye_message()
                break
        except SystemExit as e:
            print(f"\n{e}")
            break
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
