import pygame
import sys
import math
import random
import time
import traceback
from pygame import gfxdraw

# =============================
# Game Constants and Settings
# =============================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
FPS = 60
PADDLE_WIDTH = 26
PADDLE_HEIGHT = 126
BALL_SIZE = 28
PADDLE_OFFSET = 54
MAX_SCORE = 11
SERVE_ANIM_TIME = 0.38

# Color Palette (RGB)
NEON_CYAN = (20, 255, 247)
NEON_MAGENTA = (250, 36, 162)
NEON_WHITE = (255, 255, 255)
DEEP_NAVY_BLUE = (14, 19, 48)
DARK_BLUE = (35, 43, 96)
SOFT_PURPLE = (112, 21, 252)
LED_GREEN = (50, 255, 118)
PALE_GREY = (211, 218, 228)

BG_GRAD_TOP = DARK_BLUE
BG_GRAD_MID = DEEP_NAVY_BLUE
BG_GRAD_BOT = SOFT_PURPLE

# Paths to assets (fonts must exist or use pygame fallback)
FONTS = {
    "score": "assets/fonts/Orbitron-Bold.ttf",
    "menu":  "assets/fonts/Rajdhani-Semibold.ttf",
    "hud":   "assets/fonts/RobotoMono-Medium.ttf",
}
MUSIC_PATH = "assets/music/main_theme.ogg"
SFX = {
    "hit_paddle": "assets/sounds/ball_hit_paddle.wav",
    "hit_wall": "assets/sounds/ball_hit_wall.wav",
    "score": "assets/sounds/goal_explosion.wav",
    "serve": "assets/sounds/serve_release.wav",
    "score_flip": "assets/sounds/score_flip.wav",
    "win": "assets/sounds/win_fanfare.wav",
    "menu_beep": "assets/sounds/menu_beep.wav",
    "menu_confirm": "assets/sounds/menu_confirm.wav",
    "pause_in": "assets/sounds/pause_in.wav",
    "pause_out": "assets/sounds/pause_out.wav",
    "error": "assets/sounds/ui_error.wav"
}

# Neon Glow Simulation Settings
NEON_GLOW_BLUR = 8
NEON_PARTICLE_POOL = 146

# =============================
# Utility Functions
# =============================
def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def ease_out_quad(t):
    return -(t*(t-2))

def lerp(a, b, t):
    return a + (b-a) * t

def color_lerp(c1, c2, t):
    return tuple([int(lerp(c1[i], c2[i], t)) for i in range(3)])

# =============================
# Resource Manager
# =============================
class ResourceManager:
    fonts = {}
    sounds = {}
    music_loaded = False
    initialized = False

    @classmethod
    def init(cls):
        if cls.initialized:
            return
        # Fonts
        for k, path in FONTS.items():
            try:
                cls.fonts[k] = pygame.font.Font(path, 64 if k == "score" else (32 if k == "menu" else 20))
            except Exception:
                cls.fonts[k] = pygame.font.SysFont("Arial", 64 if k == "score" else (32 if k == "menu" else 20), bold=True)
        # Sounds
        for s, p in SFX.items():
            try:
                cls.sounds[s] = pygame.mixer.Sound(p)
            except Exception:
                cls.sounds[s] = None
        try:
            pygame.mixer.music.load(MUSIC_PATH)
            cls.music_loaded = True
        except Exception:
            cls.music_loaded = False
        cls.initialized = True

    @classmethod
    def get_font(cls, name):
        return cls.fonts.get(name, pygame.font.SysFont("Arial", 32, bold=True))

    @classmethod
    def play_sound(cls, name, volume=1.0):
        s = cls.sounds.get(name)
        if s:
            s.set_volume(volume)
            s.play()

# =============================
# Particle System (Object pool)
# =============================
class Particle:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.life = 0.0
        self.color = NEON_CYAN
        self.size = 8
        self.alpha = 1.0
        self.type = "trail"

    def spawn(self, x, y, vx, vy, color, size, life, alpha, ptype="trail"):
        self.active = True
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.size = size
        self.life = life
        self.alpha = alpha
        self.type = ptype

    def update(self, dt):
        if not self.active:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.alpha = clamp(self.alpha - 1.1*dt, 0, 1)
        if self.life <= 0 or self.alpha <= 0.02:
            self.active = False

