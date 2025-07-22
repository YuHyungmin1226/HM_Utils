import random
from music21 import stream, chord, key, metadata, note, meter, roman, scale, expressions, spanner, tie
import os
from datetime import datetime
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import gc
from typing import Optional, Dict, Any

# 코드 네임을 실제 화음으로 변환
def roman_to_chord(roman, tonic, mode='major'):
    k = key.Key(tonic, mode)
    rn_obj = k.romanNumeral(roman)
    if roman.upper() == 'V':
        rn_obj.figure += '7'
    base_pitches = list(rn_obj.pitches)
    # 전위(1전위, 2전위) 랜덤 적용
    inversion = random.choice([0, 1, 2]) if len(base_pitches) > 2 else 0
    pitches = base_pitches[inversion:] + base_pitches[:inversion]
    # 옥타브 분산 (C3~C5)
    chord_notes = []
    base_octave = 3
    for i, p in enumerate(pitches):
        np = p.transpose(12 * (base_octave + i // len(pitches) - p.octave))
        # 옥타브 범위 제한
        while np.octave < 3:
            np = np.transpose(12)
        while np.octave > 5:
            np = np.transpose(-12)
        chord_notes.append(np)
    rn = chord.Chord(chord_notes)
    return rn

def generate_progression(tonic='C', mode='major', length=8):
    # 대한민국 교과서 스타일: I, IV, V, vi만 사용, 반복적이고 예측 가능한 패턴
    if mode == 'major':
        basic_patterns = [
            ['I', 'IV', 'V', 'I'],
            ['I', 'vi', 'IV', 'V'],
            ['I', 'IV', 'I', 'V'],
            ['I', 'IV', 'V', 'I'],
        ]
        cadences = [
            ['IV', 'ii', 'V7', 'I'],
            ['vi', 'ii', 'V7', 'I'],
            ['ii', 'V7', 'I'],
            ['IV', 'V', 'I'],
            ['IV', 'I'],
            ['V', 'vi'],  # Deceptive
        ]
    else:
        basic_patterns = [
            ['i', 'iv', 'V', 'i'],
            ['i', 'VI', 'iv', 'V'],
            ['i', 'iv', 'i', 'V'],
            ['i', 'iv', 'V', 'i'],
        ]
        cadences = [
            ['iv', 'ii°', 'V7', 'i'],
            ['VI', 'ii°', 'V7', 'i'],
            ['ii°', 'V7', 'i'],
            ['iv', 'V', 'i'],
            ['iv', 'i'],
            ['V', 'VI'],  # Deceptive
        ]
    # 4마디 단위 반복
    base = random.choice(basic_patterns)
    progression = (base * ((length // 4) + 1))[:length]
    # 종지 처리: 마지막 3~4마디를 종지 패턴으로 대체
    if length >= 3:
        cadence = random.choice(cadences)
        c_len = min(len(cadence), length)
        progression[-c_len:] = cadence[-c_len:]
    return progression

def get_documents_dir():
    """사용자의 문서 폴더 경로를 가져옵니다."""
    try:
        if sys.platform == "win32":
            # Windows
            return os.path.join(os.environ['USERPROFILE'], 'Documents')
        elif sys.platform == "darwin":
            # macOS
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:
            # Linux 및 기타
            return os.path.join(os.path.expanduser("~"), "Documents")
    except Exception as e:
        print(f"[ERROR] 문서 폴더 경로 가져오기 실패: {e}")
        # 기본 경로 반환
        return os.path.join(os.path.expanduser("~"), "Documents")

def get_unique_filename(base_name, ext, save_dir):
    today = datetime.now().strftime("%Y%m%d")
    n = 1
    # Score 폴더 생성
    score_dir = os.path.join(save_dir, "Score")
    os.makedirs(score_dir, exist_ok=True)
    while True:
        filename = f"{base_name}_{today}_{n}.{ext}"
        full_path = os.path.join(score_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        n += 1

def progression_to_part(prog, tonic, mode='major', time_sig='4/4', analysis=None):
    p = stream.Part()
    p.append(key.Key(tonic, mode))
    p.append(meter.TimeSignature(time_sig))
    from music21 import clef
    p.append(clef.BassClef())  # 낮은음자리표 추가
    for i, rn in enumerate(prog):
        m = stream.Measure(number=i+1)  # 마디 번호 명시적으로 지정
        c = roman_to_chord(rn, tonic, mode)
        c.quarterLength = 4 if time_sig == '4/4' else 3 if time_sig == '3/4' else 3
        m.append(c)
        if i == len(prog) - 1:
            m.rightBarline = 'final'
        p.append(m)
    p.id = 'Chords'
    return p

def get_rhythm_pattern(style='basic'):
    """리듬 패턴 템플릿 반환"""
    patterns = {
        'basic': [
            [4.0],  # 온음표
            [2.0, 2.0],  # 2분음표 2개
            [1.0, 1.0, 1.0, 1.0],  # 4분음표 4개
        ],
        'syncopated': [
            [1.5, 0.5, 1.5, 0.5],  # 당김음
            [0.75, 0.25, 0.75, 0.25, 1.0, 1.0],  # 당김음 변형
            [1.0, 0.5, 0.5, 1.0, 1.0],  # 셋잇단음표 느낌
        ],
        'swing': [
            [0.66, 0.34, 0.66, 0.34, 1.0, 1.0],  # 스윙
            [1.66, 0.34, 1.0, 1.0],  # 스윙 변형
        ],
        'complex': [
            [0.25, 0.25, 0.5, 0.5, 0.5, 1.0, 1.0],  # 16분음표 혼합
            [0.5, 0.25, 0.25, 1.0, 1.0, 1.0],  # 부점 리듬
            [1.0, 0.5, 0.25, 0.25, 1.0, 1.0],  # 혼합 리듬
        ]
    }
    return patterns[style]

def apply_rhythm_pattern(notes, pattern):
    """음표들에 리듬 패턴 적용"""
    if not notes:
        return []
    
    total_duration = sum(pattern)
    if total_duration != 4.0:  # 4/4 박자 기준
        # 패턴 길이 조정
        scale_factor = 4.0 / total_duration
        pattern = [d * scale_factor for d in pattern]
    
    result = []
    pattern_idx = 0
    note_idx = 0
    
    while note_idx < len(notes):
        if pattern_idx >= len(pattern):
            pattern_idx = 0
        
        notes[note_idx].quarterLength = pattern[pattern_idx]
        result.append(notes[note_idx])
        
        note_idx += 1
        pattern_idx += 1
    
    return result

def generate_melody_part(prog, tonic, mode='major', time_sig='4/4', rhythm_option='random', use_slurs=True, use_ties=True):
    from music21 import stream, note, meter, key as m21key, scale, pitch
    melody = stream.Part()
    melody.append(meter.TimeSignature(time_sig))
    k = m21key.Key(tonic, mode)
    melody.append(k)
    s = scale.MajorScale(tonic) if mode == 'major' else scale.MinorScale(tonic)
    scale_degrees = s.getPitches()
    tonic_pitch = pitch.Pitch(tonic)
    prev_note = None
    all_notes = []  # 모든 음 저장(이음줄/붙임줄용)
    if time_sig == '4/4':
        measure_length = 4.0
        rhythm_patterns = {
            'random': [
                [4.0],
                [2.0, 2.0],
                [1.0, 1.0, 1.0, 1.0],
                [2.0, 1.0, 1.0],
                [1.0, 2.0, 1.0],
                [0.5]*8,
                [1.0, 0.5, 0.5, 2.0],
                [0.5, 0.5, 1.0, 2.0],
                [2.0, 0.5, 0.5, 1.0],
                [1.0, 1.0, 0.5, 0.5, 1.0],
            ],
            'whole': [[4.0]],
            'half': [[2.0, 2.0]],
            'quarter': [[1.0, 1.0, 1.0, 1.0]],
            'eighth': [[0.5]*8]
        }
    elif time_sig == '3/4':
        measure_length = 3.0
        rhythm_patterns = {
            'random': [
                [3.0],
                [1.5, 1.5],
                [1.0, 2.0],
                [2.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.5, 0.5, 2.0],
                [2.0, 0.5, 0.5],
                [0.5, 1.0, 1.5],
                [0.5, 0.5, 1.0, 1.0],
                [0.5]*6
            ],
            'whole': [[3.0]],
            'half': [[1.5, 1.5]],
            'quarter': [[1.0, 1.0, 1.0]],
            'eighth': [[0.5]*6]
        }
    elif time_sig == '6/8':
        measure_length = 3.0
        rhythm_patterns = {
            'random': [
                [3.0],
                [1.5, 1.5],
                [1.0, 2.0],
                [2.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.5, 0.5, 2.0],
                [2.0, 0.5, 0.5],
                [0.5, 1.0, 1.5],
                [0.5, 0.5, 1.0, 1.0],
                [0.5]*6
            ],
            'whole': [[3.0]],
            'half': [[1.5, 1.5]],
            'quarter': [[1.0, 1.0, 1.0]],
            'eighth': [[0.5]*6]
        }
    else:
        measure_length = 4.0
        rhythm_patterns = {'random': [[4.0]], 'whole': [[4.0]], 'half': [[2.0, 2.0]], 'quarter': [[1.0, 1.0, 1.0, 1.0]], 'eighth': [[0.5]*8]}
    for i, rn in enumerate(prog):
        c = roman_to_chord(rn, tonic, mode)
        m = stream.Measure(number=i+1)  # 마디 번호 명시적으로 지정
        pattern = random.choice(rhythm_patterns[rhythm_option]) if rhythm_option in rhythm_patterns else random.choice(rhythm_patterns['random'])
        notes = []
        for j, dur in enumerate(pattern):
            is_cadence_zone = (i >= len(prog) - 3)
            if j == 0:
                if is_cadence_zone:
                    n = note.Note(tonic_pitch)
                else:
                    choices = [c.root(), c.third, c.fifth, tonic_pitch]
                    n = note.Note(random.choice(choices))
            elif i == len(prog) - 1 and j == len(pattern) - 1:
                n = note.Note(tonic_pitch)
            elif is_cadence_zone:
                choices = [c.third, c.fifth, tonic_pitch]
                n = note.Note(random.choice(choices))
            else:
                if prev_note:
                    candidates = [p for p in scale_degrees if abs(p.midi - prev_note.pitch.midi) <= 2]
                    n = note.Note(random.choice(candidates)) if candidates else note.Note(random.choice(scale_degrees))
                else:
                    n = note.Note(random.choice(scale_degrees))
            n.quarterLength = dur
            if n.pitch.octave is None:
                n.pitch.octave = 4
            while n.pitch.octave < 4:
                n.pitch.octave += 1
            while n.pitch.octave > 6:
                n.pitch.octave -= 1
            notes.append(n)
            prev_note = n
        for n in notes:
            m.append(n)
            all_notes.append(n)
        total_len = sum([n.quarterLength for n in m.notes])
        if abs(total_len - measure_length) > 0.01:
            print(f"⚠️ 경고: {i+1}번째 마디의 음표 길이 합({total_len})이 박자({measure_length})와 일치하지 않습니다.")
        if i == len(prog) - 1:
            m.rightBarline = 'final'
        melody.append(m)
    # 프레이즈 단위(4마디) 이음줄 추가
    if use_slurs:
        for i in range(0, len(all_notes), 4):
            if i+3 < len(all_notes):
                slur = spanner.Slur()
                for n in all_notes[i:i+4]:
                    slur.addSpannedElements(n)
                melody.insert(0, slur)

    # 붙임줄(마디 넘어가는 같은 음)
    if use_ties:
        for i in range(len(all_notes)-1):
            n1 = all_notes[i]
            n2 = all_notes[i+1]
            if n1.nameWithOctave == n2.nameWithOctave:
                if n1.tie is None:
                    n1.tie = tie.Tie('start')
                else:
                    n1.tie = tie.Tie('continue')
                n2.tie = tie.Tie('stop')
    melody.id = 'Melody'
    return melody

def analyze_harmony(prog, tonic, mode='major'):
    """화성학적 분석 수행"""
    from music21 import key, roman, scale
    
    k = key.Key(tonic, mode)
    s = scale.MajorScale(tonic) if mode == 'major' else scale.MinorScale(tonic)
    
    analysis = {
        'key': f"{tonic} {mode}",
        'cadences': [],
        'harmonic_progressions': [],
        'scale_usage': {},
        'tensions': [],
        'voice_leading': [],
        'cadence_measures': [],
        'circle_measures': []
    }
    
    # 종지 분석 및 마디 위치 기록
    if len(prog) >= 2:
        last_two = prog[-2:]
        if mode == 'major':
            if last_two == ['V', 'I']:
                analysis['cadences'].append('Authentic Cadence')
                analysis['cadence_measures'].append({'measure': len(prog)-2, 'text': 'Authentic Cadence (V-I) 종지'})
            elif last_two == ['IV', 'I']:
                analysis['cadences'].append('Plagal Cadence')
                analysis['cadence_measures'].append({'measure': len(prog)-2, 'text': 'Plagal Cadence (IV-I) 종지'})
        else:
            if last_two == ['V', 'i']:
                analysis['cadences'].append('Authentic Cadence')
                analysis['cadence_measures'].append({'measure': len(prog)-2, 'text': 'Authentic Cadence (V-i) 종지'})
            elif last_two == ['iv', 'i']:
                analysis['cadences'].append('Plagal Cadence')
                analysis['cadence_measures'].append({'measure': len(prog)-2, 'text': 'Plagal Cadence (iv-i) 종지'})
    
    # 화성 진행 분석 및 5도권 마디 위치 기록
    for i in range(len(prog) - 1):
        current = prog[i]
        next_chord = prog[i + 1]
        if mode == 'major':
            circle_prog = ['I', 'IV', 'vii°', 'iii', 'vi', 'ii', 'V', 'I']
            if current in circle_prog and next_chord in circle_prog:
                if circle_prog.index(next_chord) == (circle_prog.index(current) + 1) % len(circle_prog):
                    analysis['harmonic_progressions'].append(f"Circle of Fifths: {current} -> {next_chord}")
                    analysis['circle_measures'].append({'measure': i, 'text': f'5도권 진행: {current}->{next_chord}'})
        else:
            circle_prog = ['i', 'iv', 'VII', 'III', 'VI', 'ii°', 'V', 'i']
            if current in circle_prog and next_chord in circle_prog:
                if circle_prog.index(next_chord) == (circle_prog.index(current) + 1) % len(circle_prog):
                    analysis['harmonic_progressions'].append(f"Circle of Fifths: {current} -> {next_chord}")
                    analysis['circle_measures'].append({'measure': i, 'text': f'5도권 진행: {current}->{next_chord}'})
    
    # 음계 사용 분석
    scale_degrees = s.getPitches()
    for chord in prog:
        rn = roman.RomanNumeral(chord, k)
        for p in rn.pitches:
            if p in scale_degrees:
                degree = scale_degrees.index(p) + 1
                analysis['scale_usage'][f"Degree {degree}"] = analysis['scale_usage'].get(f"Degree {degree}", 0) + 1
    
    # 텐션 분석
    for chord in prog:
        if '7' in chord or '9' in chord or 'sus' in chord:
            analysis['tensions'].append(f"{chord} contains tension")
    
    # 음성진행 분석
    for i in range(len(prog) - 1):
        current = roman.RomanNumeral(prog[i], k)
        next_chord = roman.RomanNumeral(prog[i + 1], k)
        
        # 공통음 유지
        common_tones = set(current.pitches) & set(next_chord.pitches)
        if common_tones:
            analysis['voice_leading'].append(f"Common tone between {prog[i]} and {prog[i+1]}")
        
        # 반음 진행
        for p1 in current.pitches:
            for p2 in next_chord.pitches:
                if abs(p1.midi - p2.midi) == 1:
                    analysis['voice_leading'].append(f"Half-step motion between {prog[i]} and {prog[i+1]}")
    
    return analysis

def print_analysis(analysis):
    """분석 결과 출력"""
    print("\n=== 화성학적 분석 ===")
    print(f"조성: {analysis['key']}")
    
    print("\n종지 분석:")
    if analysis['cadences']:
        for cadence in analysis['cadences']:
            print(f"- {cadence}")
    else:
        print("- 종지 패턴이 명확하지 않음")
    
    print("\n화성 진행 분석:")
    if analysis['harmonic_progressions']:
        for prog in analysis['harmonic_progressions']:
            print(f"- {prog}")
    else:
        print("- 특별한 화성 진행 패턴이 없음")
    
    print("\n음계 사용 분석:")
    for degree, count in analysis['scale_usage'].items():
        print(f"- {degree}: {count}회 사용")
    
    print("\n텐션 분석:")
    if analysis['tensions']:
        for tension in analysis['tensions']:
            print(f"- {tension}")
    else:
        print("- 텐션이 사용되지 않음")
    
    print("\n음성진행 분석:")
    if analysis['voice_leading']:
        for leading in analysis['voice_leading']:
            print(f"- {leading}")
    else:
        print("- 특별한 음성진행 패턴이 없음")

class MusicGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("코드 진행 생성기")
        self.root.geometry("900x800")  # 창 크기 최적화
        self.root.resizable(True, True)
        
        # 전체 창 크기 조절 설정
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.work_queue = queue.Queue()
        self.is_running = False
        self.current_process: Optional[threading.Thread] = None
        self.setup_gui()
        
    def setup_gui(self):
        """GUI 구성 요소를 설정합니다."""
        # 스타일 설정
        style = ttk.Style()
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=5)
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)
        style.configure('TLabelframe', padding=10)
        style.configure('TFrame', padding=10)

        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)

        # 메인 프레임 그리드 설정
        main_frame.grid_columnconfigure(0, weight=1)
        for i in range(5):  # 5개의 주요 섹션
            main_frame.grid_rowconfigure(i, weight=1)

        # 입력 섹션 프레임 (전체 높이의 40%)
        input_frame = ttk.LabelFrame(main_frame, text="기본 설정")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=3)  # 입력 필드 칸을 더 넓게
        input_frame.grid_columnconfigure(2, weight=1)  # 설명 칸은 좁게

        # 입력 필드
        row = 0
        field_width = 35  # 입력 필드 기본 너비

        # 키 입력
        ttk.Label(input_frame, text="키:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.tonic_var = tk.StringVar(value="C")
        ttk.Entry(input_frame, textvariable=self.tonic_var, width=field_width).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Label(input_frame, text="(예: C, D, F# 등)").grid(row=row, column=2, sticky=tk.W, padx=5)

        # 조성 선택
        row += 1
        ttk.Label(input_frame, text="조성:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.mode_var = tk.StringVar(value="major")
        mode_combo = ttk.Combobox(input_frame, textvariable=self.mode_var, values=["major", "minor"], width=field_width-3)
        mode_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        mode_combo.state(['readonly'])

        # 박자 선택
        row += 1
        ttk.Label(input_frame, text="박자:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.time_sig_var = tk.StringVar(value="4/4")
        time_sig_combo = ttk.Combobox(input_frame, textvariable=self.time_sig_var, values=["4/4", "3/4", "6/8"], width=field_width-3)
        time_sig_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        time_sig_combo.state(['readonly'])

        # 마디 수 입력
        row += 1
        ttk.Label(input_frame, text="마디 수:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.length_var = tk.StringVar(value="8")
        ttk.Entry(input_frame, textvariable=self.length_var, width=field_width).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)

        # 구조 선택
        row += 1
        ttk.Label(input_frame, text="구조:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.structure_var = tk.StringVar(value="A")
        structure_combo = ttk.Combobox(input_frame, textvariable=self.structure_var, values=["A", "AABA", "AB"], width=field_width-3)
        structure_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        structure_combo.state(['readonly'])

        # 리듬 패턴 선택
        row += 1
        ttk.Label(input_frame, text="리듬 패턴:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.rhythm_var = tk.StringVar(value="random")
        rhythm_combo = ttk.Combobox(input_frame, textvariable=self.rhythm_var, 
                                    values=["random", "whole", "half", "quarter", "eighth"], width=field_width-3)
        rhythm_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        rhythm_combo.state(['readonly'])

        # 옵션 섹션 프레임 (전체 높이의 20%)
        option_frame = ttk.LabelFrame(main_frame, text="추가 옵션")
        option_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        option_frame.grid_columnconfigure(0, weight=1)
        option_frame.grid_columnconfigure(1, weight=1)

        # 옵션 체크박스를 2x2 그리드로 배치
        self.add_melody_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="멜로디 추가", variable=self.add_melody_var).grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)

        self.use_slurs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="이음줄 사용", variable=self.use_slurs_var).grid(row=0, column=1, sticky=tk.W, padx=20, pady=5)

        self.use_ties_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="붙임줄 사용", variable=self.use_ties_var).grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)

        self.only_melody_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="멜로디만 출력", variable=self.only_melody_var).grid(row=1, column=1, sticky=tk.W, padx=20, pady=5)

        # 저장 위치 선택 프레임 (전체 높이의 15%)
        save_frame = ttk.LabelFrame(main_frame, text="저장 위치")
        save_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        save_frame.grid_columnconfigure(0, weight=4)
        save_frame.grid_columnconfigure(1, weight=1)

        self.save_path_var = tk.StringVar(value=os.path.join(get_documents_dir(), "Score"))
        ttk.Entry(save_frame, textvariable=self.save_path_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        ttk.Button(save_frame, text="찾아보기", command=self.browse_save_path).grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)

        # 상태 표시 프레임 (전체 높이의 15%)
        status_frame = ttk.LabelFrame(main_frame, text="상태")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        status_frame.grid_columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))

        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        status_info_frame.grid_columnconfigure(0, weight=1)
        status_info_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ttk.Label(status_info_frame, text="준비")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.memory_label = ttk.Label(status_info_frame, text="메모리 사용량: 0%")
        self.memory_label.grid(row=0, column=1, sticky=tk.E)

        # 버튼 프레임 (전체 높이의 10%)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="생성 시작", command=self.start_generation, width=20).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel_generation, width=20).grid(row=0, column=1, padx=5)

        # 메모리 모니터링 시작
        self.start_memory_monitoring()
        
    def browse_save_path(self):
        """저장 위치 선택 다이얼로그"""
        path = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if path:
            self.save_path_var.set(path)
            
    def get_unique_filename(self, base_name: str, ext: str) -> str:
        """저장 경로를 고려한 고유 파일명 생성"""
        save_dir = self.save_path_var.get()
        os.makedirs(save_dir, exist_ok=True)
        today = datetime.now().strftime("%Y%m%d")
        n = 1
        while True:
            filename = f"{base_name}_{today}_{n}.{ext}"
            full_path = os.path.join(save_dir, filename)
            if not os.path.exists(full_path):
                return full_path
            n += 1
        
    def start_memory_monitoring(self):
        def update_memory():
            if self.is_running:
                process = psutil.Process()
                memory_percent = process.memory_percent()
                self.memory_label.config(text=f"메모리 사용량: {memory_percent:.1f}%")
                
                if memory_percent > 90:
                    self.show_warning("메모리 사용량이 높습니다. 작업을 일시 중지합니다.")
                    self.cancel_generation()
            
            self.root.after(1000, update_memory)
        
        self.root.after(1000, update_memory)
        
    def validate_input(self) -> bool:
        try:
            tonic = self.tonic_var.get().strip().capitalize()
            if not tonic:
                raise ValueError("키를 입력해주세요.")
                
            mode = self.mode_var.get().strip().lower()
            if mode not in ['major', 'minor']:
                raise ValueError("조성은 major 또는 minor여야 합니다.")
                
            time_sig = self.time_sig_var.get().strip()
            if time_sig not in ['4/4', '3/4', '6/8']:
                raise ValueError("박자는 4/4, 3/4, 6/8 중 하나여야 합니다.")
                
            length = int(self.length_var.get().strip())
            if length < 1:
                raise ValueError("마디 수는 1 이상이어야 합니다.")
                
            structure = self.structure_var.get().strip().upper()
            if structure not in ['A', 'AABA', 'AB']:
                raise ValueError("구조는 A, AABA, AB 중 하나여야 합니다.")
                
            rhythm = self.rhythm_var.get().strip().lower()
            if rhythm not in ['random', 'whole', 'half', 'quarter', 'eighth']:
                raise ValueError("리듬 패턴이 올바르지 않습니다.")
                
            return True
        except ValueError as e:
            self.show_error(str(e))
            return False
            
    def start_generation(self):
        if self.is_running:
            return
            
        if not self.validate_input():
            return
            
        self.is_running = True
        self.progress.start()
        self.status_label.config(text="생성 중...")
        
        # 작업 파라미터 설정
        params = {
            'tonic': self.tonic_var.get().strip().capitalize(),
            'mode': self.mode_var.get().strip().lower(),
            'time_sig': self.time_sig_var.get().strip(),
            'length': int(self.length_var.get().strip()),
            'structure': self.structure_var.get().strip().upper(),
            'rhythm_option': self.rhythm_var.get().strip().lower(),
            'add_melody': self.add_melody_var.get(),
            'use_slurs': self.use_slurs_var.get(),
            'use_ties': self.use_ties_var.get(),
            'only_melody': self.only_melody_var.get()
        }
        
        # 별도 스레드에서 음악 생성
        self.current_process = threading.Thread(target=self.generate_music, args=(params,))
        self.current_process.daemon = True
        self.current_process.start()
        
    def generate_music(self, params: Dict[str, Any]):
        try:
            # 코드 진행 생성
            def get_section(length):
                return generate_progression(params['tonic'], params['mode'], length)
                
            if params['structure'] == 'A':
                prog = get_section(params['length'])
            elif params['structure'] == 'AABA':
                a_len = params['length'] // 4
                b_len = params['length'] - a_len * 3
                prog = get_section(a_len) * 2 + get_section(b_len) + get_section(a_len)
            else:  # AB
                a_len = params['length'] // 2
                b_len = params['length'] - a_len
                prog = get_section(a_len) + get_section(b_len)
                
            # 스코어 생성
            score = stream.Score()
            score.metadata = metadata.Metadata()
            score.metadata.title = f"{params['tonic'].upper()} {params['mode'].capitalize()} 코드 진행"
            
            # 멜로디 추가
            if params['add_melody']:
                melody_part = generate_melody_part(
                    prog, params['tonic'], params['mode'], params['time_sig'],
                    params['rhythm_option'], params['use_slurs'], params['use_ties']
                )
                score.append(melody_part)
                if not params['only_melody']:
                    chord_part = progression_to_part(prog, params['tonic'], params['mode'], params['time_sig'])
                    score.append(chord_part)
            else:
                chord_part = progression_to_part(prog, params['tonic'], params['mode'], params['time_sig'])
                score.append(chord_part)
                
            # 파일 저장
            base_name = f"{params['tonic']}_{params['mode']}_progression"
            save_dir = self.save_path_var.get()
            filename = self.get_unique_filename(base_name, "musicxml")
            score.write('musicxml', fp=filename)
            
            self.root.after(0, lambda: self.show_success(f"MusicXML 파일이 저장되었습니다: {filename}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"오류 발생: {str(e)}"))
        finally:
            self.root.after(0, self.cleanup)
            
    def cancel_generation(self):
        if self.is_running:
            self.is_running = False
            if self.current_process and self.current_process.is_alive():
                self.current_process.join(timeout=1.0)
            self.cleanup()
            
    def cleanup(self):
        self.is_running = False
        self.progress.stop()
        self.status_label.config(text="준비")
        gc.collect()
        
    def show_error(self, message: str):
        messagebox.showerror("오류", message)
        
    def show_warning(self, message: str):
        messagebox.showwarning("경고", message)
        
    def show_success(self, message: str):
        messagebox.showinfo("완료", message)
        
    def run(self):
        self.root.mainloop()

def main():
    app = MusicGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main()