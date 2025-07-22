import os
import random
import tkinter as tk
from tkinter import filedialog
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def sanitize_filename(name):
    # 파일명으로 사용할 수 없는 문자 제거 또는 대체
    return "".join([c if c.isalnum() or c in " .-_()" else '_' for c in name])

def rename_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.mp3') or filename.endswith('.flac'):
            file_path = os.path.join(folder_path, filename)
            try:
                if filename.endswith('.mp3'):
                    audio = MP3(file_path, ID3=ID3)
                    artist = audio.get('TPE1', None)
                    title = audio.get('TIT2', None)
                elif filename.endswith('.flac'):
                    audio = FLAC(file_path)
                    artist = audio.get('artist', None)
                    title = audio.get('title', None)

                if artist and title:
                    new_name = f"{artist[0]}-{title[0]}"
                    new_name = sanitize_filename(new_name)
                    new_filename = f"{new_name}{os.path.splitext(filename)[1]}"
                    new_file_path = os.path.join(folder_path, new_filename)
                    os.rename(file_path, new_file_path)
                    print(f"Renamed '{filename}' to '{new_filename}'")
                else:
                    print(f"Metadata not found for '{filename}', no rename performed.")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

def select_folder_and_rename():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory()  # Open dialog to choose folder
    if folder_path:
        rename_files_in_folder(folder_path)
    else:
        print("No folder selected.")

# Run the function
select_folder_and_rename()
