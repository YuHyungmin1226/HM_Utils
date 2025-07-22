import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import platform
from tkinter import filedialog, messagebox
from PIL import UnidentifiedImageError
import time

# OS 타입 확인
is_windows = platform.system() == "Windows"
is_macos = platform.system() == "Darwin"

# 디버깅용 로그 파일
DEBUG_LOG = os.path.expanduser("~/Desktop/imageviewer_debug.log")

def log_debug(message):
    """디버그 메시지를 파일에 기록"""
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

# 시작 시 로그
log_debug("===== 프로그램 시작 =====")
log_debug(f"OS: {platform.system()}")
log_debug(f"Python 버전: {sys.version}")
log_debug(f"명령줄 인수: {sys.argv}")
log_debug(f"현재 작업 디렉토리: {os.getcwd()}")

# macOS에서 앱 번들 내 위치 확인
if hasattr(sys, 'frozen') and getattr(sys, 'frozen'):
    log_debug(f"앱 번들 경로: {sys.executable}")
    log_debug(f"앱 리소스 경로: {getattr(sys, '_MEIPASS', 'Not available')}")

class ImageViewer:
    def __init__(self, initial_file=None):
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.geometry("800x600")  # 기본 창 크기를 더 크게 설정
        self.root.minsize(400, 300)  # 최소 창 크기 설정

        self.images = []
        self.current_image_index = 0
        self.fullscreen = False

        # 배경색을 더 밝은 색상으로 변경
        self.canvas = tk.Canvas(self.root, bg="#f0f0f0")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.create_menu()
        self.setup_bindings()

        # macOS의 파일 오픈 이벤트 처리
        if is_macos:
            try:
                self.root.createcommand('::tk::mac::OpenDocument', self.handle_open_document)
                log_debug("macOS 파일 오픈 이벤트 핸들러 등록 성공")
            except Exception as e:
                log_debug(f"macOS 파일 오픈 이벤트 핸들러 등록 실패: {str(e)}")
        
        # 명령줄에서 또는 파일 연결로 파일을 열 경우 처리
        log_debug(f"초기 파일: {initial_file}")
        if initial_file and os.path.isfile(initial_file):
            log_debug(f"파일 열기 시도: {initial_file}")
            self.open_file(initial_file)

        # 메인 윈도우 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()
    
    def setup_bindings(self):
        """단축키 및 이벤트 바인딩 설정"""
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.bind("<Left>", lambda e: self.show_previous_image())
        self.root.bind("<Right>", lambda e: self.show_next_image())
        self.root.bind("<space>", lambda e: self.quit())  # Spacebar로 프로그램 종료
        self.root.bind("<Escape>", lambda e: self.quit())  # ESC로 종료
        self.root.bind("<Return>", lambda e: self.toggle_fullscreen())  # Enter로 전체 화면 전환
    
    def handle_open_document(self, *args):
        """macOS의 파일 오픈 이벤트 처리"""
        log_debug(f"macOS 파일 오픈 이벤트: {args}")
        if args and os.path.isfile(args[0]):
            self.open_file(args[0])

    def create_menu(self):
        """메뉴 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image...", command=self.select_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Esc / Space")
        
        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen, accelerator="Enter")
        view_menu.add_command(label="Next Image", command=self.show_next_image, accelerator="Right")
        view_menu.add_command(label="Previous Image", command=self.show_previous_image, accelerator="Left")
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Debug Info", command=self.show_debug_info)
        
        # Ctrl+O 단축키 바인딩
        self.root.bind("<Control-o>", lambda e: self.select_image())

    def select_image(self):
        """파일 선택 대화상자를 표시하고 선택한 이미지 열기"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 열기",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.tif"),
                ("JPEG 이미지", "*.jpg *.jpeg"),
                ("PNG 이미지", "*.png"),
                ("GIF 이미지", "*.gif"),
                ("모든 파일", "*.*")
            ]
        )
        if file_path:
            log_debug(f"사용자 선택 파일: {file_path}")
            self.open_file(file_path)

    def open_file(self, file_path):
        """파일 경로를 받아 이미지를 열고 표시합니다."""
        log_debug(f"open_file 호출됨: {file_path}")
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            error_msg = f"파일이 존재하지 않음: {file_path}"
            log_debug(error_msg)
            self.show_error(error_msg)
            return
            
        if self.is_image_file(file_path):
            try:
                directory = os.path.dirname(file_path)
                log_debug(f"디렉토리: {directory}")
                self.images = self.get_image_files_from_directory(directory)
                log_debug(f"발견된 이미지 파일: {len(self.images)}개")
                self.current_image_index = self.get_current_image_index(file_path)
                log_debug(f"현재 이미지 인덱스: {self.current_image_index}")
                self.show_image(self.current_image_index)
            except Exception as e:
                error_msg = f"파일 열기 오류: {str(e)}"
                log_debug(error_msg)
                self.show_error(error_msg)
        else:
            error_msg = f"지원되지 않는 파일 형식입니다: {file_path}"
            log_debug(error_msg)
            self.show_error(error_msg)

    def get_image_files_from_directory(self, directory):
        try:
            all_files = os.listdir(directory)
            log_debug(f"디렉토리의 모든 파일: {len(all_files)}개")
            
            image_files = [os.path.join(directory, file) for file in all_files
                          if os.path.isfile(os.path.join(directory, file)) and self.is_image_file(os.path.join(directory, file))]
            image_files.sort()
            return image_files
        except Exception as e:
            log_debug(f"디렉토리 열기 오류: {str(e)}")
            return []

    def is_image_file(self, file_path):
        """파일이 지원되는 이미지 형식인지 확인"""
        _, ext = os.path.splitext(file_path)
        result = ext.lower() in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif")
        log_debug(f"파일 확인: {file_path} - 이미지 여부: {result}")
        return result

    def get_current_image_index(self, file_path):
        """주어진 파일 경로의 이미지 인덱스 반환"""
        file_path = os.path.abspath(file_path).lower()
        for i, image_path in enumerate(self.images):
            if os.path.abspath(image_path).lower() == file_path:
                return i
        return 0

    def show_image(self, index):
        """주어진 인덱스의 이미지 표시"""
        if not self.images:
            self.show_error("이미지가 없습니다.")
            return
            
        try:
            if index < len(self.images):
                file_path = self.images[index]
                log_debug(f"이미지 표시 시도: {file_path}")
                
                if self.is_image_file(file_path):
                    try:
                        image = Image.open(file_path)
                        log_debug(f"이미지 크기: {image.size}, 형식: {image.format}")
                        resized_image = self.resize_image(image)
                        log_debug(f"리사이즈된 이미지 크기: {resized_image.size}")
                        self.photo = ImageTk.PhotoImage(resized_image)
                        self.display_image()
                        self.root.title(f"Image Viewer - {os.path.basename(file_path)}")
                        log_debug("이미지 표시 성공")
                    except (UnidentifiedImageError, OSError) as e:
                        error_msg = f"이미지를 열 수 없습니다: {file_path}\n{str(e)}"
                        log_debug(error_msg)
                        self.show_error(error_msg)
        except Exception as e:
            error_msg = f"이미지 표시 중 오류 발생: {str(e)}"
            log_debug(error_msg)
            self.show_error(error_msg)

    def resize_image(self, image):
        """이미지를 캔버스 크기에 맞게 리사이즈"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 640
            canvas_height = 480
            
        image_ratio = image.width / image.height
        canvas_ratio = canvas_width / canvas_height
        
        if image_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / image_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * image_ratio)
            
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def display_image(self):
        """현재 이미지를 캔버스에 표시"""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 640
            canvas_height = 480
            
        x = (canvas_width - self.photo.width()) // 2
        y = (canvas_height - self.photo.height()) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)

    def show_next_image(self):
        """다음 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image(self.current_image_index)

    def show_previous_image(self):
        """이전 이미지 표시"""
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image(self.current_image_index)

    def on_window_resize(self, event):
        """윈도우 크기 변경 시 이미지 리사이즈"""
        if hasattr(self, 'photo'):
            self.show_image(self.current_image_index)

    def toggle_fullscreen(self):
        """전체 화면 전환"""
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        if not self.fullscreen:
            self.root.geometry("800x600")  # 전체화면 해제 시 기본 크기 변경

    def quit(self):
        """프로그램 종료"""
        log_debug("프로그램 종료")
        self.root.quit()

    def show_error(self, message):
        """오류 메시지 표시"""
        messagebox.showerror("오류", message)

    def show_debug_info(self):
        """디버그 정보 표시"""
        info = f"OS: {platform.system()}\n"
        info += f"Python 버전: {sys.version}\n"
        info += f"현재 작업 디렉토리: {os.getcwd()}\n"
        info += f"이미지 파일 수: {len(self.images)}\n"
        info += f"현재 이미지 인덱스: {self.current_image_index}\n"
        if self.images and self.current_image_index < len(self.images):
            info += f"현재 이미지: {self.images[self.current_image_index]}\n"
        messagebox.showinfo("디버그 정보", info)

if __name__ == "__main__":
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    ImageViewer(initial_file)
