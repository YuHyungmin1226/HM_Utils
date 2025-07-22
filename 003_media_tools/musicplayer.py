import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import pygame
from pygame import mixer
from natsort import natsorted
import logging
import time
import traceback

# 디버깅 설정
DEBUG = True

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("musicplayer_debug.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MusicPlayer")

class MusicPlayer:
    def __init__(self, root):
        logger.info("음악 플레이어 초기화 시작")
        
        # 예외 처리 설정
        self.root = root
        self.root.report_callback_exception = self.handle_exception
        
        # macOS에서 SDL과 Tkinter 충돌 방지를 위한 환경 변수 설정
        os.environ["SDL_VIDEODRIVER"] = "Quartz"
        
        # Pygame Mixer 초기화
        try:
            pygame.init()
            mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            logger.debug("pygame mixer 초기화 성공")
        except pygame.error as e:
            logger.error(f"오디오 믹서 초기화 실패: {e}")
            messagebox.showerror("초기화 오류", f"오디오 믹서 초기화 실패: {e}\n\n해결 방법:\n1. 오디오 장치 연결 확인\n2. pygame 재설치: pip install pygame --upgrade")
            exit(1)
        except Exception as e:
            logger.error(f"pygame 초기화 오류: {e}")
            messagebox.showerror("초기화 오류", f"pygame 초기화 중 오류 발생: {e}")
            exit(1)
        
        # 메인 윈도우 설정
        self.root.title("음악 플레이어")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 재생 목록 및 현재 트랙 관련 변수
        self.playlist = []
        self.current_track_index = -1
        self.play_mode_var = tk.StringVar(value="순차재생")
        self.scheduled_task = None  # 나중에 취소할 태스크 ID 저장
        
        # UI 구성 호출
        self._create_ui()
        
        # 주기적 작업 시작
        self.scheduled_task = self.root.after(100, self._check_music_end)
        self._update_track_progress()
        
        logger.info("음악 플레이어 초기화 완료")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """예외 처리 핸들러"""
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"예외 발생: {error_msg}")
        messagebox.showerror("오류 발생", f"예상치 못한 오류가 발생했습니다:\n{exc_value}")
    
    def on_closing(self):
        """프로그램 종료 처리"""
        try:
            if self.scheduled_task:
                self.root.after_cancel(self.scheduled_task)
            mixer.music.stop()
            pygame.quit()
            logger.info("음악 플레이어 정상 종료")
        except Exception as e:
            logger.error(f"종료 중 오류: {e}")
        finally:
            self.root.destroy()
    
    def _create_ui(self):
        """UI 요소 생성 및 배치"""
        # 현재 재생 중인 트랙 표시 레이블
        self.current_track_label = tk.Label(self.root, text="재생중: 없음", fg="blue")
        self.current_track_label.pack(side="top", fill="x")
        
        # 트랙 시간 진행 표시 레이블
        self.progress_label = tk.Label(self.root, text="진행 시간: 00:00", fg="green")
        self.progress_label.pack(side="top", fill="x")
        
        # 메인 윈도우 메뉴 초기화
        self._create_menus()
        
        # 재생 목록 박스
        self.playlist_box = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        self.playlist_box.bind("<Double-1>", self.play_selected)
        
        # 컨트롤 버튼 프레임
        self._create_control_buttons()
    
    def _create_menus(self):
        """메뉴 생성"""
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        # 파일 메뉴
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="메뉴", menu=file_menu)
        file_menu.add_command(label="파일 열기", command=self.open_file)
        file_menu.add_command(label="폴더 열기", command=self.open_folder)
        file_menu.add_command(label="재생 목록 초기화", command=self.clear_playlist)
        file_menu.add_command(label="재생 목록 저장", command=self.save_playlist)
        file_menu.add_command(label="재생 목록 불러오기", command=self.load_playlist)
        
        # 재생 모드 메뉴
        play_mode_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="재생방식", menu=play_mode_menu)
        play_mode_menu.add_radiobutton(label="순차재생", value="순차재생", variable=self.play_mode_var)
        play_mode_menu.add_radiobutton(label="랜덤재생", value="랜덤재생", variable=self.play_mode_var)
        play_mode_menu.add_radiobutton(label="반복재생", value="반복재생", variable=self.play_mode_var)
    
    def _create_control_buttons(self):
        """컨트롤 버튼 생성"""
        control_frame = tk.Frame(self.root)
        control_frame.pack()
        
        prev_button = tk.Button(control_frame, text="이전", command=self.play_previous)
        prev_button.grid(row=0, column=0)
        
        play_button = tk.Button(control_frame, text="재생", command=self.play_selected)
        play_button.grid(row=0, column=1)
        
        stop_button = tk.Button(control_frame, text="정지", command=self.stop_music)
        stop_button.grid(row=0, column=2)
        
        next_button = tk.Button(control_frame, text="다음", command=self.play_next)
        next_button.grid(row=0, column=3)
        
        volume_label = tk.Label(control_frame, text="볼륨")
        volume_label.grid(row=0, column=4)
        
        self.volume_slider = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(50)  # 초기 볼륨 50%로 설정
        self.volume_slider.grid(row=0, column=5)
    
    def validate_play_mode(self):
        """재생 모드 유효성 검사"""
        valid_modes = ["순차재생", "랜덤재생", "반복재생"]
        if self.play_mode_var.get() not in valid_modes:
            self.play_mode_var.set("순차재생")
    
    def add_to_playlist(self, files):
        """재생 목록에 파일 추가"""
        for file in files:
            if file.lower().endswith(('.flac', '.mp3')) and file not in self.playlist:
                self.playlist.append(file)
            elif not file.lower().endswith(('.flac', '.mp3')):
                messagebox.showwarning("지원되지 않는 파일", f"파일 {file}은 지원되는 형식이 아닙니다.")
        self.playlist = natsorted(self.playlist)
        self._update_playlist_display()
    
    def _update_playlist_display(self):
        """재생 목록 표시 업데이트"""
        self.playlist_box.delete(0, tk.END)
        for file in self.playlist:
            self.playlist_box.insert(tk.END, os.path.basename(file))
    
    def open_file(self):
        """파일 선택 대화상자 열기"""
        files = filedialog.askopenfilenames(filetypes=[("오디오 파일", "*.flac *.mp3")])
        if files:
            self.add_to_playlist(files)
    
    def open_folder(self):
        """폴더 선택 대화상자 열기"""
        folder = filedialog.askdirectory()
        if folder:
            files = self._get_audio_files(folder)
            self.add_to_playlist(files)
    
    def _get_audio_files(self, folder):
        """폴더 내 오디오 파일 찾기"""
        audio_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.flac', '.mp3')):
                    audio_files.append(os.path.join(root, file))
        return audio_files
    
    def play_track(self, index):
        """특정 인덱스의 트랙 재생"""
        if not self.playlist:
            logger.warning("재생 목록이 비어 있음")
            return
            
        try:
            if index < 0 or index >= len(self.playlist):
                logger.warning(f"유효하지 않은 트랙 인덱스: {index}, 총 트랙: {len(self.playlist)}")
                return
                
            self.current_track_index = index
            track_path = self.playlist[self.current_track_index]
            
            # 파일 존재 여부 확인
            if not os.path.exists(track_path):
                logger.error(f"파일을 찾을 수 없음: {track_path}")
                messagebox.showerror("파일 오류", f"파일을 찾을 수 없습니다:\n{track_path}")
                return
            
            mixer.music.load(track_path)
            mixer.music.play()
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_track_index)
            self.playlist_box.activate(self.current_track_index)
            self.playlist_box.see(self.current_track_index)  # 현재 재생 트랙 보이게 스크롤
            self.current_track_label.config(text="재생중: " + os.path.basename(track_path))
            logger.info(f"트랙 재생 시작: {os.path.basename(track_path)}")
        except pygame.error as e:
            logger.error(f"트랙 재생 오류: {e}, 파일: {self.playlist[index]}")
            messagebox.showerror("재생 오류", f"파일을 재생할 수 없습니다:\n{e}")
        except IndexError:
            logger.error(f"인덱스 오류: {index}")
            messagebox.showerror("오류", "잘못된 트랙 인덱스입니다.")
        except Exception as e:
            logger.error(f"기타 재생 오류: {e}")
            messagebox.showerror("오류", f"트랙 재생 중 오류 발생:\n{e}")
    
    def play_selected(self, event=None):
        """선택된 트랙 재생 또는 현재 모드에 따라 재생"""
        if not self.playlist:
            return
            
        selected = self.playlist_box.curselection()
        if selected:
            self.play_track(selected[0])
        else:
            # 선택된 트랙이 없는 경우 현재 재생 모드에 따라 재생
            self.validate_play_mode()
            current_mode = self.play_mode_var.get()
            
            if current_mode == "랜덤재생":
                self.play_track(random.randint(0, len(self.playlist) - 1))
            elif current_mode == "반복재생":
                if self.current_track_index != -1:
                    self.play_track(self.current_track_index)
                else:
                    self.play_track(0)  # 재생 중인 트랙이 없으면 첫 번째 트랙으로 기본 설정
            else:  # 순차재생 모드
                if self.current_track_index < len(self.playlist) - 1:
                    self.play_track(self.current_track_index + 1)
                else:
                    self.play_track(0)  # 마지막 트랙인 경우 처음으로 돌아감
    
    def stop_music(self):
        """음악 재생 중지"""
        mixer.music.stop()
        self.current_track_index = -1
        self.playlist_box.selection_clear(0, tk.END)
        self.current_track_label.config(text="재생중: 없음")
        self.progress_label.config(text="진행 시간: 00:00")
        if self.scheduled_task:
            self.root.after_cancel(self.scheduled_task)
            self.scheduled_task = None
    
    def play_previous(self):
        """이전 트랙 재생"""
        if not self.playlist:
            return
            
        self.validate_play_mode()
        current_mode = self.play_mode_var.get()
        
        if current_mode == "반복재생":  # 현재 트랙 반복
            self.play_track(self.current_track_index)
        elif current_mode == "랜덤재생":  # 랜덤 트랙 재생
            self.play_track(random.randint(0, len(self.playlist) - 1))
        elif self.current_track_index > 0:  # 순차적으로 이전 트랙 재생
            self.play_track(self.current_track_index - 1)
        elif self.current_track_index == 0:  # 처음에 있는 경우 마지막 트랙으로 루프
            self.play_track(len(self.playlist) - 1)
    
    def play_next(self):
        """다음 트랙 재생"""
        if not self.playlist:
            return
            
        self.validate_play_mode()
        current_mode = self.play_mode_var.get()
        
        if current_mode == "반복재생":  # 현재 트랙 반복
            self.play_track(self.current_track_index)
        elif current_mode == "랜덤재생":  # 랜덤 트랙 재생
            self.play_track(random.randint(0, len(self.playlist) - 1))
        elif self.current_track_index < len(self.playlist) - 1:  # 순차적으로 다음 트랙 재생
            self.play_track(self.current_track_index + 1)
        else:  # 마지막에 있는 경우 처음으로 루프
            self.play_track(0)
    
    def _check_music_end(self):
        """음악 재생 종료 확인 및 다음 트랙 자동 재생"""
        try:
            if self.current_track_index != -1 and not mixer.music.get_busy():
                self.play_next()
            self.scheduled_task = self.root.after(100, self._check_music_end)
        except Exception as e:
            logger.error(f"음악 종료 확인 중 오류: {e}")
            self.scheduled_task = self.root.after(1000, self._check_music_end)  # 오류 시 더 긴 간격으로 재시도
    
    def set_volume(self, val):
        """볼륨 설정"""
        try:
            volume = float(val) / 100
            mixer.music.set_volume(volume)
        except (ValueError, TypeError):
            mixer.music.set_volume(0.5)  # 기본값 50% 볼륨
    
    def clear_playlist(self):
        """재생 목록 초기화"""
        if messagebox.askyesno("재생 목록 초기화", "현재 재생 목록을 모두 지우시겠습니까?"):
            self.playlist = []
            self.current_track_index = -1
            self._update_playlist_display()
            self.current_track_label.config(text="재생중: 없음")
            self.stop_music()
    
    def save_playlist(self):
        """재생 목록을 파일로 저장"""
        if not self.playlist:
            messagebox.showinfo("알림", "저장할 재생 목록이 없습니다.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("텍스트 파일", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for track in self.playlist:
                        f.write(track + "\n")
                messagebox.showinfo("저장 완료", "재생 목록이 저장되었습니다.")
            except IOError as e:
                messagebox.showerror("파일 오류", f"재생 목록 저장 실패: {e}")
    
    def load_playlist(self):
        """파일에서 재생 목록 불러오기"""
        file_path = filedialog.askopenfilename(filetypes=[("텍스트 파일", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tracks = [line.strip() for line in f.readlines()]
                
                # 존재하는 파일만 추가
                valid_tracks = []
                for track in tracks:
                    if os.path.exists(track):
                        valid_tracks.append(track)
                    else:
                        messagebox.showwarning("파일 없음", f"파일을 찾을 수 없습니다: {track}")
                
                self.add_to_playlist(valid_tracks)
                if valid_tracks:
                    messagebox.showinfo("불러오기 완료", f"{len(valid_tracks)}개의 트랙을 불러왔습니다.")
            except IOError as e:
                messagebox.showerror("파일 오류", f"재생 목록 불러오기 실패: {e}")
    
    def _update_track_progress(self):
        """트랙 진행 시간 업데이트"""
        if mixer.music.get_busy() and self.current_track_index != -1:
            current_time = mixer.music.get_pos() // 1000
            minutes, seconds = divmod(current_time, 60)
            self.progress_label.config(text=f"진행 시간: {minutes:02}:{seconds:02}")
        else:
            self.progress_label.config(text="진행 시간: 00:00")
        self.root.after(1000, self._update_track_progress)


# 메인 실행 코드
if __name__ == "__main__":
    try:
        # pygame 및 natsort 확인
        modules_to_check = [
            ("pygame", "pygame 라이브러리가 설치되어 있지 않습니다. 'pip install pygame' 명령으로 설치하세요."),
            ("natsort", "natsort 라이브러리가 설치되어 있지 않습니다. 'pip install natsort' 명령으로 설치하세요.")
        ]
        
        for module_name, error_msg in modules_to_check:
            try:
                __import__(module_name)
            except ImportError:
                messagebox.showerror("라이브러리 오류", error_msg)
                logger.error(f"필수 라이브러리 없음: {module_name}")
                sys.exit(1)
        
        root = tk.Tk()
        player = MusicPlayer(root)
        root.mainloop()
    except Exception as e:
        error_msg = traceback.format_exc()
        logging.error(f"프로그램 실행 중 오류: {error_msg}")
        try:
            messagebox.showerror("오류", f"프로그램 실행 중 오류가 발생했습니다:\n{e}")
        except:
            print(f"치명적 오류: {e}\n{error_msg}")
        sys.exit(1)