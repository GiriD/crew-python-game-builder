import pygame
import random
import sys
import math
import os

# --- CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# COLOR SCHEME
COLOR_BG = (20, 22, 30)
COLOR_GRID = (40, 44, 50)
COLOR_NEON = [(0, 255, 242), (0, 255, 144), (0, 120, 255), (255, 0, 190)]
COLOR_GLOW = [(0, 255, 220, 160), (0, 220, 120, 180)]
COLOR_FOOD_GLOW = [(255, 0, 100, 160), (255, 255, 0, 180)]
COLOR_FONT = (255, 255, 255)
COLOR_UI_ACCENT = (120, 240, 255)
COLOR_SNAKE_DEAD = (255, 0, 80)
COLOR_SNAKE_PARTICLE = (0, 255, 240)
COLOR_BUTTON = (40, 44, 60)
COLOR_BUTTON_HOVER = (0, 255, 242)
COLOR_ACHIEVEMENT = (0, 255, 180)
# FPS
FPS = 60
MAX_LEVEL = 10

# RESOURCE PATH
HIGH_SCORE_FILE = "snake_highscore.dat"

# --- UTILITY FUNCTIONS ---
def lerp_color(c1, c2, t):
    """Linear interpolate between colors."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_text(surface, text, size, color, x, y, font_name=None, center=True, bold=True, shadow=True):
    """Draw neon-style text with optional shadow."""
    font = pygame.font.Font(font_name or None, size)
    if bold:
        font.set_bold(True)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    if shadow:
        shadow_surface = font.render(text, True, (30,30,60))
        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        surface.blit(shadow_surface, shadow_rect)
    surface.blit(text_surface, rect)
    return rect

def draw_rounded_rect(surface, rect, color, radius):
    """Draw filled rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def load_high_score():
    try:
        if not os.path.isfile(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write('0')
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except Exception:
        return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

# --- PARTICLE SYSTEM ---
class Particle:
    def __init__(self, pos, vel, color, life, radius, glow=False):
        self.pos = list(pos)
        self.vel = list(vel)
        self.color = color
        self.life = life
        self.radius = radius
        self.glow = glow

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1

    def draw(self, surface):
        if self.glow:
            s = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], 60), (self.radius*2,self.radius*2), self.radius*2)
            surface.blit(s, (self.pos[0]-self.radius*2, self.pos[1]-self.radius*2))
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def spawn(self, pos, count, spread, base_vel, color, life, radius, glow=False):
        for _ in range(count):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(0.5, spread)
            vel = [base_vel[0]+math.cos(angle)*speed, base_vel[1]+math.sin(angle)*speed]
            self.particles.append(
                Particle(pos, vel, color, life+random.randint(-4,4), radius+random.randint(-1,1), glow)
            )

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# --- FOOD CLASS ---
class Food:
    TYPES = ['normal', 'speed', 'bonus', 'freeze']
    COLORS = {
        'normal': (255, 0, 190),
        'speed': (0, 255, 100),
        'bonus': (255, 255, 0),
        'freeze': (0, 180, 255)
    }
    GLOWS = {
        'normal': (255, 0, 190, 160),
        'speed': (0, 255, 100, 120),
        'bonus': (255, 255, 0, 120),
        'freeze': (0, 180, 255, 120)
    }

    def __init__(self, grid_pos=None, type_=None):
        self.grid_pos = grid_pos if grid_pos else (
            random.randint(1, GRID_WIDTH-2), 
            random.randint(2, GRID_HEIGHT-4)
        )
        self.type = type_ if type_ else random.choices(self.TYPES, [0.7,0.1,0.15,0.05], k=1)[0]
        self.anim_phase = 0
        self.pulse = 0

    def update(self):
        self.anim_phase += 0.12
        self.pulse = math.sin(self.anim_phase)*5+10

    def draw(self, surface):
        x, y = self.grid_pos[0]*GRID_SIZE + GRID_SIZE//2, self.grid_pos[1]*GRID_SIZE + GRID_SIZE//2
        color = self.COLORS[self.type]
        glow = self.GLOWS[self.type]
        s = pygame.Surface((GRID_SIZE*3, GRID_SIZE*3), pygame.SRCALPHA)
        pygame.draw.circle(s, glow, (GRID_SIZE*1.5, GRID_SIZE*1.5), 13+self.pulse)
        surface.blit(s, (x-GRID_SIZE*1.5, y-GRID_SIZE*1.5))
        pygame.draw.circle(surface, color, (x, y), 10)
        # Inner pulse
        pygame.draw.circle(surface, (255,255,255), (x, y), int(5+math.fabs(math.sin(self.anim_phase)*2)), 2)

