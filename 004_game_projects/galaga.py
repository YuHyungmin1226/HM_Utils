import pygame
import random
import math
import os
import pathlib
import json
import time

# 게임 설정
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 60

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 128, 255)
GREEN = (0, 255, 0)

# 설정 파일 로드
try:
    script_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_path, 'galaga.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
except (FileNotFoundError, NameError):
    try:
        with open('007_game_projects/galaga.json', 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
    except FileNotFoundError:
        try:
            with open('galaga.json', 'r', encoding='utf-8') as f:
                CONFIG = json.load(f)
        except FileNotFoundError:
            # 기본 설정
            CONFIG = {
                "enemy": {
                    "base_cols": 8,
                    "max_cols": 12,
                    "base_rows": 3,
                    "max_rows": 5,
                    "boss_hp": 3,
                    "mid_hp": 2,
                    "basic_hp": 1,
                    "boss_score": 300,
                    "mid_score": 150,
                    "basic_score": 100
                },
                "item": {
                    "drop_rate": 0.2
                },
                "difficulty": {
                    "dive_speed": 0.05,
                    "dive_speed_per_wave": 0.003,
                    "dive_cooldown": 800,
                    "dive_cooldown_per_wave": 20,
                    "tractor_cooldown": 1200,
                    "tractor_cooldown_per_wave": 30,
                    "missile_base_chance": 0.005,
                    "missile_per_wave": 0.0005,
                    "max_missiles": 10
                }
            }

# 주요 파라미터를 config에서 불러오기
ENEMY_CONFIG = CONFIG['enemy']
ITEM_CONFIG = CONFIG['item']
DIFFICULTY_CONFIG = CONFIG['difficulty']

# 적 종류
ENEMY_TYPES = [
    {'name': 'boss', 'color': BLUE, 'score': 300, 'hp': 3},
    {'name': 'mid', 'color': RED, 'score': 150, 'hp': 2},
    {'name': 'basic', 'color': YELLOW, 'score': 100, 'hp': 1}
]

ITEM_TYPES = [
    {'name': 'double', 'color': (0, 255, 255)},
    {'name': 'shield', 'color': (0, 255, 0)},
    {'name': 'bomb', 'color': (255, 0, 255), 'description': '화면 내 적에게 70% 확률로 피해'},
    {'name': 'score', 'color': (255, 255, 0)}
]

# 진형 이동 관련 변수
FORMATION_LEFT = 40
FORMATION_RIGHT = SCREEN_WIDTH - 40
FORMATION_TOP = 40  # 화면 위쪽에 위치
FORMATION_MOVE_X = 2
FORMATION_MOVE_Y = 15

def get_korean_font(size=24):
    # 1. 프로젝트 폴더에 폰트 파일이 있으면 우선 사용
    for fname in ["NanumGothic.ttf", "malgun.ttf", "AppleGothic.ttf"]:
        if os.path.exists(fname):
            return pygame.font.Font(fname, size)
    # 2. 시스템 폰트 탐색
    try:
        return pygame.font.SysFont("AppleGothic", size)  # macOS
    except:
        try:
            return pygame.font.SysFont("Malgun Gothic", size)  # Windows
        except:
            return pygame.font.SysFont("NanumGothic", size)  # Linux

# 사운드 로딩 함수
def load_sound(filename):
    try:
        return pygame.mixer.Sound(str(pathlib.Path('sounds')/filename))
    except Exception:
        return None

# 효과음 로딩
shoot_sound = load_sound('shoot.wav')
explosion_sound = load_sound('explosion.wav')
item_sound = load_sound('item.wav')
bomb_sound = load_sound('bomb.wav')
gameover_sound = load_sound('gameover.wav')

# 플레이어 우주선 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # 픽셀 아트 스타일 우주선
        pygame.draw.polygon(self.image, (0,255,0), [(20,2),(6,36),(34,36)])
        pygame.draw.rect(self.image, (255,255,255), (16,20,8,16))
        pygame.draw.rect(self.image, (255,0,0), (18,30,4,6))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.lives = 3
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        self.invincible_duration = 5000  # 게임 시작 시 5초 무적
        self.double_fire = False
        self.captured = False
        self.shield = False

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        # 무적 상태 해제
        if self.invincible and pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration:
            self.invincible = False

    def shoot(self, bullets_group, all_sprites):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if shoot_sound:
                shoot_sound.play()
            if self.double_fire:
                bullet1 = Bullet(self.rect.centerx - 8, self.rect.top)
                bullet2 = Bullet(self.rect.centerx + 8, self.rect.top)
                all_sprites.add(bullet1, bullet2)
                bullets_group.add(bullet1, bullet2)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets_group.add(bullet)
            self.last_shot = now

# 플레이어 총알 클래스
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255,255,0), (0,0,4,12))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# 적 우주선 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, formation_pos):
        super().__init__()
        self.type = enemy_type['name']
        self.color = enemy_type['color']
        self.score = enemy_type['score']
        self.hp = enemy_type['hp']
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        # 픽셀 아트 스타일 적
        if self.type == 'boss':
            pygame.draw.rect(self.image, self.color, (4,4,24,24))
            pygame.draw.rect(self.image, (255,255,255), (10,10,12,12))
            pygame.draw.rect(self.image, (255,0,0), (14,18,4,6))
        elif self.type == 'mid':
            pygame.draw.rect(self.image, self.color, (6,6,20,20))
            pygame.draw.rect(self.image, (255,255,255), (12,12,8,8))
        else:
            pygame.draw.rect(self.image, self.color, (8,8,16,16))
            pygame.draw.rect(self.image, (255,255,255), (14,14,4,4))
        self.rect = self.image.get_rect()
        self.formation_x, self.formation_y = formation_pos
        self.rect.x = self.formation_x
        self.rect.y = -40
        self.target_y = self.formation_y
        self.move_dir = 1
        self.move_count = 0
        self.in_formation = False
        self.dive_angle = 0
        self.dive_radius = 0
        self.dive_center = (0, 0)
        self.dive_time = 0
        # 기본 속도 제한 (더 느리게 시작)
        self.dive_speed = 0.03 + random.random() * 0.02
        self.dive_pattern = random.choice(['curve', 'zigzag'])
        self.dive_cooldown = random.randint(400, 1000)
        self.entrance = True
        self.tractor_beam_ready = False
        self.tractor_beam_cooldown = random.randint(900, 1500)
        self.tractor_beam_active = False
        self.tractor_beam = None
        self.capturing = False
        self.returning_to_formation = False  # 진형으로 복귀 중인지 여부
        self.return_speed = 5  # 진형 복귀 속도

    def update(self):
        if self.entrance:
            self.rect.y += 4
            if self.rect.y >= self.target_y:
                self.rect.y = self.target_y
                self.entrance = False
                self.in_formation = True
            return
            
        # 진형 복귀 중인 경우 처리
        if self.returning_to_formation:
            # x, y 방향으로 진형 위치로 이동
            dx = self.formation_x - self.rect.x
            dy = self.formation_y - self.rect.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # 플레이어 영역 피하기
            player_area_top = SCREEN_HEIGHT - 120
            
            # 진형 위치에 도달했거나 매우 가까울 경우
            if dist < self.return_speed:
                self.rect.x = self.formation_x
                self.rect.y = self.formation_y
                self.returning_to_formation = False
                self.in_formation = True
            else:
                # 플레이어 영역 접근 시 우회 경로 설정
                if self.rect.y > player_area_top:
                    # 먼저 화면 좌우 가장자리로 빠르게 이동
                    if self.rect.centerx < SCREEN_WIDTH / 2:
                        target_x = 20  # 왼쪽 가장자리로
                    else:
                        target_x = SCREEN_WIDTH - 20  # 오른쪽 가장자리로
                        
                    dx_edge = target_x - self.rect.x
                    dy_edge = -50  # 위로 이동
                    edge_dist = math.sqrt(dx_edge*dx_edge + 50*50)
                    
                    if edge_dist > 0:
                        ratio = self.return_speed / edge_dist
                        self.rect.x += dx_edge * ratio
                        self.rect.y += -7  # 빠르게 위로 이동
                else:
                    # 정상적으로 진형으로 복귀
                    if dist > 0:
                        ratio = self.return_speed / dist
                        self.rect.x += dx * ratio
                        self.rect.y += dy * ratio
            return
            
        if self.in_formation:
            self.rect.x = self.formation_x
            self.rect.y = self.formation_y
            
            # 현재 시간 체크 - 스테이지 시작 직후에는 돌진 준비 안 함
            current_time = pygame.time.get_ticks()
            is_startup_period = current_time - stage_start_time < missile_cooldown_duration
            
            # 보스 트랙터 빔 준비 (스테이지 시작 3초 후부터)
            if not is_startup_period and self.type == 'boss':
                self.tractor_beam_cooldown -= 1
                if self.tractor_beam_cooldown <= 0 and not self.tractor_beam_active and random.random() < 0.01 + 0.002*wave:
                    self.tractor_beam_active = True
                    self.tractor_beam = TractorBeam(self)
                    all_sprites.add(self.tractor_beam)
                    tractor_beams_group.add(self.tractor_beam)
                    self.tractor_beam_cooldown = random.randint(900, 1800)
                    
            # 돌진 패턴 준비 (스테이지 시작 3초 후부터)
            if not is_startup_period:
                self.dive_cooldown -= 1
                if self.dive_cooldown <= 0 and random.random() < 0.01 + 0.003*wave:
                    self.in_formation = False
                    self.dive_angle = math.pi/2
                    self.dive_radius = 0
                    self.dive_center = (self.rect.centerx, self.rect.centery)
                    self.dive_time = 0
                    
                    # 돌진 시작 방향 결정 - 화면 좌/우측 선택
                    if random.random() < 0.5:
                        # 좌측으로 시작
                        target_x = FORMATION_LEFT - 20
                    else:
                        # 우측으로 시작
                        target_x = FORMATION_RIGHT + 20
                        
                    # 플레이어 영역 피하기 위한 목표 y값 설정
                    target_y = random.randint(FORMATION_TOP, SCREEN_HEIGHT - 200)
                    
                    # 목표 지점 향하는 벡터 설정
                    dx = target_x - self.rect.centerx
                    dy = target_y - self.rect.centery
                    self.dive_direction = (dx, dy)
                    
                    # 스테이지가 높을수록 다양한 돌진 패턴 등장
                    patterns = ['curve', 'zigzag']
                    if wave >= 3:
                        patterns.append('spiral')
                    self.dive_pattern = random.choice(patterns)
        else:
            # 돌진 중 속도 제한
            max_time_increment = min(0.08, self.dive_speed)
            self.dive_time += max_time_increment
            
            if self.dive_pattern == 'curve':
                # 커브 패턴 수정 - 플레이어 영역 침범 방지
                self.rect.x = int(self.dive_center[0] + 100 * math.cos(self.dive_angle + self.dive_time))
                y_offset = 100 * math.sin(self.dive_angle + self.dive_time)
                # 최대 y 위치 제한 (플레이어 위쪽)
                max_allowed_y = min(SCREEN_HEIGHT - 150, self.dive_center[1] + 120)
                self.rect.y = int(min(self.dive_center[1] + y_offset, max_allowed_y))
            elif self.dive_pattern == 'zigzag':
                # 지그재그 패턴 수정 - 플레이어 영역 침범 방지
                self.rect.x = int(self.dive_center[0] + 60 * math.sin(2.5 * self.dive_time))
                y_progress = min(1.0, self.dive_time / 4)  # 진행도 0~1 사이로 제한
                max_allowed_y = SCREEN_HEIGHT - 150
                self.rect.y = int(self.dive_center[1] + (max_allowed_y - self.dive_center[1]) * y_progress)
            elif self.dive_pattern == 'spiral':
                # 나선형 패턴 수정 - 플레이어 영역 침범 방지
                r = 40 + 8*self.dive_time
                self.rect.x = int(self.dive_center[0] + r * math.cos(self.dive_angle + self.dive_time))
                
                # y 방향 계산 후 최대값 제한
                y_offset = r * math.sin(self.dive_angle + self.dive_time)
                max_allowed_y = SCREEN_HEIGHT - 150
                self.rect.y = int(min(self.dive_center[1] + y_offset, max_allowed_y))
            # 돌진 중 총알 발사(보스/중간 적만)
            if self.type in ['boss', 'mid'] and random.random() < DIFFICULTY_CONFIG['missile_base_chance'] + DIFFICULTY_CONFIG['missile_per_wave']*wave:
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                all_sprites.add(bullet)
                enemy_bullets_group.add(bullet)
            # 화면 밖으로 나가거나 돌진 시간이 길어지면 진형으로 복귀
            if (self.rect.top > SCREEN_HEIGHT or 
                self.rect.bottom < -50 or 
                self.rect.left < -50 or 
                self.rect.right > SCREEN_WIDTH + 50 or
                self.dive_time > 12 or  # 돌진 최대 시간 제한
                # 추가: 플레이어 영역에 도달하면 즉시 진형으로 복귀
                self.rect.bottom > SCREEN_HEIGHT - 120):  # 플레이어 위치보다 위쪽
                
                # 돌진 종료 후 진형으로 복귀 시작
                self.returning_to_formation = True
                self.in_formation = False
                self.dive_cooldown = max(100, random.randint(300, 800) - wave*20)
                self.tractor_beam_active = False
                self.tractor_beam = None

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
            return True
        return False

