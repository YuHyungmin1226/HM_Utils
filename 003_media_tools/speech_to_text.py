import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import sys
import subprocess
import traceback
import urllib.request
import tempfile
import pygame
import time
from pathlib import Path
import zipfile
import shutil

# FFmpeg 설치 함수
def install_ffmpeg():
    """FFmpeg를 자동으로 설치합니다."""
    try:
        if sys.platform == "win32":
            # Windows용 FFmpeg 다운로드 및 설치
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")
            
            # 다운로드 진행 상태 표시
            progress_window = tk.Toplevel()
            progress_window.title("FFmpeg 설치")
            progress_window.geometry("400x200")
            
            # 상태 메시지 표시
            status_label = ttk.Label(progress_window, text="FFmpeg 설치 준비 중...")
            status_label.pack(pady=10)
            
            # 진행 상태 표시
            progress_label = ttk.Label(progress_window, text="0%")
            progress_label.pack(pady=5)
            
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            
            def update_progress(block_num, block_size, total_size):
                if total_size > 0:
                    progress = min(100, int(block_num * block_size * 100 / total_size))
                    progress_bar['value'] = progress
                    progress_label['text'] = f"{progress}%"
                    progress_window.update()
            
            # FFmpeg 다운로드
            status_label['text'] = "FFmpeg 다운로드 중..."
            urllib.request.urlretrieve(ffmpeg_url, zip_path, update_progress)
            
            # 압축 해제
            status_label['text'] = "압축 해제 중..."
            progress_bar['value'] = 0
            progress_label['text'] = "0%"
            progress_window.update()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_files = len(zip_ref.namelist())
                for i, file in enumerate(zip_ref.namelist()):
                    zip_ref.extract(file, temp_dir)
                    progress = int((i + 1) * 100 / total_files)
                    progress_bar['value'] = progress
                    progress_label['text'] = f"{progress}%"
                    progress_window.update()
            
            # FFmpeg 실행 파일을 시스템 경로에 복사
            status_label['text'] = "FFmpeg 설치 중..."
            progress_bar['value'] = 0
            progress_label['text'] = "0%"
            progress_window.update()
            
            ffmpeg_dir = os.path.join(temp_dir, "ffmpeg-master-latest-win64-gpl", "bin")
            system_path = os.environ.get('PATH', '')
            new_path = os.path.join(os.path.expanduser("~"), "ffmpeg", "bin")
            
            # FFmpeg 폴더 생성
            os.makedirs(new_path, exist_ok=True)
            
            # 실행 파일 복사
            files = [f for f in os.listdir(ffmpeg_dir) if f.endswith('.exe')]
            total_files = len(files)
            for i, file in enumerate(files):
                shutil.copy2(os.path.join(ffmpeg_dir, file), new_path)
                progress = int((i + 1) * 100 / total_files)
                progress_bar['value'] = progress
                progress_label['text'] = f"{progress}%"
                progress_window.update()
            
            # 환경 변수 PATH에 추가
            if new_path not in system_path:
                os.environ['PATH'] = f"{new_path};{system_path}"
            
            # 임시 파일 정리
            status_label['text'] = "임시 파일 정리 중..."
            progress_bar['value'] = 0
            progress_label['text'] = "0%"
            progress_window.update()
            
            shutil.rmtree(temp_dir)
            
            progress_bar['value'] = 100
            progress_label['text'] = "100%"
            status_label['text'] = "설치 완료!"
            progress_window.update()
            
            time.sleep(1)  # 완료 메시지를 잠시 보여줌
            progress_window.destroy()
            messagebox.showinfo("설치 완료", "FFmpeg가 성공적으로 설치되었습니다.")
            return True
            
        elif sys.platform == "darwin":
            # macOS용 FFmpeg 설치 (Homebrew 사용)
            progress_window = tk.Toplevel()
            progress_window.title("FFmpeg 설치")
            progress_window.geometry("400x150")
            
            status_label = ttk.Label(progress_window, text="FFmpeg 설치 중...")
            status_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start()
            
            try:
                subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showinfo("설치 완료", "FFmpeg가 성공적으로 설치되었습니다.")
                return True
            except subprocess.CalledProcessError:
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showerror("설치 실패", "Homebrew를 통해 FFmpeg 설치에 실패했습니다.")
                return False
        else:
            messagebox.showerror("지원되지 않는 시스템", "현재 시스템에서는 자동 설치를 지원하지 않습니다.")
            return False
            
    except Exception as e:
        messagebox.showerror("설치 오류", f"FFmpeg 설치 중 오류가 발생했습니다: {e}")
        return False

