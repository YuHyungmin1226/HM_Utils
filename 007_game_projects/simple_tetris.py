import pygame
import random
import os
import json
from datetime import datetime
import sys
import platform  # 플랫폼 모듈 상단에 추가

# 초기화
pygame.init()

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_BLUE = (0, 0, 128)

# 게임 설정
GRID_SIZE = 30  # 각 블록의 픽셀 크기
GRID_WIDTH = 10  # 테트리스 보드의 가로 블록 수
GRID_HEIGHT = 20  # 테트리스 보드의 세로 블록 수
PREVIEW_SIZE = 4  # 다음 블록 미리보기 크기

# 화면 설정
SCREEN_WIDTH = GRID_SIZE * (GRID_WIDTH + 8)  # 게임 보드 + 오른쪽 정보창
SCREEN_HEIGHT = GRID_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("테트리스")

# 시계 설정
clock = pygame.time.Clock()
FPS = 60

# 테트로미노 모양 정의 (I, O, T, S, Z, J, L)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    
    [[1, 1],
     [1, 1]],  # O
     
    [[0, 1, 0],
     [1, 1, 1]],  # T
     
    [[0, 1, 1],
     [1, 1, 0]],  # S
     
    [[1, 1, 0],
     [0, 1, 1]],  # Z
     
    [[1, 0, 0],
     [1, 1, 1]],  # J
     
    [[0, 0, 1],
     [1, 1, 1]]   # L
]

# 각 테트로미노의 색상
SHAPE_COLORS = [
    BLUE,    # I
    YELLOW,  # O
    PURPLE,  # T
    GREEN,   # S
    RED,     # Z
    ORANGE,  # J
    DARK_BLUE     # L
]

# 사용 가능한 한글 폰트 목록을 찾습니다
def find_korean_font():
    """한글 폰트를 찾는 함수."""
    mac_korean_fonts = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/AppleGothic.ttf",
        "/System/Library/Fonts/AppleGothic.ttf"
    ]
    win_korean_fonts = [
        "c:/Windows/Fonts/malgun.ttf",
        "c:/Windows/Fonts/gulim.ttc"
    ]
    system = platform.system()
    font_paths = mac_korean_fonts if system == "Darwin" else win_korean_fonts if system == "Windows" else []
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    return None

# 한글 폰트 설정
korean_font = find_korean_font()
print(f"선택된 한글 폰트: {korean_font}")

def get_font(size):
    """한글 폰트를 로드합니다"""
    try:
        if korean_font:
            if os.path.exists(korean_font):  # 경로인 경우
                print(f"{size}pt 크기의 폰트 로드: {korean_font}")
                return pygame.font.Font(korean_font, size)
            else:  # 폰트 이름인 경우
                print(f"{size}pt 크기의 시스템 폰트 로드: {korean_font}")
                return pygame.font.SysFont(korean_font, size)
        
        # 마지막 대안: Arial 등 기본 폰트 사용
        print(f"기본 폰트 사용 (Arial): {size}pt")
        return pygame.font.SysFont("Arial", size)
    except Exception as e:
        print(f"폰트 로드 오류: {e}")
        return pygame.font.SysFont("Arial", size)

# 폰트 생성
print("폰트 생성 시작...")
font_small = get_font(18)
font_medium = get_font(24) 
font_large = get_font(36)
font_title = get_font(48)
print("폰트 생성 완료")

# 점수 파일 경로
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tetris_scores.json")

# 게임 상태
class GameState:
    START = 0
    PLAYING = 1
    GAME_OVER = 2

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        # 블록 회전
        self.rotation = (self.rotation + 1) % 4
        self.shape = self.get_rotated_shape()
        
    def get_rotated_shape(self):
        if self.rotation == 0:
            return self.shape
        
        # 시계 방향으로 90도씩 회전
        if self.rotation == 1:
            return self._rotate_90_clockwise(self.shape)
        elif self.rotation == 2:
            return self._rotate_180(self.shape)
        elif self.rotation == 3:
            return self._rotate_90_counterclockwise(self.shape)
    
    def _rotate_90_clockwise(self, shape):
        # 90도 시계방향 회전
        return [[shape[y][x] for y in range(len(shape)-1, -1, -1)] for x in range(len(shape[0]))]
    
    def _rotate_180(self, shape):
        # 180도 회전
        return [[shape[y][x] for x in range(len(shape[0])-1, -1, -1)] for y in range(len(shape)-1, -1, -1)]
    
    def _rotate_90_counterclockwise(self, shape):
        # 90도 반시계방향 회전
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0])-1, -1, -1)]

class ScoreManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.scores = self.load_scores()
        
    def load_scores(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"점수 로드 중 오류 발생: {e}")
            return []
    
    def save_scores(self):
        try:
            # 디렉토리가 존재하는지 확인
            save_dir = os.path.dirname(self.filepath)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
                
            # 파일 저장
            with open(self.filepath, 'w') as f:
                json.dump(self.scores, f)
            print(f"점수가 저장되었습니다: {self.filepath}")
        except Exception as e:
            print(f"점수 저장 오류: {e}")
            
            # 대체 경로에 저장 시도
            try:
                alternate_path = os.path.join(os.path.expanduser("~"), "tetris_scores.json")
                with open(alternate_path, 'w') as f:
                    json.dump(self.scores, f)
                print(f"대체 경로에 점수 저장: {alternate_path}")
            except Exception as backup_error:
                print(f"백업 저장 실패: {backup_error}")
    
    def add_score(self, score):
        # 현재 날짜와 시간 저장
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.scores.append({"score": score, "date": now})
        # 점수 기준으로 내림차순 정렬
        self.scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)
        # 상위 10개만 유지
        self.scores = self.scores[:10]
        self.save_scores()
        
    def get_top_scores(self, count=10):
        return self.scores[:count]
    
    def get_rank(self, score):
        # 현재 점수의 순위 반환
        count = 1
        for s in self.scores:
            if score >= s["score"]:
                return count
            count += 1
        return count if count <= 10 else None  # 10위 밖이면 None 반환

# 테스트용 텍스트 렌더링
def test_font_rendering():
    """폰트 렌더링 테스트"""
    print("폰트 렌더링 테스트 중...")
    test_text = "테스트 텍스트"
    try:
        test_surface = font_medium.render(test_text, True, WHITE)
        print(f"렌더링 결과: {test_surface.get_width()}x{test_surface.get_height()} 픽셀")
        if test_surface.get_width() < 10:
            print("경고: 렌더링된 텍스트가 너무 작습니다. 한글이 제대로 렌더링되지 않을 수 있습니다.")
    except Exception as e:
        print(f"텍스트 렌더링 실패: {e}")

# 렌더링 테스트 실행
test_font_rendering()