class ParticlePool:
    def __init__(self, pool_size=NEON_PARTICLE_POOL):
        self.pool = [Particle() for _ in range(pool_size)]

    def spawn(self, *args, **kwargs):
        for p in self.pool:
            if not p.active:
                p.spawn(*args, **kwargs)
                return p
        return None

    def update(self, dt):
        for p in self.pool:
            if p.active:
                p.update(dt)

    def render(self, surface):
        for p in self.pool:
            if p.active:
                s = int(p.size * (0.9 + 0.1*p.alpha))
                color = tuple(
                    int(clamp(pc * p.alpha + 40 * (1-p.alpha), 0, 255)) for pc in p.color
                )
                if p.type == "trail":
                    pygame.gfxdraw.filled_circle(surface, int(p.x), int(p.y), s, color)
                    pygame.gfxdraw.aacircle(surface, int(p.x), int(p.y), s, color)
                elif p.type == "burst":
                    pygame.gfxdraw.filled_circle(surface, int(p.x), int(p.y), int(s*1.25), color)
                    pygame.gfxdraw.aacircle(surface, int(p.x), int(p.y), int(s*1.25), color)

# =============================
# Paddle Entity
# =============================
class Paddle:
    def __init__(self, x, y, color, player_id, control_scheme):
        self.x = x
        self.y = y
        self.vy = 0.0
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.color = color
        self.player_id = player_id
        self.control_scheme = control_scheme
        self.score = 0
        self.glow = 0.0
        self.last_hit_time = 0.0
        self.shadow_alpha = 0.26
        self.name = "PLAYER " + str(player_id+1)
        self.glow_pulse = 0.0 # For post-hit effect

    def move(self, dir, dt, speed_scale):
        self.vy = 0.0
        if dir == -1:
            self.vy = -420 * speed_scale
        elif dir == 1:
            self.vy = 420 * speed_scale
        self.y += self.vy * dt
        self.y = clamp(self.y, 8, SCREEN_HEIGHT - self.height - 8)

    def ai_control(self, ball, dt):
        target = clamp(ball.y - self.height//2, 0, SCREEN_HEIGHT - self.height)
        # Smooth follow
        delta = target - self.y
        self.vy = clamp(delta * dt * 7, -340, 340)
        self.y += self.vy * dt
        self.y = clamp(self.y, 8, SCREEN_HEIGHT - self.height - 8)

    def render(self, surface, pulse_flash=0.0):
        # Shadow
        shadow_col = (DEEP_NAVY_BLUE[0], DEEP_NAVY_BLUE[1], DEEP_NAVY_BLUE[2], int(255*self.shadow_alpha))
        shadow_rect = pygame.Rect(int(self.x+8), int(self.y+10), self.width, self.height)
        pygame.draw.rect(surface, DEEP_NAVY_BLUE, shadow_rect, border_radius=12)
        # Body
        neon_bright = tuple([clamp(int(c*1.28+40*pulse_flash), 0,255) for c in self.color])
        paddle_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        pygame.draw.rect(surface, neon_bright, paddle_rect, border_radius=18)
        # Neon Edge
        edge_col = tuple([clamp(int(c*0.68+180*pulse_flash),0,255) for c in self.color])
        pygame.draw.rect(surface, edge_col, paddle_rect, 5, border_radius=18)
        # 3D Highlight Contours
        pygame.draw.rect(surface, NEON_WHITE, (self.x+3, self.y+9, self.width-6, max(9, self.height//8)), border_radius=8)
        # Glow simulation (multiple alpha rects)
        for i in range(5):
            glow_lvl = int(40*pulse_flash + 46 - i*10)
            glow_alpha = clamp(90 - i*15 + 65*pulse_flash, 0, 150)
            glow_rect = paddle_rect.inflate(10+i*5,10+i*4)
            surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color, glow_alpha), surf.get_rect(), border_radius=18)
            surface.blit(surf, glow_rect.topleft)

# =======================
# Ball Entity
# =======================
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.size = BALL_SIZE
        self.spin = 0.0
        self.color = NEON_WHITE
        self.glow = 0.9
        self.trail_points = []
        self.in_serve_anim = False
        self.serve_time = 0.0
        self.max_speed = 880.0
        self.last_collision_time = 0.0
        self.trail_length = 14
        self.trail_alpha_decay = 0.098
        self.last_pos = (x, y)

    def update_physics(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Friction for spin
        if abs(self.spin) > 0.01:
            self.spin *= (0.97 - 0.0007*dt)
        else:
            self.spin = 0.0
        # Clamp speeds
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            f = self.max_speed/speed
            self.vx *= f
            self.vy *= f
        self.trail_points.insert(0, (self.x, self.y))
        if len(self.trail_points) > self.trail_length:
            self.trail_points = self.trail_points[:self.trail_length]
        self.last_pos = (self.x, self.y)

    def apply_spin(self, paddle, collide_norm, dt):
        self.spin += paddle.vy * 0.0048
        norm_v = math.hypot(self.vx, self.vy)
        if norm_v > 30:
            self.vx += self.spin * collide_norm[0] * 6.5
            self.vy += self.spin * collide_norm[1] * 3.3

    def trigger_particle_effect(self, pool, is_burst=False):
        # Ball trail or collision burst
        color = NEON_CYAN if not is_burst else NEON_MAGENTA
        for i in range(random.randint(14,22) if not is_burst else random.randint(24,36)):
            angle = random.uniform(0,math.pi*2) if is_burst else None
            speed = random.uniform(85,165) if is_burst else random.uniform(32,52)
            if is_burst:
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
            else:
                vx = random.uniform(-7,7)
                vy = random.uniform(-7,7)
            alpha = random.uniform(0.7,1.0)
            pool.spawn(
                self.x, self.y,
                vx, vy,
                color,
                random.randint(8,15) if not is_burst else random.randint(11,21),
                random.uniform(0.22,0.34) if not is_burst else random.uniform(0.36,0.58),
                alpha,
                ptype = "trail" if not is_burst else "burst"
            )

    def reset(self, serve_left, speed_scale=1.0, dramatic=False):
        self.x = SCREEN_WIDTH//2
        self.y = SCREEN_HEIGHT//2 + random.randint(-48, 48)
        angle = math.radians(random.uniform(28, 42))
        direction = -1 if serve_left else 1
        base_speed = 480.0 * speed_scale
        self.vx = math.cos(angle)*base_speed*direction
        self.vy = math.sin(angle)*base_speed * (1 if random.random()>0.4 else -1)
        self.spin = 0.0
        self.in_serve_anim = dramatic
        self.serve_time = 0.0
        self.max_speed = 880.0 * speed_scale
        self.trail_points.clear()
        self.last_collision_time = 0.0

    def serve_animation(self, dt):
        self.serve_time += dt

    def render(self, surface, flash_f=0.0):
        # Under Ball Shadow
        shadow_col = color_lerp(DEEP_NAVY_BLUE, PALE_GREY, 0.17)
        s_rect = pygame.Rect(int(self.x-BALL_SIZE//2+8), int(self.y-BALL_SIZE//2+8), BALL_SIZE, BALL_SIZE)
        surf_shadow = pygame.Surface(s_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(surf_shadow, (*shadow_col, int(66+38*flash_f)), surf_shadow.get_rect())
        surface.blit(surf_shadow, s_rect.topleft)
        # Ball Glow Layer
        glow_rad = int(self.size*1.55)
        glow_surf = pygame.Surface((glow_rad*2,glow_rad*2), pygame.SRCALPHA)
        for g in range(9,0,-1):
            c_val = int(220 + g*4 * flash_f)
            col = color_lerp(NEON_CYAN, NEON_WHITE, g/9)
            pygame.gfxdraw.filled_circle(glow_surf, glow_rad, glow_rad, int(glow_rad*0.7)+g*2, (*col, clamp(58+g*17-int(80*flash_f),0,180)))
        bs = int(self.size / 2)
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y), bs, NEON_WHITE)
        surface.blit(glow_surf, (self.x-glow_rad, self.y-glow_rad), special_flags=pygame.BLEND_ADD)
        # Ball edge neon
        pygame.gfxdraw.aacircle(surface, int(self.x), int(self.y), bs, NEON_CYAN)
        # Optionally, draw smiley face on ball for feedback (optional, fun)

# =======================
# Physics Engine
# =======================
class PhysicsEngine:
    def __init__(self, paddles, ball):
        self.paddles = paddles
        self.ball = ball
        self.court_rect = pygame.Rect(PADDLE_OFFSET, 12, SCREEN_WIDTH - PADDLE_OFFSET*2, SCREEN_HEIGHT-24)
        self.difficulty_scale = 1.0

    def update(self, dt, pool, score_cb):
        self.ball.update_physics(dt)
        # Ball collisions: paddles/court boundaries
        b = self.ball
        scored = None
        # Paddle collisions
        for p in self.paddles:
            paddle_rect = pygame.Rect(int(p.x), int(p.y), p.width, p.height)
            ball_rect = pygame.Rect(int(b.x-b.size//2), int(b.y-b.size//2), b.size, b.size)
            if paddle_rect.colliderect(ball_rect):
                # Actual side collision
                if (p.player_id == 0 and b.vx < 0) or (p.player_id == 1 and b.vx > 0):
                    # Sound/particle
                    ResourceManager.play_sound("hit_paddle", 0.74)
                    b.trigger_particle_effect(pool, is_burst=True)
                    # Calculate spin
                    collide_norm = (1 if p.player_id==0 else -1, 0)
                    b.apply_spin(p, collide_norm, dt)
                    # Reflection velocity
                    speed = math.hypot(b.vx, b.vy)
                    b.vx = -b.vx * 1.04 + (0.31*p.vy)
                    b.vy += (0.22*p.vy)
                    speed_boost = 1.0 + min(p.score*0.031, 0.19)
                    b.vx *= speed_boost
                    b.vy *= speed_boost
                    b.x += collide_norm[0] * (p.width//2+BALL_SIZE//2+3)
                    p.glow_pulse = 1.2
                    p.last_hit_time = time.time()
                    b.last_collision_time = time.time()
                else:
                    # Not side collision, e.g. grazing top/bottom
                    b.vy = -b.vy
                    b.y += (1 if b.vy>0 else -1)*20
                    ResourceManager.play_sound("hit_wall",0.59)
        # Top/bot walls
        if b.y < self.court_rect.top + BALL_SIZE//2:
            b.vy = abs(b.vy) * 0.97
            b.y = self.court_rect.top + BALL_SIZE//2
            ResourceManager.play_sound("hit_wall",0.49)
            b.trigger_particle_effect(pool)
        elif b.y > self.court_rect.bottom - BALL_SIZE//2:
            b.vy = -abs(b.vy) * 0.97
            b.y = self.court_rect.bottom - BALL_SIZE//2
            ResourceManager.play_sound("hit_wall",0.49)
            b.trigger_particle_effect(pool)
        # Left/right goals
        if b.x < self.court_rect.left:
            scored = 1
        elif b.x > self.court_rect.right:
            scored = 0
        if scored is not None:
            score_cb(scored)
            ResourceManager.play_sound("score",1.0)
            b.trigger_particle_effect(pool, is_burst=True)

    def increase_difficulty(self, scale):
        self.difficulty_scale = clamp(scale,1.0,2.6)
        for p in self.paddles:
            pass
        self.ball.max_speed = 880.0 * self.difficulty_scale

# ========================
# ScoreBoard UI System
# ========================
class ScoreBoard:
    def __init__(self):
        self.scores = {0:0, 1:0}
        self.anim_flip = [0.0, 0.0] # Score animation flip Y
        self.anim_glow = [0.0, 0.0] # Pulse glow
        self.font = ResourceManager.get_font("score")
        self.last_anim = [0, 0]

    def update_score(self, scorer):
        self.scores[scorer] += 1
        self.anim_flip[scorer] = 1.0
        self.anim_glow[scorer] = 1.25
        ResourceManager.play_sound("score_flip",0.91)
        self.last_anim[scorer] = time.time()

    def animate_score(self, dt):
        for i in range(2):
            # Number flip
            if self.anim_flip[i]>0.01:
                self.anim_flip[i] -= dt*2.69
                self.anim_flip[i] = max(0.0,self.anim_flip[i])
            # Pulse glow
            if self.anim_glow[i]>0.01:
                self.anim_glow[i] -= dt*1.78
                self.anim_glow[i] = max(0.0,self.anim_glow[i])

    def render(self, surface):
        score_pad = 239
        for i in range(2):
            x = SCREEN_WIDTH//2 + (-score_pad if i==0 else score_pad)
            y = 78
            num = self.scores[i]
            # LED-style animated flip effect
            flip = self.anim_flip[i]
            scale_y = 1.0 + flip*0.61
            font_size = int(86 * scale_y)
            font = ResourceManager.get_font("score")
            score_str = str(num)
            text_surf = font.render(score_str, True, NEON_CYAN if i==0 else NEON_MAGENTA)
            color_glow = color_lerp(LED_GREEN if num==MAX_SCORE else NEON_CYAN if i==0 else NEON_MAGENTA,NEON_WHITE, 0.27)
            # LED Glow/Pulse
            for j in range(4):
                alpha = clamp(150-j*29 + int(220*self.anim_glow[i]),0,255)
                glow_surf = pygame.Surface((text_surf.get_width()+14,text_surf.get_height()+14), pygame.SRCALPHA)
                pygame.gfxdraw.box(glow_surf,glow_surf.get_rect(), (*color_glow, alpha))
                surface.blit(glow_surf, (x-7,y-7), special_flags=pygame.BLEND_ADD)
            # Main Score
            surface.blit(text_surf,(x, y))
        # Center LED separator
        sep_rect = pygame.Rect(SCREEN_WIDTH//2-9,76,18, 46)
        pygame.draw.rect(surface, LED_GREEN, sep_rect, border_radius=7)

    def reset(self):
        self.scores = {0:0, 1:0}
        self.anim_flip = [0.0, 0.0]
        self.anim_glow = [0.0, 0.0]

# =========================
# Game State Management
# =========================
class GameState:
    MENU, SERVE, PLAY, SCORE, VICTORY, PAUSE = 'MENU','SERVE','PLAY','SCORE','VICTORY','PAUSE'
    def __init__(self):
        self.current_state = self.MENU
        self.transition_time = 0.0
        self.animation = 0.0 # Sweep
        self.entry_time = time.time()
        self.next_state = self.MENU
        self.transitioning = False
        self.victory_player = None

    def transition(self, state):
        self.next_state = state
        self.transitioning = True
        self.transition_time = 0.0
        self.animation = 0.0

    def update(self, dt):
        if self.transitioning:
            self.transition_time += dt
            if self.transition_time >= 0.32:
                self.current_state = self.next_state
                self.transitioning = False
                self.entry_time = time.time()
                self.animation = 0.0
            else:
                self.animation = ease_out_quad(clamp(self.transition_time/0.32,0,1))

    def in_state(self, state):
        return self.current_state == state

    def show_victory(self, player):
        self.victory_player = player
        self.current_state = self.VICTORY
        self.transition_time = 0.0
        self.animation = 0.0

# =========================
# Menu System / Pause
# =========================
class MenuSystem:
    def __init__(self):
        self.showing = True
        self.selected = 0
        self.options = ["Start Game", "Game Modes", "Options", "Exit"]
        self.font = ResourceManager.get_font("menu")
        self.last_input_time = time.time()
        self.anim = 0.0
        self.input_blocked = False

    def show_menu(self):
        self.showing = True
        self.selected = 0
        self.anim = 0.0
        self.input_blocked = False

    def handle_selection(self, dir):
        if self.input_blocked:
            return
        self.selected = clamp(self.selected+dir,0,len(self.options)-1)
        self.last_input_time=time.time()
        ResourceManager.play_sound("menu_beep",0.66)
        self.anim = 0.19

    def confirm(self):
        ResourceManager.play_sound("menu_confirm",0.82)
        self.input_blocked = True
        self.anim = 0.29

    def render(self, surface):
        # BG glass
        menu_rect = pygame.Rect(SCREEN_WIDTH//2-256, SCREEN_HEIGHT//2-164, 512, 372)
        glass_surf = pygame.Surface(menu_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glass_surf,(40,44,76,110),glass_surf.get_rect(),border_radius=24)
        surface.blit(glass_surf,menu_rect.topleft)
        # Neon border
        for i in range(3):
            border_col = color_lerp(NEON_CYAN,NEON_MAGENTA,i/(3-1))
            pygame.draw.rect(surface,border_col,menu_rect.inflate(i*10,i*7),4, border_radius=28)
        # Logo
        font_logo = ResourceManager.get_font("menu")
        logo_surf = font_logo.render("PONG NEON",True,NEON_CYAN)
        surface.blit(logo_surf,(SCREEN_WIDTH//2-logo_surf.get_width()//2,menu_rect.top+38))
        # Options
        opt_y = menu_rect.top+120
        for i,opt in enumerate(self.options):
            c = NEON_CYAN if i%2==0 else NEON_MAGENTA
            glow = 1.8 if self.selected==i else (0.72 if self.anim>0 and self.selected==i else 0.0)
            font = ResourceManager.get_font("menu")
            surf_opt = font.render(opt,True,c)
            # Glow simulation
            if glow>0.05:
                for j in range(4):
                    opt_glow = pygame.Surface(surf_opt.get_size(),pygame.SRCALPHA)
                    pygame.gfxdraw.box(opt_glow,opt_glow.get_rect(),(c[0],c[1],c[2],88+j*18))
                    surface.blit(opt_glow,(SCREEN_WIDTH//2-surf_opt.get_width()//2,opt_y+i*46-j*2),special_flags=pygame.BLEND_ADD)
            surface.blit(surf_opt,(SCREEN_WIDTH//2-surf_opt.get_width()//2,opt_y+i*46))
        # Footer / last stat
        font_footer = ResourceManager.get_font("hud")
        ft = font_footer.render("v1.0 by NeonArc",True,PALE_GREY)
        surface.blit(ft,(SCREEN_WIDTH//2-ft.get_width()//2,menu_rect.bottom-36))

# =========================
# Rendering System
# =========================
class RenderingSystem:
    def __init__(self, paddles, ball, particle_pool, scoreboard, game_state):
        self.paddles = paddles
        self.ball = ball
        self.particle_pool = particle_pool
        self.scoreboard = scoreboard
        self.game_state = game_state
        self.bg_anim_phase = 0.0
        self.flash_alpha = 0.0
        self.victory_flash = 0.0
        self.ambient_particles = ParticlePool(36)
        self.last_score_flash = 0.0

    def draw_background(self, surface, dt):
        # Animated gradient diagonal
        self.bg_anim_phase = (self.bg_anim_phase + dt*0.06) % 1.0
        grad = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            t = (i/SCREEN_HEIGHT + self.bg_anim_phase*0.9) % 1.0
            if i<(SCREEN_HEIGHT//2):
                c = color_lerp(BG_GRAD_TOP,BG_GRAD_MID,min(1, t*1.2))
            else:
                c = color_lerp(BG_GRAD_MID,BG_GRAD_BOT,min(1,(t-0.24)*1.2))
            pygame.gfxdraw.hline(grad,0,SCREEN_WIDTH-1,i,c)
        surface.blit(grad,(0,0))
        # Floating ambient particles
        for j in range(36):
            ap = self.ambient_particles.pool[j]
            if not ap.active or random.random()>0.012:
                ap.spawn(
                    random.randint(64,SCREEN_WIDTH-82),
                    random.randint(44,SCREEN_HEIGHT-44),
                    random.uniform(-6.5,7.7),
                    random.uniform(-4.5,6.7),
                    random.choice([NEON_CYAN,NEON_MAGENTA,SOFT_PURPLE,NEON_WHITE]),
                    random.randint(8,14),random.uniform(0.19,0.31),random.uniform(0.08,0.38),ptype="trail")
        self.ambient_particles.update(dt)
        self.ambient_particles.render(surface)

    def draw_court(self, surface, dt):
        # Neon court lines
        neon_lines = [
            (PADDLE_OFFSET,12,SCREEN_WIDTH-PADDLE_OFFSET,12),
            (PADDLE_OFFSET,SCREEN_HEIGHT-12,SCREEN_WIDTH-PADDLE_OFFSET,SCREEN_HEIGHT-12),
            (PADDLE_OFFSET,12,PADDLE_OFFSET,SCREEN_HEIGHT-12),
            (SCREEN_WIDTH-PADDLE_OFFSET,12,SCREEN_WIDTH-PADDLE_OFFSET,SCREEN_HEIGHT-12)
        ]
        for i,(x1,y1,x2,y2) in enumerate(neon_lines):
            col = NEON_WHITE if i>1 else (NEON_CYAN if i==0 else NEON_MAGENTA)
            pygame.gfxdraw.line(surface,x1,y1,x2,y2,col)
            for g in range(4):
                glow = pygame.Surface((abs(x2-x1)+14,abs(y2-y1)+14),pygame.SRCALPHA)
                pygame.draw.line(glow,(col[0],col[1],col[2],85-g*17),
                (7,7),(abs(x2-x1)+7,abs(y2-y1)+7),max(4-g*2,1))
                surface.blit(glow, (min(x1,x2)-7,min(y1,y2)-7), special_flags=pygame.BLEND_ADD)
        # Neon corners (pulse anim)
        pulse = math.sin(time.time()*2.1)*0.5+0.5
        for pt in [(PADDLE_OFFSET,12),(SCREEN_WIDTH-PADDLE_OFFSET,12),(PADDLE_OFFSET,SCREEN_HEIGHT-12),(SCREEN_WIDTH-PADDLE_OFFSET,SCREEN_HEIGHT-12)]:
            pygame.gfxdraw.filled_circle(surface,pt[0],pt[1],14,color_lerp(NEON_MAGENTA,NEON_CYAN,pulse))
            pygame.gfxdraw.aacircle(surface,pt[0],pt[1],19,color_lerp(NEON_CYAN,NEON_WHITE,pulse))

    def draw_particles(self, surface):
        self.particle_pool.render(surface)

    def draw_all(self, surface, dt):
        self.draw_background(surface,dt)
        self.draw_court(surface,dt)
        self.draw_particles(surface)
        # Paddles
        for p in self.paddles:
            pulse_flash = max(0.0,min(1.0,(1.2-p.glow_pulse)))
            p.render(surface,pulse_flash)
            p.glow_pulse = max(0.0,p.glow_pulse-dt*2.1)
        # Ball
        self.ball.render(surface,flash_f=1.0 if time.time()-self.ball.last_collision_time<0.16 else 0.0)
        # Scoreboard
        self.scoreboard.render(surface)
        # Screen flash on score
        if self.flash_alpha>0.02:
            flash_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
            pygame.gfxdraw.box(flash_surf,flash_surf.get_rect(),(255,255,255,int(255*self.flash_alpha)))
            surface.blit(flash_surf,(0,0))
            self.flash_alpha = max(0.0,self.flash_alpha-dt*4.4)
        # Victory flash (magenta/cyan sweep)
        if self.victory_flash>0.01:
            v_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
            col = color_lerp(NEON_MAGENTA,SOFT_PURPLE,self.victory_flash)
            pygame.gfxdraw.box(v_surf,v_surf.get_rect(),(*col,int(128*self.victory_flash)))
            surface.blit(v_surf,(0,0))
            self.victory_flash = max(0.0,self.victory_flash-dt*2.7)

# =========================
# Main Game
# =========================
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=48000, size=-16, channels=2, buffer=1024)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SCALED|pygame.DOUBLEBUF)
        pygame.display.set_caption("Pong Neon Edition")
        ResourceManager.init()
        if ResourceManager.music_loaded:
            pygame.mixer.music.set_volume(0.72)
            pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.dt = 0.016
        # Entities
        self.paddles = [
            Paddle(PADDLE_OFFSET-18, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, NEON_CYAN, 0, "keyboard"),
            Paddle(SCREEN_WIDTH-PADDLE_OFFSET-8-PADDLE_WIDTH, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, NEON_MAGENTA, 1, "ai")
        ]
        self.ball = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.ball.reset(serve_left=random.choice([True,False]),speed_scale=1.0,dramatic=True)
        self.particle_pool = ParticlePool(NEON_PARTICLE_POOL)
        self.scoreboard = ScoreBoard()
        self.game_state = GameState()
        self.menu_system = MenuSystem()
        self.renderer = RenderingSystem(self.paddles, self.ball, self.particle_pool, self.scoreboard, self.game_state)
        self.physics_engine = PhysicsEngine(self.paddles, self.ball)
        self.paused = False
        self.game_mode = "Classic"
        self.winner_stats = {"rallies":0, "fastest_serve":0.0, "winner":""}
        self.last_victory_time = 0.0
        self.last_score_delta_scale = 1.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if self.game_state.in_state(GameState.MENU):
                    if event.key == pygame.K_UP:
                        self.menu_system.handle_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        self.menu_system.handle_selection(1)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.menu_system.confirm()
                        if self.menu_system.selected==0:
                            self.game_state.transition(GameState.SERVE)
                        elif self.menu_system.selected==3:
                            pygame.quit()
                            sys.exit(0)
                        else:
                            pass # TODO: Options, Modes
                elif self.game_state.in_state(GameState.PLAY) or self.game_state.in_state(GameState.SERVE):
                    if event.key == pygame.K_p:
                        ResourceManager.play_sound("pause_in",0.83)
                        self.game_state.transition(GameState.PAUSE)
                elif self.game_state.in_state(GameState.PAUSE):
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        ResourceManager.play_sound("pause_out",0.81)
                        self.game_state.transition(GameState.PLAY)
                elif self.game_state.in_state(GameState.VICTORY):
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.scoreboard.reset()
                        for p in self.paddles:
                            p.score = 0
                            p.y = SCREEN_HEIGHT//2-PADDLE_HEIGHT//2
                        self.ball.reset(serve_left=random.choice([True,False]),speed_scale=1.0,dramatic=True)
                        self.game_state.transition(GameState.MENU)
                # Always allow escape
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

        if self.game_state.in_state(GameState.PLAY) or self.game_state.in_state(GameState.SERVE):
            # Paddle control - Player 1 (left, keyboard)
            dir = 0
            if keys[pygame.K_w]:
                dir = -1
            elif keys[pygame.K_s]:
                dir = 1
            self.paddles[0].move(dir,self.dt,self.physics_engine.difficulty_scale)
        else:
            # Block paddle
            self.paddles[0].vy = 0

    def update(self):
        try:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.game_state.update(self.dt)
            self.menu_system.anim = max(0.0,self.menu_system.anim-self.dt*2.8)
            # Victory flash decay
            if self.renderer.victory_flash>0.02:
                self.renderer.victory_flash = max(0.0,self.renderer.victory_flash-self.dt*2.7)
            # Animate scores
            self.scoreboard.animate_score(self.dt)
            # Game State Step
            if self.game_state.transitioning:
                return # Wait transition
            if self.game_state.in_state(GameState.MENU):
                pass
            elif self.game_state.in_state(GameState.SERVE):
                self.ball.serve_animation(self.dt)
                if self.ball.serve_time>=SERVE_ANIM_TIME:
                    self.game_state.transition(GameState.PLAY)
            elif self.game_state.in_state(GameState.PLAY):
                # AI control (Paddle 2)
                self.paddles[1].ai_control(self.ball,self.dt * self.physics_engine.difficulty_scale)
                # Physics & score
                def score_callback(player_id):
                    self.paddles[player_id].score += 1
                    self.scoreboard.update_score(player_id)
                    self.renderer.flash_alpha = 0.24
                    self.last_score_delta_scale = 1.0 + 0.13*(self.paddles[0].score+self.paddles[1].score)
                    # Progressive difficulty
                    self.physics_engine.increase_difficulty(1.0 + 0.08*(self.paddles[0].score+self.paddles[1].score))
                    # Serve reset
                    self.ball.reset(serve_left=player_id==1,speed_scale=self.physics_engine.difficulty_scale,dramatic=True)
                    self.game_state.transition(GameState.SERVE)
                    # Winner?
                    if self.paddles[player_id].score>=MAX_SCORE:
                        self.game_state.show_victory(player_id)
                        ResourceManager.play_sound("win",1.0)
                        self.renderer.victory_flash = 1.0
                        self.winner_stats["winner"] = self.paddles[player_id].name
                        self.last_victory_time = time.time()
                # Physics
                self.physics_engine.update(self.dt,self.particle_pool,score_cb=score_callback)
                self.particle_pool.update(self.dt)
            elif self.game_state.in_state(GameState.SCORE):
                pass
            elif self.game_state.in_state(GameState.VICTORY):
                # Win screen animation
                if time.time()-self.last_victory_time>2.4:
                    pass
            elif self.game_state.in_state(GameState.PAUSE):
                pass
        except Exception as e:
            print("Game Update Exception: ",str(e))
            traceback.print_exc()

    def render(self):
        try:
            self.screen.fill(DARK_BLUE)
            self.renderer.draw_all(self.screen, self.dt)
            # Menus/UI
            if self.game_state.in_state(GameState.MENU):
                self.menu_system.render(self.screen)
            if self.game_state.in_state(GameState.PAUSE):
                # Pause overlay
                surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
                pygame.draw.rect(surf,(38,44,58,176),surf.get_rect(),border_radius=20)
                self.screen.blit(surf,(0,0))
                font = ResourceManager.get_font("menu")
                txt = font.render("PAUSED",True,LED_GREEN)
                self.screen.blit(txt,(SCREEN_WIDTH//2-txt.get_width()//2,SCREEN_HEIGHT//2-44))
                btn_font = ResourceManager.get_font("hud")
                resume = btn_font.render("Press Esc / P to Resume",True,NEON_CYAN)
                self.screen.blit(resume,(SCREEN_WIDTH//2-resume.get_width()//2,SCREEN_HEIGHT//2+22))
            if self.game_state.in_state(GameState.VICTORY):
                # Victory screen overlay
                surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
                pygame.draw.rect(surf,(112,21,252,132),surf.get_rect(),border_radius=20)
                self.screen.blit(surf,(0,0))
                font = ResourceManager.get_font("score")
                txt = font.render("WINNER!",True,LED_GREEN)
                self.screen.blit(txt,(SCREEN_WIDTH//2-txt.get_width()//2,SCREEN_HEIGHT//2-98))
                winner_font = ResourceManager.get_font("menu")
                winner_txt = winner_font.render(self.paddles[self.game_state.victory_player].name,True,(LED_GREEN if self.game_state.victory_player==0 else NEON_MAGENTA))
                self.screen.blit(winner_txt,(SCREEN_WIDTH//2-winner_txt.get_width()//2,SCREEN_HEIGHT//2-38))
                stats = ResourceManager.get_font("hud").render(f"Score: {self.paddles[self.game_state.victory_player].score}",True,NEON_CYAN if self.game_state.victory_player==0 else NEON_MAGENTA)
                self.screen.blit(stats,(SCREEN_WIDTH//2-stats.get_width()//2,SCREEN_HEIGHT//2+22))
                replay = winner_font.render("Press Enter/Space to Replay",True,NEON_WHITE)
                self.screen.blit(replay,(SCREEN_WIDTH//2-replay.get_width()//2,SCREEN_HEIGHT//2+66))
        except Exception as e:
            print("Game Render Exception: ",str(e))
            traceback.print_exc()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.render()

# =========================
def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print("Main Exception:",str(e))
        traceback.print_exc()

if __name__ == "__main__":
    main()