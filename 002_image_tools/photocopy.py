import os
import shutil
import hashlib
import threading
from tkinter import Tk, filedialog, Label, Button, messagebox, Frame, Text, Scrollbar, RIGHT, Y, END
from datetime import datetime

CONFIG_FILE = "last_paths.txt"
LOG_FILE = "copy_log.txt"
VALID_EXTENSIONS = ('jpg', 'jpeg', 'png', 'mp4', 'cr3', 'cr2', 'mov')

def is_valid_file(filename):
    return filename.lower().endswith(VALID_EXTENSIONS)

def get_file_modification_date(filepath):
    try:
        modification_time = os.path.getmtime(filepath)
        date = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d')
        return date
    except Exception as e:
        print(f"Error getting modification date: {e}")
        return None

def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def calculate_file_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:  # ✅ 여기를 수정함!
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

def get_existing_hashes(folder_path):
    hash_set = set()
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            file_hash = calculate_file_hash(full_path)
            if file_hash:
                hash_set.add(file_hash)
    return hash_set

def save_last_paths(input_path=None, output_path=None):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"input_path={input_path or getattr(input_path_label, 'input_path', '')}\n")
            f.write(f"output_path={output_path or getattr(output_path_label, 'output_path', '')}\n")
    except Exception as e:
        print(f"경로 저장 실패: {e}")

def load_last_paths():
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("input_path="):
                    path = line.strip().split("=", 1)[1]
                    if os.path.exists(path):
                        input_path_label.config(text=f"입력 경로: {path}")
                        input_path_label.input_path = path
                elif line.startswith("output_path="):
                    path = line.strip().split("=", 1)[1]
                    if os.path.exists(path):
                        output_path_label.config(text=f"출력 경로: {path}")
                        output_path_label.output_path = path
    except Exception as e:
        print(f"경로 불러오기 실패: {e}")

def select_input_path():
    folder = filedialog.askdirectory(title="입력 경로 선택")
    if folder:
        input_path_label.config(text=f"입력 경로: {folder}")
        input_path_label.input_path = folder
        save_last_paths(input_path=folder)

def select_output_path():
    folder = filedialog.askdirectory(title="출력 경로 선택")
    if folder:
        output_path_label.config(text=f"출력 경로: {folder}")
        output_path_label.output_path = folder
        save_last_paths(output_path=folder)

def log_message(message):
    log_output.insert(END, message + "\n")
    log_output.see(END)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    root_window.update()

def threaded_copy_files():
    try:
        copy_files()
    except Exception as e:
        messagebox.showerror("오류", f"복사 중 오류 발생: {e}")

def start_copy_thread():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== 파일 복사 로그 시작: {datetime.now()} ===\n")
    threading.Thread(target=threaded_copy_files, daemon=True).start()

def copy_files():
    input_path = getattr(input_path_label, "input_path", None)
    output_path = getattr(output_path_label, "output_path", None)

    if not input_path or not output_path:
        messagebox.showerror("오류", "입력 경로와 출력 경로를 선택하세요.")
        return

    files = []
    for root, _, filenames in os.walk(input_path):
        for file in filenames:
            if is_valid_file(file):
                files.append((root, file))

    total_files = len(files)
    if total_files == 0:
        messagebox.showinfo("알림", "복사할 파일이 없습니다.")
        return

    copied_files = 0
    skipped_files = 0
    log_output.delete("1.0", END)

    hash_cache = {}

    for idx, (root_dir, file) in enumerate(files, start=1):
        source_file = os.path.join(root_dir, file)
        file_date = get_file_modification_date(source_file)

        if not file_date:
            log_message(f"[{idx}/{total_files}] {source_file} → [수정일 오류] 건너뜀")
            skipped_files += 1
            continue

        date_folder = os.path.join(output_path, file_date)
        create_directory_if_not_exists(date_folder)

        if date_folder not in hash_cache:
            hash_cache[date_folder] = get_existing_hashes(date_folder)

        source_hash = calculate_file_hash(source_file)
        if source_hash in hash_cache[date_folder]:
            log_message(f"[{idx}/{total_files}] {source_file} → [건너뜀: 동일 파일 존재]")
            skipped_files += 1
            continue

        existing_files = [f for f in os.listdir(date_folder) if os.path.isfile(os.path.join(date_folder, f))]
        next_index = len(existing_files) + 1
        _, ext = os.path.splitext(file)
        ext = ext.lower()
        padded_index = str(next_index).zfill(4)
        new_filename = f"{file_date.replace('-', '')}-{padded_index}{ext}"
        target_file = os.path.join(date_folder, new_filename)

        try:
            shutil.copy2(source_file, target_file)
            copied_files += 1
            hash_cache[date_folder].add(source_hash)
            log_message(f"[{idx}/{total_files}] {source_file} → {new_filename}")
        except Exception as e:
            skipped_files += 1
            log_message(f"[{idx}/{total_files}] 오류: {source_file} → {new_filename} ({e})")

    messagebox.showinfo("작업 완료", f"총 파일 수: {total_files}\n복사된 파일 수: {copied_files}\n건너뛴 파일 수: {skipped_files}")
    log_message(f"=== 완료: 복사됨 {copied_files}, 건너뜀 {skipped_files} ===")

# GUI 설정
root_window = Tk()
root_window.title("파일 복사 프로그램")
root_window.geometry("700x500")

frame = Frame(root_window)
frame.pack(pady=10)

input_path_button = Button(frame, text="입력 경로 선택", command=select_input_path, width=20)
input_path_button.grid(row=0, column=0, padx=5, pady=5)
input_path_label = Label(frame, text="입력 경로: 선택되지 않음", anchor="w", width=60)
input_path_label.grid(row=0, column=1, padx=5, pady=5)

output_path_button = Button(frame, text="출력 경로 선택", command=select_output_path, width=20)
output_path_button.grid(row=1, column=0, padx=5, pady=5)
output_path_label = Label(frame, text="출력 경로: 선택되지 않음", anchor="w", width=60)
output_path_label.grid(row=1, column=1, padx=5, pady=5)

log_frame = Frame(root_window)
log_frame.pack(pady=10, fill="both", expand=True)

scrollbar = Scrollbar(log_frame)
scrollbar.pack(side=RIGHT, fill=Y)

log_output = Text(log_frame, wrap="none", yscrollcommand=scrollbar.set, height=15)
log_output.pack(fill="both", expand=True)
scrollbar.config(command=log_output.yview)

start_button = Button(root_window, text="복사 시작", command=start_copy_thread, width=20)
start_button.pack(pady=10)

load_last_paths()
root_window.mainloop()
