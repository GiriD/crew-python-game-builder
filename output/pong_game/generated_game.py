import pygame
import sys
import math
import random
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 650
FPS = 60

# Colors (Retro-futuristic Neon Theme)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 220)
WHITE = (255, 255, 255)
DARK_BLUE = (12, 18, 48)
NEON_BLUE = (30, 255, 255)
NEON_PINK = (255, 60, 255)
NEON_SHADOW = (0, 5, 30)
GRAY = (122, 122, 164)

# Game Settings
PADDLE_WIDTH = 22
PADDLE_HEIGHT = 120
PADDLE_SPEED = 7
BALL_RADIUS = 19
INIT_BALL_SPEED = 7
MAX_BALL_SPEED = 16
BALL_ACCELERATION = 0.12
BALL_SPIN_FACTOR = 0.45
WIN_SCORE = 11
SCORE_ANIM_TIME = 0.33

# LED font
LED_FONT_PATH = None  # Use default system font if not found
LED_FONT_SIZE = 72
MENU_FONT_SIZE = 34

# Game Modes
GAME_MODES = [
    {'name': 'Classic', 'ai_level': 1, 'description': 'Retro-Futuristic Pong.'},
    {'name': 'Pro', 'ai_level': 2, 'description': 'Faster Ball. Smarter AI.'},
    {'name': 'Spin Master', 'ai_level': 2, 'description': 'Add spin to shots.'}
]

# Exception Classes
class GameException(Exception):
    pass

# Utilities
def load_font(path, size):
    # Load LED font if available, else system font
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.SysFont('Consolas', size, bold=True)

def gradient_surface(width, height, color_top, color_bottom, animated_offset=0):
    """Creates a vertical gradient surface, with optional animation."""
    surface = pygame.Surface((width, height))
    for y in range(height):
        mix = y / height
        offset = math.sin((y + animated_offset) / 50.0) * 50
        r = int(color_top[0] * (1 - mix) + color_bottom[0] * mix)
        g = int(color_top[1] * (1 - mix) + color_bottom[1] * mix)
        b = int(color_top[2] * (1 - mix) + color_bottom[2] * mix)
        pygame.draw.line(surface, (max(0,min(255,r+offset)), max(0,min(255,g)), max(0,min(255,b+offset))), (0, y), (width, y))
    return surface

def neon_glow_blit(surface, image, pos, color, intensity=4, alpha=100):
    # Blit glow effect behind image
    glow = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    glow.fill((0,0,0,0))
    for i in range(1, intensity+1):
        pygame.draw.rect(
            glow,
            (color[0], color[1], color[2], int(alpha/i)),
            pygame.Rect(-i, -i, image.get_width()+2*i, image.get_height()+2*i),
            border_radius=18
        )
    surface.blit(glow, pos)
    surface.blit(image, pos)

