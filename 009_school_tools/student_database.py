import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
import pandas as pd
import re
from pathlib import Path

class StudentDatabase:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("학생 관리 시스템")
        self.root.geometry("1200x700")  # 윈도우 크기 증가
        
        # 데이터베이스 초기화
        self.init_database()
        
        # GUI 설정
        self.setup_gui()
        
    def init_database(self):
        """데이터베이스와 테이블을 초기화합니다."""
        # OS의 기본 문서 폴더 경로 구하기
        documents_path = str(Path.home() / 'Documents' / 'student.db')
        os.makedirs(documents_path, exist_ok=True)
        db_path = os.path.join(documents_path, 'school.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 학생 테이블 생성
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT UNIQUE,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 평가 요소 테이블 생성
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject TEXT NOT NULL,
                score REAL,
                evaluation_date DATE,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        self.conn.commit()
        
    def import_excel(self):
        """엑셀 파일에서 학생 정보를 가져와 데이터베이스에 추가합니다."""
        try:
            # 파일 선택 대화상자
            file_path = filedialog.askopenfilename(
                title="엑셀 파일 선택",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if not file_path:
                return
            
            # 엑셀 파일 읽기
            try:
                students_df = pd.read_excel(file_path, sheet_name='학생정보')
                evaluations_df = pd.read_excel(file_path, sheet_name='평가정보')
            except ValueError as e:
                messagebox.showerror("오류", "엑셀 파일은 '학생정보'와 '평가정보' 시트를 포함해야 합니다.")
                return
            
            # 학생 정보 시트 검증
            required_columns = ['학번', '이름']
            missing_columns = [col for col in required_columns if col not in students_df.columns]
            
            if missing_columns:
                messagebox.showerror("오류", f"학생정보 시트에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")
                return
            
            # 학생 데이터 유효성 검사
            for index, row in students_df.iterrows():
                if pd.isna(row['학번']) or pd.isna(row['이름']):
                    messagebox.showerror("오류", f"학생정보 시트의 {index + 2}번째 행에 빈 값이 있습니다.")
                    return
            
            # 평가 정보 시트 검증 (선택적)
            if not evaluations_df.empty:
                eval_required_columns = ['학번', '이름', '과목', '점수', '평가일']
                eval_missing_columns = [col for col in eval_required_columns if col not in evaluations_df.columns]
                
                if eval_missing_columns:
                    messagebox.showerror("오류", f"평가정보 시트에 다음 컬럼이 없습니다: {', '.join(eval_missing_columns)}")
                    return
            
            # 데이터베이스에 추가
            success_count = 0
            error_count = 0
            
            # 학생 정보 추가
            for _, row in students_df.iterrows():
                try:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.cursor.execute('''
                        INSERT INTO students (student_number, name, created_at, last_modified)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        str(row['학번']),
                        str(row['이름']),
                        current_time,
                        current_time
                    ))
                    success_count += 1
                except sqlite3.IntegrityError:
                    error_count += 1
                    continue
            
            # 평가 정보 추가 (있는 경우)
            if not evaluations_df.empty:
                for _, row in evaluations_df.iterrows():
                    try:
                        # 학생 ID 조회
                        self.cursor.execute('SELECT id FROM students WHERE student_number = ?', (str(row['학번']),))
                        result = self.cursor.fetchone()
                        if not result:
                            messagebox.showerror("오류", "선택한 학생을 찾을 수 없습니다.")
                            continue
                        student_id = result[0]
                        
                        # 평가일 형식 검증
                        eval_date = str(row['평가일'])
                        if not self.validate_date(eval_date):
                            continue
                        
                        self.cursor.execute('''
                            INSERT INTO evaluations (student_id, subject, score, evaluation_date, notes)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            student_id,
                            str(row['과목']),
                            float(row['점수']),
                            eval_date,
                            str(row['비고']) if '비고' in row and not pd.isna(row['비고']) else None
                        ))
                        
                        # 학생의 최종수정일 업데이트
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.cursor.execute('''
                            UPDATE students
                            SET last_modified = ?
                            WHERE id = ?
                        ''', (current_time, student_id))
                        
                    except (ValueError, sqlite3.Error):
                        continue
            
            self.conn.commit()
            
            # 결과 메시지
            message = f"처리 완료\n성공: {success_count}명\n실패: {error_count}명"
            if error_count > 0:
                message += "\n\n실패한 항목은 이미 존재하는 학번이거나 잘못된 데이터입니다."
            messagebox.showinfo("일괄 등록 결과", message)
            
            # 목록 새로고침
            self.load_students()
            
        except Exception as e:
            messagebox.showerror("오류", f"파일 처리 중 오류가 발생했습니다:\n{str(e)}")
        
    def validate_date(self, date_str):
        """날짜 형식이 YYYY-MM-DD인지 검증합니다."""
        if not date_str:
            return False
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def setup_gui(self):
        """GUI 구성 요소를 설정합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # 학생 정보 입력 프레임
        input_frame = ttk.LabelFrame(main_frame, text="학생 정보 입력", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        
        # 입력 필드
        ttk.Label(input_frame, text="학번:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.student_number_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.student_number_var, width=15).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="이름:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var, width=15).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 버튼 프레임
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        
        ttk.Button(button_frame, text="추가", command=self.add_student, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="수정", command=self.update_student, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="삭제", command=self.delete_student, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="엑셀 가져오기", command=self.import_excel, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="엑셀 내보내기", command=self.export_excel, width=12).pack(side=tk.LEFT, padx=2)
        
        # 학생 목록 트리뷰
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, columns=("학번", "이름", "등록일", "최종수정일"), show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 컬럼 설정
        self.tree.heading("학번", text="학번")
        self.tree.heading("이름", text="이름")
        self.tree.heading("등록일", text="등록일")
        self.tree.heading("최종수정일", text="최근평가일")
        
        self.tree.column("학번", width=120, minwidth=100)
        self.tree.column("이름", width=120, minwidth=100)
        self.tree.column("등록일", width=150, minwidth=120)
        self.tree.column("최종수정일", width=150, minwidth=120)
        
        # 평가 정보 프레임
        eval_frame = ttk.LabelFrame(main_frame, text="평가 정보", padding="10")
        eval_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        eval_frame.grid_columnconfigure(1, weight=1)
        eval_frame.grid_columnconfigure(3, weight=1)
        eval_frame.grid_columnconfigure(5, weight=1)
        eval_frame.grid_columnconfigure(7, weight=2)
        
        # 평가 입력 필드
        ttk.Label(eval_frame, text="과목:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.subject_var = tk.StringVar()
        ttk.Entry(eval_frame, textvariable=self.subject_var, width=15).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(eval_frame, text="점수:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.score_var = tk.StringVar()
        ttk.Entry(eval_frame, textvariable=self.score_var, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(eval_frame, text="평가일:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.eval_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(eval_frame, textvariable=self.eval_date_var, width=15).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(eval_frame, text="비고:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.E)
        self.notes_var = tk.StringVar()
        ttk.Entry(eval_frame, textvariable=self.notes_var, width=30).grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        
        # 평가 버튼
        eval_button_frame = ttk.Frame(eval_frame)
        eval_button_frame.grid(row=0, column=8, padx=5, pady=5, sticky=tk.E)
        
        ttk.Button(eval_button_frame, text="평가 추가", command=self.add_evaluation, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(eval_button_frame, text="평가 삭제", command=self.delete_evaluation, width=10).pack(side=tk.LEFT, padx=2)
        
        # 평가 목록 트리뷰
        eval_tree_frame = ttk.Frame(main_frame)
        eval_tree_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        eval_tree_frame.grid_columnconfigure(0, weight=1)
        eval_tree_frame.grid_rowconfigure(0, weight=1)
        
        self.eval_tree = ttk.Treeview(eval_tree_frame, columns=("과목", "점수", "평가일", "비고"), show="headings", height=8)
        self.eval_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 평가 스크롤바
        eval_scrollbar = ttk.Scrollbar(eval_tree_frame, orient=tk.VERTICAL, command=self.eval_tree.yview)
        eval_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.eval_tree.configure(yscrollcommand=eval_scrollbar.set)
        
        # 평가 컬럼 설정
        self.eval_tree.heading("과목", text="과목")
        self.eval_tree.heading("점수", text="점수")
        self.eval_tree.heading("평가일", text="평가일")
        self.eval_tree.heading("비고", text="비고")
        
        self.eval_tree.column("과목", width=120, minwidth=100)
        self.eval_tree.column("점수", width=60, minwidth=50)
        self.eval_tree.column("평가일", width=120, minwidth=100)
        self.eval_tree.column("비고", width=300, minwidth=200)
        
        # 이벤트 바인딩
        self.tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # 초기 데이터 로드
        self.load_students()
        
    def load_students(self):
        """학생 목록을 로드합니다."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute('''
            SELECT student_number, name, created_at, last_modified
            FROM students
            ORDER BY student_number
        ''')
        
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)
            
    def load_evaluations(self, student_id):
        """선택된 학생의 평가 목록을 로드합니다."""
        for item in self.eval_tree.get_children():
            self.eval_tree.delete(item)
            
        self.cursor.execute('''
            SELECT subject, score, evaluation_date, notes
            FROM evaluations
            WHERE student_id = ?
            ORDER BY evaluation_date DESC
        ''', (student_id,))
        
        for row in self.cursor.fetchall():
            self.eval_tree.insert('', 'end', values=row)
            
    def add_student(self):
        """새로운 학생을 추가합니다."""
        try:
            student_number = self.student_number_var.get().strip()
            name = self.name_var.get().strip()
            
            if not all([student_number, name]):
                messagebox.showerror("오류", "모든 필드를 입력해주세요.")
                return
                
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
                INSERT INTO students (student_number, name, created_at, last_modified)
                VALUES (?, ?, ?, ?)
            ''', (student_number, name, current_time, current_time))
            
            self.conn.commit()
            self.load_students()
            self.clear_inputs()
            messagebox.showinfo("성공", "학생이 추가되었습니다.")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("오류", "이미 존재하는 학번입니다.")
        except Exception as e:
            messagebox.showerror("오류", f"학생 추가 중 오류가 발생했습니다: {str(e)}")
            
    def update_student(self):
        """선택된 학생의 정보를 수정합니다."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "수정할 학생을 선택해주세요.")
            return
            
        try:
            student_number = self.student_number_var.get().strip()
            name = self.name_var.get().strip()
            
            if not all([student_number, name]):
                messagebox.showerror("오류", "모든 필드를 입력해주세요.")
                return
                
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
                UPDATE students
                SET student_number = ?, name = ?, last_modified = ?
                WHERE student_number = ?
            ''', (student_number, name, current_time, self.tree.item(selected[0])['values'][0]))
            
            self.conn.commit()
            self.load_students()
            self.clear_inputs()
            messagebox.showinfo("성공", "학생 정보가 수정되었습니다.")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("오류", "이미 존재하는 학번입니다.")
        except Exception as e:
            messagebox.showerror("오류", f"학생 정보 수정 중 오류가 발생했습니다: {str(e)}")
            
    def delete_student(self):
        """선택된 학생을 삭제합니다."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 학생을 선택해주세요.")
            return
            
        if messagebox.askyesno("확인", "선택한 학생을 삭제하시겠습니까?"):
            try:
                student_number = self.tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM students WHERE student_number = ?', (student_number,))
                self.conn.commit()
                self.load_students()
                self.clear_inputs()
                messagebox.showinfo("성공", "학생이 삭제되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"학생 삭제 중 오류가 발생했습니다: {str(e)}")
                
    def add_evaluation(self):
        """새로운 평가를 추가합니다."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "평가를 추가할 학생을 선택해주세요.")
            return
            
        try:
            student_number = self.tree.item(selected[0])['values'][0]
            subject = self.subject_var.get().strip()
            score_str = self.score_var.get().strip()
            eval_date = self.eval_date_var.get().strip()
            notes = self.notes_var.get().strip()
            
            if not subject or score_str == "" or not eval_date:
                messagebox.showerror("오류", "과목, 점수, 평가일을 입력해주세요.")
                return
            
            score = float(score_str)
            
            if not self.validate_date(eval_date):
                messagebox.showerror("오류", "평가일은 YYYY-MM-DD 형식으로 입력해주세요.")
                return
                
            # 학생 ID 조회
            self.cursor.execute('SELECT id FROM students WHERE student_number = ?', (student_number,))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("오류", "선택한 학생을 찾을 수 없습니다.")
                return
            student_id = result[0]
            
            self.cursor.execute('''
                INSERT INTO evaluations (student_id, subject, score, evaluation_date, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, subject, score, eval_date, notes))
            
            # 학생의 최종수정일 업데이트
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
                UPDATE students
                SET last_modified = ?
                WHERE id = ?
            ''', (current_time, student_id))
            
            self.conn.commit()
            self.load_evaluations(student_id)
            self.load_students()  # 학생 목록 새로고침
            self.clear_eval_inputs()
            messagebox.showinfo("성공", "평가가 추가되었습니다.")
            
        except ValueError:
            messagebox.showerror("오류", "점수는 숫자로 입력해주세요.")
        except Exception as e:
            messagebox.showerror("오류", f"평가 추가 중 오류가 발생했습니다: {str(e)}")
            
    def delete_evaluation(self):
        """선택된 평가를 삭제합니다."""
        selected = self.eval_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 평가를 선택해주세요.")
            return
            
        if messagebox.askyesno("확인", "선택한 평가를 삭제하시겠습니까?"):
            try:
                student_selected = self.tree.selection()
                if not student_selected:
                    return
                    
                student_number = self.tree.item(student_selected[0])['values'][0]
                self.cursor.execute('SELECT id FROM students WHERE student_number = ?', (student_number,))
                student_id = self.cursor.fetchone()[0]
                
                eval_values = self.eval_tree.item(selected[0])['values']
                self.cursor.execute('''
                    DELETE FROM evaluations
                    WHERE student_id = ? AND subject = ? AND score = ? AND evaluation_date = ?
                ''', (student_id, eval_values[0], eval_values[1], eval_values[2]))
                
                # 학생의 최종수정일 업데이트
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute('''
                    UPDATE students
                    SET last_modified = ?
                    WHERE id = ?
                ''', (current_time, student_id))
                
                self.conn.commit()
                self.load_evaluations(student_id)
                self.load_students()  # 학생 목록 새로고침
                messagebox.showinfo("성공", "평가가 삭제되었습니다.")
                
            except Exception as e:
                messagebox.showerror("오류", f"평가 삭제 중 오류가 발생했습니다: {str(e)}")
                
    def on_student_select(self, event):
        """학생 선택 시 평가 목록을 로드합니다."""
        selected = self.tree.selection()
        if not selected:
            return
            
        student_number = self.tree.item(selected[0])['values'][0]
        self.cursor.execute('SELECT id FROM students WHERE student_number = ?', (student_number,))
        student_id = self.cursor.fetchone()[0]
        self.load_evaluations(student_id)
        
    def clear_inputs(self):
        """학생 정보 입력 필드를 초기화합니다."""
        self.student_number_var.set("")
        self.name_var.set("")
        
    def clear_eval_inputs(self):
        """평가 정보 입력 필드를 초기화합니다."""
        self.subject_var.set("")
        self.score_var.set("")
        self.eval_date_var.set(datetime.now().strftime('%Y-%m-%d'))  # 오늘 날짜로 초기화
        self.notes_var.set("")
        
    def export_excel(self):
        """학생 정보와 평가 정보를 엑셀 파일로 내보냅니다."""
        try:
            # 기본 파일명 생성 (프로그램명_날짜)
            default_filename = f"student_database_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            # 파일 저장 대화상자
            file_path = filedialog.asksaveasfilename(
                title="엑셀 파일 저장",
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if not file_path:
                return
            
            # 학생 정보 조회
            self.cursor.execute('''
                SELECT student_number, name, created_at, last_modified
                FROM students
                ORDER BY student_number
            ''')
            students_data = self.cursor.fetchall()
            
            # 평가 정보 조회
            self.cursor.execute('''
                SELECT s.student_number, s.name, e.subject, e.score, e.evaluation_date, e.notes
                FROM students s
                LEFT JOIN evaluations e ON s.id = e.student_id
                ORDER BY s.student_number, e.evaluation_date DESC
            ''')
            evaluations_data = self.cursor.fetchall()
            
            # DataFrame 생성
            students_df = pd.DataFrame(students_data, columns=['학번', '이름', '등록일', '최근평가일'])
            evaluations_df = pd.DataFrame(evaluations_data, columns=['학번', '이름', '과목', '점수', '평가일', '비고'])
            
            # ExcelWriter 객체 생성
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 학생 정보 시트
                students_df.to_excel(writer, sheet_name='학생정보', index=False)
                
                # 평가 정보 시트
                evaluations_df.to_excel(writer, sheet_name='평가정보', index=False)
                
                # 열 너비 자동 조정
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for idx, col in enumerate(worksheet.columns):
                        max_length = max(
                            len(str(cell.value)) for cell in col
                        )
                        worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            messagebox.showinfo("성공", "엑셀 파일이 저장되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"엑셀 파일 저장 중 오류가 발생했습니다:\n{str(e)}")
        
    def run(self):
        """애플리케이션을 실행합니다."""
        self.root.mainloop()
        
if __name__ == "__main__":
    app = StudentDatabase()
    app.run() 