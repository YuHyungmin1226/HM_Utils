import streamlit as st
import random
from music21 import stream, chord, key, metadata, note, meter, roman, scale, expressions, spanner, tie, tempo
import os
from datetime import datetime
import sys
import io
import base64
from typing import Optional, Dict, Any

# 페이지 설정
st.set_page_config(
    page_title="🎵 코드 진행 생성기",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링 (다크모드 호환)
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: var(--primary-color, #1f77b4);
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: var(--text-color, inherit);
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: var(--secondary-background-color, rgba(31, 119, 180, 0.1));
        color: var(--text-color, inherit);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color, #1f77b4);
        margin: 1rem 0;
    }
    .success-box {
        background-color: rgba(40, 167, 69, 0.1);
        color: var(--text-color, inherit);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: rgba(220, 53, 69, 0.1);
        color: var(--text-color, inherit);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    /* 브라우저 다크모드 감지 */
    @media (prefers-color-scheme: dark) {
        .info-box {
            background-color: rgba(31, 119, 180, 0.2) !important;
            color: #ffffff !important;
        }
        .success-box {
            background-color: rgba(40, 167, 69, 0.2) !important;
            color: #ffffff !important;
        }
        .error-box {
            background-color: rgba(220, 53, 69, 0.2) !important;
            color: #ffffff !important;
        }
        .sub-header {
            color: #ffffff !important;
        }
        .main-header {
            color: #58a6ff !important;
        }
    }
    
    /* 다크모드 대응 (Streamlit 테마) */
    [data-theme="dark"] .info-box,
    .stApp[data-theme="dark"] .info-box {
        background-color: rgba(31, 119, 180, 0.2) !important;
        color: #ffffff !important;
    }
    [data-theme="dark"] .success-box,
    .stApp[data-theme="dark"] .success-box {
        background-color: rgba(40, 167, 69, 0.2) !important;
        color: #ffffff !important;
    }
    [data-theme="dark"] .error-box,
    .stApp[data-theme="dark"] .error-box {
        background-color: rgba(220, 53, 69, 0.2) !important;
        color: #ffffff !important;
    }
    [data-theme="dark"] .sub-header,
    .stApp[data-theme="dark"] .sub-header {
        color: #ffffff !important;
    }
    [data-theme="dark"] .main-header,
    .stApp[data-theme="dark"] .main-header {
        color: #58a6ff !important;
    }
    
    /* 라이트모드 명시적 설정 */
    @media (prefers-color-scheme: light) {
        .info-box {
            background-color: #f0f2f6 !important;
            color: #333333 !important;
        }
        .success-box {
            background-color: #d4edda !important;
            color: #155724 !important;
        }
        .error-box {
            background-color: #f8d7da !important;
            color: #721c24 !important;
        }
        .sub-header {
            color: #333333 !important;
        }
    }
    
    [data-theme="light"] .info-box,
    .stApp[data-theme="light"] .info-box {
        background-color: #f0f2f6 !important;
        color: #333333 !important;
    }
    [data-theme="light"] .success-box,
    .stApp[data-theme="light"] .success-box {
        background-color: #d4edda !important;
        color: #155724 !important;
    }
    [data-theme="light"] .error-box,
    .stApp[data-theme="light"] .error-box {
        background-color: #f8d7da !important;
        color: #721c24 !important;
    }
    [data-theme="light"] .sub-header,
    .stApp[data-theme="light"] .sub-header {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# 코어 함수들 (원본에서 가져옴)
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
    # 다양한 코드 진행 패턴으로 확장
    if mode == 'major':
        basic_patterns = [
            # 기본 클래식 패턴
            ['I', 'IV', 'V', 'I'],
            ['I', 'vi', 'IV', 'V'],
            
            # 캐논 진행 변형
            ['I', 'V', 'vi', 'IV'],
            ['vi', 'IV', 'I', 'V'],
            
            # iii 화음 활용
            ['I', 'iii', 'vi', 'IV'],
            ['I', 'iii', 'IV', 'V'],
            ['vi', 'iii', 'IV', 'V'],
            
            # ii 화음 중심
            ['I', 'ii', 'V', 'vi'],
            ['I', 'ii', 'IV', 'V'],
            ['vi', 'ii', 'V', 'I'],
            
            # 순환 패턴
            ['I', 'vi', 'ii', 'V'],
            ['I', 'iii', 'vi', 'ii'],
            ['vi', 'IV', 'ii', 'V'],
            
            # 팝/록 스타일
            ['I', 'V', 'IV', 'V'],
            ['vi', 'V', 'IV', 'V'],
            ['I', 'vi', 'V', 'IV'],
            
            # 발라드 스타일
            ['I', 'iii', 'IV', 'vi'],
            ['I', 'vi', 'iii', 'IV'],
            ['vi', 'I', 'IV', 'V'],
            
            # 모던 팝
            ['I', 'V', 'vi', 'iii'],
            ['vi', 'V', 'I', 'IV'],
            ['I', 'IV', 'vi', 'V'],
        ]
        cadences = [
            ['IV', 'ii', 'V7', 'I'],
            ['vi', 'ii', 'V7', 'I'],
            ['iii', 'vi', 'ii', 'V7'],
            ['ii', 'V7', 'I'],
            ['IV', 'V', 'I'],
            ['IV', 'I'],
            ['V', 'vi'],  # Deceptive
            ['iii', 'IV', 'V'],
            ['vi', 'IV', 'I'],
        ]
    else:
        basic_patterns = [
            # 기본 단조 패턴
            ['i', 'iv', 'V', 'i'],
            ['i', 'VI', 'iv', 'V'],
            
            # 자연 단조 활용
            ['i', 'VII', 'VI', 'V'],
            ['i', 'III', 'VI', 'iv'],
            ['VI', 'VII', 'i', 'V'],
            
            # ii° 화음 활용
            ['i', 'ii°', 'V', 'i'],
            ['i', 'ii°', 'iv', 'V'],
            ['VI', 'ii°', 'V', 'i'],
            
            # 모던 단조
            ['i', 'VI', 'VII', 'i'],
            ['i', 'III', 'VII', 'VI'],
            ['vi', 'VII', 'III', 'iv'],
            
            # 드라마틱 패턴
            ['i', 'V', 'VI', 'iv'],
            ['i', 'VII', 'IV', 'V'],  # 피카르디 3화음 준비
            ['VI', 'iv', 'i', 'V'],
            
            # 감정적 진행
            ['i', 'VI', 'ii°', 'V'],
            ['i', 'III', 'iv', 'V'],
            ['VI', 'VII', 'III', 'i'],
            
            # 순환 단조
            ['i', 'iv', 'VII', 'VI'],
            ['i', 'VI', 'III', 'VII'],
            ['iv', 'i', 'V', 'VI'],
        ]
        cadences = [
            ['iv', 'ii°', 'V7', 'i'],
            ['VI', 'ii°', 'V7', 'i'],
            ['III', 'iv', 'V7', 'i'],
            ['ii°', 'V7', 'i'],
            ['iv', 'V', 'i'],
            ['iv', 'i'],
            ['V', 'VI'],  # Deceptive
            ['VII', 'VI', 'V'],
            ['iv', 'VII', 'i'],
        ]
    # 다양한 패턴 조합으로 생성
    progression = []
    remaining_length = length
    
    while remaining_length > 0:
        # 매번 새로운 패턴 선택
        pattern = random.choice(basic_patterns)
        pattern_length = len(pattern)
        
        if remaining_length >= pattern_length:
            # 패턴 전체 추가
            progression.extend(pattern)
            remaining_length -= pattern_length
        else:
            # 남은 길이만큼만 추가
            progression.extend(pattern[:remaining_length])
            remaining_length = 0
    
    # 종지 처리: 마지막 3~4마디를 종지 패턴으로 대체
    if length >= 3:
        cadence = random.choice(cadences)
        c_len = min(len(cadence), length)
        progression[-c_len:] = cadence[-c_len:]
    
    return progression

def progression_to_part(prog, tonic, mode='major', time_sig='4/4', analysis=None):
    from music21 import clef
    p = stream.Part()
    p.append(key.Key(tonic, mode))
    p.append(meter.TimeSignature(time_sig))
    p.append(clef.BassClef())  # 낮은음자리표 추가
    
    for i, rn in enumerate(prog):
        m = stream.Measure(number=i+1)  # 마디 번호 명시적으로 지정
        c = roman_to_chord(rn, tonic, mode)
        c.quarterLength = 4 if time_sig == '4/4' else 3 if time_sig == '3/4' else 3
        m.append(c)
        
        # 마지막 마디만 final barline
        if i == len(prog) - 1:
            m.rightBarline = 'final'
            
        p.append(m)
    p.id = 'Chords'
    return p

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
            st.warning(f"⚠️ 경고: {i+1}번째 마디의 음표 길이 합({total_len})이 박자({measure_length})와 일치하지 않습니다.")
        
        # 마지막 마디만 final barline
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

def create_musicxml_download(score, filename):
    """MusicXML 파일을 생성하고 다운로드 링크 제공"""
    import tempfile
    import os
    
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(mode='w', suffix='.musicxml', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # MusicXML 파일로 저장
        score.write('musicxml', fp=temp_path)
        
        # 파일 읽기
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        # Base64 인코딩
        b64 = base64.b64encode(file_data).decode()
        
        # 다운로드 링크 생성
        href = f'<a href="data:application/vnd.recordare.musicxml+xml;base64,{b64}" download="{filename}">📁 {filename} 다운로드</a>'
        return href
        
    finally:
        # 임시 파일 삭제
        try:
            os.unlink(temp_path)
        except:
            pass

# 메인 앱
def main():
    # 헤더
    st.markdown('<h1 class="main-header">🎵 코드 진행 생성기</h1>', unsafe_allow_html=True)
    st.info("🎼 코드 진행을 자동으로 생성해드립니다.")
    
    # 사이드바 설정
    st.sidebar.header("🎹 생성 설정")
    
    # 기본 설정
    st.sidebar.subheader("📋 기본 설정")
    tonic = st.sidebar.selectbox("키 (Key)", 
        ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"], 
        index=0)
    mode = st.sidebar.selectbox("조성", ["major", "minor"], help="장조 또는 단조")
    time_sig = st.sidebar.selectbox("박자", ["4/4", "3/4", "6/8"])
    length = st.sidebar.slider("마디 수", min_value=2, max_value=64, value=8)
    
    # 구조 설정
    st.sidebar.subheader("🏗️ 구조 설정")
    structure = st.sidebar.selectbox("구조", ["A", "AABA", "AB"], help="A: 단일 구조, AABA: 32마디 팝송 구조, AB: 2부 형식")
    rhythm_option = st.sidebar.selectbox("리듬 패턴", ["random", "whole", "half", "quarter", "eighth"])
    
    # 멜로디 설정
    st.sidebar.subheader("🎶 멜로디 설정")
    add_melody = st.sidebar.checkbox("멜로디 추가", value=True)
    if add_melody:
        only_melody = st.sidebar.checkbox("멜로디만 출력", value=False)
        use_slurs = st.sidebar.checkbox("이음줄 사용", value=False)
        use_ties = st.sidebar.checkbox("붙임줄 사용", value=False)
    else:
        only_melody = False
        use_slurs = False
        use_ties = False
    
    # 메인 컨텐츠 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">생성 결과</h2>', unsafe_allow_html=True)
        
        # 생성 버튼
        if st.button("🎵 코드 진행 생성하기", type="primary", use_container_width=True):
            try:
                with st.spinner("🎵 아름다운 코드 진행을 생성하고 있습니다..."):
                    # 드롭다운에서 선택하므로 검증 불필요
                    tonic_clean = tonic
                    
                    # 코드 진행 생성
                    def get_section(length):
                        return generate_progression(tonic_clean, mode, length)
                    
                    if structure == 'A':
                        prog = get_section(length)
                    elif structure == 'AABA':
                        a_len = length // 4
                        b_len = length - a_len * 3
                        prog = get_section(a_len) * 2 + get_section(b_len) + get_section(a_len)
                    else:  # AB
                        a_len = length // 2
                        b_len = length - a_len
                        prog = get_section(a_len) + get_section(b_len)
                    
                    # 세션 상태에 저장
                    st.session_state.progression = prog
                    st.session_state.settings = {
                        'tonic': tonic_clean,
                        'mode': mode,
                        'time_sig': time_sig,
                        'length': length,
                        'structure': structure,
                        'rhythm_option': rhythm_option,
                        'add_melody': add_melody,
                        'only_melody': only_melody,
                        'use_slurs': use_slurs,
                        'use_ties': use_ties
                    }
                    
                    st.success("✅ 코드 진행이 성공적으로 생성되었습니다!")
            
            except Exception as e:
                st.error(f"❌ 생성 중 오류가 발생했습니다: {str(e)}")
        
        # 결과 표시
        if hasattr(st.session_state, 'progression') and st.session_state.progression:
            prog = st.session_state.progression
            settings = st.session_state.settings
            
            # 코드 진행 표시
            st.markdown("### 📊 생성된 코드 진행")
            
            # 4마디씩 그룹화해서 표시
            chord_display = ""
            for i, chord in enumerate(prog):
                if i > 0 and i % 4 == 0:
                    chord_display += "\n"
                chord_display += f"{chord:8}"
            
            st.code(chord_display, language="text")
            
            # 로마숫자 표기
            st.markdown("**로마숫자 표기:**")
            st.info(" → ".join(prog))
            
            # MusicXML 생성 및 다운로드
            if st.button("💾 MusicXML 파일 생성", type="secondary", use_container_width=True):
                try:
                    with st.spinner("🎼 MusicXML 파일을 생성하고 있습니다..."):
                        # 스코어 생성
                        score = stream.Score()
                        score.metadata = metadata.Metadata()
                        score.metadata.title = f"{settings['tonic']} {settings['mode'].capitalize()} 코드 진행"
                        score.metadata.composer = "코드 진행 생성기 (Streamlit)"
                        
                        # 템포 설정
                        tempo_marking = tempo.TempoIndication(number=120)
                        score.insert(0, tempo_marking)
                        
                        # 멜로디 추가
                        if settings['add_melody']:
                            melody_part = generate_melody_part(
                                prog, settings['tonic'], settings['mode'], settings['time_sig'],
                                settings['rhythm_option'], settings['use_slurs'], settings['use_ties']
                            )
                            score.append(melody_part)
                            if not settings['only_melody']:
                                chord_part = progression_to_part(prog, settings['tonic'], settings['mode'], settings['time_sig'])
                                score.append(chord_part)
                        else:
                            chord_part = progression_to_part(prog, settings['tonic'], settings['mode'], settings['time_sig'])
                            score.append(chord_part)
                        

                        
                        # 파일명 생성
                        today = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{settings['tonic']}_{settings['mode']}_progression_{today}.musicxml"
                        
                        # 다운로드 링크 생성
                        download_link = create_musicxml_download(score, filename)
                        st.markdown(download_link, unsafe_allow_html=True)
                        
                        st.success("✅ MusicXML 파일이 준비되었습니다! 위의 링크를 클릭해서 다운로드하세요.")
                        
                except Exception as e:
                    st.error(f"❌ MusicXML 생성 중 오류: {str(e)}")
    
    with col2:
        st.markdown('<h2 class="sub-header">ℹ️ 사용 가이드</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        **🎼 구조 설명:**
        - **A**: 단순한 반복 구조
        - **AABA**: 팝송에서 많이 사용
        - **AB**: 2부 형식 (클래식 소나타 등)
        
        **🎵 활용 팁:**
        - 짧은 진행은 2-4마디로 시작
        - 장조는 밝고 경쾌한 느낌
        - 단조는 슬프고 감성적인 느낌
        - 멜로디 추가하면 더 완성도 높은 곡
        """)
        
        st.info("💡 **알아두세요!**  \n생성된 MusicXML 파일은 MuseScore, Finale, Sibelius 등 대부분의 악보 프로그램에서 열 수 있습니다.")
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        🎵 코드 진행 생성기 | Made by YHM using Streamlit & Music21
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 