# --- SNAKE CLASS ---
class Snake:
    def __init__(self, color_list):
        self.color_list = color_list
        self.reset()
        self.particle_timer = 0

    def reset(self):
        self.segments = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.length = 5
        self.dir = (1,0)
        self.pending_dir = (1,0)
        self.speed = 7
        self.level = 1
        self.alive = True
        self.accel = 0.0
        self.move_tick = 0
        self.grow_segments = 0
        self.freeze_timer = 0
        self.screen_shake = 0
        self.body_anim = 0

    def set_direction(self, dir_):
        # Prevent direction reverse
        if dir_ != (-self.dir[0], -self.dir[1]):
            self.pending_dir = dir_

    def update(self, food_list):
        self.body_anim += 1
        moved = False
        speed_mod = 1.0
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            speed_mod = 0.5

        self.accel = min(1.0+self.level*0.06, 1.7)
        self.move_tick += self.accel * self.speed * speed_mod/FPS

        if self.move_tick >= 1:
            self.dir = self.pending_dir
            # Move head
            new_pos = (self.segments[0][0] + self.dir[0], self.segments[0][1] + self.dir[1])
            self.segments = [new_pos] + self.segments
            if self.grow_segments <= 0:  # only trim if not growing
                while len(self.segments) > self.length:
                    self.segments.pop()
            else:
                self.grow_segments -= 1
            self.move_tick -= 1
            moved = True

        # Check collision with food
        ate_food = None
        for f in food_list:
            if self.segments[0] == f.grid_pos:
                ate_food = f
                break
        if ate_food:
            self.on_eat_food(ate_food)
            food_list.remove(ate_food)

        return moved, ate_food

    def on_eat_food(self, food):
        if food.type == 'normal':
            self.length += 1
            self.grow_segments += 1
        elif food.type == 'bonus':
            self.length += 2
            self.grow_segments += 2
        elif food.type == 'speed':
            self.accel = min(self.accel + 0.2, 1.9)
        elif food.type == 'freeze':
            self.freeze_timer = FPS*1
        self.level = 1 + (self.length-5) // 7

    def check_collision(self):
        # Borders
        headx, heady = self.segments[0]
        if not (0 <= headx < GRID_WIDTH and 0 <= heady < GRID_HEIGHT):
            self.alive = False
            self.screen_shake = 20
            return 'wall'
        # Self
        for idx, seg in enumerate(self.segments[1:]):
            if self.segments[0] == seg:
                self.alive = False
                self.screen_shake = 20
                return 'self'
        return None

    def draw(self, surface, pmgr):
        # Draw glow trail before body
        for idx, seg in enumerate(reversed(self.segments)):
            x = seg[0]*GRID_SIZE + GRID_SIZE//2
            y = seg[1]*GRID_SIZE + GRID_SIZE//2
            s = pygame.Surface((GRID_SIZE*2, GRID_SIZE*2), pygame.SRCALPHA)
            coloridx = int(lerp(idx/len(self.segments), 0, len(self.color_list)-1))
            neoncol = self.color_list[(idx*2)%len(self.color_list)]
            pygame.draw.circle(s, (*neoncol,50), (GRID_SIZE, GRID_SIZE), GRID_SIZE//2 + idx//3)
            surface.blit(s, (x-GRID_SIZE, y-GRID_SIZE))
        # Draw snake body with gradient
        for idx, seg in enumerate(self.segments):
            x = seg[0]*GRID_SIZE + GRID_SIZE//2
            y = seg[1]*GRID_SIZE + GRID_SIZE//2
            t = idx / max(len(self.segments)-1,1)
            color = lerp_color(self.color_list[0], self.color_list[-1], t)
            glow_surf = pygame.Surface((GRID_SIZE*2, GRID_SIZE*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, min(120, 30+idx*10)), (GRID_SIZE, GRID_SIZE), GRID_SIZE//2 + 4)
            surface.blit(glow_surf, (x-GRID_SIZE, y-GRID_SIZE))
            pygame.draw.circle(surface, color, (x, y), GRID_SIZE//2)
        # Head outline
        headx, heady = self.segments[0]
        hx, hy = headx*GRID_SIZE + GRID_SIZE//2, heady*GRID_SIZE + GRID_SIZE//2
        pygame.draw.circle(surface, (255,255,255), (hx, hy), GRID_SIZE//2, 2)
        # Animate eyes
        phase = math.sin(self.body_anim*0.25)*2
        pygame.draw.circle(surface, (0,255,255), (hx-5, hy-2+int(phase)), 3)
        pygame.draw.circle(surface, (0,255,255), (hx+5, hy-2+int(phase)), 3)

        # Particle trail
        if self.particle_timer <= 0:
            pmgr.spawn((hx,hy), random.randint(1,2), 2, [0,0], COLOR_SNAKE_PARTICLE, 12, 2, glow=True)
            self.particle_timer = 4
        else:
            self.particle_timer -= 1

def lerp(a,b,t):
    return a+(b-a)*t

# --- ACHIEVEMENT SYSTEM ---
class Achievement:
    def __init__(self, icon, text):
        self.icon = icon
        self.text = text
        self.timer = FPS*3

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, surface, idx):
        box_width, box_height = 250, 50
        base_y = 90 + idx*box_height
        rect = pygame.Rect(SCREEN_WIDTH - box_width - 25, base_y, box_width, box_height)
        draw_rounded_rect(surface, rect, (10,50,30,200), 20)
        draw_text(surface, self.text, 25, COLOR_ACHIEVEMENT, rect.x+60, rect.y+box_height//2, center=False, bold=True)
        # Icon
        pygame.draw.circle(surface, COLOR_ACHIEVEMENT, (rect.x+30, rect.y+box_height//2), 15)
        pygame.draw.circle(surface, (255,255,255), (rect.x+30, rect.y+box_height//2), 10, 2)

class AchievementManager:
    def __init__(self):
        self.achievements = []

    def unlock(self, text):
        self.achievements.append(Achievement('medal', text))

    def update(self):
        self.achievements = [ach for ach in self.achievements if ach.update()]

    def draw(self, surface):
        for idx, ach in enumerate(self.achievements):
            ach.draw(surface, idx)

# --- UI BUTTON ---
class UIButton:
    def __init__(self, rect, text, onclick):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.hover = False
        self.font_size = 32

    def update(self, mouse_pos, mouse_down):
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.hover and mouse_down:
            self.onclick()

    def draw(self, surface):
        color = COLOR_BUTTON_HOVER if self.hover else COLOR_BUTTON
        draw_rounded_rect(surface, self.rect, color, 16)
        draw_text(surface, self.text, self.font_size, COLOR_FONT, self.rect.centerx, self.rect.centery, bold=True)

# --- GAME STATES ---
MENU, PLAYING, GAME_OVER, LOADING = 0, 1, 2, 3

# --- MAIN GAME CLASS ---
class SnakeGame:
    def __init__(self):
        # Setup pygame
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption('NEON SNAKE')
        self.clock = pygame.time.Clock()
        self.load_font()
        self.game_state = LOADING
        self.state_transition = 0
        self.transitioning_to = None
        self.particle_mgr = ParticleManager()
        self.achieve_mgr = AchievementManager()
        self.bg_anim_phase = 0.0
        self.snake = None
        self.foods = []
        self.score = 0
        self.level = 1
        self.high_score = load_high_score()
        self.buttons = []
        self.game_stats = {"length":0, "score":0}
        self.control_scheme = "Keyboard" # Mouse, WASD
        self.loading_timer = FPS*2
        self.start_time = 0
        self.food_spawn_timer = 0
        self.screen_shake = 0
        self.shake_offset = [0,0]
        self.show_menu()

    def load_font(self):
        self.font_name = None
        for f in ['Montserrat-Bold.ttf','Arial.ttf','Verdana.ttf',None]:
            try:
                font_t = pygame.font.Font(f, 30)
                self.font_name = f
                break
            except Exception:
                continue

    def show_menu(self):
        self.buttons = []
        playbtn = UIButton((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-40, 240,60), "PLAY", self.start_game)
        optbtn = UIButton((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+30, 240,60), "OPTIONS", self.show_options)
        self.buttons = [playbtn, optbtn]
        self.menu_selected = 0
        self.game_state = MENU
        self.state_transition = 1.0

    def start_game(self):
        # Initialize snake & food
        self.snake = Snake(COLOR_NEON)
        self.foods = [Food()]
        self.score = 0
        self.level = 1
        self.food_spawn_timer = 0
        self.screen_shake = 0
        self.start_time = pygame.time.get_ticks()
        self.game_state = PLAYING
        self.state_transition = 1.0
        self.game_stats = {"length":5, "score":0}
        self.achieve_mgr.unlock("Started new game!")

    def show_game_over(self):
        self.buttons = []
        restartbtn = UIButton((SCREEN_WIDTH//2-140, SCREEN_HEIGHT//2+30, 160,60), "RESTART", self.start_game)
        menubtn = UIButton((SCREEN_WIDTH//2+20, SCREEN_HEIGHT//2+30, 160,60), "MENU", self.show_menu)
        self.buttons = [restartbtn, menubtn]
        self.game_state = GAME_OVER
        self.state_transition = 1.0
        self.achieve_mgr.unlock("GAME OVER")

    def show_options(self):
        self.buttons = []
        kbbtn = UIButton((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2-40, 240,60), "Keyboard", lambda:self.set_control("Keyboard"))
        wasdbtn = UIButton((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+30, 240,60), "WASD", lambda:self.set_control("WASD"))
        mousebtn = UIButton((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+100, 240,60), "Mouse", lambda:self.set_control("Mouse"))
        self.buttons = [kbbtn, wasdbtn, mousebtn]
        self.menu_selected = 2
        self.game_state = MENU
        self.state_transition = 1.0

    def set_control(self, scheme):
        self.control_scheme = scheme
        self.achieve_mgr.unlock(f"{scheme} control activated")

    def transition_to(self, state):
        self.state_transition = 1.0
        self.transitioning_to = state

    def handle_events(self):
        mouse_pressed = False
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if self.game_state == PLAYING and self.snake and self.snake.alive:
                # Keyboard Controls
                if event.type == pygame.KEYDOWN:
                    if self.control_scheme in ("Keyboard","WASD"):
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.snake.set_direction((-1,0))
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.snake.set_direction((1,0))
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.snake.set_direction((0,-1))
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.snake.set_direction((0,1))
                # Mouse Controls
                if self.control_scheme=="Mouse" and event.type == pygame.MOUSEMOTION:
                    mx,my = mouse_pos
                    hx,hy = self.snake.segments[0]
                    wx,wy = hx*GRID_SIZE+GRID_SIZE//2, hy*GRID_SIZE+GRID_SIZE//2
                    dx = mx-wx
                    dy = my-wy
                    if abs(dx)>abs(dy):
                        self.snake.set_direction((1 if dx>0 else -1,0))
                    else:
                        self.snake.set_direction((0,1 if dy>0 else -1))
            if event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
                for btn in self.buttons:
                    btn.update(mouse_pos, True)
        # Button hover state update
        for btn in self.buttons:
            btn.update(mouse_pos, False)

    def quit(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # Game transitions
        if self.state_transition > 0:
            self.state_transition -= 0.05
        # Loading screen
        if self.game_state == LOADING:
            self.loading_timer -= 1
            self.bg_anim_phase += 0.025
            if self.loading_timer <= 0:
                self.show_menu()
        elif self.game_state == MENU:
            self.bg_anim_phase += 0.03
        # Main game update
        elif self.game_state == PLAYING:
            self.bg_anim_phase += 0.07
            if self.snake.alive:
                moved, ate_food = self.snake.update(self.foods)
                if ate_food:
                    # Spawn particles
                    fx,fy=self.snake.segments[0]
                    px,py = fx*GRID_SIZE+GRID_SIZE//2, fy*GRID_SIZE+GRID_SIZE//2
                    self.particle_mgr.spawn((px,py), 10, 3, [0,0], Food.COLORS[ate_food.type], 16, 7, glow=True)
                    self.score += 1
                    self.game_stats["score"] = self.score
                    self.game_stats["length"] = self.snake.length
                    if ate_food.type == "bonus":
                        self.score += 10
                    if self.score>self.high_score:
                        self.high_score = self.score
                        save_high_score(self.high_score)
                        self.achieve_mgr.unlock("High score achieved!")
                    if ate_food.type=="bonus":
                        self.achieve_mgr.unlock("Bonus food!")
                    if self.snake.length>=25:
                        self.achieve_mgr.unlock("Snake Master!")
                # Spawn food
                self.food_spawn_timer += 1
                if len(self.foods)<2 and self.food_spawn_timer > random.randint(40,80):
                    self.foods.append(Food())
                    self.food_spawn_timer = 0
                # Update food animations
                for food in self.foods:
                    food.update()
                collision = self.snake.check_collision()
                if collision is not None:
                    self.screen_shake = max(12, self.screen_shake)
                    self.particle_mgr.spawn((self.snake.segments[0][0]*GRID_SIZE+GRID_SIZE//2,self.snake.segments[0][1]*GRID_SIZE+GRID_SIZE//2), 30, 5, [0,0], COLOR_SNAKE_DEAD, 18, 11, glow=True)
                    self.show_game_over()
                # Progressive difficulty
                self.level = min(MAX_LEVEL, self.snake.level)
            else:
                pass # dead
            # Achievement update
            self.achieve_mgr.update()
            # Particle update
            self.particle_mgr.update()
            # Screen shake
            if self.screen_shake > 0:
                self.shake_offset[0] = random.randint(-self.screen_shake, self.screen_shake)
                self.shake_offset[1] = random.randint(-self.screen_shake, self.screen_shake)
                self.screen_shake -= 1
            else:
                self.shake_offset = [0,0]
        elif self.game_state == GAME_OVER:
            self.bg_anim_phase += 0.04
            self.achieve_mgr.update()
            self.particle_mgr.update()
            if self.screen_shake > 0:
                self.shake_offset[0] = random.randint(-self.screen_shake, self.screen_shake)
                self.shake_offset[1] = random.randint(-self.screen_shake, self.screen_shake)
                self.screen_shake -= 1
            else:
                self.shake_offset = [0,0]

    def draw(self):
        # --- Draw background with grid & subtle neon anim ---
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg.fill(COLOR_BG)
        grid_color = lerp_color(COLOR_BG, COLOR_GRID, 0.22 + math.sin(self.bg_anim_phase)*0.07)
        for gx in range(0,SCREEN_WIDTH,GRID_SIZE):
            pygame.draw.line(bg, grid_color, (gx,0), (gx,SCREEN_HEIGHT),1)
        for gy in range(0,SCREEN_HEIGHT,GRID_SIZE):
            pygame.draw.line(bg, grid_color, (0,gy), (SCREEN_WIDTH,gy),1)
        self.screen.blit(bg, (self.shake_offset[0], self.shake_offset[1]))
        # Animated background glow
        glow_anim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i, col in enumerate(COLOR_NEON):
            phase = self.bg_anim_phase + i*2
            pygame.draw.circle(glow_anim, (*col, 14), (SCREEN_WIDTH//2 + int(70*math.sin(phase+i)), SCREEN_HEIGHT//2 + int(80*math.cos(phase+i))), 300, 0)
        self.screen.blit(glow_anim, (0,0))
        # --- Game-specific drawing ---
        if self.game_state==LOADING:
            draw_text(self.screen, "NEON SNAKE", 60, COLOR_UI_ACCENT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-70, self.font_name, bold=True, shadow=True)
            draw_text(self.screen, "Loading...", 32, COLOR_FONT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+40, self.font_name, shadow=True)
        elif self.game_state==MENU:
            # Game title
            draw_text(self.screen, "NEON SNAKE", 64, COLOR_UI_ACCENT, SCREEN_WIDTH//2, 100, self.font_name, bold=True)
            for btn in self.buttons:
                btn.draw(self.screen)
            draw_text(self.screen, f"High Score: {self.high_score}", 26, COLOR_UI_ACCENT, SCREEN_WIDTH//2, 170, self.font_name)
            draw_text(self.screen, f"Controls: {self.control_scheme}", 24, COLOR_FONT, SCREEN_WIDTH//2, 220, self.font_name)
        elif self.game_state==PLAYING:
            # Draw food
            for food in self.foods:
                food.draw(self.screen)
            # Draw snake
            if self.snake:
                self.snake.draw(self.screen, self.particle_mgr)
            # Draw particles
            self.particle_mgr.draw(self.screen)
            # Draw HUD
            hud_rect = pygame.Rect(20, 20, 220, 70)
            draw_rounded_rect(self.screen, hud_rect, (30,40,65,190), 18)
            draw_text(self.screen, f"Score: {self.score}", 32, COLOR_FONT, hud_rect.x+15, hud_rect.y+18, self.font_name, center=False)
            draw_text(self.screen, f"Level: {self.level}", 22, COLOR_UI_ACCENT, hud_rect.x+15, hud_rect.y+52, self.font_name, center=False)
            draw_text(self.screen, f"High: {self.high_score}", 22, COLOR_UI_ACCENT, hud_rect.x+140, hud_rect.y+52, self.font_name, center=False)
            # Achievements
            self.achieve_mgr.draw(self.screen)
        elif self.game_state==GAME_OVER:
            self.particle_mgr.draw(self.screen)
            draw_text(self.screen, "GAME OVER", 56, COLOR_SNAKE_DEAD, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-70, self.font_name, bold=True)
            draw_text(self.screen, f"Score: {self.score}", 32, COLOR_FONT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-10, self.font_name, bold=True)
            draw_text(self.screen, f"Length: {self.snake.length}", 26, COLOR_UI_ACCENT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+28, self.font_name)
            draw_text(self.screen, f"High: {self.high_score}", 22, COLOR_UI_ACCENT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+55, self.font_name)
            # Animated stats (particles when game over)
            for btn in self.buttons:
                btn.draw(self.screen)
            self.achieve_mgr.draw(self.screen)
            # Screen shake effect overlays
        # --- Transition effect ---
        if self.state_transition>0:
            radius = int(lerp(0, SCREEN_WIDTH*1.4, self.state_transition))
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(fade_surf, (20,40,50,int(180*self.state_transition)), (SCREEN_WIDTH//2,SCREEN_HEIGHT//2), radius)
            self.screen.blit(fade_surf, (0,0))
        pygame.display.flip()

    def run(self):
        # Main loop
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

def main():
    try:
        game = SnakeGame()
        game.run()
    except Exception as ex:
        pygame.quit()
        print("Game crashed:", ex)

if __name__ == "__main__":
    main()