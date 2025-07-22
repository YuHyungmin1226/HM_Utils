import os
import yt_dlp as youtube_dl
from pathlib import Path
import re
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import platform
import shutil
import sys

class YouTubeDownloader:
    def __init__(self, url, status_callback=None, progress_callback=None):
        self.url = url
        self.video_path_template = str(Path.home() / "Videos" / "%(title)s.%(ext)s")
        self.last_percent = 0
        self.status_callback = status_callback  # 진행상황 텍스트 콜백
        self.progress_callback = progress_callback  # 프로그레스바 콜백

    def validate_url(self):
        # 기본적인 URL 형식 검사
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/', self.url):
            raise ValueError("유효하지 않은 YouTube URL입니다.")
        
        # URL에서 video_id 추출 시도
        video_id = None
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # 일반적인 video ID
            r'shorts\/([0-9A-Za-z_-]{11})',     # Shorts 형식
            r'embed\/([0-9A-Za-z_-]{11})',      # Embed 형식
            r'v\/([0-9A-Za-z_-]{11})'           # v/ 형식
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            raise ValueError("YouTube 영상 ID를 찾을 수 없습니다.")
        
        # 표준 URL 형식으로 변환
        self.url = f"https://www.youtube.com/watch?v={video_id}"

    def get_ffmpeg_path(self):
        # 시스템에 설치된 ffmpeg만 탐색
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path and platform.system() == "Windows":
            ffmpeg_path = shutil.which("ffmpeg.exe")
        if not ffmpeg_path and platform.system() == "Darwin":
            # macOS Homebrew 기본 경로도 시도
            if os.path.exists("/opt/homebrew/bin/ffmpeg"):
                ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
            elif os.path.exists("/usr/local/bin/ffmpeg"):
                ffmpeg_path = "/usr/local/bin/ffmpeg"
        return ffmpeg_path

    def download_video(self):
        try:
            self.validate_url()
        except ValueError as e:
            if self.status_callback:
                self.status_callback(f"오류: {e}")
            return
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            if self.status_callback:
                self.status_callback("\n다운로드 오류: ffmpeg가 설치되어 있지 않습니다.\nhttps://ffmpeg.org/download.html 에서 설치 후 다시 시도하세요.")
            return
        # Videos 폴더 없으면 생성
        videos_dir = Path.home() / "Videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': self.video_path_template,
            'progress_hooks': [self.my_hook],
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_path,
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            if self.status_callback:
                self.status_callback("\n성공: 영상이 성공적으로 다운로드되었습니다.")
            if self.progress_callback:
                self.progress_callback(100)
        except youtube_dl.utils.DownloadError as e:
            if self.status_callback:
                self.status_callback(f"\n다운로드 오류: {e}")
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"\n예기치 못한 오류 발생: {e}")

    def my_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0%'))
            try:
                percent = float(percent_str.strip('%'))
            except:
                percent = 0
            if self.progress_callback:
                self.progress_callback(percent)
            if self.status_callback:
                status = f"{percent_str} of {d.get('_total_bytes_str', '')} at {d.get('_speed_str', '')} ETA {d.get('_eta_str', '')}"
                self.status_callback(status, replace=True)

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 영상 다운로드 도구")
        self.root.geometry("700x350")
        self.root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ENTRY_WIDTH = 85
        BUTTON_WIDTH = 40
        LABEL_WIDTH = 85
        # URL 입력
        tk.Label(self.root, text="YouTube 링크 입력:", anchor='w').pack(pady=(15, 0), fill='x')
        self.url_entry = tk.Entry(self.root, width=ENTRY_WIDTH, font=('Arial', 12))
        self.url_entry.pack(pady=5, fill='x', padx=10)
        self.url_entry.focus()
        # 붙여넣기 버튼
        paste_btn = tk.Button(self.root, text="링크 붙여넣기", command=self.on_paste_link, width=BUTTON_WIDTH)
        paste_btn.pack(pady=(5, 0))
        # 다운로드 버튼
        self.download_btn = tk.Button(self.root, text="영상 다운로드", command=self.on_download, width=BUTTON_WIDTH)
        self.download_btn.pack(pady=5)
        # 진행상황 Progressbar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.pack(pady=5, padx=10)
        # 상태 출력창
        self.status_text = scrolledtext.ScrolledText(self.root, width=ENTRY_WIDTH, height=6, wrap=tk.WORD, font=('Arial', 12))
        self.status_text.pack(pady=10, fill='x', padx=10)
        self.status_text.insert(tk.END, "YouTube 링크를 입력하고 다운로드 버튼을 누르세요.\n")
        self.status_text.config(state=tk.DISABLED)
        # 저장 폴더 열기 버튼
        self.open_folder_btn = tk.Button(self.root, text="저장 폴더 열기", command=self.on_open_folder, width=BUTTON_WIDTH)
        self.open_folder_btn.pack(pady=(0, 10))

    def set_status(self, msg, replace=False):
        self.status_text.config(state=tk.NORMAL)
        if replace:
            self.status_text.delete('end-2l', 'end-1l')  # 마지막 줄만 교체
        self.status_text.insert(tk.END, msg + '\n')
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def set_progress(self, percent):
        self.progress['value'] = percent
        self.root.update_idletasks()

    def on_paste_link(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
        except Exception:
            messagebox.showwarning("클립보드 오류", "클립보드에서 텍스트를 읽을 수 없습니다.")

    def on_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("입력 오류", "YouTube 링크를 입력하세요.")
            return
        self.set_status("다운로드를 시작합니다...", replace=False)
        self.download_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        threading.Thread(target=self.download_thread, args=(url,)).start()

    def download_thread(self, url):
        try:
            downloader = YouTubeDownloader(
                url,
                status_callback=self.thread_safe_status,
                progress_callback=self.thread_safe_progress
            )
            downloader.download_video()
        finally:
            self.download_btn.config(state=tk.NORMAL)

    def thread_safe_status(self, msg, replace=False):
        self.root.after(0, self.set_status, msg, replace)

    def thread_safe_progress(self, percent):
        self.root.after(0, self.set_progress, percent)

    def on_open_folder(self):
        folder = str(Path.home() / "Videos")
        if os.path.exists(folder):
            if platform.system() == 'Darwin':
                os.system(f'open "{folder}"')
            elif platform.system() == 'Windows':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showinfo("안내", "Videos 폴더가 존재하지 않습니다.")

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()