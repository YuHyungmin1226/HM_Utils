#!/usr/bin/env python3
import os
import sys
import importlib.util
import platform
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

# 초기 설정: 필요한 디렉토리 생성
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# transcripts 폴더가 없으면 생성
transcripts_dir = os.path.join(script_dir, "transcripts")
if not os.path.exists(transcripts_dir):
    os.makedirs(transcripts_dir)

# 홈 디렉토리의 youtube_transcripts 폴더가 없으면 생성
home_transcripts_dir = os.path.join(os.path.expanduser("~"), "Documents", "youtube_transcripts")
if not os.path.exists(home_transcripts_dir):
    os.makedirs(home_transcripts_dir)

# 필요한 모듈 확인
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("필수 패키지 누락", "youtube_transcript_api 패키지가 필요합니다.\n\npip install youtube-transcript-api\n명령어로 설치하세요.")
    sys.exit(1)

import webbrowser

def extract_video_id(youtube_url):
    """유튜브 URL에서 비디오 ID 추출"""
    import re
    # 여러 형식의 유튜브 URL에서 ID를 추출하는 정규식
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # 일반적인 유튜브 URL
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # 짧은 URL
        r'(?:embed\/)([0-9A-Za-z_-]{11})',  # 임베드 URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def get_transcript(video_id, language='ko'):
    """동영상 자막 가져오기"""
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 요청한 언어로 자막 찾기
        try:
            transcript = transcript_list.find_transcript([language])
        except:
            # 요청한 언어가 없으면 자동 번역 시도
            try:
                transcript = transcript_list.find_transcript(['en']).translate(language)
            except:
                # 영어 자막도 없으면 가용한 첫 번째 자막 사용
                try:
                    transcript = list(transcript_list)[0]
                except:
                    return None, "자막을 찾을 수 없습니다."
        
        # 자막을 텍스트로 변환
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript.fetch())
        
        return formatted_transcript, None
    except Exception as e:
        return None, f"자막을 가져오는 중 오류 발생: {str(e)}"