def draw_neon_line(surface, color, start_pos, end_pos, width=4, glow_radius=9):
    # Draw neon-glow line with core and shadow
    shadow_color = (color[0]//8, color[1]//8, color[2]//8)
    pygame.draw.line(surface, shadow_color, start_pos, end_pos, width+glow_radius)
    pygame.draw.line(surface, color, start_pos, end_pos, width)

def draw_neon_rect(surface, rect, color, width=6, glow_radius=10):
    # Neon glowing rectangle (court boundary)
    glow_color = (color[0]//4, color[1]//4, color[2]//4)
    pygame.draw.rect(surface, glow_color, rect.inflate(glow_radius*2, glow_radius*2), border_radius=24)
    pygame.draw.rect(surface, color, rect, width, border_radius=16)

def led_text(surf, text, font, pos, color, glow=6):
    # Draw glowing LED-style text
    x, y = pos
    txt_surface = font.render(text, True, color)
    if glow:
        for i in range(glow, 0, -2):
            glow_txt = font.render(text, True, (color[0]//2, color[1]//2, color[2]//3))
            surf.blit(glow_txt, (x-i, y-i))
            surf.blit(glow_txt, (x+i, y+i))
    surf.blit(txt_surface, (x, y))

# Particle System: Ball trail and collision effects
class Particle:
    def __init__(self, x, y, color, vx, vy, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), int(self.size))
        surface.blit(s, (int(self.x-self.size), int(self.y-self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, n=15, speed=4):
        for _ in range(n):
            angle = random.uniform(0, math.pi * 2)
            vx = math.cos(angle) * random.uniform(0.5, speed)
            vy = math.sin(angle) * random.uniform(0.5, speed)
            size = random.randint(2, 7)
            life = random.randint(12, 27)
            self.particles.append(Particle(x, y, color, vx, vy, size, life))

    def trail(self, x, y, color, n=2, speed=0.7):
        # Generate trailing particles (smaller, slower)
        for _ in range(n):
            angle = random.uniform(-0.6, 0.6)
            vx = math.cos(angle) * random.uniform(0, speed)
            vy = math.sin(angle) * random.uniform(0, speed)
            size = random.randint(2, 4)
            life = random.randint(6, 18)
            self.particles.append(Particle(x, y, color, vx, vy, size, life))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life < 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# Paddle Class
class Paddle:
    def __init__(self, x, y, width, height, color, name="Player", is_ai=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.score = 0
        self.name = name
        self.velocity = 0
        self.is_ai = is_ai
        self.target_y = y
        self.glow_intensity = 0
        self.shadow_offset = 12
        self.spin_dir = 0  # Used for ball spin

    def move(self, dy):
        self.velocity = dy
        self.y += dy
        self.y = max(40, min(SCREEN_HEIGHT - self.height - 40, self.y))

    def update_ai(self, ball, difficulty=1):
        # Simple: Follow ball slowly. Difficulty adds challenge.
        aim_y = ball.y - self.height//2
        if difficulty == 1:
            speed = PADDLE_SPEED * 0.78
        elif difficulty == 2:
            speed = PADDLE_SPEED * 1.14
        else:
            speed = PADDLE_SPEED * 1.24
        if abs(self.y - aim_y) > speed:
            if self.y < aim_y:
                self.move(speed)
                self.spin_dir = 1
            else:
                self.move(-speed)
                self.spin_dir = -1
        else:
            self.spin_dir = 0

    def draw(self, surface):
        # Paddle with neon glow and shadow. Simulate 3D style via gradients and shadow
        shadow_rect = pygame.Rect(int(self.x + self.shadow_offset), int(self.y + self.shadow_offset), self.width, self.height)
        pygame.draw.rect(surface, NEON_SHADOW, shadow_rect, border_radius=18)
        paddle_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        grad = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(self.height):
            mix = i / self.height
            r = int(self.color[0] * (1-mix) + WHITE[0] * mix)
            g = int(self.color[1] * (1-mix) + WHITE[1] * mix)
            b = int(self.color[2] * (1-mix) + WHITE[2] * mix)
            pygame.draw.line(grad, (r, g, b, 230), (0,i), (self.width,i))
        neon_glow_blit(surface, grad, (self.x, self.y), self.color)
        # Neon edge
        pygame.draw.rect(surface, self.color, paddle_rect, 6, border_radius=18)
        # Neon glow
        for i in range(3,11,2):
            pygame.draw.rect(surface, (self.color[0], self.color[1], self.color[2], 33), paddle_rect.inflate(i,i), border_radius=22)

# Ball Class
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.choice((1, -1)) * INIT_BALL_SPEED
        self.vy = random.uniform(-3.5, 3.5)
        self.speed = abs(self.vx)
        self.spin = 0
        self.state = 'moving'
        self.serve_anim_pct = 0
        self.serve_dir = 1
        self.last_collision_time = 0

    def serve_reset(self, direction=1):
        # Dramatic serve animation
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = INIT_BALL_SPEED
        self.spin = 0
        self.state = 'serving'
        self.serve_anim_pct = 0
        self.serve_dir = direction
        self.vx = 0.01  # minimal movement during serve
        self.vy = 0

    def start_move(self):
        angle = random.uniform(-0.25, 0.25)
        self.vx = self.serve_dir * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        self.state = 'moving'
        self.last_collision_time = time.time()

    def update(self, paddles, particles, mode_features):
        # Serve animation
        if self.state == 'serving':
            self.serve_anim_pct += 0.043
            bounce_amp = 32 * math.sin(self.serve_anim_pct * math.pi)
            self.x = SCREEN_WIDTH//2 + self.serve_dir * (180 * self.serve_anim_pct)
            self.y = SCREEN_HEIGHT // 2 + bounce_amp
            if self.serve_anim_pct > 0.93:
                self.start_move()
            return

        # Normal movement
        self.x += self.vx
        self.y += self.vy

        # Wall collision
        if self.y < BALL_RADIUS + 28:
            self.y = BALL_RADIUS + 28
            self.vy *= -1
            particles.emit(self.x, self.y-BALL_RADIUS, CYAN, n=26, speed=4)
            # Wall collision glow
        elif self.y > SCREEN_HEIGHT - BALL_RADIUS - 28:
            self.y = SCREEN_HEIGHT - BALL_RADIUS - 28
            self.vy *= -1
            particles.emit(self.x, self.y+BALL_RADIUS, MAGENTA, n=24, speed=4)

        # Paddle collisions
        for paddle in paddles:
            pr = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
            br = pygame.Rect(self.x-BALL_RADIUS, self.y-BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)
            if pr.colliderect(br):
                now = time.time()
                # Prevent double collision per frame
                if now - self.last_collision_time < 0.1:
                    continue
                self.last_collision_time = now
                hit_pos = ((self.y - paddle.y) / paddle.height - 0.5) * 2
                spin_factor = BALL_SPIN_FACTOR * paddle.velocity if mode_features['spin'] else 0
                if paddle.spin_dir != 0 and mode_features['spin']:
                    # More spin at edge hits
                    spin_factor += paddle.spin_dir * abs(hit_pos) * 1.8
                self.vx = (abs(self.vx)+BALL_ACCELERATION) * (-1 if self.vx > 0 else 1)
                self.vx += spin_factor
                self.vy = (self.vy + hit_pos * 4.2 + spin_factor) * 0.82  # More edge impact
                self.speed = min(MAX_BALL_SPEED, abs(self.vx))
                # Visual feedback: Glow and particles
                particles.emit(self.x, self.y, paddle.color, n=random.randint(16,30), speed=abs(self.vx)//2+3)
                self.color = paddle.color
                # For progressive difficulty: glow effect, screen flash handled in main loop

        # Ball trail effect
        particles.trail(self.x, self.y, self.color, n=3, speed=1.2)

    def draw(self, surface):
        # 3D-style, glowing, neon ball with glow and shadow
        s = pygame.Surface((self.radius*2+32, self.radius*2+32), pygame.SRCALPHA)
        # Ball shadow
        pygame.draw.circle(s, NEON_SHADOW, (self.radius+14, self.radius+19), self.radius+10)
        # Neon glow layers
        for g in range(12, 0, -2):
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], 18+g*4), (self.radius+12, self.radius+12), self.radius+g)
        # Main ball
        pygame.draw.circle(s, self.color, (self.radius+12, self.radius+12), self.radius)
        pygame.draw.circle(s, WHITE, (self.radius+12, self.radius+12), int(self.radius*0.82))
        # Inner glow
        pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], 55), (self.radius+12, self.radius+12), int(self.radius*0.67))
        surface.blit(s, (int(self.x-self.radius-12), int(self.y-self.radius-12)))
        # Additional particle effects drawn elsewhere

# Scoreboard & HUD
class Scoreboard:
    def __init__(self, font, led_font, player1, player2):
        self.font = font
        self.led_font = led_font
        self.player1 = player1
        self.player2 = player2
        self.anim = [0.0, 0.0]  # score animation (pct)

    def flash_score(self, who):
        # Animate score on scoring
        self.anim[who] = SCORE_ANIM_TIME

    def update(self, dt):
        # Update score animations
        for i in range(2):
            self.anim[i] = max(0, self.anim[i] - dt)

    def draw(self, surf):
        # Draw modern LED-style scoreboard
        x1 = SCREEN_WIDTH//2 - 168
        x2 = SCREEN_WIDTH//2 + 72
        y = 65
        s1 = str(self.player1.score)
        s2 = str(self.player2.score)
        # Animated Score Change
        if self.anim[0] > 0:
            sz = int(LED_FONT_SIZE+19*math.sin(5*self.anim[0]))
        else:
            sz = LED_FONT_SIZE
        score_font1 = load_font(LED_FONT_PATH, sz)
        if self.anim[1] > 0:
            sz2 = int(LED_FONT_SIZE+22*math.sin(4*self.anim[1]))
        else:
            sz2 = LED_FONT_SIZE
        score_font2 = load_font(LED_FONT_PATH, sz2)
        led_text(surf, s1, score_font1, (x1, y), CYAN)
        led_text(surf, s2, score_font2, (x2, y), MAGENTA)
        # Player Names
        name_font = load_font(None, 26)
        led_text(surf, self.player1.name, name_font, (x1, y+66), CYAN, glow=2)
        led_text(surf, self.player2.name, name_font, (x2, y+66), MAGENTA, glow=2)
        # Score divider
        pygame.draw.rect(surf, WHITE, (SCREEN_WIDTH//2-11, y+17, 22, 8), border_radius=6)

# Neon Court
class NeonCourt:
    def __init__(self, margin=64):
        self.rect = pygame.Rect(margin, margin, SCREEN_WIDTH-2*margin, SCREEN_HEIGHT-2*margin)

    def draw(self, surface):
        # Neon boundary
        draw_neon_rect(surface, self.rect, NEON_BLUE, width=6, glow_radius=12)
        # Dotted Center Line
        for y in range(self.rect.top, self.rect.bottom, 36):
            pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2-4, y, 8, 22), border_radius=9)
        # Neon corners
        for dx in [self.rect.left, self.rect.right-1]:
            for dy in [self.rect.top, self.rect.bottom-1]:
                pygame.draw.circle(surface, NEON_PINK, (dx, dy), 16)

# Menu System
class Menu:
    def __init__(self, game_modes):
        self.game_modes = game_modes
        self.selected = 0
        self.font = load_font(None, MENU_FONT_SIZE)
        self.big_font = load_font(None, 66)
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected = (self.selected - 1) % len(self.game_modes)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected = (self.selected + 1) % len(self.game_modes)
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                return 'select'
            elif event.key == pygame.K_ESCAPE:
                return 'quit'
        elif event.type == pygame.QUIT:
            return 'quit'
        return None

    def draw(self, surf, anim_phase):
        surf.fill(DARK_BLUE)
        t = int(time.time() * 2)
        # Animated gradient background
        grad = gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (2,10,22), (8,28,70), animated_offset=anim_phase*24)
        surf.blit(grad, (0,0))
        # Animated neon title
        neon_title = 'NEON PONG'
        title_font = load_font(None, 69)
        led_text(surf, neon_title, title_font, (SCREEN_WIDTH//2-190, 96), NEON_PINK, glow=8)
        # Instructions
        instr_font = load_font(None, 23)
        led_text(surf, "UP/DOWN or W/S to Select. ENTER to Start.", instr_font, (SCREEN_WIDTH//2-180, 185), WHITE, glow=3)
        for i, gm in enumerate(self.game_modes):
            y = SCREEN_HEIGHT//2 - 44 + i*74
            col = CYAN if i == self.selected else GRAY
            led_text(surf, gm['name'], self.big_font, (SCREEN_WIDTH//2-110, y), col, glow=9 if i == self.selected else 3)
            desc_col = WHITE if i == self.selected else GRAY
            led_text(surf, gm['description'], self.font, (SCREEN_WIDTH//2-94, y+52), desc_col, glow=3)
        # Neon effect under selection
        pygame.draw.rect(surf, NEON_BLUE, (SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2 - 44 + self.selected*74+68, 300, 6), border_radius=4)

class PauseMenu:
    def __init__(self):
        self.font = load_font(None, 46)
        self.menu_font = load_font(None, 32)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                return 'resume'
            elif event.key == pygame.K_q:
                return 'quit'
        elif event.type == pygame.QUIT:
            return 'quit'
        return None

    def draw(self, surf):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,32,150))
        surf.blit(s, (0,0))
        led_text(surf, "PAUSE", self.font, (SCREEN_WIDTH//2-98, SCREEN_HEIGHT//2-88), NEON_PINK, glow=11)
        led_text(surf, "Press P or ESC to Resume", self.menu_font, (SCREEN_WIDTH//2-192, SCREEN_HEIGHT//2-32), WHITE, glow=3)
        led_text(surf, "Q to Quit", self.menu_font, (SCREEN_WIDTH//2-62, SCREEN_HEIGHT//2+18), CYAN, glow=1)

# Victory & Stats Screen
class VictoryScreen:
    def __init__(self, winner_name, stats, font, led_font):
        self.winner_name = winner_name
        self.stats = stats
        self.font = font
        self.led_font = led_font
        self.menu_font = load_font(None, 32)
        self.anim_phase = 0
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_r]:
                return 'replay'
            elif event.key in [pygame.K_ESCAPE, pygame.K_q]:
                return 'quit'
        elif event.type == pygame.QUIT:
            return 'quit'
        return None

    def draw(self, surf):
        surf.fill(DARK_BLUE)
        grad = gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (32,50,125), (8,10,32), animated_offset=self.anim_phase*60)
        surf.blit(grad, (0,0))
        led_text(surf, "WINNER:", self.font, (SCREEN_WIDTH//2-68, 92), NEON_PINK, glow=9)
        led_text(surf, self.winner_name, self.led_font, (SCREEN_WIDTH//2-160, 162), CYAN, glow=12)
        led_text(surf, "Stats:", self.menu_font, (SCREEN_WIDTH//2-48, 262), WHITE, glow=3)
        stat_font = load_font(None, 27)
        for i, (k, v) in enumerate(self.stats.items()):
            led_text(surf, f"{k}: {v}", stat_font, (SCREEN_WIDTH//2-120, 310+i*32), WHITE, glow=2)
        led_text(surf, "R: Replay        Q: Quit", self.menu_font, (SCREEN_WIDTH//2-150, SCREEN_HEIGHT-85), MAGENTA, glow=6)

# Main Game Loop & State Manager
class PongGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        # Fonts
        self.led_font = load_font(LED_FONT_PATH, LED_FONT_SIZE)
        self.font = load_font(None, 44)
        # State
        self.state = 'menu'
        self.game_mode_idx = 0
        self.court = NeonCourt()
        self.particles = ParticleSystem()
        self.pause_menu = PauseMenu()
        self.menu = Menu(GAME_MODES)
        self.victory_screen = None
        self.screen_flash_t = 0
        self.last_flash_col = DARK_BLUE
        self.player1 = None
        self.player2 = None
        self.ball = None
        self.scoreboard = None
        self.mode_features = {'spin': False}
        self.stats = {}

    def set_players(self, mode_idx):
        if mode_idx == 0:
            # Classic: vs AI
            self.player1 = Paddle(76, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, CYAN, name="PLAYER", is_ai=False)
            self.player2 = Paddle(SCREEN_WIDTH-76-PADDLE_WIDTH, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, MAGENTA, name="NEON AI", is_ai=True)
            self.mode_features = {'spin': False}
        elif mode_idx == 1:
            # Pro: Faster ball, smarter AI
            self.player1 = Paddle(76, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, CYAN, name="PLAYER", is_ai=False)
            self.player2 = Paddle(SCREEN_WIDTH-76-PADDLE_WIDTH, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, MAGENTA, name="NEON PRO AI", is_ai=True)
            self.mode_features = {'spin': False}
        elif mode_idx == 2:
            # Spin Master: 2 Player, spin physics
            self.player1 = Paddle(76, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, CYAN, name="P1", is_ai=False)
            self.player2 = Paddle(SCREEN_WIDTH-76-PADDLE_WIDTH, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, MAGENTA, name="P2", is_ai=False)
            self.mode_features = {'spin': True}
        else:
            raise GameException("Invalid game mode")
        self.ball = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BALL_RADIUS, WHITE)
        self.scoreboard = Scoreboard(self.font, self.led_font, self.player1, self.player2)
        self.screen_flash_t = 0
        self.stats = {"Total Hits": 0, "Max Ball Speed": 0}

    def handle_menu(self):
        for event in pygame.event.get():
            action = self.menu.handle_event(event)
            if action == 'select':
                self.state = 'game'
                self.game_mode_idx = self.menu.selected
                self.set_players(self.game_mode_idx)
                self.ball.serve_reset(direction=random.choice((1,-1)))
            elif action == 'quit':
                pygame.quit()
                sys.exit()

    def handle_pause(self):
        for event in pygame.event.get():
            action = self.pause_menu.handle_event(event)
            if action == 'resume':
                self.state = 'game'
                self.pause_menu.active = False
            elif action == 'quit':
                pygame.quit()
                sys.exit()

    def handle_victory(self):
        for event in pygame.event.get():
            action = self.victory_screen.handle_event(event)
            if action == 'replay':
                self.state = 'menu'
                self.victory_screen.active = False
                self.menu.active = True
            elif action == 'quit':
                pygame.quit()
                sys.exit()

    def handle_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Pause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.state = 'pause'
                    self.pause_menu.active = True

        keys = pygame.key.get_pressed()

        # Paddle controls
        # Left Paddle: Up/Down or W/S
        if not self.player1.is_ai:
            dy = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -PADDLE_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = PADDLE_SPEED
            self.player1.move(dy)
        else:
            difficulty = 1 if self.game_mode_idx == 0 else 2
            self.player1.update_ai(self.ball, difficulty)

        # Right Paddle: Two player mode (Spin Master) -> I/K
        if not self.player2.is_ai:
            dy = 0
            if keys[pygame.K_i]:
                dy = -PADDLE_SPEED
            if keys[pygame.K_k]:
                dy = PADDLE_SPEED
            self.player2.move(dy)
        else:
            difficulty = GAME_MODES[self.game_mode_idx]['ai_level']
            self.player2.update_ai(self.ball, difficulty)

    def update(self, dt):
        if self.state == 'game':
            paddles = [self.player1, self.player2]
            self.ball.update(paddles, self.particles, self.mode_features)
            # Ball out of bounds (left/right) -> Score
            if self.ball.x < 0 or self.ball.x > SCREEN_WIDTH:
                scorer = 1 if self.ball.x > SCREEN_WIDTH else 0
                if scorer == 0:
                    self.player1.score += 1
                    self.scoreboard.flash_score(0)
                else:
                    self.player2.score += 1
                    self.scoreboard.flash_score(1)
                self.screen_flash_t = 0.36
                self.last_flash_col = CYAN if scorer == 0 else MAGENTA
                # Ball reset, serve animation
                self.ball.serve_reset(direction=(-1 if scorer==0 else 1))
                # Stats
                self.stats["Max Ball Speed"] = max(self.stats.get("Max Ball Speed",0), int(self.ball.speed*10))
            # Stats: Count paddle hits
            self.stats["Total Hits"] = self.stats.get("Total Hits",0)

            # Victory Condition
            if self.player1.score >= WIN_SCORE or self.player2.score >= WIN_SCORE:
                winner = self.player1.name if self.player1.score >= WIN_SCORE else self.player2.name
                self.victory_screen = VictoryScreen(winner, self.stats, self.font, self.led_font)
                self.state = 'victory'
            self.scoreboard.update(dt)
            self.particles.update()
            # Update progressive difficulty: Ball speed (more glow)
            if abs(self.ball.vx) > INIT_BALL_SPEED+3:
                self.ball.color = NEON_PINK if self.ball.vx > 0 else NEON_BLUE
            else:
                self.ball.color = WHITE
        elif self.state == 'pause':
            pass  # Pause logic handled elsewhere
        elif self.state == 'menu':
            pass  # Menu logic handled elsewhere
        elif self.state == 'victory':
            if self.victory_screen:
                self.victory_screen.anim_phase += dt

    def draw(self):
        # Animated background gradient
        frame_time = pygame.time.get_ticks()/1000.0
        grad = gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (18,26,56), (8,16,44), animated_offset=int(120*math.sin(frame_time*0.2)))
        self.screen.blit(grad, (0,0))

        if self.state == 'menu':
            self.menu.draw(self.screen, frame_time)
        elif self.state == 'game':
            # Game background elements
            self.court.draw(self.screen)
            # Ball trail and collision particle effects
            self.particles.draw(self.screen)
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.ball.draw(self.screen)
            self.scoreboard.draw(self.screen)
            # HUD
            hud_font = load_font(None, 22)
            led_text(self.screen, f"{GAME_MODES[self.game_mode_idx]['name']}   First to {WIN_SCORE}", hud_font, (SCREEN_WIDTH//2-170, 26), WHITE, glow=2)
            # Screen flash
            if self.screen_flash_t > 0:
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                alpha = int(255 * self.screen_flash_t / 0.36)
                flash_surf.fill((*self.last_flash_col, alpha))
                self.screen.blit(flash_surf, (0,0))
                self.screen_flash_t -= 1.0/FPS
        elif self.state == 'pause':
            self.court.draw(self.screen)
            self.particles.draw(self.screen)
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.ball.draw(self.screen)
            self.scoreboard.draw(self.screen)
            self.pause_menu.draw(self.screen)
        elif self.state == 'victory' and self.victory_screen:
            self.victory_screen.draw(self.screen)
        # Fade in/out transitions could be added here

    def run(self):
        dt = 1.0 / FPS
        while True:
            if self.state == 'menu':
                self.handle_menu()
            elif self.state == 'game':
                self.handle_game()
            elif self.state == 'pause':
                self.handle_pause()
            elif self.state == 'victory' and self.victory_screen:
                self.handle_victory()
            self.update(dt)
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

def main():
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Pong - Retro Futuristic")
        game = PongGame(screen)
        game.run()
    except Exception as e:
        print("An error occurred:", e)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()