# 적 총알 클래스
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255,0,0), (0,0,4,12))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed_y = 3 + wave * 0.3  # 스테이지가 올라갈수록 조금씩 빨라짐 (최대 속도 제한)
        if self.speed_y > 6:  # 최대 속도 제한
            self.speed_y = 6

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# 트랙터 빔 클래스
class TractorBeam(pygame.sprite.Sprite):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy
        self.image = pygame.Surface((20, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0,100,255,80), (0,0,20,SCREEN_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = enemy.rect.centerx
        self.rect.top = enemy.rect.bottom
        self.active = True
        self.timer = 120  # 2초

    def update(self):
        self.rect.centerx = self.enemy.rect.centerx
        self.rect.top = self.enemy.rect.bottom
        self.timer -= 1
        if self.timer <= 0 or not self.enemy.alive():
            self.active = False
            self.kill()

# 폭발 애니메이션
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        # 픽셀 아트 폭발
        pygame.draw.circle(self.image, (255,255,0), (16,16), 16)
        pygame.draw.circle(self.image, (255,0,0), (16,16), 10)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.frame += 1
            self.last_update = now
            if self.frame == 1:
                self.image.fill((0,0,0,0))
                pygame.draw.circle(self.image, (255,255,0), (16,16), 12)
            elif self.frame == 2:
                self.image.fill((0,0,0,0))
                pygame.draw.circle(self.image, (255,0,0), (16,16), 8)
            elif self.frame > 3:
                self.kill()

# 진형 전체 이동 로직
def update_formation(formation, move_state):
    # in_formation인 적이 없으면 이동 건너뜀
    if not formation:  # 빈 리스트인 경우 처리
        return
    
    in_formation_enemies = [e for e in formation if e.in_formation]
    if not in_formation_enemies:
        return
    min_x = min(e.formation_x for e in in_formation_enemies)
    max_x = max(e.formation_x for e in in_formation_enemies)
    
    # 좌우 이동만 수행 (아래로 내려가지 않음)
    if (move_state['dir'] == 1 and max_x + FORMATION_MOVE_X > FORMATION_RIGHT) or (move_state['dir'] == -1 and min_x - FORMATION_MOVE_X < FORMATION_LEFT):
        # 방향 전환
        move_state['dir'] *= -1
    else:
        for e in in_formation_enemies:
            e.formation_x += FORMATION_MOVE_X * move_state['dir']

# 웨이브 생성 함수 (formation 리스트 반환)
def create_wave(wave, all_sprites, enemies_group):
    formation = []
    # config 기반 적 수/배치/종류 변화
    base_cols = ENEMY_CONFIG['base_cols']
    max_cols = ENEMY_CONFIG['max_cols']
    base_rows = ENEMY_CONFIG['base_rows']
    max_rows = ENEMY_CONFIG['max_rows']
    cols = min(base_cols + wave//2, max_cols)
    rows = min(base_rows + (wave % 3), max_rows)
    for i in range(cols):
        for j in range(rows):
            # 보스/중간/일반 적 비율 변화
            if j == 0:
                if i % (4 - min(wave//3, 2)) == 0:
                    enemy_type = {
                        'name': 'boss',
                        'color': BLUE,
                        'score': ENEMY_CONFIG['boss_score'] + wave*10,
                        'hp': ENEMY_CONFIG['boss_hp'] + wave//3
                    }
                else:
                    enemy_type = {
                        'name': 'mid',
                        'color': RED,
                        'score': ENEMY_CONFIG['mid_score'] + wave*10,
                        'hp': ENEMY_CONFIG['mid_hp'] + wave//3
                    }
            else:
                enemy_type = {
                    'name': 'basic',
                    'color': YELLOW,
                    'score': ENEMY_CONFIG['basic_score'] + wave*10,
                    'hp': ENEMY_CONFIG['basic_hp'] + wave//3
                }
            x = 30 + i*35
            y = FORMATION_TOP + j*32
            enemy = Enemy(x, y, enemy_type, (x, y))
            # 적 속도/공격 빈도 조절 - 웨이브에 따라 서서히 증가 (상한선 적용)
            base_speed = 0.03 + min(0.02, 0.005 * wave)
            max_speed = min(0.08, DIFFICULTY_CONFIG['dive_speed'] + (wave * DIFFICULTY_CONFIG['dive_speed_per_wave']))
            enemy.dive_speed = base_speed + random.random() * (max_speed - base_speed)
            # 돌진 빈도 점진적 증가
            enemy.dive_cooldown = max(300, DIFFICULTY_CONFIG['dive_cooldown'] - min(300, wave*DIFFICULTY_CONFIG['dive_cooldown_per_wave']))
            enemy.tractor_beam_cooldown = max(600, DIFFICULTY_CONFIG['tractor_cooldown'] - min(400, wave*DIFFICULTY_CONFIG['tractor_cooldown_per_wave']))
            all_sprites.add(enemy)
            enemies_group.add(enemy)
            formation.append(enemy)
    return formation

# 플레이어 포획/구출/더블 파이어 상태 관리
def handle_player_capture(player, tractor_beams_group, all_sprites, explosions_group):
    if player.captured:
        # 포획된 상태: 플레이어를 위로 이동(적 방향)
        player.rect.y -= 3
        if player.rect.bottom < 0:
            # 완전히 사라지면 목숨 감소, 플레이어 재생성
            exp = Explosion(player.rect.center)
            all_sprites.add(exp)
            explosions_group.add(exp)
            player.lives -= 1
            player.captured = False
            player.rect.centerx = SCREEN_WIDTH // 2
            player.rect.bottom = SCREEN_HEIGHT - 10
            player.double_fire = False
    else:
        # 트랙터 빔에 닿으면 포획
        for beam in tractor_beams_group:
            if beam.active and player.rect.colliderect(beam.rect):
                player.captured = True
                player.double_fire = False
                break

# 아이템 클래스
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type['name']
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        # 픽셀 아트 스타일 아이템
        pygame.draw.rect(self.image, item_type['color'], (2,2,16,16))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# 쉴드 이펙트
class ShieldEffect(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (0, 255, 0, 80), [0, 0, 48, 48], 4)
        self.rect = self.image.get_rect()
        self.timer = 240  # 4초

    def update(self):
        self.rect.center = self.player.rect.center
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# 폭탄 이펙트
class BombEffect(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # 더 강렬한 폭발 효과 - 여러 원 겹침
        pygame.draw.circle(self.image, (255, 0, 255, 100), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 200)
        pygame.draw.circle(self.image, (255, 0, 0, 80), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 150)
        pygame.draw.circle(self.image, (255, 255, 0, 60), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 100)
        self.rect = self.image.get_rect()
        self.timer = 30
        self.frame = 0

    def update(self):
        self.timer -= 1
        # 폭발 애니메이션 효과 (깜박임)
        self.frame += 1
        if self.frame % 5 == 0:
            self.image.fill((0,0,0,0))
            alpha = max(30, 100 - (30 - self.timer) * 3)
            pygame.draw.circle(self.image, (255, 0, 255, alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 200)
            pygame.draw.circle(self.image, (255, 0, 0, alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 150)
            pygame.draw.circle(self.image, (255, 255, 0, alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 100)
            
        if self.timer <= 0:
            self.kill()

# 하이스코어 파일
def get_highscore_path():
    """OS별 문서 폴더 내 galaga 폴더에 highscore.txt 파일 경로 반환"""
    # OS별 문서 폴더 경로 얻기
    if os.name == 'nt':  # Windows
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    elif os.name == 'posix':  # macOS, Linux
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    else:
        # 기본값으로 현재 폴더 사용
        documents_path = os.path.dirname(os.path.abspath(__file__))
    
    # galaga 폴더 생성
    galaga_folder = os.path.join(documents_path, 'galaga')
    os.makedirs(galaga_folder, exist_ok=True)
    
    # highscore.txt 파일 경로 반환
    return os.path.join(galaga_folder, 'highscore.txt')

def load_highscore():
    try:
        with open(get_highscore_path(), 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(score):
    try:
        with open(get_highscore_path(), 'w') as f:
            f.write(str(score))
    except:
        pass

# 별 배경 애니메이션
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(1, 2)
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = 0
            self.speed = random.uniform(1, 3)
            self.size = random.randint(1, 2)
    def draw(self, surface):
        pygame.draw.circle(surface, (200,200,255), (int(self.x), int(self.y)), self.size)

# 튜토리얼 텍스트
TUTORIAL_TEXT = [
    "<조작법>",
    "좌/우 방향키: 이동",
    "스페이스바: 발사",
    "P키: 일시정지/해제",
    "R키: 재시작, N키: 다음 스테이지",
    "F1: 도움말/튜토리얼",
    "",
    "<아이템 설명>",
    "하늘색: 더블 파이어 (2발)",
    "초록색: 쉴드 (일정 시간 무적)",
    "보라색: 폭탄 (화면 내 적에게 피해)",
    "노란색: 점수 +300",
    "",
    "스페이스바로 게임 시작"
]

# 게임 초기화
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga (Python Edition)")
clock = pygame.time.Clock()

# 스프라이트 그룹
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
enemy_bullets_group = pygame.sprite.Group()
explosions_group = pygame.sprite.Group()
tractor_beams_group = pygame.sprite.Group()
items_group = pygame.sprite.Group()
shield_effects_group = pygame.sprite.Group()
bomb_effects_group = pygame.sprite.Group()

# 플레이어 생성
player = Player()
all_sprites.add(player)
player_group.add(player)

# 웨이브/스테이지
wave = 1
formation = create_wave(wave, all_sprites, enemies_group)
score = 0
font = get_korean_font(24)
game_over = False
stage_clear = False
paused = False

# 진형 전체 이동 로직
move_state = {'dir': 1}

highscore = load_highscore()
stars = [Star() for _ in range(60)]
show_tutorial = True
start_screen = True

# 스테이지 시작 시간 - 미사일 발사 금지 기간 계산용
stage_start_time = pygame.time.get_ticks()
missile_cooldown_duration = 3000  # 3초

def draw_stars(surface):
    for star in stars:
        star.draw(surface)

def update_stars():
    for star in stars:
        star.update()

def reset_player(player):
    player.lives = 3
    player.invincible = True
    player.invincible_timer = pygame.time.get_ticks()
    player.invincible_duration = 5000  # 게임 시작/재시작 시 5초 무적
    player.captured = False
    player.double_fire = False
    player.shield = False
    player.rect.centerx = SCREEN_WIDTH // 2
    player.rect.bottom = SCREEN_HEIGHT - 10

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                show_tutorial = not show_tutorial
            if start_screen and event.key == pygame.K_SPACE:
                start_screen = False
                show_tutorial = False
                reset_player(player)
                stage_start_time = pygame.time.get_ticks()  # 게임 시작 시간 저장
            if event.key == pygame.K_SPACE and not game_over and not stage_clear and not paused:
                # 스테이지 시작 후 3초 동안은 미사일 발사 불가
                current_time = pygame.time.get_ticks()
                if current_time - stage_start_time > missile_cooldown_duration:
                    player.shoot(bullets_group, all_sprites)
            if event.key == pygame.K_r and (game_over or stage_clear):
                # 게임/스테이지 리셋
                for s in all_sprites:
                    s.kill()
                player = Player()
                all_sprites.add(player)
                player_group.add(player)
                wave = 1
                formation = create_wave(wave, all_sprites, enemies_group)
                score = 0
                game_over = False
                stage_clear = False
                paused = False
                move_state = {'dir': 1}
                reset_player(player)
                stage_start_time = pygame.time.get_ticks()  # 게임 재시작 시 시간 저장
            if event.key == pygame.K_n and stage_clear:
                # 다음 스테이지
                for s in all_sprites:
                    if not isinstance(s, Player):
                        s.kill()
                wave += 1
                formation = create_wave(wave, all_sprites, enemies_group)
                stage_clear = False
                paused = False
                move_state = {'dir': 1}  # 진형 이동 방향 초기화
                reset_player(player)
                stage_start_time = pygame.time.get_ticks()  # 다음 스테이지 시작 시간 저장
            if event.key == pygame.K_p:
                paused = not paused

    if paused:
        screen.fill((20, 20, 40))
        all_sprites.draw(screen)
        score_text = font.render(f"점수: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"목숨: {player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH-110, 10))
        wave_text = font.render(f"스테이지: {wave}", True, WHITE)
        screen.blit(wave_text, (SCREEN_WIDTH//2-60, 10))
        pause_text = font.render("일시정지 (P키로 해제)", True, YELLOW)
        screen.blit(pause_text, (SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-20))
        pygame.display.flip()
        continue

    if not game_over and not stage_clear and not paused:
        # 진형 전체 이동
        update_formation(formation, move_state)
        # 플레이어 포획/구출 처리
        handle_player_capture(player, tractor_beams_group, all_sprites, explosions_group)
        # 아이템/이펙트 업데이트
        items_group.update()
        shield_effects_group.update()
        bomb_effects_group.update()
        
        # 현재 시간 체크
        current_time = pygame.time.get_ticks()
        is_startup_period = current_time - stage_start_time < missile_cooldown_duration
        
        # 적이 랜덤하게 총알 발사 (스테이지 시작 3초 후부터)
        if not is_startup_period:
            # 화면에 표시된 적 총알 개수 제한
            max_missiles = DIFFICULTY_CONFIG['max_missiles'] + wave
            if len(enemy_bullets_group) < max_missiles:
                for enemy in enemies_group:
                    if not enemy.in_formation and random.random() < DIFFICULTY_CONFIG['missile_base_chance']:
                        bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                        all_sprites.add(bullet)
                        enemy_bullets_group.add(bullet)

        # 업데이트
        all_sprites.update()
        explosions_group.update()
        
        # 적들의 돌진 시작도 스테이지 시작 3초 후부터 가능하도록 설정
        if is_startup_period:
            for enemy in enemies_group:
                if not enemy.in_formation:
                    enemy.in_formation = True

        # 충돌 판정: 플레이어 총알 vs 적
        hits = pygame.sprite.groupcollide(enemies_group, bullets_group, False, True)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                if enemy.hit():
                    score += enemy.score
                    exp = Explosion(enemy.rect.center)
                    all_sprites.add(exp)
                    explosions_group.add(exp)
                    if explosion_sound:
                        explosion_sound.play()
                    # 아이템 드랍
                    if random.random() < ITEM_CONFIG['drop_rate']:
                        item_type = random.choice(ITEM_TYPES)
                        item = Item(enemy.rect.centerx, enemy.rect.centery, item_type)
                        all_sprites.add(item)
                        items_group.add(item)

        # 아이템 획득 처리
        item_hits = pygame.sprite.spritecollide(player, items_group, True)
        for item in item_hits:
            if item_sound:
                item_sound.play()
            if item.type == 'double':
                player.double_fire = True
            elif item.type == 'shield':
                shield = ShieldEffect(player)
                all_sprites.add(shield)
                shield_effects_group.add(shield)
                player.shield = True
            elif item.type == 'bomb':
                bomb = BombEffect()
                all_sprites.add(bomb)
                bomb_effects_group.add(bomb)
                # 화면 내 적 전체가 아닌 일부 피해
                damage_count = 0
                for enemy in list(enemies_group):
                    # 화면 안에 있는 적만 피해
                    if (0 <= enemy.rect.centerx <= SCREEN_WIDTH and 
                        0 <= enemy.rect.centery <= SCREEN_HEIGHT):
                        # 일정 확률로 처치 또는 HP 감소
                        if random.random() < 0.7:  # 70% 확률로 피해
                            if enemy.hit():  # hit()은 이미 HP 감소 및 HP가 0이면 kill 처리
                                exp = Explosion(enemy.rect.center)
                                all_sprites.add(exp)
                                explosions_group.add(exp)
                                damage_count += 1
                                score += enemy.score // 2  # 일반 처치보다 적은 점수
                score += 200 + damage_count * 50  # 기본 점수 + 처치한 적 수에 따른 추가 점수
            elif item.type == 'score':
                score += 300

        # 쉴드 효과 적용: 적 총알/적과 충돌 시 무적
        if hasattr(player, 'shield') and player.shield:
            if pygame.sprite.spritecollide(player, enemy_bullets_group, True):
                pass  # 무적
            if pygame.sprite.spritecollide(player, enemies_group, False):
                pass  # 무적
            # 쉴드 지속시간 끝나면 해제
            if len(shield_effects_group) == 0:
                player.shield = False
        else:
            # 무적 상태일 때는 충돌 무시
            if player.invincible:
                # 무적 상태 시각적 표시 (깜빡임)
                if pygame.time.get_ticks() % 200 < 100:
                    player.image.set_alpha(100)
                else:
                    player.image.set_alpha(255)
                # 무적 상태에서도 적 총알은 제거
                pygame.sprite.spritecollide(player, enemy_bullets_group, True)
            else:
                player.image.set_alpha(255)
                # 기존 충돌 판정
                if pygame.sprite.spritecollide(player, enemy_bullets_group, True):
                    player.lives -= 1
                    exp = Explosion(player.rect.center)
                    all_sprites.add(exp)
                    explosions_group.add(exp)
                    if player.lives > 0:
                        # 목숨이 남아있으면 잠시 무적 상태로 설정
                        player.invincible = True
                        player.invincible_timer = pygame.time.get_ticks()
                        player.invincible_duration = 3000  # 충돌 후 3초 무적
                    else:
                        game_over = True
                if pygame.sprite.spritecollide(player, enemies_group, True):
                    player.lives -= 1
                    exp = Explosion(player.rect.center)
                    all_sprites.add(exp)
                    explosions_group.add(exp)
                    if player.lives > 0:
                        # 목숨이 남아있으면 잠시 무적 상태로 설정
                        player.invincible = True
                        player.invincible_timer = pygame.time.get_ticks()
                        player.invincible_duration = 3000  # 충돌 후 3초 무적
                    else:
                        game_over = True

        # 적 제거
        for enemy in enemies_group:
            if not enemy.alive():
                enemies_group.remove(enemy)

        # 웨이브 클리어
        if len(enemies_group) == 0:
            stage_clear = True

        # 폭탄 효과음
        for bomb in bomb_effects_group:
            if bomb_sound and bomb.timer == 30:
                bomb_sound.play()

        # 게임 오버 효과음
        if game_over and gameover_sound:
            gameover_sound.play()

    # 배경/별 애니메이션
    bg_color = (20, 20, 40 + min(wave*10, 100))
    screen.fill(bg_color)
    update_stars()
    draw_stars(screen)

    if start_screen or show_tutorial:
        y = 120
        for line in TUTORIAL_TEXT:
            t = font.render(line, True, YELLOW if "<" in line else WHITE)
            screen.blit(t, (SCREEN_WIDTH//2-150, y))
            y += 32
        pygame.display.flip()
        continue

    # 그리기
    screen.fill((20, 20, 40))
    all_sprites.draw(screen)
    # 쉴드/폭탄 이펙트는 맨 위에 그리기
    shield_effects_group.draw(screen)
    bomb_effects_group.draw(screen)
    # 점수/목숨/스테이지 표시
    score_text = font.render(f"점수: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"목숨: {player.lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH-110, 10))
    wave_text = font.render(f"스테이지: {wave}", True, WHITE)
    screen.blit(wave_text, (SCREEN_WIDTH//2-60, 10))
    
    # 스테이지 시작 3초 동안 메시지 표시
    current_time = pygame.time.get_ticks()
    if current_time - stage_start_time < missile_cooldown_duration and not game_over and not stage_clear:
        ready_text = font.render("준비하세요!", True, YELLOW)
        screen.blit(ready_text, (SCREEN_WIDTH//2-80, SCREEN_HEIGHT//2-20))
    if game_over:
        over_text = font.render("게임 오버! R키로 재시작", True, YELLOW)
        screen.blit(over_text, (SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-20))
    if stage_clear:
        clear_text = font.render("스테이지 클리어! N키로 다음 스테이지", True, GREEN)
        screen.blit(clear_text, (SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2-20))
    pygame.display.flip()

    # 하이스코어 갱신/표시
    if score > highscore:
        highscore = score
        save_highscore(highscore)
    highscore_text = font.render(f"하이스코어: {highscore}", True, (255,255,0))
    screen.blit(highscore_text, (SCREEN_WIDTH//2-80, 40))

pygame.quit() 