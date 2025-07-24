import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, QMessageBox
)

from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QFileDialog
import csv

class StudentDatabase(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학생 관리 시스템 (PyQt5)")
        self.resize(1100, 650)
        self.conn = sqlite3.connect('student.db')
        self.cursor = self.conn.cursor()
        self.init_database()
        self.init_ui()
        self.load_students()

    def init_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT UNIQUE,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
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

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 메뉴바 추가
        self.menubar = QMenuBar(self)
        file_menu = QMenu("파일", self)
        export_csv_action = QAction("CSV 내보내기", self)
        import_csv_action = QAction("CSV 불러오기", self)
        export_csv_action.triggered.connect(self.export_csv)
        import_csv_action.triggered.connect(self.import_csv)
        file_menu.addAction(export_csv_action)
        file_menu.addAction(import_csv_action)
        self.menubar.addMenu(file_menu)
        main_layout.setMenuBar(self.menubar)

        # 학생 정보 입력
        input_group = QGroupBox("학생 정보 입력")
        input_layout = QHBoxLayout()
        self.num_edit = QLineEdit()
        self.name_edit = QLineEdit()
        input_layout.addWidget(QLabel("학번:"))
        input_layout.addWidget(self.num_edit)
        input_layout.addWidget(QLabel("이름:"))
        input_layout.addWidget(self.name_edit)
        self.add_btn = QPushButton("추가")
        self.update_btn = QPushButton("수정")
        self.delete_btn = QPushButton("삭제")
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.update_btn)
        input_layout.addWidget(self.delete_btn)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # 학생 목록 테이블
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["학번", "이름", "등록일", "최근평가일"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # 평가 정보 입력
        eval_group = QGroupBox("평가 정보")
        eval_layout = QHBoxLayout()
        self.subject_edit = QLineEdit()
        self.score_edit = QLineEdit()
        self.eval_date_edit = QLineEdit(datetime.now().strftime('%Y-%m-%d'))
        self.notes_edit = QLineEdit()
        eval_layout.addWidget(QLabel("과목:"))
        eval_layout.addWidget(self.subject_edit)
        eval_layout.addWidget(QLabel("점수:"))
        eval_layout.addWidget(self.score_edit)
        eval_layout.addWidget(QLabel("평가일:"))
        eval_layout.addWidget(self.eval_date_edit)
        eval_layout.addWidget(QLabel("비고:"))
        eval_layout.addWidget(self.notes_edit)
        self.eval_add_btn = QPushButton("평가 추가")
        self.eval_delete_btn = QPushButton("평가 삭제")
        eval_layout.addWidget(self.eval_add_btn)
        eval_layout.addWidget(self.eval_delete_btn)
        eval_group.setLayout(eval_layout)
        main_layout.addWidget(eval_group)

        # 평가 목록 테이블
        self.eval_table = QTableWidget(0, 4)
        self.eval_table.setHorizontalHeaderLabels(["과목", "점수", "평가일", "비고"])
        self.eval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.eval_table)

        self.setLayout(main_layout)

        # 이벤트 연결
        self.add_btn.clicked.connect(self.add_student)
        self.update_btn.clicked.connect(self.update_student)
        self.delete_btn.clicked.connect(self.delete_student)
        self.table.cellClicked.connect(self.on_student_select)
        self.eval_add_btn.clicked.connect(self.add_evaluation)
        self.eval_delete_btn.clicked.connect(self.delete_evaluation)

    def export_csv(self):
        # 학생 및 평가 정보를 각각 CSV로 내보내기
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "학생정보 CSV 내보내기", "students.csv", "CSV Files (*.csv)", options=options)
        if file_path:
            try:
                # 학생 정보 내보내기
                self.cursor.execute('SELECT student_number, name, created_at, last_modified FROM students ORDER BY student_number')
                students = self.cursor.fetchall()
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["학번", "이름", "등록일", "최근평가일"])
                    writer.writerows(students)
                # 평가 정보도 같은 경로에 _evaluations.csv로 저장
                eval_path = file_path.replace('.csv', '_evaluations.csv')
                self.cursor.execute('''SELECT s.student_number, s.name, e.subject, e.score, e.evaluation_date, e.notes FROM students s LEFT JOIN evaluations e ON s.id = e.student_id ORDER BY s.student_number, e.evaluation_date DESC''')
                evals = self.cursor.fetchall()
                with open(eval_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["학번", "이름", "과목", "점수", "평가일", "비고"])
                    writer.writerows(evals)
                QMessageBox.information(self, "성공", f"학생정보와 평가정보가 CSV로 저장되었습니다.\n\n학생정보: {file_path}\n평가정보: {eval_path}")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"CSV 내보내기 중 오류 발생: {str(e)}")

    def import_csv(self):
        # 학생 및 평가 정보를 CSV에서 불러오기
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "학생정보 CSV 불러오기", "", "CSV Files (*.csv)", options=options)
        if file_path:
            try:
                # 학생 정보 불러오기
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    students = list(reader)
                # 평가 정보는 같은 경로의 _evaluations.csv에서 불러옴
                eval_path = file_path.replace('.csv', '_evaluations.csv')
                evals = []
                try:
                    with open(eval_path, 'r', encoding='utf-8-sig') as f:
                        eval_reader = csv.DictReader(f)
                        evals = list(eval_reader)
                except FileNotFoundError:
                    pass
                # 기존 데이터 삭제
                self.cursor.execute('DELETE FROM evaluations')
                self.cursor.execute('DELETE FROM students')
                # 학생 정보 삽입
                for stu in students:
                    self.cursor.execute('INSERT INTO students (student_number, name, created_at, last_modified) VALUES (?, ?, ?, ?)',
                        (stu["학번"], stu["이름"], stu["등록일"], stu["최근평가일"]))
                # 평가 정보 삽입
                for ev in evals:
                    # 학생 ID 찾기
                    self.cursor.execute('SELECT id FROM students WHERE student_number=?', (ev["학번"],))
                    res = self.cursor.fetchone()
                    if res:
                        student_id = res[0]
                        self.cursor.execute('INSERT INTO evaluations (student_id, subject, score, evaluation_date, notes) VALUES (?, ?, ?, ?, ?)',
                            (student_id, ev["과목"], ev["점수"] if ev["점수"] else None, ev["평가일"], ev["비고"]))
                self.conn.commit()
                self.load_students()
                self.eval_table.setRowCount(0)
                QMessageBox.information(self, "성공", "CSV에서 학생정보와 평가정보를 불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"CSV 불러오기 중 오류 발생: {str(e)}")

    def load_students(self):
        self.table.setRowCount(0)
        self.cursor.execute('SELECT student_number, name, created_at, last_modified FROM students ORDER BY student_number')
        for row in self.cursor.fetchall():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            for col, val in enumerate(row):
                self.table.setItem(row_pos, col, QTableWidgetItem(str(val)))

    def on_student_select(self, row, col):
        self.selected_student_number = self.table.item(row, 0).text()
        self.num_edit.setText(self.selected_student_number)
        self.name_edit.setText(self.table.item(row, 1).text())
        self.load_evaluations()

    def add_student(self):
        num = self.num_edit.text().strip()
        name = self.name_edit.text().strip()
        if not num or not name:
            QMessageBox.warning(self, "오류", "모든 필드를 입력해주세요.")
            return
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('INSERT INTO students (student_number, name, created_at, last_modified) VALUES (?, ?, ?, ?)', (num, name, now, now))
            self.conn.commit()
            self.load_students()
            self.num_edit.clear()
            self.name_edit.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "오류", "이미 존재하는 학번입니다.")

    def update_student(self):
        if not hasattr(self, 'selected_student_number'):
            QMessageBox.warning(self, "경고", "수정할 학생을 선택해주세요.")
            return
        num = self.num_edit.text().strip()
        name = self.name_edit.text().strip()
        if not num or not name:
            QMessageBox.warning(self, "오류", "모든 필드를 입력해주세요.")
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.cursor.execute('UPDATE students SET student_number=?, name=?, last_modified=? WHERE student_number=?', (num, name, now, self.selected_student_number))
            self.conn.commit()
            self.load_students()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "오류", "이미 존재하는 학번입니다.")

    def delete_student(self):
        if not hasattr(self, 'selected_student_number'):
            QMessageBox.warning(self, "경고", "삭제할 학생을 선택해주세요.")
            return
        self.cursor.execute('DELETE FROM students WHERE student_number=?', (self.selected_student_number,))
        self.conn.commit()
        self.load_students()
        self.eval_table.setRowCount(0)
        self.num_edit.clear()
        self.name_edit.clear()

    def load_evaluations(self):
        self.eval_table.setRowCount(0)
        self.cursor.execute('SELECT id FROM students WHERE student_number=?', (self.selected_student_number,))
        result = self.cursor.fetchone()
        if not result:
            return
        student_id = result[0]
        self.cursor.execute('SELECT subject, score, evaluation_date, notes FROM evaluations WHERE student_id=? ORDER BY evaluation_date DESC', (student_id,))
        for row in self.cursor.fetchall():
            row_pos = self.eval_table.rowCount()
            self.eval_table.insertRow(row_pos)
            for col, val in enumerate(row):
                self.eval_table.setItem(row_pos, col, QTableWidgetItem(str(val)))

    def add_evaluation(self):
        if not hasattr(self, 'selected_student_number'):
            QMessageBox.warning(self, "경고", "평가를 추가할 학생을 선택해주세요.")
            return
        subject = self.subject_edit.text().strip()
        score = self.score_edit.text().strip()
        eval_date = self.eval_date_edit.text().strip()
        notes = self.notes_edit.text().strip()
        if not subject or not score or not eval_date:
            QMessageBox.warning(self, "오류", "과목, 점수, 평가일을 입력해주세요.")
            return
        try:
            score_val = float(score)
        except ValueError:
            QMessageBox.warning(self, "오류", "점수는 숫자로 입력해주세요.")
            return
        self.cursor.execute('SELECT id FROM students WHERE student_number=?', (self.selected_student_number,))
        result = self.cursor.fetchone()
        if not result:
            return
        student_id = result[0]
        self.cursor.execute('INSERT INTO evaluations (student_id, subject, score, evaluation_date, notes) VALUES (?, ?, ?, ?, ?)', (student_id, subject, score_val, eval_date, notes))
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('UPDATE students SET last_modified=? WHERE id=?', (now, student_id))
        self.conn.commit()
        self.load_evaluations()
        self.load_students()
        self.subject_edit.clear()
        self.score_edit.clear()
        self.eval_date_edit.setText(datetime.now().strftime('%Y-%m-%d'))
        self.notes_edit.clear()

    def delete_evaluation(self):
        selected = self.eval_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "경고", "삭제할 평가를 선택해주세요.")
            return
        subject = self.eval_table.item(selected, 0).text()
        score = self.eval_table.item(selected, 1).text()
        eval_date = self.eval_table.item(selected, 2).text()
        self.cursor.execute('SELECT id FROM students WHERE student_number=?', (self.selected_student_number,))
        student_id = self.cursor.fetchone()[0]
        self.cursor.execute('DELETE FROM evaluations WHERE student_id=? AND subject=? AND score=? AND evaluation_date=?', (student_id, subject, score, eval_date))
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('UPDATE students SET last_modified=? WHERE id=?', (now, student_id))
        self.conn.commit()
        self.load_evaluations()
        self.load_students()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StudentDatabase()
    win.show()
    sys.exit(app.exec_())