# FFmpeg 확인 및 설치
def check_and_install_ffmpeg():
    """FFmpeg가 설치되어 있는지 확인하고, 없으면 설치를 시도합니다."""
    # 가능한 FFmpeg 경로 목록 (macOS)
    possible_ffmpeg_paths = [
        'ffmpeg',  # 기본 PATH
        '/usr/local/bin/ffmpeg',  # Homebrew 기본 설치 경로
        '/opt/homebrew/bin/ffmpeg',  # Apple Silicon Homebrew 경로
        '/usr/bin/ffmpeg',  # 시스템 경로
        os.path.expanduser('~/bin/ffmpeg'),  # 사용자 bin 디렉토리
    ]
    
    # Windows에서 추가 검색 경로
    if sys.platform == "win32":
        possible_ffmpeg_paths.extend([
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        ])
    
    # 각 경로 시도
    for ffmpeg_path in possible_ffmpeg_paths:
        try:
            subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print(f"FFmpeg found at: {ffmpeg_path}")
            # 찾은 경로를 환경 변수에 추가
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            if ffmpeg_dir and ffmpeg_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{ffmpeg_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    # 모든 경로에서 찾지 못한 경우
    response = messagebox.askyesno("FFmpeg 설치 필요", 
                                  "FFmpeg가 설치되어 있지 않습니다. 자동으로 설치하시겠습니까?\n"
                                  "설치하지 않으려면 '아니오'를 선택하세요.")
    if response:
        return install_ffmpeg()
    else:
        messagebox.showwarning("FFmpeg 필요", 
                              "FFmpeg가 필요합니다. 수동으로 설치하세요:\n"
                              "macOS: brew install ffmpeg\n"
                              "Windows: https://ffmpeg.org/download.html에서 다운로드")
        return False

# 필요한 패키지 확인
required_packages = {
    "speech_recognition": "SpeechRecognition",
    "pydub": "pydub",
    "pygame": "pygame"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    messagebox.showerror("필수 패키지 누락", 
                        f"다음 패키지를 설치해야 합니다: {', '.join(missing_packages)}\n"
                        f"다음 명령어를 실행하세요: pip install {' '.join(missing_packages)}")
    sys.exit(1)

# FFmpeg 확인 및 설치
if not check_and_install_ffmpeg():
    sys.exit(1)

# 필요한 패키지 임포트
import speech_recognition as sr
from pydub import AudioSegment

# 문서 폴더 경로 가져오기
def get_documents_dir():
    """사용자의 문서 폴더 경로를 가져옵니다."""
    try:
        if sys.platform == "win32":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    return winreg.QueryValueEx(key, "Personal")[0]
            except ImportError:
                return os.path.join(os.path.expanduser("~"), "Documents")
            except Exception as e:
                print(f"[ERROR] 문서 폴더 경로 가져오기 실패 (Windows): {e}")
                return os.path.join(os.path.expanduser("~"), "Documents")
        elif sys.platform == "darwin":
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:
            return os.path.join(os.path.expanduser("~"), "Documents")
    except Exception as e:
        print(f"[ERROR] 문서 폴더 경로 가져오기 실패: {e}")
        return os.path.join(os.path.expanduser("~"), "Documents")

class AudioTranscriber:
    def __init__(self, master):
        self.master = master
        self.master.title("음성 텍스트 변환기")
        self.master.geometry("800x600")
        self.master.resizable(True, True)
        
        # 변수 초기화
        self.audio_file = None
        self.audio_segment = None
        self.is_playing = False
        self.playing_thread = None
        self.recognizing_thread = None
        
        # 임시 디렉토리 생성
        try:
            self.temp_dir = tempfile.TemporaryDirectory(dir=os.path.expanduser("~"))
            self.temp_wav = os.path.join(self.temp_dir.name, "temp_audio.wav")
        except Exception as e:
            messagebox.showerror("오류", f"임시 디렉토리 생성 실패: {e}")
            sys.exit(1)
        
        # Pygame 초기화
        try:
            pygame.mixer.init()
        except pygame.error as e:
            messagebox.showwarning("오디오 초기화 오류", f"Pygame 초기화 실패: {e}")
        
        # GUI 구성
        self.create_widgets()
    
    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 프레임 (파일 선택 및 제어)
        control_frame = ttk.LabelFrame(main_frame, text="음성/영상 파일 선택 및 제어", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 파일 선택
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=60)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(file_frame, text="파일 찾기", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 오디오 제어
        audio_control_frame = ttk.Frame(control_frame)
        audio_control_frame.pack(fill=tk.X, pady=5)
        
        self.play_button = ttk.Button(audio_control_frame, text="재생", command=self.toggle_play, width=10)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # 음성 인식 설정
        recognition_frame = ttk.LabelFrame(main_frame, text="음성 인식 설정", padding=10)
        recognition_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 언어 선택
        language_frame = ttk.Frame(recognition_frame)
        language_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(language_frame, text="언어:").pack(side=tk.LEFT, padx=5)
        
        self.language_var = tk.StringVar(value="한국어")
        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                    values=["한국어", "영어", "자동 감지"], width=15)
        language_combo.pack(side=tk.LEFT, padx=5)
        
        # 실행 버튼
        button_frame = ttk.Frame(recognition_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.recognize_button = ttk.Button(button_frame, text="음성 인식 시작", 
                                         command=self.start_recognition)
        self.recognize_button.pack(side=tk.RIGHT, padx=5)
        
        # 진행 상태 표시
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(button_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 결과 텍스트
        result_frame = ttk.LabelFrame(main_frame, text="변환 결과", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_result = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.text_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 하단 버튼들
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        save_button = ttk.Button(bottom_frame, text="텍스트 저장", command=self.save_text)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = ttk.Button(bottom_frame, text="결과 지우기", command=self.clear_result)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # 상태 표시줄
        self.status_var = tk.StringVar(value="준비됨")
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_file(self):
        filetypes = [
            ("미디어 파일", "*.mp3 *.wav *.m4a *.aac *.flac *.ogg *.mp4 *.avi *.mkv *.mov *.wmv"),
            ("오디오 파일", "*.mp3 *.wav *.m4a *.aac *.flac *.ogg"),
            ("비디오 파일", "*.mp4 *.avi *.mkv *.mov *.wmv"),
            ("모든 파일", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="미디어 파일 선택",
            filetypes=filetypes
        )
        
        if filepath:
            self.audio_file = filepath
            self.file_var.set(filepath)
            
            # 비디오 파일인 경우 오디오 추출
            file_ext = os.path.splitext(filepath)[1].lower()
            if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
                self.extract_audio_from_video(filepath)
            else:
                self.load_audio()
            
            filename = os.path.basename(filepath)
            self.status_var.set(f"파일 로드됨: {filename}")
    
    def extract_audio_from_video(self, video_path):
        """비디오 파일에서 오디오를 추출합니다."""
        try:
            self.status_var.set("비디오에서 오디오 추출 중...")
            self.master.update_idletasks()
            
            # 임시 오디오 파일 경로
            temp_audio = os.path.join(self.temp_dir.name, "extracted_audio.wav")
            
            # FFmpeg 경로 확인 (여러 가능한 경로 시도)
            ffmpeg_path = 'ffmpeg'  # 기본값
            possible_ffmpeg_paths = [
                'ffmpeg',  # 기본 PATH
                '/usr/local/bin/ffmpeg',  # Homebrew 기본 설치 경로
                '/opt/homebrew/bin/ffmpeg',  # Apple Silicon Homebrew 경로
                '/usr/bin/ffmpeg',  # 시스템 경로
                os.path.expanduser('~/bin/ffmpeg'),  # 사용자 bin 디렉토리
            ]
            
            # Windows에서 추가 검색 경로
            if sys.platform == "win32":
                possible_ffmpeg_paths.extend([
                    os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                ])
            
            # 각 경로 시도하여 작동하는 FFmpeg 찾기
            for path in possible_ffmpeg_paths:
                try:
                    subprocess.run([path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    ffmpeg_path = path
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            
            # FFmpeg를 사용하여 오디오 추출
            command = [
                ffmpeg_path, '-i', video_path,
                '-vn',  # 비디오 스트림 제외
                '-acodec', 'pcm_s16le',  # WAV 형식으로 인코딩
                '-ar', '44100',  # 샘플레이트
                '-ac', '2',  # 스테레오
                '-y',  # 기존 파일 덮어쓰기
                temp_audio
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 진행 상태 표시
            progress_window = tk.Toplevel(self.master)
            progress_window.title("오디오 추출")
            progress_window.geometry("300x150")
            
            status_label = ttk.Label(progress_window, text="오디오 추출 중...")
            status_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, length=200, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start()
            
            # 프로세스 완료 대기
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.audio_file = temp_audio
                self.load_audio()
                progress_window.destroy()
                messagebox.showinfo("추출 완료", "비디오에서 오디오가 성공적으로 추출되었습니다.")
            else:
                progress_window.destroy()
                messagebox.showerror("추출 실패", f"오디오 추출 중 오류가 발생했습니다:\n{stderr.decode()}")
                
        except Exception as e:
            messagebox.showerror("오류", f"오디오 추출 중 오류가 발생했습니다: {e}")
            self.status_var.set("오류: 오디오 추출 실패")
    
    def load_audio(self):
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_button.config(text="재생")
            
            file_ext = os.path.splitext(self.audio_file)[1].lower()
            self.status_var.set(f"오디오 파일 로드 중...")
            self.master.update_idletasks()
            
            # FFmpeg 경로 확인 (여러 가능한 경로 시도)
            ffmpeg_path = 'ffmpeg'  # 기본값
            ffprobe_path = 'ffprobe'  # 기본값
            
            possible_ffmpeg_paths = [
                'ffmpeg',  # 기본 PATH
                '/usr/local/bin/ffmpeg',  # Homebrew 기본 설치 경로
                '/opt/homebrew/bin/ffmpeg',  # Apple Silicon Homebrew 경로
                '/usr/bin/ffmpeg',  # 시스템 경로
                os.path.expanduser('~/bin/ffmpeg'),  # 사용자 bin 디렉토리
            ]
            
            possible_ffprobe_paths = [
                'ffprobe',  # 기본 PATH
                '/usr/local/bin/ffprobe',  # Homebrew 기본 설치 경로
                '/opt/homebrew/bin/ffprobe',  # Apple Silicon Homebrew 경로
                '/usr/bin/ffprobe',  # 시스템 경로
                os.path.expanduser('~/bin/ffprobe'),  # 사용자 bin 디렉토리
            ]
            
            # Windows에서 추가 검색 경로
            if sys.platform == "win32":
                possible_ffmpeg_paths.extend([
                    os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'FFmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                ])
                
                possible_ffprobe_paths.extend([
                    os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'FFmpeg', 'bin', 'ffprobe.exe'),
                    os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'FFmpeg', 'bin', 'ffprobe.exe'),
                    os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffprobe.exe'),
                ])
            
            # 각 경로 시도하여 작동하는 FFmpeg/FFprobe 찾기
            for path in possible_ffmpeg_paths:
                try:
                    subprocess.run([path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    ffmpeg_path = path
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
                    
            for path in possible_ffprobe_paths:
                try:
                    subprocess.run([path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    ffprobe_path = path
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            
            # pydub에 FFmpeg 경로 설정 (환경 변수 사용)
            os.environ['FFMPEG_BINARY'] = ffmpeg_path
            os.environ['FFPROBE_BINARY'] = ffprobe_path
            
            from pydub.utils import mediainfo
            
            # pydub가 FFmpeg 경로를 인식할 수 있도록 설정
            try:
                from pydub import utils
                utils.get_ffmpeg_path = lambda: ffmpeg_path
                utils.get_ffprobe_path = lambda: ffprobe_path
            except Exception as e:
                print(f"pydub 경로 설정 오류: {e}")
            
            try:
                if file_ext == ".mp3":
                    self.audio_segment = AudioSegment.from_mp3(self.audio_file)
                elif file_ext == ".wav":
                    self.audio_segment = AudioSegment.from_wav(self.audio_file)
                elif file_ext == ".m4a" or file_ext == ".aac":
                    self.audio_segment = AudioSegment.from_file(self.audio_file, format="m4a")
                elif file_ext == ".flac":
                    self.audio_segment = AudioSegment.from_file(self.audio_file, format="flac")
                elif file_ext == ".ogg":
                    self.audio_segment = AudioSegment.from_file(self.audio_file, format="ogg")
                else:
                    self.audio_segment = AudioSegment.from_file(self.audio_file)
            except Exception as e:
                if "ffmpeg" in str(e).lower():
                    messagebox.showerror("FFmpeg 오류", 
                                       f"FFmpeg 관련 오류: {e}\n\n"
                                       f"사용한 FFmpeg 경로: {ffmpeg_path}\n"
                                       f"사용한 FFprobe 경로: {ffprobe_path}\n\n"
                                       "경로가 올바른지 확인하세요.")
                    self.status_var.set("오류: FFmpeg가 필요합니다")
                    return
                else:
                    raise e
            
            try:
                # 임시 파일이 이미 존재하면 삭제
                if os.path.exists(self.temp_wav):
                    os.remove(self.temp_wav)
                
                # WAV 파일로 변환
                self.audio_segment.export(self.temp_wav, format="wav")
                
                # 파일 권한 확인
                if not os.access(self.temp_wav, os.R_OK):
                    os.chmod(self.temp_wav, 0o666)  # 읽기/쓰기 권한 부여
                
                pygame.mixer.music.load(self.temp_wav)
                self.status_var.set(f"오디오 파일이 로드되었습니다")
            except (pygame.error, OSError) as e:
                messagebox.showerror("재생 오류", f"오디오 파일을 재생할 수 없습니다: {e}")
                self.status_var.set("오류: 파일을 재생할 수 없습니다")
        
        except Exception as e:
            messagebox.showerror("오류", f"오디오 파일 로드 실패: {e}")
            self.status_var.set("오류: 오디오 파일을 로드할 수 없습니다.")
    
    def toggle_play(self):
        if not self.audio_file:
            messagebox.showinfo("알림", "먼저 오디오 파일을 선택하세요.")
            return
        
        if not self.temp_wav or not os.path.exists(self.temp_wav):
            messagebox.showinfo("알림", "오디오 파일이 아직 준비되지 않았습니다.")
            return
        
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.is_playing = False
                self.play_button.config(text="재생")
                self.status_var.set("일시 정지됨")
            else:
                pygame.mixer.music.load(self.temp_wav)
                pygame.mixer.music.play()
                self.is_playing = True
                self.play_button.config(text="일시 정지")
                self.status_var.set("재생 중...")
        except pygame.error as e:
            messagebox.showerror("재생 오류", f"오디오 재생 중 오류 발생: {e}")
            self.status_var.set(f"오류: {e}")
    
    def start_recognition(self):
        if not self.audio_file:
            messagebox.showinfo("알림", "먼저 오디오 파일을 선택하세요.")
            return
        
        if self.recognizing_thread and self.recognizing_thread.is_alive():
            messagebox.showinfo("알림", "이미 음성 인식이 진행 중입니다.")
            return
        
        self.recognizing_thread = threading.Thread(target=self.recognize_audio)
        self.recognizing_thread.daemon = True
        self.recognizing_thread.start()
        
        self.recognize_button.config(state=tk.DISABLED)
        self.status_var.set("음성 인식 진행 중...")
        self.progress_var.set(0)
    
    def recognize_audio(self):
        try:
            language = self.language_var.get()
            lang_code = "ko-KR" if language == "한국어" else "en-US" if language == "영어" else None
            
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, "인식 중...\n\n")
            self.master.update_idletasks()
            
            recognized_text = self.recognize_with_google(lang_code)
            
            self.progress_var.set(100)
            self.status_var.set("음성 인식 완료")
            
            if recognized_text:
                # 인식된 텍스트가 있는 경우
                self.text_result.delete(1.0, tk.END)
                self.text_result.insert(tk.END, recognized_text)
                
                # 완료 메시지 표시
                completion_window = tk.Toplevel(self.master)
                completion_window.title("변환 완료")
                completion_window.geometry("300x150")
                
                # 완료 메시지
                message_frame = ttk.Frame(completion_window, padding=20)
                message_frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(message_frame, text="음성 인식이 완료되었습니다!", 
                         font=('Helvetica', 12, 'bold')).pack(pady=10)
                
                # 인식된 텍스트 길이 표시
                text_length = len(recognized_text.strip())
                ttk.Label(message_frame, 
                         text=f"인식된 텍스트 길이: {text_length}자").pack(pady=5)
                
                # 확인 버튼
                ttk.Button(message_frame, text="확인", 
                          command=completion_window.destroy).pack(pady=10)
                
                # 자동 저장
                self.save_text_to_file(recognized_text, auto_save=True)
            else:
                # 인식된 텍스트가 없는 경우
                self.text_result.delete(1.0, tk.END)
                self.text_result.insert(tk.END, "인식된 텍스트가 없습니다.")
                messagebox.showwarning("알림", "음성 인식 결과가 없습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"음성 인식 중 오류 발생: {e}")
            self.status_var.set(f"오류: {e}")
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, f"오류 발생: {e}")
        
        finally:
            self.recognize_button.config(state=tk.NORMAL)
    
    def recognize_with_google(self, language=None):
        if not self.temp_wav:
            self.temp_wav = os.path.join(self.temp_dir.name, "temp_audio.wav")
            self.audio_segment.export(self.temp_wav, format="wav")
        
        chunk_length_ms = 60000  # 60초 청크
        chunks = self.split_audio_to_chunks(self.audio_segment, chunk_length_ms)
        
        recognizer = sr.Recognizer()
        
        try:
            urllib.request.urlopen('http://google.com', timeout=1)
        except:
            messagebox.showwarning("경고", "인터넷 연결이 확인되지 않습니다. Google 음성 인식은 인터넷이 필요합니다.")
        
        full_text = ""
        for i, chunk in enumerate(chunks):
            progress = (i / len(chunks)) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"인식 중... 청크 {i+1}/{len(chunks)}")
            self.master.update_idletasks()
            
            chunk_file = os.path.join(self.temp_dir.name, f"chunk_{i}.wav")
            chunk.export(chunk_file, format="wav")
            
            with sr.AudioFile(chunk_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language=language)
                    full_text += text + " "
                    
                    self.text_result.delete(1.0, tk.END)
                    self.text_result.insert(tk.END, full_text)
                    self.master.update_idletasks()
                    
                except sr.UnknownValueError:
                    full_text += "[인식 불가] "
                except sr.RequestError as e:
                    full_text += f"[API 요청 오류: {e}] "
            
            # 청크 파일 즉시 삭제
            try:
                os.remove(chunk_file)
            except:
                pass
        
        return full_text
    
    def split_audio_to_chunks(self, audio_segment, chunk_length_ms):
        chunks = []
        total_length = len(audio_segment)
        
        for i in range(0, total_length, chunk_length_ms):
            chunk = audio_segment[i:i + chunk_length_ms]
            chunks.append(chunk)
        
        return chunks
    
    def save_text_to_file(self, text, filepath=None, auto_save=False):
        if not text:
            if not auto_save:
                messagebox.showinfo("알림", "저장할 텍스트가 없습니다.")
            return False
        
        if filepath is None:
            if auto_save:
                docs_dir = get_documents_dir()
                speech_to_text_dir = os.path.join(docs_dir, "speech_to_text")
                os.makedirs(speech_to_text_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
                filepath = os.path.join(speech_to_text_dir, f"{base_name}.txt")
            else:
                default_filename = "audio_transcript.txt"
                if self.audio_file:
                    base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
                    default_filename = f"{base_name}_transcript.txt"
                
                filepath = filedialog.asksaveasfilename(
                    title="텍스트 저장",
                    defaultextension=".txt",
                    initialfile=default_filename,
                    filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
                )
        
        if not filepath:
            return False
        
        try:
            try:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(text)
            except UnicodeEncodeError:
                with open(filepath, 'w', encoding='cp949') as file:
                    file.write(text)
            
            self.status_var.set(f"텍스트가 저장되었습니다: {os.path.basename(filepath)}")
            if not auto_save:
                messagebox.showinfo("저장 성공", f"텍스트가 성공적으로 저장되었습니다:\n{filepath}")
            return True
            
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"[ERROR] 텍스트 저장 실패:\n{error_detail}")
            if not auto_save:
                messagebox.showerror("오류", f"파일 저장 중 오류 발생: {e}")
            return False
    
    def save_text(self):
        text = self.text_result.get(1.0, tk.END).strip()
        self.save_text_to_file(text)
    
    def clear_result(self):
        self.text_result.delete(1.0, tk.END)
        self.status_var.set("결과가 지워졌습니다.")
    
    def __del__(self):
        try:
            pygame.mixer.music.stop()
            self.temp_dir.cleanup()
        except:
            pass

def main():
    root = tk.Tk()
    app = AudioTranscriber(root)
    root.mainloop()

if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()