import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from music21 import stream, converter, key, spanner, tie, scale, note
import os
from typing import Optional, Dict, Any

class MusicXMLEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MusicXML 편집기")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.current_file: Optional[str] = None
        self.score: Optional[stream.Score] = None
        
        self.setup_gui()
        
    def setup_gui(self):
        """GUI 구성 요소를 설정합니다."""
        # 스타일 설정
        style = ttk.Style()
        style.configure('TLabel', padding=6, font=("맑은 고딕", 11))
        style.configure('TButton', padding=6, font=("맑은 고딕", 11))
        style.configure('TEntry', padding=6, font=("맑은 고딕", 11))
        style.configure('TCombobox', padding=6, font=("맑은 고딕", 11))
        style.configure('TLabelframe', padding=12, font=("맑은 고딕", 12, 'bold'))
        style.configure('TFrame', padding=0)

        # 메인 프레임 (수직 2행: 파일, 아래 2단)
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=16, pady=16)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)  # 파일 프레임
        main_frame.grid_rowconfigure(1, weight=1)  # 아래 2단
        main_frame.grid_rowconfigure(2, weight=1)

        # 파일 프레임 (좌우 전체)
        file_frame = ttk.LabelFrame(main_frame, text="파일")
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        file_frame.grid_columnconfigure(0, weight=5)
        file_frame.grid_columnconfigure(1, weight=1)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=48).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ttk.Button(file_frame, text="파일 열기", command=self.open_file, width=14).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        # 현재 조성 정보 프레임
        current_key_frame = ttk.LabelFrame(main_frame, text="현재 조성")
        current_key_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        current_key_frame.grid_columnconfigure(0, weight=1)
        current_key_frame.grid_columnconfigure(1, weight=1)
        self.original_key_label = ttk.Label(current_key_frame, text="원본 조성: -")
        self.original_key_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        self.current_key_label = ttk.Label(current_key_frame, text="조성: -")
        self.current_key_label.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        self.current_mode_label = ttk.Label(current_key_frame, text="조성 타입: -")
        self.current_mode_label.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        self.change_key_label = ttk.Label(current_key_frame, text="")
        self.change_key_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=4)

        # 아래 2단 프레임
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=3, minsize=320)
        bottom_frame.grid_columnconfigure(1, weight=2, minsize=240)
        bottom_frame.grid_rowconfigure(0, weight=1)

        # 좌측 프레임 (조옮김)
        left_frame = ttk.Frame(bottom_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=2)
        left_frame.grid_columnconfigure(0, weight=1)

        # 조옮김 옵션 프레임
        transposition_frame = ttk.LabelFrame(left_frame, text="조옮김")
        transposition_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        transposition_frame.grid_columnconfigure(0, weight=1)
        transposition_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(transposition_frame, text="조성:").grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)
        self.key_var = tk.StringVar(value="C")
        key_combo = ttk.Combobox(transposition_frame, textvariable=self.key_var, 
                                values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                                width=12)
        key_combo.grid(row=0, column=1, sticky=tk.W, padx=8, pady=8)
        key_combo.state(['readonly'])
        ttk.Label(transposition_frame, text="조성 타입:").grid(row=1, column=0, sticky=tk.W, padx=8, pady=8)
        self.key_type_var = tk.StringVar(value="major")
        key_type_combo = ttk.Combobox(transposition_frame, textvariable=self.key_type_var,
                                     values=["major", "minor"],
                                     width=12)
        key_type_combo.grid(row=1, column=1, sticky=tk.W, padx=8, pady=8)
        key_type_combo.state(['readonly'])
        ttk.Button(transposition_frame, text="조옮김 적용", command=self.transpose, width=22).grid(row=2, column=0, columnspan=2, pady=16)

        # 우측 프레임 (이음줄/붙임줄/저장)
        right_frame = ttk.Frame(bottom_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right_frame.grid_rowconfigure(0, weight=2)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 이음줄/붙임줄 옵션 프레임
        articulation_frame = ttk.LabelFrame(right_frame, text="이음줄/붙임줄")
        articulation_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8), padx=0)
        articulation_frame.grid_columnconfigure(0, weight=1)
        articulation_frame.grid_rowconfigure(0, weight=1)
        articulation_inner = ttk.Frame(articulation_frame)
        articulation_inner.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        articulation_inner.grid_columnconfigure(0, weight=1)
        articulation_inner.grid_columnconfigure(1, weight=1)
        articulation_inner.grid_rowconfigure(0, weight=1)
        articulation_inner.grid_rowconfigure(1, weight=1)
        articulation_inner.grid_rowconfigure(2, weight=1)

        self.use_slurs_var = tk.BooleanVar(value=True)
        self.slur_btn = ttk.Button(articulation_inner, text="이음줄 추가", command=self.toggle_slurs, width=16)
        self.slur_chk = ttk.Checkbutton(articulation_inner, text="이음줄 사용", variable=self.use_slurs_var, command=self.update_slur_btn_text)
        self.slur_chk.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        self.slur_btn.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        self.use_ties_var = tk.BooleanVar(value=True)
        self.tie_btn = ttk.Button(articulation_inner, text="붙임줄 추가", command=self.toggle_ties, width=16)
        self.tie_chk = ttk.Checkbutton(articulation_inner, text="붙임줄 사용", variable=self.use_ties_var, command=self.update_tie_btn_text)
        self.tie_chk.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        self.tie_btn.grid(row=1, column=1, sticky="ew", padx=8, pady=8)

        # 변경사항 적용 버튼
        self.apply_btn = ttk.Button(articulation_inner, text="변경사항 적용", command=self.apply_articulation_changes, width=24)
        self.apply_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=12)

        self.update_slur_btn_text()
        self.update_tie_btn_text()

        # 확장성 보장
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=3)
        bottom_frame.grid_columnconfigure(1, weight=2)
        right_frame.grid_rowconfigure(0, weight=2)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

    def open_file(self):
        """MusicXML 파일을 엽니다."""
        file_path = filedialog.askopenfilename(
            filetypes=[("MusicXML files", "*.musicxml"), ("All files", "*.*")]
        )
        if not file_path:
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("오류", "파일이 존재하지 않습니다.")
            return
            
        try:
            # 파일 크기 확인
            if os.path.getsize(file_path) == 0:
                messagebox.showerror("오류", "파일이 비어있습니다.")
                return
                
            # 파일 읽기 시도
            self.score = converter.parse(file_path)
            
            # 파트 확인
            if not self.score.parts:
                messagebox.showerror("오류", "파일에 음악 파트가 없습니다.")
                return
                
            self.current_file = file_path
            self.file_path_var.set(file_path)
            
            # 원본 조성(KeySignature) 저장
            from music21 import key
            ks = next(self.score.recurse().getElementsByClass(key.KeySignature), None)
            if ks is not None:
                k = ks.asKey()
                self.original_tonic = k.tonic.name
                self.original_mode = k.mode
            else:
                # fallback: analyze
                k = self.score.analyze('key')
                self.original_tonic = k.tonic.name
                self.original_mode = k.mode

            # 현재 조성 정보 업데이트
            self.update_current_key_info()
            
            # 파일 정보 표시
            part_count = len(self.score.parts)
            messagebox.showinfo("성공", f"파일을 성공적으로 열었습니다.\n파트 수: {part_count}")
            
        except Exception as e:
            error_msg = str(e)
            if "No module named" in error_msg:
                messagebox.showerror("오류", "필요한 라이브러리가 설치되어 있지 않습니다.")
            elif "Permission denied" in error_msg:
                messagebox.showerror("오류", "파일 접근 권한이 없습니다.")
            else:
                messagebox.showerror("오류", f"파일을 열 수 없습니다: {error_msg}")
            self.score = None
            self.current_file = None
            self.file_path_var.set("")
            self.clear_current_key_info()

    def update_current_key_info(self, before=None, after=None):
        from music21 import key, interval
        def get_key_info_from_score(score):
            ks = next(score.recurse().getElementsByClass(key.KeySignature), None)
            if ks is not None:
                k = ks.asKey()
                return k.tonic.name, k.mode
            return '-', '-'
        # 원본 조성 표시
        orig = (getattr(self, 'original_tonic', '-'), getattr(self, 'original_mode', '-'))
        self.original_key_label.config(text=f"원본 조성: {orig[0]} {orig[1]}")
        # 현재 조성 표시
        tonic, mode = get_key_info_from_score(self.score)
        self.current_key_label.config(text=f"조성: {tonic}")
        self.current_mode_label.config(text=f"조성 타입: {mode}")
        # 변경 전/후 조성 및 반음 차이 표시
        if before and after:
            try:
                ivl = interval.Interval(key.Key(before[0], before[1]).tonic, key.Key(after[0], after[1]).tonic)
                semitones = ivl.semitones
                diff_str = f" (반음 차이: {semitones})"
            except Exception:
                diff_str = ""
            self.change_key_label.config(text=f"변경 전: {before[0]} {before[1]} / 변경 후: {after[0]} {after[1]}{diff_str}")
        else:
            self.change_key_label.config(text="")

    def clear_current_key_info(self):
        """현재 조성 정보를 초기화합니다."""
        self.current_key_label.config(text="조성: -")
        self.current_mode_label.config(text="조성 타입: -")

    def transpose(self):
        """조옮김을 적용합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        try:
            from music21 import key, interval, scale, note
            # 변경 전 조성: 조옮김 직전의 KeySignature
            ks = next(self.score.recurse().getElementsByClass(key.KeySignature), None)
            if ks is not None:
                before_key = ks.asKey()
                before_tonic = before_key.tonic.name
                before_mode = before_key.mode
            else:
                before_key = self.score.analyze('key')
                before_tonic = before_key.tonic.name
                before_mode = before_key.mode

            # 목표 조성 설정
            target_tonic = self.key_var.get()
            target_mode = self.key_type_var.get()
            target_key_obj = key.Key(target_tonic, target_mode)

            # 조옮김 간격 계산
            ivl = interval.Interval(before_key.tonic, target_key_obj.tonic)

            # 실제 조옮김 적용
            if before_tonic != target_tonic:
                # tonic이 다르면 일반 transpose
                self.score = self.score.transpose(ivl)
            elif before_mode != target_mode:
                # tonic은 같고 mode만 다르면 모드 변환
                if before_mode == 'major' and target_mode == 'minor':
                    from_scale = scale.MajorScale(before_tonic)
                    to_scale = scale.MinorScale(target_tonic)
                elif before_mode == 'minor' and target_mode == 'major':
                    from_scale = scale.MinorScale(before_tonic)
                    to_scale = scale.MajorScale(target_tonic)
                else:
                    from_scale = None
                    to_scale = None
                if from_scale and to_scale:
                    for n in self.score.recurse().notes:
                        if isinstance(n, note.Note):
                            try:
                                deg = from_scale.getScaleDegreeFromPitch(n.pitch)
                                if deg is not None:
                                    new_pitch = to_scale.pitchFromDegree(deg)
                                    n.pitch = new_pitch
                            except Exception:
                                continue
            else:
                # tonic, mode 모두 같으면 아무것도 하지 않음
                pass

            # 기존 조표(KeySignature) 모두 삭제
            for part in self.score.parts:
                for ks in list(part.recurse().getElementsByClass(key.KeySignature)):
                    if ks.activeSite is not None:
                        ks.activeSite.remove(ks)

            # 새로운 조표 추가 (각 파트의 시작 부분에)
            new_ks = key.KeySignature(target_key_obj.sharps)
            for part in self.score.parts:
                part.insert(0, new_ks)

            # 변경 후 조성 정보
            after_tonic = target_tonic
            after_mode = target_mode

            # 변경 전/후 조성 정보 모두 표시
            self.update_current_key_info(before=(before_tonic, before_mode), after=(after_tonic, after_mode))

            # 결과 메시지
            messagebox.showinfo("성공", 
                f"조성을 {before_tonic} {before_mode}에서 {target_tonic} {target_mode}로 변경했습니다.\n"
                f"({ivl.niceName} 조옮김)\n사본으로 저장합니다.")

            # 변경된 파일을 사본으로 저장
            self.save_transposed_copy(before_tonic, before_mode, target_tonic, target_mode)

        except Exception as e:
            error_msg = str(e)
            if "No key found" in error_msg:
                messagebox.showerror("오류", "현재 파일에서 조성을 찾을 수 없습니다.")
            else:
                messagebox.showerror("오류", f"조옮김 중 오류가 발생했습니다: {error_msg}")

    def save_transposed_copy(self, from_tonic, from_mode, to_tonic, to_mode):
        """조옮김된 사본을 저장합니다."""
        import os
        if not self.current_file:
            messagebox.showerror("오류", "원본 파일 경로를 알 수 없습니다.")
            return
        base, ext = os.path.splitext(self.current_file)
        new_filename = f"{base}_{from_tonic}_{from_mode}_to_{to_tonic}_{to_mode}{ext}"
        try:
            self.score.write('musicxml', fp=new_filename)
            messagebox.showinfo("사본 저장 완료", f"사본이 저장되었습니다:\n{new_filename}")
        except Exception as e:
            messagebox.showerror("오류", f"사본 저장 중 오류가 발생했습니다: {str(e)}")

    def toggle_slurs(self):
        """이음줄을 토글합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        try:
            if self.use_slurs_var.get():
                # 기존 이음줄 제거
                for part in self.score.parts:
                    for sp in part.spanners:
                        if isinstance(sp, spanner.Slur):
                            part.remove(sp)
                
                # 이음줄 추가
                for part in self.score.parts:
                    notes = list(part.flat.notes)
                    if not notes:
                        continue
                        
                    # 4음표 단위로 이음줄 추가
                    for i in range(0, len(notes)-1, 4):
                        if i+3 < len(notes):
                            # 음표 간격이 너무 큰 경우 건너뛰기
                            if any(abs(notes[j].offset - notes[j+1].offset) > 4.0 
                                  for j in range(i, i+3)):
                                continue
                                
                            slur = spanner.Slur()
                            for n in notes[i:i+4]:
                                slur.addSpannedElements(n)
                            part.insert(0, slur)
                            
                messagebox.showinfo("성공", "이음줄을 추가했습니다.")
            else:
                # 이음줄 제거
                removed_count = 0
                for part in self.score.parts:
                    for sp in part.spanners:
                        if isinstance(sp, spanner.Slur):
                            part.remove(sp)
                            removed_count += 1
                            
                messagebox.showinfo("성공", f"{removed_count}개의 이음줄을 제거했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"이음줄 토글 중 오류가 발생했습니다: {str(e)}")

    def toggle_ties(self):
        """붙임줄을 토글합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        try:
            if self.use_ties_var.get():
                # 기존 붙임줄 제거
                for part in self.score.parts:
                    for n in part.flat.notes:
                        n.tie = None
                
                # 붙임줄 추가
                added_count = 0
                for part in self.score.parts:
                    notes = list(part.flat.notes)
                    for i in range(len(notes)-1):
                        n1 = notes[i]
                        n2 = notes[i+1]
                        if n1.nameWithOctave == n2.nameWithOctave:
                            # offset이 정확히 이어지는 경우에만 붙임줄 추가
                            if abs((n1.offset + n1.quarterLength) - n2.offset) > 0.01:
                                continue
                            # 이미 tie가 있으면 덮어쓰지 않음
                            if n1.tie is None:
                                n1.tie = tie.Tie('start')
                            if n2.tie is None:
                                n2.tie = tie.Tie('stop')
                            added_count += 1
                messagebox.showinfo("성공", f"{added_count}개의 붙임줄을 추가했습니다.")
            else:
                # 붙임줄 제거
                removed_count = 0
                for part in self.score.parts:
                    for n in part.flat.notes:
                        if n.tie is not None:
                            n.tie = None
                            removed_count += 1
                messagebox.showinfo("성공", f"{removed_count}개의 붙임줄을 제거했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"붙임줄 토글 중 오류가 발생했습니다: {str(e)}")

    def update_slur_btn_text(self):
        if self.use_slurs_var.get():
            self.slur_btn.config(text="이음줄 추가")
        else:
            self.slur_btn.config(text="이음줄 제거")

    def update_tie_btn_text(self):
        if self.use_ties_var.get():
            self.tie_btn.config(text="붙임줄 추가")
        else:
            self.tie_btn.config(text="붙임줄 제거")

    def apply_articulation_changes(self):
        """이음줄/붙임줄 변경사항을 적용하고 사본을 저장합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        try:
            # 이음줄 처리
            if self.use_slurs_var.get():
                # 기존 이음줄 제거
                for part in self.score.parts:
                    for sp in part.spanners:
                        if isinstance(sp, spanner.Slur):
                            part.remove(sp)
                
                # 이음줄 추가
                for part in self.score.parts:
                    notes = list(part.flat.notes)
                    if not notes:
                        continue
                        
                    # 4음표 단위로 이음줄 추가
                    for i in range(0, len(notes)-1, 4):
                        if i+3 < len(notes):
                            # 음표 간격이 너무 큰 경우 건너뛰기
                            if any(abs(notes[j].offset - notes[j+1].offset) > 4.0 
                                  for j in range(i, i+3)):
                                continue
                                
                            slur = spanner.Slur()
                            for n in notes[i:i+4]:
                                slur.addSpannedElements(n)
                            part.insert(0, slur)

            # 붙임줄 처리
            if self.use_ties_var.get():
                # 기존 붙임줄 제거
                for part in self.score.parts:
                    for n in part.flat.notes:
                        n.tie = None
                
                # 붙임줄 추가
                added_count = 0
                for part in self.score.parts:
                    notes = list(part.flat.notes)
                    for i in range(len(notes)-1):
                        n1 = notes[i]
                        n2 = notes[i+1]
                        if n1.nameWithOctave == n2.nameWithOctave:
                            # offset이 정확히 이어지는 경우에만 붙임줄 추가
                            if abs((n1.offset + n1.quarterLength) - n2.offset) > 0.01:
                                continue
                            # 이미 tie가 있으면 덮어쓰지 않음
                            if n1.tie is None:
                                n1.tie = tie.Tie('start')
                            if n2.tie is None:
                                n2.tie = tie.Tie('stop')
                            added_count += 1

            # 변경사항을 사본으로 저장
            if not self.current_file:
                messagebox.showerror("오류", "원본 파일 경로를 알 수 없습니다.")
                return

            base, ext = os.path.splitext(self.current_file)
            new_filename = f"{base}_articulation_changes{ext}"
            self.score.write('musicxml', fp=new_filename)
            messagebox.showinfo("성공", f"변경사항이 적용되어 사본이 저장되었습니다:\n{new_filename}")

        except Exception as e:
            messagebox.showerror("오류", f"변경사항 적용 중 오류가 발생했습니다: {str(e)}")

    def save_file(self):
        """현재 파일을 저장합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        if not self.current_file:
            self.save_as()
            return

        try:
            # 파일 쓰기 권한 확인
            if not os.access(os.path.dirname(self.current_file), os.W_OK):
                messagebox.showerror("오류", "파일 저장 권한이 없습니다.")
                return
                
            # 임시 파일로 먼저 저장
            temp_file = self.current_file + ".tmp"
            self.score.write('musicxml', fp=temp_file)
            
            # 임시 파일이 성공적으로 생성되었는지 확인
            if not os.path.exists(temp_file):
                raise Exception("임시 파일 생성 실패")
                
            # 기존 파일 백업
            if os.path.exists(self.current_file):
                backup_file = self.current_file + ".bak"
                os.replace(self.current_file, backup_file)
            
            # 임시 파일을 실제 파일로 이동
            os.replace(temp_file, self.current_file)
            
            # 백업 파일 삭제
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
            messagebox.showinfo("성공", "파일을 저장했습니다.")
            
        except Exception as e:
            error_msg = str(e)
            if "Permission denied" in error_msg:
                messagebox.showerror("오류", "파일 저장 권한이 없습니다.")
            else:
                messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다: {error_msg}")
            
            # 임시 파일 정리
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def save_as(self):
        """다른 이름으로 저장합니다."""
        if not self.score:
            messagebox.showwarning("경고", "먼저 파일을 열어주세요.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".musicxml",
            filetypes=[("MusicXML files", "*.musicxml"), ("All files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            # 파일 쓰기 권한 확인
            if not os.access(os.path.dirname(file_path), os.W_OK):
                messagebox.showerror("오류", "파일 저장 권한이 없습니다.")
                return
                
            # 임시 파일로 먼저 저장
            temp_file = file_path + ".tmp"
            self.score.write('musicxml', fp=temp_file)
            
            # 임시 파일이 성공적으로 생성되었는지 확인
            if not os.path.exists(temp_file):
                raise Exception("임시 파일 생성 실패")
                
            # 기존 파일이 있다면 백업
            if os.path.exists(file_path):
                backup_file = file_path + ".bak"
                os.replace(file_path, backup_file)
            
            # 임시 파일을 실제 파일로 이동
            os.replace(temp_file, file_path)
            
            # 백업 파일 삭제
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
            self.current_file = file_path
            self.file_path_var.set(file_path)
            messagebox.showinfo("성공", "파일을 저장했습니다.")
            
        except Exception as e:
            error_msg = str(e)
            if "Permission denied" in error_msg:
                messagebox.showerror("오류", "파일 저장 권한이 없습니다.")
            else:
                messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다: {error_msg}")
            
            # 임시 파일 정리
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def run(self):
        """프로그램을 실행합니다."""
        self.root.mainloop()

def main():
    app = MusicXMLEditor()
    app.run()

if __name__ == "__main__":
    main() 