def save_transcript_to_file(video_id, transcript):
    """자막을 txt 파일로 저장"""
    # 저장할 폴더 생성 - 현재 실행 위치 기준 상대 경로로 변경
    # 기존 홈 디렉토리 방식도 유지하고 선택할 수 있게 함
    
    # 1. 현재 스크립트 위치 기준 상대경로
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_save_dir = os.path.join(script_dir, "transcripts")
    
    # 2. 기존 홈 디렉토리 경로
    home_save_dir = os.path.join(os.path.expanduser("~"), "Documents", "youtube_transcripts")
    
    # 두 위치 모두 폴더 생성
    os.makedirs(local_save_dir, exist_ok=True)
    os.makedirs(home_save_dir, exist_ok=True)
    
    # 현재 시간을 파일명에 추가
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{video_id}_{timestamp}.txt"
    
    # 두 경로에 모두 저장
    local_file_path = os.path.join(local_save_dir, file_name)
    home_file_path = os.path.join(home_save_dir, file_name)
    
    # 파일 저장
    try:
        # 1. 프로그램 폴더에 저장
        with open(local_file_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # 2. 홈 디렉토리에도 저장 (기존 호환성 유지)
        with open(home_file_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        print(f"자막이 두 위치에 저장되었습니다:")
        print(f"1. 프로그램 폴더: {local_file_path}")
        print(f"2. 홈 디렉토리: {home_file_path}")
        
        return local_file_path, home_file_path
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")
        
        # 만약 로컬 저장에 실패했다면, 홈 디렉토리에만 저장 시도
        try:
            with open(home_file_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"홈 디렉토리에만 저장됨: {home_file_path}")
            return home_file_path, None
        except:
            print("모든 저장 위치에 저장 실패")
            return None, None

def copy_to_clipboard(text):
    """텍스트를 클립보드에 복사"""
    import subprocess
    os_name = platform.system()
    
    try:
        if os_name == 'Darwin':  # macOS
            # macOS에서 유니코드 텍스트를 안전하게 처리하기 위한 설정
            env = {'LC_CTYPE': 'UTF-8', 'LANG': 'ko_KR.UTF-8'}
            process = subprocess.Popen('pbcopy', env=env, stdin=subprocess.PIPE)
            
            # UTF-8로 명시적 인코딩하여 전달
            process.communicate(text.encode('utf-8'))
            return True
            
        elif os_name == 'Windows':
            # 윈도우에서는 임시 파일을 통해 한글 처리를 더 안정적으로 수행
            import tempfile
            
            # 임시 파일 생성하여 UTF-8로 저장
            fd, path = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # PowerShell을 사용하여 클립보드에 복사
                # Get-Content로 파일을 읽고 Set-Clipboard로 클립보드에 설정
                powershell_cmd = f'powershell -command "Get-Content -Path \'{path}\' -Encoding UTF8 | Set-Clipboard"'
                subprocess.run(powershell_cmd, shell=True)
                return True
            finally:
                os.remove(path)  # 임시 파일 삭제
                
        else:  # Linux나 다른 OS는 xclip 사용
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
            
    except Exception as e:
        print(f"클립보드에 복사하는 중 오류 발생: {str(e)}")
        
        # 오류가 발생하면 대체 방법 시도
        try:
            # 파이썬 클립보드 모듈 시도
            import pyperclip
            pyperclip.copy(text)
            print("pyperclip을 사용하여 클립보드에 복사했습니다.")
            return True
        except:
            print("pyperclip 모듈을 사용할 수 없습니다. pip install pyperclip으로 설치하세요.")
            return False

def open_chatgpt_web(transcript, video_id, gui_callback=None):
    """ChatGPT 웹페이지 열기"""
    import webbrowser
    base_url = "https://chat.openai.com/"
    
    # 자막이 너무 길면 잘라내기 (ChatGPT 입력 한도 고려)
    if len(transcript) > 15000:
        print("자막이 너무 깁니다. 처음 15,000자만 사용합니다.")
        transcript = transcript[:15000]
    
    # 요약 안내 메시지 표시
    print("\n=== ChatGPT 웹 요약 안내 ===")
    print(f"영상 ID: {video_id}")
    print(f"자막 길이: {len(transcript)} 글자")
    
    # 사용자에게 지침 제공
    print("\n1. ChatGPT 웹페이지가 잠시 후 열립니다.")
    print("2. 클립보드에 복사된 자막을 ChatGPT 입력창에 붙여넣기(Ctrl+V 또는 Cmd+V)하세요.")
    print("3. 다음 프롬프트를 먼저 입력한 후 자막을 붙여넣으세요: '이 유튜브 영상 자막을 간결하게 요약해주세요:'")
    print("4. Enter를 눌러 요약을 요청하세요.")
    
    # 5초 대기 후 ChatGPT 웹페이지 열기
    print("\n5초 후 ChatGPT 웹사이트가 열립니다...")
    import time
    time.sleep(5)
    webbrowser.open(base_url)
    
    return True

# ===================== GUI 구현 =====================
class YoutubeTranscriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("유튜브 자막 추출 및 ChatGPT 요약 도구")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ENTRY_WIDTH = 85
        BUTTON_WIDTH = 40
        tk.Label(self.root, text="유튜브 URL 입력:", anchor='w').pack(pady=(15, 0), fill='x')
        self.url_entry = tk.Entry(self.root, width=ENTRY_WIDTH, font=('Arial', 12))
        self.url_entry.pack(pady=5, fill='x', padx=10)
        self.url_entry.focus()
        # 붙여넣기 단축키 바인딩 (macOS Cmd+V, Windows/Linux Ctrl+V, X11 등)
        def paste_event(event=None):
            try:
                self.url_entry.event_generate('<<Paste>>')
            except Exception:
                try:
                    clipboard = self.root.clipboard_get()
                    import tkinter
                    self.url_entry.insert(tkinter.INSERT, clipboard)
                except Exception:
                    pass
            return "break"
        if platform.system() == "Darwin":
            self.url_entry.bind('<Command-v>', paste_event)
            self.url_entry.bind('<Command-V>', paste_event)
        else:
            self.url_entry.bind('<Control-v>', paste_event)
            self.url_entry.bind('<Control-V>', paste_event)
        self.url_entry.bind('<Button-2>', paste_event)  # X11 middle click
        # 링크 붙여넣기 버튼 (가로폭 맞춤, fetch_btn 위에)
        self.paste_btn = tk.Button(self.root, text="링크 붙여넣기", command=self.on_paste_link, width=BUTTON_WIDTH)
        self.paste_btn.pack(pady=(5, 0))
        self.fetch_btn = tk.Button(self.root, text="자막 추출 및 요약 준비", command=self.on_fetch, width=BUTTON_WIDTH)
        self.fetch_btn.pack(pady=5)
        self.status_text = scrolledtext.ScrolledText(self.root, width=ENTRY_WIDTH, height=20, wrap=tk.WORD, font=('Arial', 12))
        self.status_text.pack(pady=10, fill='x', padx=10)
        self.status_text.insert(tk.END, "유튜브 URL을 입력하고 버튼을 누르세요.\n")
        self.status_text.config(state=tk.DISABLED)
        self.open_chatgpt_btn = tk.Button(self.root, text="ChatGPT 웹사이트 열기", command=self.on_open_chatgpt, state=tk.DISABLED, width=BUTTON_WIDTH)
        self.open_chatgpt_btn.pack(pady=5)
        self.save_btn = tk.Button(self.root, text="자막 파일 저장 위치 열기", command=self.on_open_folder, state=tk.DISABLED, width=BUTTON_WIDTH)
        self.save_btn.pack(pady=5)
        self.transcript = None
        self.video_id = None
        self.saved_paths = None

    def set_status(self, msg, append=True):
        self.status_text.config(state=tk.NORMAL)
        if not append:
            self.status_text.delete('1.0', tk.END)
        self.status_text.insert(tk.END, msg + '\n')
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def on_fetch(self):
        url = self.url_entry.get().strip()
        if not url or not ("youtube.com" in url or "youtu.be" in url):
            messagebox.showwarning("입력 오류", "올바른 유튜브 URL을 입력하세요.")
            return
        self.set_status("자막을 추출 중입니다...", append=False)
        self.fetch_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.fetch_transcript, args=(url,)).start()

    def fetch_transcript(self, url):
        try:
            video_id = extract_video_id(url)
            if not video_id:
                self.set_status("유효한 유튜브 URL이 아닙니다.")
                self.fetch_btn.config(state=tk.NORMAL)
                return
            self.set_status(f"비디오 ID: {video_id}\n자막을 가져오는 중...")
            transcript, error = get_transcript(video_id)
            if error:
                self.set_status(f"오류: {error}")
                self.fetch_btn.config(state=tk.NORMAL)
                return
            self.set_status(f"자막 길이: {len(transcript)} 글자\n자막 미리보기: {transcript[:150]}...\n자막을 파일로 저장하는 중...")
            local_path, home_path = save_transcript_to_file(video_id, transcript)
            if not local_path:
                self.set_status("자막 파일 저장에 실패했습니다.")
                self.fetch_btn.config(state=tk.NORMAL)
                return
            
            # 자막을 클립보드에 자동 복사
            self.set_status("자막을 클립보드에 복사하는 중...")
            if copy_to_clipboard(transcript):
                self.set_status("✓ 자막이 클립보드에 복사되었습니다.")
            else:
                self.set_status("✗ 클립보드 복사에 실패했습니다. pyperclip 설치를 확인하세요.")
            
            self.transcript = transcript
            self.video_id = video_id
            self.saved_paths = (local_path, home_path)
            self.set_status(f"자막이 성공적으로 저장되었습니다.\n1. 프로그램 폴더: {local_path}\n2. 홈 디렉토리: {home_path}\n\n아래 버튼으로 ChatGPT 웹사이트를 열어 요약을 요청하세요.")
            self.open_chatgpt_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.set_status(f"오류 발생: {str(e)}")
        finally:
            self.fetch_btn.config(state=tk.NORMAL)

    def on_open_chatgpt(self):
        if not self.transcript or not self.video_id:
            messagebox.showinfo("안내", "먼저 자막을 추출하세요.")
            return
        self.set_status("ChatGPT 웹사이트를 엽니다...", append=True)
        threading.Thread(target=open_chatgpt_web, args=(self.transcript, self.video_id, self.set_status)).start()

    def on_open_folder(self):
        # 항상 OS 기본 문서 폴더의 youtube_transcripts 폴더를 엽니다.
        folder = os.path.join(os.path.expanduser("~"), "Documents", "youtube_transcripts")
        if os.path.exists(folder):
            if platform.system() == 'Darwin':
                os.system(f'open "{folder}"')
            elif platform.system() == 'Windows':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showinfo("안내", "문서 폴더에 youtube_transcripts 폴더가 없습니다.")

    def on_paste_link(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
        except Exception:
            messagebox.showwarning("클립보드 오류", "클립보드에서 텍스트를 읽을 수 없습니다.")

def main():
    root = tk.Tk()
    app = YoutubeTranscriptGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 