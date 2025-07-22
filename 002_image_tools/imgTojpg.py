import os
from PIL import Image
from tkinter import filedialog, messagebox, scrolledtext
import tkinter as tk
from tkinter.ttk import Frame, Progressbar
import threading

class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.image_folder = ''
        self.image_files = []
        self.text_widget = None
        self.progress = None

    def create_widgets(self):
        frame = Frame(self.root, width=640, height=480)
        frame.pack()

        self.text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=85, height=25)
        self.text_widget.place(x=10, y=10)

        select_button = tk.Button(frame, text="이미지 폴더 선택", command=self.select_folder)
        select_button.place(x=200, y=420)

        convert_button = tk.Button(frame, text="이미지 변환", command=self.start_conversion)
        convert_button.place(x=330, y=420)

        self.progress = Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.place(x=10, y=390)

    def select_folder(self):
        self.image_folder = filedialog.askdirectory(title="폴더 선택")
        self.text_widget.delete('1.0', tk.END)
        if self.image_folder:
            self.list_image_files()

    def list_image_files(self):
        self.image_files = []
        for root, dirs, files in os.walk(self.image_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if self.is_image_file(file_path):
                    self.image_files.append(file_path)

        if self.image_files:
            self.text_widget.delete('1.0', tk.END)
            for file_path in self.image_files:
                self.text_widget.insert(tk.END, file_path + '\n')
        else:
            self.text_widget.delete('1.0', tk.END)
            self.text_widget.insert(tk.END, "변환 가능한 이미지가 없습니다.")

    def is_image_file(self, file_path):
        _, ext = os.path.splitext(file_path)
        return ext.lower() in (".png", ".jpeg", ".gif", ".bmp", ".webp")

    def start_conversion(self):
        if not self.image_files:
            messagebox.showinfo("알림", "변환 가능한 이미지가 없습니다.")
            return

        conversion_thread = threading.Thread(target=self.convert_images)
        conversion_thread.start()

    def convert_images(self):
        self.text_widget.delete('1.0', tk.END)
        total_files = len(self.image_files)
        converted_files = 0

        for i, file_path in enumerate(self.image_files):
            try:
                img = Image.open(file_path)
                file_root, file_ext = os.path.splitext(file_path)
                new_file_path = file_root + ".jpg"
                img.convert("RGB").save(new_file_path, "JPEG")
                os.remove(file_path)
                converted_files += 1
                self.text_widget.insert(tk.END, f"[{converted_files}/{total_files}] 파일 {file_path}을 {new_file_path}로 변환하였습니다.\n")
                self.text_widget.see(tk.END)
                self.root.update()
            except Exception as e:
                self.text_widget.insert(tk.END, f"[{converted_files}/{total_files}] 파일 {file_path} 변환 중 에러 발생: {e}\n")
                self.text_widget.see(tk.END)
                self.root.update()
            finally:
                self.progress['value'] = (i + 1) / total_files * 100
                self.root.update_idletasks()

        messagebox.showinfo("알림", f"이미지 변환이 완료되었습니다. 변환된 파일 수: {converted_files}/{total_files}")

def run_program():
    root = tk.Tk()
    root.title("이미지 변환 프로그램")
    root.geometry("640x480")
    root.resizable(False, False)

    converter = ImageConverter(root)
    converter.create_widgets()

    root.mainloop()

if __name__ == "__main__":
    run_program()
