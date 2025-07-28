import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys
import platform

class SilentTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("소리 없는 타이머")
        self.root.geometry("300x200")

        # 입력 필드 레이블
        tk.Label(root, text="시간(시:분:초)").pack(pady=5)

        # 입력 필드
        self.entry_time = tk.Entry(root, justify="center", font=("Arial", 14))
        self.entry_time.insert(0, "00:10:00")  # 기본값 설정 (10분)
        self.entry_time.pack(pady=5)

        # 남은 시간 표시 라벨
        self.remaining_label = tk.Label(root, text="남은 시간: 00:00:00", font=("Arial", 12))
        self.remaining_label.pack(pady=5)

        # 버튼 프레임
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # 시작 버튼
        self.start_button = tk.Button(button_frame, text="타이머 시작", command=self.start_timer)
        self.start_button.pack(side="left", padx=5)

        # 중단 버튼
        self.stop_button = tk.Button(button_frame, text="타이머 중단", command=self.stop_timer, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # macOS에서 앱이 활성화되는 메서드 등록
        if platform.system() == 'Darwin':  # macOS 확인
            self.root.createcommand('::tk::mac::RaiseWindow', self.root.lift)

        self.timer_running = False  # 타이머 실행 상태 플래그
        self.popup = None  # 팝업 창 참조 저장

    def start_timer(self):
        time_str = self.entry_time.get()
        
        try:
            h, m, s = map(int, time_str.split(":"))
            total_seconds = h * 3600 + m * 60 + s
            
            if total_seconds <= 0:
                messagebox.showerror("오류", "시간을 1초 이상 입력하세요.")
                return

            self.timer_running = True
            self.start_button.config(state="disabled")  # 시작 버튼 비활성화
            self.stop_button.config(state="normal")  # 중단 버튼 활성화
            self.entry_time.config(state="disabled")  # 입력 필드 비활성화
            threading.Thread(target=self.countdown, args=(total_seconds,), daemon=True).start()

        except ValueError:
            messagebox.showerror("오류", "올바른 시간 형식(HH:MM:SS)으로 입력하세요.")

    def stop_timer(self):
        self.timer_running = False
        self.remaining_label.config(text="남은 시간: 00:00:00")  # 남은 시간 초기화
        self.start_button.config(state="normal")  # 시작 버튼 활성화
        self.stop_button.config(state="disabled")  # 중단 버튼 비활성화
        self.entry_time.config(state="normal")  # 입력 필드 활성화

    def countdown(self, total_seconds):
        while total_seconds > 0 and self.timer_running:
            self.update_time_label(total_seconds)
            time.sleep(1)
            total_seconds -= 1

        if self.timer_running:  # 타이머가 중단되지 않은 경우
            self.show_popup()

    def update_time_label(self, total_seconds):
        mins, secs = divmod(total_seconds, 60)
        hours, mins = divmod(mins, 60)
        time_format = f"{hours:02}:{mins:02}:{secs:02}"
        self.remaining_label.config(text=f"남은 시간: {time_format}")
        self.root.update()

    def show_popup(self):
        """팝업이 항상 화면에 보이도록 설정"""
        # 기존 팝업이 있으면 닫기
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.destroy()
            
        self.popup = tk.Toplevel(self.root)
        self.popup.title("타이머 완료")
        self.popup.geometry("250x100")
        
        # 맨 앞에 표시하기 위한 설정들
        self.popup.attributes("-topmost", True)  # 항상 위에 표시
        self.popup.lift()  # 창을 최상단으로 이동
        self.popup.focus_force()  # 팝업에 포커스 설정
        self.popup.grab_set()  # 모달 창으로 설정
        
        # macOS에서 앱을 Dock에서 활성화
        if platform.system() == 'Darwin':
            try:
                self.popup.attributes('-topmost', False)  # 잠시 topmost 해제
                self.popup.after(100, lambda: self.popup.attributes('-topmost', True))  # 다시 topmost 설정
                self.root.bell()  # 시스템 알림음
                
                # macOS에서 앱 활성화 명령 (Apple Event)
                if hasattr(self.root, 'tk') and hasattr(self.root.tk, 'call'):
                    self.root.tk.call('::tk::mac::activateApp')
            except Exception:
                pass
                
        # 팝업 내용
        label = tk.Label(self.popup, text="⏰ 시간이 완료되었습니다!", font=("Arial", 14))
        label.pack(pady=20)

        button = tk.Button(self.popup, text="확인", command=lambda: self.close_popup())
        button.pack()
        
        # 일정 시간 후에 다시 팝업을 최상위로 가져오기
        self.popup.after(1000, self.re_raise_popup)
        
    def re_raise_popup(self):
        """팝업이 뒤로 숨겨지는 것을 방지하기 위해 주기적으로 최상위로 가져옴"""
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.lift()
            self.popup.attributes('-topmost', True)
            # 1초 후 다시 확인
            self.popup.after(1000, self.re_raise_popup)

    def close_popup(self):
        """팝업 닫기 + 남은 시간 초기화 + 버튼 활성화"""
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.grab_release()  # 모달 상태 해제
            self.popup.destroy()
        self.popup = None
        self.stop_timer()  # 타이머 중단 로직 호출

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = SilentTimer(root)
    root.mainloop()