class TetrisGame:
    def __init__(self):
        # 게임 보드 생성 (0은 빈 공간)
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # 블록이 떨어지는 속도 (초)
        self.fall_time = 0
        self.state = GameState.START
        # 점수 관리자 초기화
        self.score_manager = ScoreManager(SCORE_FILE)
    
    def reset(self):
        # 게임 초기화
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.state = GameState.PLAYING
        
    def new_piece(self):
        # 새로운 테트로미노 생성
        shape = random.choice(SHAPES)
        # 상단 중앙에서 시작
        return Tetromino(GRID_WIDTH // 2 - len(shape[0]) // 2, 0, shape)
    
    def valid_move(self, piece, x, y, shape=None):
        # 이동이 유효한지 확인
        if shape is None:
            shape = piece.shape
            
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= GRID_WIDTH or
                        y + i >= GRID_HEIGHT or
                        (y + i >= 0 and self.board[y + i][x + j])):
                        return False
        return True
    
    def add_to_board(self, piece):
        # 테트로미노를 보드에 추가
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[piece.y + i][piece.x + j] = piece.color
    
    def clear_lines(self):
        # 완성된 줄 제거
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.board[i]):  # 모든 셀이 채워져 있으면
                # 현재 줄 제거
                del self.board[i]
                # 상단에 새 줄 추가
                self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        
        # 점수 계산
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared == 4:  # 테트리스!
            self.score += 800 * self.level
        
        self.lines_cleared += lines_cleared
        # 레벨 업
        self.level = self.lines_cleared // 10 + 1
        # 레벨에 따라 속도 증가
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
        
        return lines_cleared
    
    def move(self, dx, dy):
        # 테트로미노 이동
        if self.valid_move(self.current_piece, self.current_piece.x + dx, self.current_piece.y + dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate(self):
        # 회전 전 모양 저장
        original_rotation = self.current_piece.rotation
        # 회전
        self.current_piece.rotate()
        # 회전이 유효하지 않으면 원상태로
        if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, self.current_piece.shape):
            self.current_piece.rotation = original_rotation
            self.current_piece.shape = self.current_piece.get_rotated_shape()
            return False
        return True
    
    def drop(self):
        # 테트로미노 한칸씩 떨어뜨림
        if self.move(0, 1):
            return True
        else:
            # 더이상 떨어질 수 없으면 보드에 고정
            self.add_to_board(self.current_piece)
            # 라인 체크
            self.clear_lines()
            # 새 테트로미노 생성
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            # 게임 오버 체크
            if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                self.game_over = True
                self.state = GameState.GAME_OVER
                # 게임 오버시 점수 저장
                self.score_manager.add_score(self.score)
            return False
    
    def hard_drop(self):
        # 즉시 바닥으로 떨어뜨림
        while self.drop():
            continue
    
    def draw_game(self, screen):
        # 보드 그리기
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # 테두리 그리기
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                
                # 블록 그리기
                if self.board[y][x]:
                    pygame.draw.rect(screen, self.board[y][x], 
                                    (x * GRID_SIZE + 1, y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2))
        
        # 현재 떨어지는 테트로미노 그리기
        if self.current_piece:
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece.color, 
                                        ((self.current_piece.x + j) * GRID_SIZE + 1, 
                                         (self.current_piece.y + i) * GRID_SIZE + 1, 
                                         GRID_SIZE - 2, GRID_SIZE - 2))
        
        # 오른쪽 정보창 그리기
        info_x = GRID_WIDTH * GRID_SIZE + 20
        
        # 점수 표시
        score_text = font_medium.render(f"점수: {self.score}", True, WHITE)
        screen.blit(score_text, (info_x, 20))
        
        # 레벨 표시
        level_text = font_medium.render(f"레벨: {self.level}", True, WHITE)
        screen.blit(level_text, (info_x, 60))
        
        # 다음 블록 표시
        next_text = font_medium.render("다음 블록", True, WHITE)
        screen.blit(next_text, (info_x, 120))
        
        # 다음 블록 그리기
        if self.next_piece:
            preview_x = info_x + GRID_SIZE
            preview_y = 160
            
            # 미리보기 박스
            pygame.draw.rect(screen, WHITE, 
                           (preview_x - 5, preview_y - 5, 
                            PREVIEW_SIZE * GRID_SIZE + 10, PREVIEW_SIZE * GRID_SIZE + 10), 1)
            
            # 다음 블록
            shape_width = len(self.next_piece.shape[0])
            shape_height = len(self.next_piece.shape)
            
            for i, row in enumerate(self.next_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.next_piece.color, 
                                      (preview_x + j * GRID_SIZE + 1, 
                                       preview_y + i * GRID_SIZE + 1, 
                                       GRID_SIZE - 2, GRID_SIZE - 2))
                                      
    def draw_start_screen(self, screen):
        # 배경
        screen.fill(BLACK)
        
        # 타이틀
        title_text = font_title.render("테트리스", True, WHITE)
        screen.blit(title_text, 
                  (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 
                   SCREEN_HEIGHT // 4 - title_text.get_height() // 2))
        
        # 시작 안내
        start_text = font_medium.render("스페이스바를 눌러 게임 시작", True, WHITE)
        screen.blit(start_text, 
                  (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 
                   SCREEN_HEIGHT // 2 - start_text.get_height() // 2 + 40))
        
        # 조작 안내
        controls_text1 = font_small.render("← → : 좌우 이동", True, WHITE)
        controls_text2 = font_small.render("↓ : 아래로 이동", True, WHITE)
        controls_text3 = font_small.render("↑ : 회전", True, WHITE)
        controls_text4 = font_small.render("스페이스바 : 하드 드롭", True, WHITE)
        
        y_pos = SCREEN_HEIGHT // 2 + 100
        screen.blit(controls_text1, (SCREEN_WIDTH // 2 - controls_text1.get_width() // 2, y_pos))
        screen.blit(controls_text2, (SCREEN_WIDTH // 2 - controls_text2.get_width() // 2, y_pos + 30))
        screen.blit(controls_text3, (SCREEN_WIDTH // 2 - controls_text3.get_width() // 2, y_pos + 60))
        screen.blit(controls_text4, (SCREEN_WIDTH // 2 - controls_text4.get_width() // 2, y_pos + 90))
        
    def draw_game_over_screen(self, screen):
        """게임 오버 화면을 그립니다."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # 텍스트 렌더링 중복 제거
        def render_text(text, font, color, y_offset):
            rendered_text = font.render(text, True, color)
            screen.blit(rendered_text, (SCREEN_WIDTH // 2 - rendered_text.get_width() // 2, y_offset))

        render_text("게임 오버!", font_large, WHITE, 50)
        render_text(f"획득 점수: {self.score}", font_medium, WHITE, 100)

        rank = self.score_manager.get_rank(self.score)
        if rank and rank <= 10:
            render_text(f"순위: {rank}위", font_medium, YELLOW, 140)

        render_text("최고 점수", font_medium, WHITE, 180)
        y_pos = 220
        for i, score_data in enumerate(self.score_manager.get_top_scores()):
            score_val = score_data["score"]
            score_date = score_data["date"]
            color = YELLOW if score_val == self.score and i + 1 == rank else WHITE
            render_text(f"{i+1}. {score_val} ({score_date})", font_small, color, y_pos)
            y_pos += 25

        render_text("1 키를 눌러 재시작", font_medium, WHITE, SCREEN_HEIGHT - 80)
        render_text("2 키를 눌러 종료", font_medium, WHITE, SCREEN_HEIGHT - 40)

    def draw(self, screen):
        # 현재 게임 상태에 따라 다른 화면 그리기
        if self.state == GameState.START:
            self.draw_start_screen(screen)
        elif self.state == GameState.PLAYING:
            self.draw_game(screen)
        elif self.state == GameState.GAME_OVER:
            self.draw_game(screen)  # 게임 화면 먼저 그리고
            self.draw_game_over_screen(screen)  # 그 위에 게임 오버 화면 그리기

def main():
    game = TetrisGame()
    last_drop_time = pygame.time.get_ticks()
    drop_speed = game.fall_speed * 1000  # 밀리초 단위로 변환
    
    running = True
    last_key_time = pygame.time.get_ticks()  # 키 입력 시간 추적을 위한 변수 추가
    
    # 키 입력 디버깅 변수
    key_debug = True
    last_debug_time = pygame.time.get_ticks()
    
    try:
        # 게임 루프
        while running:
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 모든 키 입력을 디버깅 (문제 해결용)
                if event.type == pygame.KEYDOWN and key_debug:
                    key_name = pygame.key.name(event.key)
                    try:
                        unicode_char = event.unicode
                        key_code = event.key
                        print(f"키 입력 감지: {key_name} (코드: {key_code}, 유니코드: {unicode_char!r})")
                    except Exception as e:
                        print(f"키 정보 출력 중 오류: {e}")
                
                # 종료 키 처리
                if event.type == pygame.KEYDOWN:
                    # 종료 키 - ESC 키 또는 숫자 키 2
                    if event.key in (pygame.K_ESCAPE, pygame.K_2):
                        print(f"종료 키 입력 감지: {pygame.key.name(event.key)}")
                        running = False
                        continue
                    
                    # 재시작 키 - 숫자 키 1 (게임 오버 상태일 때)
                    if event.key == pygame.K_1 and game.state == GameState.GAME_OVER:
                        print(f"재시작 키 입력 감지: {pygame.key.name(event.key)}")
                        game.reset()
                        continue
                    
                    # 일반 키 처리
                    if game.state == GameState.START and event.key == pygame.K_SPACE:
                        game.reset()
                    elif game.state == GameState.PLAYING:
                        if event.key == pygame.K_LEFT:
                            game.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            game.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            game.move(0, 1)
                        elif event.key == pygame.K_UP:
                            game.rotate()
                        elif event.key == pygame.K_SPACE:
                            game.hard_drop()
                            last_drop_time = pygame.time.get_ticks()
            
            # 키 상태 직접 확인 (한글 입력 모드에서도 작동하도록)
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            
            # 디버깅용: 1초마다 눌린 키 확인 (key_debug가 True인 경우만)
            if key_debug and current_time - last_debug_time > 1000:
                pressed_keys = []
                for i in range(len(keys)):
                    if keys[i]:
                        try:
                            key_name = pygame.key.name(i)
                            pressed_keys.append(f"{key_name}({i})")
                        except:
                            pressed_keys.append(f"Unknown({i})")
                
                if pressed_keys:
                    print(f"현재 눌린 키: {', '.join(pressed_keys)}")
                last_debug_time = current_time
            
            # 게임 오버 상태에서 특정 키 상태 확인
            if game.state == GameState.GAME_OVER:
                # 재시작: 1 키
                if keys[pygame.K_1]:
                    if current_time - last_key_time > 300:
                        print("키 상태로 재시작: 1")
                        game.reset()
                        last_key_time = current_time
                
                # 종료: 2 키 또는 ESC 키
                if keys[pygame.K_2] or keys[pygame.K_ESCAPE]:
                    if current_time - last_key_time > 300:
                        key_name = 'ESC' if keys[pygame.K_ESCAPE] else '2'
                        print(f"키 상태로 종료: {key_name}")
                        running = False
                        last_key_time = current_time
            
            # 자동 낙하 (게임 플레이 중일 때만)
            if game.state == GameState.PLAYING:
                current_time = pygame.time.get_ticks()
                drop_speed = game.fall_speed * 1000  # 현재 레벨에 맞는 속도로 업데이트
                
                if current_time - last_drop_time > drop_speed:
                    game.drop()
                    last_drop_time = current_time
            
            # 화면 지우기
            screen.fill(BLACK)
            
            # 게임 그리기
            game.draw(screen)
            
            # 화면 업데이트
            pygame.display.flip()
            
            # 프레임 레이트 설정
            clock.tick(FPS)
    except Exception as e:
        print(f"게임 실행 중 오류 발생: {e}")
    finally:
        # 종료 시 자원 정리
        try:
            pygame.quit()
            print("게임이 안전하게 종료되었습니다.")
        except Exception as e:
            print(f"종료 과정에서 오류 발생: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()