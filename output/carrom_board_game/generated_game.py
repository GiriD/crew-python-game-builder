import pygame
import sys
import math
import random
import logging

# Constants and color palette
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60
BOARD_SIZE = 720
BOARD_MARGIN = 40
POCKET_RADIUS = 34

COIN_RADIUS = 23
STRIKER_RADIUS = 27

STRIKER_MAX_POWER = 24.0
STRIKER_MIN_POWER = 6.0
STRIKER_POWER_STEP = 1.5

FRICTION = 0.992
ELASTICITY = 0.97
COIN_MIN_SPEED = 0.08

MAX_PLAYERS = 4
WHITE_COIN_COUNT = 9
BLACK_COIN_COUNT = 9
QUEEN_PRESENT = True

LOG_FILENAME = "carrom_game_log.txt"

# Professional Color Palette (see architecture doc)
COL_BG = (245, 241, 230)
COL_WOOD = (177, 118, 60)
COL_BORDER = (141, 85, 36)
COL_MARKING = (216, 146, 81)
COL_COIN_WHITE = (253, 252, 247)
COL_COIN_BLACK = (44, 44, 44)
COL_COIN_QUEEN = (211, 47, 47)
COL_STRIKER_BODY = (239, 239, 239)
COL_STRIKER_RIM = (38, 151, 243)
COL_UI_ACCENT = (38, 151, 243)
COL_BUTTON_BG = (104, 69, 27)
COL_TEXT = (34, 34, 34)
COL_TEXT_SECONDARY = (142, 142, 142)
COL_POSITIVE = (25, 182, 135)
COL_NEGATIVE = (231, 76, 60)
COL_PARTICLE_SPARKLE = (255, 206, 84)

# Logging setup
logging.basicConfig(filename=LOG_FILENAME, filemode="w", level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s]: %(message)s")

# State Machine pattern
class GameState:
    INIT, MENU, AIM, SHOOT, PHYSICS, TURN_END, GAME_OVER, SETTINGS, HOWTOPLAY = range(9)

    def __init__(self):
        self.current_state = GameState.MENU
    def change_state(self, new_state):
        logging.info(f"State changed from {self.current_state} to {new_state}")
        self.current_state = new_state
    def update(self, dt):
        pass

# Utility functions
def vec_length(vec):
    return math.hypot(vec[0], vec[1])

def vec_normalize(vec):
    l = vec_length(vec)
    if l == 0:
        return (0, 0)
    return (vec[0]/l, vec[1]/l)

def vec_scale(vec, scale):
    return (vec[0]*scale, vec[1]*scale)

def clamp(val, minval, maxval):
    return max(minval, min(val, maxval))

# Coin base class
class Coin(pygame.sprite.Sprite):
    def __init__(self, position, color, radius, coin_type="normal"):
        super().__init__()
        self.position = list(position)
        self.velocity = [0.0, 0.0]
        self.color = color
        self.radius = radius
        self.is_pocketed = False
        self.coin_type = coin_type
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(position[0]), int(position[1])))
    def update_position(self, dt):
        if self.is_pocketed:
            return
        self.position[0] += self.velocity[0]*dt
        self.position[1] += self.velocity[1]*dt
        self.rect.center = (int(self.position[0]), int(self.position[1]))
    def apply_friction(self):
        self.velocity[0] *= FRICTION
        self.velocity[1] *= FRICTION
        if vec_length(self.velocity) < COIN_MIN_SPEED:
            self.velocity = [0.0, 0.0]
    def set_velocity(self, vel):
        self.velocity = vel
    def draw(self, surface):
        if self.is_pocketed:
            return
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.radius)
        if self.coin_type == "queen":
            pygame.draw.circle(surface, COL_MARKING, (int(self.position[0]), int(self.position[1])), self.radius-6, 3)
            pygame.draw.circle(surface, (255,215,0), (int(self.position[0]), int(self.position[1])), 6)
        elif self.coin_type == "black":
            pygame.draw.circle(surface, (52,52,52), (int(self.position[0]), int(self.position[1])), self.radius-4, 2)
        elif self.coin_type == "white":
            pygame.draw.circle(surface, (232,230,221), (int(self.position[0]), int(self.position[1])), self.radius-5, 2)

# Striker subclass
class Striker(Coin):
    def __init__(self, position):
        super().__init__(position, COL_STRIKER_BODY, STRIKER_RADIUS, coin_type="striker")
        self.controlled_by_player = True
        self.angle = 0.0
        self.power = STRIKER_MIN_POWER
    def set_direction(self, power, angle):
        self.power = clamp(power, STRIKER_MIN_POWER, STRIKER_MAX_POWER)
        self.angle = angle
    def shoot(self):
        self.velocity = [math.cos(self.angle)*self.power, math.sin(self.angle)*self.power]
    def draw(self, surface, highlight=False):
        if self.is_pocketed:
            return
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.radius)
        pygame.draw.circle(surface, COL_STRIKER_RIM, (int(self.position[0]), int(self.position[1])), self.radius-4, 3)
        if highlight:
            pygame.draw.circle(surface, COL_STRIKER_RIM, (int(self.position[0]), int(self.position[1])), self.radius+5, 2)

# Pocket
class Pocket:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
    def check_collision(self, coin):
        if coin.is_pocketed:
            return False
        dist = vec_length((self.position[0]-coin.position[0], self.position[1]-coin.position[1]))
        return dist < (self.radius - coin.radius/2)

# Board
class Board:
    def __init__(self, cx, cy, size):
        self.cx = cx
        self.cy = cy
        self.size = size
        self.top = cy - size//2
        self.left = cx - size//2
        self.right = cx + size//2
        self.bottom = cy + size//2
        self.coins = pygame.sprite.Group()
        self.queen = None
        self.striker = None
        self.pockets = []
        self.boundaries = pygame.Rect(self.left, self.top, size, size)
        self.init_pockets()
    def init_pockets(self):
        self.pockets.clear()
        r = self.size//2 - POCKET_RADIUS - 1
        positions = [
            (self.cx-r, self.cy-r),
            (self.cx+r, self.cy-r),
            (self.cx+r, self.cy+r),
            (self.cx-r, self.cy+r)
        ]
        for pos in positions:
            self.pockets.append(Pocket(pos, POCKET_RADIUS))
    def reset_board(self, coin_objs, queen_obj, striker_obj):
        self.coins.empty()
        self.striker = striker_obj
        if queen_obj:
            self.queen = queen_obj
            self.coins.add(queen_obj)
        for coin in coin_objs:
            self.coins.add(coin)
    def draw(self, surface):
        pygame.draw.rect(surface, COL_WOOD, self.boundaries, border_radius=36)
        pygame.draw.rect(surface, COL_BORDER, self.boundaries, 11, border_radius=40)
        for pocket in self.pockets:
            pygame.draw.circle(surface, (0,0,0), (int(pocket.position[0]), int(pocket.position[1])), pocket.radius)
            pygame.draw.circle(surface, (255, 215, 0), (int(pocket.position[0]), int(pocket.position[1])), pocket.radius-5, 3)
        # Draw markings
        pygame.draw.circle(surface, COL_MARKING, (self.cx, self.cy), self.size//2-POCKET_RADIUS-15, 2)
        pygame.draw.circle(surface, COL_MARKING, (self.cx, self.cy), 62, 3)
        pygame.draw.circle(surface, (255,215,0), (self.cx, self.cy), 9)
        # Draw coins and striker
        for coin in self.coins:
            coin.draw(surface)
        if self.striker:
            self.striker.draw(surface, highlight=True)

# Physics
class PhysicsEngine:
    def __init__(self, board):
        self.board = board
    def update_coin_positions(self, dt):
        for coin in self.board.coins:
            coin.update_position(dt)
            coin.apply_friction()
            self.handle_boundaries(coin)
        if self.board.striker:
            self.board.striker.update_position(dt)
            self.board.striker.apply_friction()
            self.handle_boundaries(self.board.striker)
    def handle_boundaries(self, coin):
        if coin.is_pocketed:
            return
        x, y = coin.position
        r = coin.radius
        # Left wall
        if x - r < self.board.left:
            coin.position[0] = self.board.left + r
            coin.velocity[0] *= -ELASTICITY
            coin.velocity[1] *= ELASTICITY
            Renderer.play_sfx("coin_bounce_wall")
        # Right wall
        if x + r > self.board.right:
            coin.position[0] = self.board.right - r
            coin.velocity[0] *= -ELASTICITY
            coin.velocity[1] *= ELASTICITY
            Renderer.play_sfx("coin_bounce_wall")
        # Top wall
        if y - r < self.board.top:
            coin.position[1] = self.board.top + r
            coin.velocity[1] *= -ELASTICITY
            coin.velocity[0] *= ELASTICITY
            Renderer.play_sfx("coin_bounce_wall")
        # Bottom wall
        if y + r > self.board.bottom:
            coin.position[1] = self.board.bottom - r
            coin.velocity[1] *= -ELASTICITY
            coin.velocity[0] *= ELASTICITY
            Renderer.play_sfx("coin_bounce_wall")
    def resolve_collisions(self):
        coins = list(self.board.coins) + [self.board.striker]
        n = len(coins)
        for i in range(n):
            for j in range(i+1, n):
                c1, c2 = coins[i], coins[j]
                if c1.is_pocketed or c2.is_pocketed:
                    continue
                dx = c2.position[0]-c1.position[0]
                dy = c2.position[1]-c1.position[1]
                dist = math.hypot(dx, dy)
                min_dist = c1.radius + c2.radius
                if dist < min_dist and dist != 0:
                    nx, ny = dx/dist, dy/dist
                    rel_vel = ((c2.velocity[0]-c1.velocity[0])*nx +
                               (c2.velocity[1]-c1.velocity[1])*ny)
                    if rel_vel < 0:
                        imp = -2*rel_vel / (1 + 1)
                        c1.velocity[0] -= imp*nx
                        c1.velocity[1] -= imp*ny
                        c2.velocity[0] += imp*nx
                        c2.velocity[1] += imp*ny
                        # Separate the coins
                        overlap = min_dist - dist + 0.5
                        c1.position[0] -= nx*overlap/2
                        c1.position[1] -= ny*overlap/2
                        c2.position[0] += nx*overlap/2
                        c2.position[1] += ny*overlap/2
                        if c1.coin_type=="striker" or c2.coin_type=="striker":
                            Renderer.play_sfx("striker_hit_coin")
                        else:
                            Renderer.play_sfx("coin_hit_coin")
    def apply_friction(self):
        for coin in self.board.coins:
            coin.apply_friction()
        if self.board.striker:
            self.board.striker.apply_friction()
    def coins_are_moving(self):
        moving = False
        for coin in self.board.coins:
            if not coin.is_pocketed and (abs(coin.velocity[0]) > COIN_MIN_SPEED or abs(coin.velocity[1]) > COIN_MIN_SPEED):
                moving = True
                break
        s = self.board.striker
        if s and not s.is_pocketed and (abs(s.velocity[0]) > COIN_MIN_SPEED or abs(s.velocity[1]) > COIN_MIN_SPEED):
            moving = True
        return moving

# Player and score logic
class Player:
    def __init__(self, name, color, idx):
        self.name = name
        self.score = 0
        self.coins_pocketed = []
        self.has_covered_queen = False
        self.color = color
        self.idx = idx
        self.avatar_shape = idx%3 # 0:circle, 1:square, 2:triangle
    def add_coin(self, coin):
        self.coins_pocketed.append(coin)
    def get_coin_count(self, color_enum):
        return sum(1 for c in self.coins_pocketed if c.coin_type==color_enum)

# Turn management
class TurnManager:
    def __init__(self, num_players):
        self.current_player_index = 0
        self.turn_order = list(range(num_players))
        self.num_players = num_players
    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % self.num_players
    def get_current_player(self, players):
        return players[self.current_player_index]
    def reset(self):
        self.current_player_index = 0

# Scorer and queen rules
class Scorer:
    def __init__(self):
        self.queen_pocketed = False
        self.queen_covered = None
        self.pending_queen_cover = None
    def update_score(self, player, coins):
        for coin in coins:
            if coin.coin_type == "white":
                player.score += 1
            elif coin.coin_type == "black":
                player.score += 1
            elif coin.coin_type == "queen":
                # Only add queen when covered
                self.queen_pocketed = True
                self.pending_queen_cover = player
    def queen_capture_rule(self, player, covering_coin):
        success = False
        if self.queen_pocketed and self.pending_queen_cover == player and covering_coin:
            player.score += 3
            player.has_covered_queen = True
            self.queen_covered = player
            self.queen_pocketed = False
            self.pending_queen_cover = None
            success = True
        elif self.queen_pocketed and self.pending_queen_cover == player:
            # Queen not covered
            self.queen_pocketed = False
            self.pending_queen_cover = None
            success = False
        return success

# Input handling
class InputHandler:
    def __init__(self, board):
        self.board = board
        self.aiming = False
        self.aim_angle = 0.0
        self.power = STRIKER_MIN_POWER
        self.last_mouse_pos = None
    def handle_mouse_event(self, event):
        striker = self.board.striker
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self._on_striker(mx,my):
                self.aiming = True
                self.last_mouse_pos = (mx, my)
                Renderer.play_sfx("striker_aim_start")
        elif event.type == pygame.MOUSEMOTION and self.aiming:
            mx, my = event.pos
            cx, cy = striker.position
            dx, dy = mx-cx, my-cy
            self.aim_angle = math.atan2(dy, dx)
            drag_len = vec_length((dx,dy))
            self.power = clamp(drag_len/7.5, STRIKER_MIN_POWER, STRIKER_MAX_POWER)
        elif event.type == pygame.MOUSEBUTTONUP and self.aiming:
            self.aiming = False
            Renderer.play_sfx("striker_shoot")
            striker.set_direction(self.power, self.aim_angle)
            striker.shoot()
            self.power = STRIKER_MIN_POWER
            self.last_mouse_pos = None
    def handle_keyboard_event(self, event):
        pass # Space for helper keyboard controls
    def _on_striker(self, mx, my):
        s = self.board.striker
        return vec_length((mx-s.position[0], my-s.position[1])) <= (s.radius+8)

# Renderer (Singleton for game visuals and audio)
class Renderer:
    _instance = None
    @staticmethod
    def get_instance():
        if Renderer._instance is None:
            Renderer._instance = Renderer()
        return Renderer._instance
    def __init__(self):
        self.screen = None
        self.fonts = {}
        self.load_fonts()
        self.sfx = {}
        self.load_sfx()
        self.menu_particles = []
    def setup_screen(self, screen):
        self.screen = screen
    def load_fonts(self):
        try:
            self.fonts["title"] = pygame.font.SysFont("Montserrat,Arial", 46, bold=True)
            self.fonts["heading"] = pygame.font.SysFont("Montserrat,Arial", 29, bold=True)
            self.fonts["label"] = pygame.font.SysFont("Montserrat,Arial", 20)
            self.fonts["score"] = pygame.font.SysFont("RobotoMono,Consolas", 37, bold=True)
            self.fonts["body"] = pygame.font.SysFont("Montserrat,Arial", 17)
            self.fonts["small"] = pygame.font.SysFont("Montserrat,Arial", 14)
        except Exception as e:
            logging.warning(f"Font load failed: {e}")
            self.fonts["title"] = pygame.font.SysFont("Arial", 44, bold=True)
            self.fonts["score"] = pygame.font.SysFont("Arial", 37, bold=True)
            self.fonts["label"] = pygame.font.SysFont("Arial", 18)
            self.fonts["body"] = pygame.font.SysFont("Arial", 15)
            self.fonts["small"] = pygame.font.SysFont("Arial", 12)
    def load_sfx(self):
        # Map event names to SFX files (must be under assets/audio/sfx/)
        sfx_files = {
            "striker_aim_start": "assets/audio/sfx/striker_aim_start1.ogg",
            "striker_shoot": "assets/audio/sfx/striker_shoot1.ogg",
            "striker_hit_coin": "assets/audio/sfx/striker_hit_coin1.ogg",
            "coin_hit_coin": "assets/audio/sfx/coin_hit1.ogg",
            "coin_bounce_wall": "assets/audio/sfx/coin_bounce_wall.ogg",
            "coin_pocketed": "assets/audio/sfx/coin_pocketed.ogg",
            "queen_pocketed": "assets/audio/sfx/queen_pocketed.ogg",
            "turn_end": "assets/audio/sfx/turn_end.ogg",
            "score_update": "assets/audio/sfx/score_updated.ogg",
            "menu_click": "assets/audio/sfx/menu_click1.ogg",
            "game_start": "assets/audio/sfx/game_start.ogg",
            "game_over": "assets/audio/sfx/victory_theme.ogg",
            "invalid_action": "assets/audio/sfx/invalid_action.ogg",
            "queen_cover_success": "assets/audio/sfx/queen_cover_success.ogg",
            "queen_cover_fail": "assets/audio/sfx/queen_cover_fail.ogg"
        }
        for name, path in sfx_files.items():
            try:
                self.sfx[name] = pygame.mixer.Sound(path)
            except Exception:
                self.sfx[name] = None # File missing
    @staticmethod
    def play_sfx(name, volume=1.0):
        self = Renderer.get_instance()
        sfx_obj = self.sfx.get(name, None)
        if sfx_obj:
            try:
                sfx_obj.set_volume(volume)
                sfx_obj.play()
            except Exception as e:
                logging.info(f"SFX play failed: {name} - {e}")
    def draw_board(self, board):
        board.draw(self.screen)
    def draw_ui(self, players, turn_mgr, scorer, state, coins_left):
        surf = self.screen
        cx,cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        # Turn indicator
        p = turn_mgr.get_current_player(players)
        turn_surf = self.fonts["label"].render(
            f"Turn: {p.name}", True, COL_UI_ACCENT)
        pygame.draw.rect(surf, COL_BUTTON_BG,
                         (cx-110, 66, 220, 46), border_radius=13)
        surf.blit(turn_surf, (cx-102, 76))
        # Scoreboard
        for idx, player in enumerate(players):
            px = cx + (idx-1.5)*220
            py = 18
            pygame.draw.rect(surf,
                COL_BORDER if turn_mgr.current_player_index==idx else COL_WOOD,
                (px-88, py,176,56), border_radius=16)
            avatar_col = player.color
            apx = px-71
            apy = py+33
            if player.avatar_shape==0:
                pygame.draw.circle(surf, avatar_col, (apx,apy), 19)
            elif player.avatar_shape==1:
                pygame.draw.rect(surf, avatar_col, (apx-14,apy-18,28,28), border_radius=8)
            else:
                pygame.draw.polygon(surf, avatar_col,
                    [(apx,apy-18),(apx-18,apy+18),(apx+18,apy+18)])
            name_surf = self.fonts["label"].render(player.name, True, COL_TEXT)
            surf.blit(name_surf, (px-34, py+9))
            score_surf = self.fonts["score"].render(str(player.score), True, COL_POSITIVE if player.score>0 else COL_NEGATIVE)
            surf.blit(score_surf, (px+31, py+7))
        # Queen indicator
        qstat = "Queen Pocketed" if scorer.queen_pocketed else \
            f"Queen Covered by {scorer.queen_covered.name}" if scorer.queen_covered else "Queen On Board"
        qs = self.fonts["body"].render(qstat, True, COL_COIN_QUEEN if scorer.queen_pocketed else COL_TEXT_SECONDARY)
        pygame.draw.rect(surf, COL_WOOD, (cx-105, SCREEN_HEIGHT-66,210,38), border_radius=11)
        surf.blit(qs, (cx-93, SCREEN_HEIGHT-61))
        # Remaining coins
        cs = self.fonts["body"].render(f"Coins left: {coins_left}", True, COL_MARKING)
        surf.blit(cs, (26, SCREEN_HEIGHT-20))
    def draw_aim_indicator(self, input_hdl):
        if input_hdl.aiming and self.screen:
            striker = input_hdl.board.striker
            mx,my = pygame.mouse.get_pos()
            cx,cy = striker.position
            pygame.draw.line(self.screen, COL_UI_ACCENT, (cx,cy), (mx,my), 7)
            # Circle showing power
            power = input_hdl.power
            pcol = COL_UI_ACCENT if power>STRIKER_MIN_POWER+6 else COL_MARKING
            pygame.draw.circle(self.screen, pcol, (cx,cy), int(20+power*0.8), 2)
            # Semi-transparent arrow
            endx = cx + math.cos(input_hdl.aim_angle)*power*3.2
            endy = cy + math.sin(input_hdl.aim_angle)*power*3.2
            pygame.draw.line(self.screen, (38,151,243,128), (cx,cy), (endx,endy), 10)
    def draw_menu(self, state, menu_selected): # Main menu with buttons and overlays
        surf = self.screen
        pygame.draw.rect(surf, COL_BG, (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
        ttext = self.fonts["title"].render("Carrom Board Game", True, COL_TEXT)
        surf.blit(ttext, (SCREEN_WIDTH//2 - ttext.get_width()//2, 100))
        buttons = [("PLAY",GameState.INIT),("HOW TO PLAY",GameState.HOWTOPLAY),
                   ("SETTINGS",GameState.SETTINGS),("QUIT",None)]
        basey = 230
        for i, (label, act) in enumerate(buttons):
            bx = SCREEN_WIDTH//2 - 130
            by = basey + i*74
            pygame.draw.rect(surf, COL_BUTTON_BG,
                (bx,by,260,54), border_radius=14)
            if menu_selected==i:
                pygame.draw.rect(surf, COL_UI_ACCENT, (bx-7,by-5,274,63),2, border_radius=20)
            label_surf = self.fonts["heading"].render(label, True, COL_TEXT)
            surf.blit(label_surf, (SCREEN_WIDTH//2-label_surf.get_width()//2, by+16))
        credits = self.fonts["small"].render("© 2024, v1.0", True, COL_TEXT_SECONDARY)
        surf.blit(credits, (28, SCREEN_HEIGHT-38))
    def draw_howtoplay(self):
        surf = self.screen
        info_lines = [
            "• Use your mouse to aim and shoot the striker. Hold and drag for power, release to shoot.",
            "• Pocket white or black coins to score. Queen (red) must be covered immediately after pocketing.",
            "• The game supports 2-4 players. On your turn, pocket coins to gain points.",
            "• First to pocket all assigned color coins and cover the queen wins!",
            "• Physics-based collisions, realistic board. Menu: ESC to return."
        ]
        basey = 220
        for i, txt in enumerate(info_lines):
            surf.blit(self.fonts["body"].render(txt, True, COL_TEXT), (80, basey+37*i))
    def draw_settings(self, settings_vols, selected_setting):
        surf = self.screen
        pygame.draw.rect(surf, COL_BG, (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
        ttext = self.fonts["title"].render("Settings", True, COL_TEXT)
        surf.blit(ttext, (SCREEN_WIDTH//2 - ttext.get_width()//2, 90))
        labels = ["SFX Volume","Music Volume","Mute All"]
        y_base = 210
        for i, label in enumerate(labels):
            ly = y_base + i*74
            pygame.draw.rect(surf, COL_BUTTON_BG, (340,ly,340,52), border_radius=11)
            if selected_setting==i:
                pygame.draw.rect(surf, COL_UI_ACCENT, (338,ly-4,344,58),2, border_radius=13)
            label_surf = self.fonts["heading"].render(f"{label}: {settings_vols[i]}", True, COL_TEXT)
            surf.blit(label_surf, (355,ly+12))
        hint = self.fonts["small"].render("ESC to return", True, COL_TEXT_SECONDARY)
        surf.blit(hint, (SCREEN_WIDTH//2-66, SCREEN_HEIGHT-60))
    def draw_game_over(self, winner, players, fireworks_state, play_again_sel):
        surf = self.screen
        # Dimmed bg
        overlay = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((240,240,245,197))
        surf.blit(overlay, (0,0))
        winner_card_x = SCREEN_WIDTH//2-170
        winner_card_y = 116
        pygame.draw.rect(surf, COL_POSITIVE, (winner_card_x, winner_card_y,340,138), border_radius=22)
        t = self.fonts["title"].render(f"Winner: {winner.name}", True, COL_BG)
        surf.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, winner_card_y+23))
        trophy = pygame.Surface((65,65), pygame.SRCALPHA)
        pygame.draw.circle(trophy, (255,215,0), (32,32), 32)
        pygame.draw.rect(trophy, (186,163,48), (10,38,44,20), border_radius=8)
        surf.blit(trophy, (SCREEN_WIDTH//2-34, winner_card_y+58))
        # Fireworks
        if fireworks_state:
            for _ in range(7):
                fx = random.randint(130,870)
                fy = random.randint(78,188)
                pygame.draw.circle(surf, COL_PARTICLE_SPARKLE, (fx,fy), random.randint(8,14))
        # Score table
        score_y = winner_card_y + 162
        for idx, player in enumerate(sorted(players, key=lambda p: -p.score)):
            px = SCREEN_WIDTH//2-88
            py = score_y+idx*44
            pygame.draw.rect(surf, COL_WOOD, (px,py,176,36), border_radius=10)
            title = self.fonts["label"].render(player.name, True, player.color)
            surf.blit(title, (px+11, py+6))
            sc = self.fonts["score"].render(str(player.score), True, COL_POSITIVE if player.score>0 else COL_NEGATIVE)
            surf.blit(sc, (px+98, py+3))
        # Buttons
        buttons = ["PLAY AGAIN","MAIN MENU","SHARE"]
        basey = score_y+len(players)*44+38
        bx = SCREEN_WIDTH//2-162
        for i, label in enumerate(buttons):
            by = basey + i*57
            pygame.draw.rect(surf, COL_BUTTON_BG, (bx,by,325,41), border_radius=13)
            if play_again_sel==i:
                pygame.draw.rect(surf, COL_UI_ACCENT, (bx-3,by-3,332,47),2, border_radius=17)
            label_surf = self.fonts["label"].render(label, True, COL_TEXT)
            surf.blit(label_surf, (bx+93, by+11))
    def draw_particles(self, group):
        for particle in list(group):
            pygame.draw.circle(self.screen, particle.color, particle.pos, particle.radius)
            particle.radius -= 0.29
            if particle.radius <= 0:
                group.remove(particle)

# Simple particle system
class Particle:
    def __init__(self, pos, color, radius):
        self.pos = pos
        self.color = color
        self.radius = radius

# Game class (main stateful object)
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=640)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Carrom Board Game")
        self.clock = pygame.time.Clock()
        Renderer.get_instance().setup_screen(self.screen)
        self.fonts = Renderer.get_instance().fonts
        self.state = GameState()
        self.players = []
        self.turn_manager = None
        self.scorer = Scorer()
        self.board = None
        self.physics_engine = None
        self.input_handler = None
        self.current_menu_sel = 0
        self.settings_vols = [1.0, 0.6, False]
        self.selected_setting = 0
        self.winner = None
        self.fireworks_state = False
        self.play_again_sel = 0
        self.particle_group = []
        self.background_music_playing = False
        self.menu_particles = []
        self.error_message = ""
    def setup_game(self, num_players=2):
        # Set up board, coins, striker, players (center coin positions standard)
        cx,cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        bsize = BOARD_SIZE
        board = Board(cx, cy, bsize)
        # Arrange coins in 2 rings plus one queen
        coins = []
        colors = []
        for i in range(WHITE_COIN_COUNT):
            colors.append("white")
        for i in range(BLACK_COIN_COUNT):
            colors.append("black")
        angle = 0.0
        N = len(colors)
        ring_radii = [55, 109]
        ring_angles = [math.pi*2*(i/N) for i in range(N)]
        positions = []
        idx, n_ring = 0, len(ring_radii)
        for rr in ring_radii:
            for j in range(N//n_ring):
                a = ring_angles[idx]
                px = cx + math.cos(a)*rr
                py = cy + math.sin(a)*rr
                positions.append((px,py))
                idx+=1
        coin_objs = []
        for i, pos in enumerate(positions):
            ctype = colors[i] if i<len(colors) else "white"
            coin = Coin(pos, COL_COIN_WHITE if ctype=="white" else COL_COIN_BLACK, COIN_RADIUS, coin_type=ctype)
            coin_objs.append(coin)
        queen_obj = None
        if QUEEN_PRESENT:
            queen_obj = Coin((cx,cy), COL_COIN_QUEEN, COIN_RADIUS, coin_type="queen")
        striker_pos = (cx, cy + BOARD_SIZE//2 - 86)
        striker_obj = Striker(striker_pos)
        board.reset_board(coin_objs, queen_obj, striker_obj)
        self.board = board
        self.physics_engine = PhysicsEngine(board)
        self.input_handler = InputHandler(board)
        self.scorer = Scorer()
        self.particle_group = []
        self.winner = None
        self.fireworks_state = False
        self.play_again_sel = 0
    def setup_players(self, num_players=2):
        palette = [COL_UI_ACCENT, COL_POSITIVE, COL_COIN_QUEEN, COL_MARKING]
        self.players = []
        names = ["Blue","Green","Red","Gold"]
        for idx in range(num_players):
            p = Player(names[idx%len(names)],
                       palette[idx%len(palette)], idx)
            self.players.append(p)
        self.turn_manager = TurnManager(num_players)
    def run(self):
        running = True
        self.setup_game(num_players=2)
        self.setup_players(num_players=2)
        Renderer.play_sfx("game_start")
        try:
            while running:
                dt = self.clock.tick(FPS)/20.0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif self.state.current_state == GameState.MENU:
                        self.menu_handle_event(event)
                    elif self.state.current_state == GameState.SETTINGS:
                        self.settings_handle_event(event)
                    elif self.state.current_state == GameState.HOWTOPLAY:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.state.change_state(GameState.MENU)
                    elif self.state.current_state == GameState.INIT:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.state.change_state(GameState.MENU)
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            self.state.change_state(GameState.AIM)
                    elif self.state.current_state == GameState.GAME_OVER:
                        self.game_over_handle_event(event)
                    elif self.state.current_state == GameState.AIM:
                        self.input_handler.handle_mouse_event(event)
                        self.input_handler.handle_keyboard_event(event)
                self.update(dt)
                self.render()
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            pygame.quit()
            sys.exit()
    def update(self, dt):
        # Main state update and transitions
        if self.state.current_state in [GameState.MENU, GameState.SETTINGS, GameState.HOWTOPLAY]:
            return
        if self.state.current_state == GameState.INIT:
            self.setup_game(num_players=len(self.players))
            self.turn_manager.reset()
            self.state.change_state(GameState.AIM)
            self.background_music("assets/audio/music/gameplay_loop.ogg")
            return
        if self.state.current_state == GameState.AIM:
            pass # wait for input
            if not self.board.striker.velocity == [0.0,0.0]:
                self.state.change_state(GameState.SHOOT)
        elif self.state.current_state == GameState.SHOOT:
            self.physics_engine.update_coin_positions(dt)
            self.physics_engine.resolve_collisions()
            if not self.physics_engine.coins_are_moving():
                self.state.change_state(GameState.PHYSICS)
        elif self.state.current_state == GameState.PHYSICS:
            self.check_pockets_and_scoring()
            self.state.change_state(GameState.TURN_END)
        elif self.state.current_state == GameState.TURN_END:
            self.turn_end_flow()
            if self.check_game_over():
                Renderer.play_sfx("game_over")
                self.background_music("assets/audio/music/victory_theme.ogg")
                self.state.change_state(GameState.GAME_OVER)
                return
            self.turn_manager.next_turn()
            self.prepare_next_turn()
            self.state.change_state(GameState.AIM)
        elif self.state.current_state == GameState.GAME_OVER:
            self.fireworks_state = random.random() < 0.7
    def render(self):
        surf = self.screen
        surf.fill(COL_BG)
        if self.state.current_state == GameState.MENU:
            Renderer.get_instance().draw_menu(self.state.current_state, self.current_menu_sel)
        elif self.state.current_state == GameState.SETTINGS:
            Renderer.get_instance().draw_settings(self.settings_vols, self.selected_setting)
        elif self.state.current_state == GameState.HOWTOPLAY:
            Renderer.get_instance().draw_howtoplay()
        elif self.state.current_state == GameState.GAME_OVER:
            Renderer.get_instance().draw_game_over(self.winner, self.players, self.fireworks_state, self.play_again_sel)
        else:
            Renderer.get_instance().draw_board(self.board)
            Renderer.get_instance().draw_ui(self.players, self.turn_manager,
                self.scorer, self.state, self.get_coins_left())
            Renderer.get_instance().draw_particles(self.particle_group)
            Renderer.get_instance().draw_aim_indicator(self.input_handler)
        pygame.display.flip()
    def menu_handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.current_menu_sel = (self.current_menu_sel+1)%4
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_UP:
                self.current_menu_sel = (self.current_menu_sel-1)%4
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_RETURN:
                Renderer.play_sfx("menu_click")
                if self.current_menu_sel==0:
                    self.state.change_state(GameState.INIT)
                elif self.current_menu_sel==1:
                    self.state.change_state(GameState.HOWTOPLAY)
                elif self.current_menu_sel==2:
                    self.state.change_state(GameState.SETTINGS)
                elif self.current_menu_sel==3:
                    pygame.quit()
                    sys.exit()
    def settings_handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_setting = (self.selected_setting+1)%3
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_UP:
                self.selected_setting = (self.selected_setting-1)%3
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_RIGHT:
                self.settings_vols[self.selected_setting] += 0.1
                self.settings_vols[self.selected_setting] = clamp(self.settings_vols[self.selected_setting],0,1)
                Renderer.play_sfx("menu_click", volume=self.settings_vols[0] if self.selected_setting==0 else 1.0)
            elif event.key == pygame.K_LEFT:
                self.settings_vols[self.selected_setting] -= 0.1
                self.settings_vols[self.selected_setting] = clamp(self.settings_vols[self.selected_setting],0,1)
                Renderer.play_sfx("menu_click", volume=self.settings_vols[0] if self.selected_setting==0 else 1.0)
            elif event.key == pygame.K_ESCAPE:
                self.state.change_state(GameState.MENU)
    def game_over_handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.play_again_sel = (self.play_again_sel+1)%3
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_UP:
                self.play_again_sel = (self.play_again_sel-1)%3
                Renderer.play_sfx("menu_click")
            elif event.key == pygame.K_RETURN:
                if self.play_again_sel==0:
                    self.state.change_state(GameState.INIT)
                    self.background_music("assets/audio/music/gameplay_loop.ogg")
                elif self.play_again_sel==1:
                    self.state.change_state(GameState.MENU)
                    self.background_music("assets/audio/music/main_menu.ogg")
                elif self.play_again_sel==2:
                    Renderer.play_sfx("menu_click") # Place for future share implementation
    def check_pockets_and_scoring(self):
        pocketed_this_turn = []
        covering_coin = None
        queen_pocketed = None
        # Check coins for pockets
        for coin in list(self.board.coins):
            if coin.is_pocketed:
                continue
            for pocket in self.board.pockets:
                if pocket.check_collision(coin):
                    coin.is_pocketed = True
                    self.particle_group.append(Particle(pocket.position, COL_PARTICLE_SPARKLE if coin.coin_type!="queen" else COL_COIN_QUEEN, random.randint(17,22)))
                    Renderer.play_sfx("queen_pocketed" if coin.coin_type=="queen" else "coin_pocketed")
                    pocketed_this_turn.append(coin)
                    if coin.coin_type=="queen":
                        queen_pocketed = coin
                    else:
                        covering_coin = coin
                    self.board.coins.remove(coin)
        # Striker pocketing disables shooting for next turn
        s = self.board.striker
        for pocket in self.board.pockets:
            if s and not s.is_pocketed and pocket.check_collision(s):
                s.is_pocketed = True
                Renderer.play_sfx("coin_pocketed")
                self.board.striker = Striker((SCREEN_WIDTH//2, SCREEN_HEIGHT//2+BOARD_SIZE//2-86))
        # Scorer update
        current_player = self.turn_manager.get_current_player(self.players)
        self.scorer.update_score(current_player, pocketed_this_turn)
        if queen_pocketed and covering_coin and covering_coin.coin_type in ["white","black"]:
            if self.scorer.queen_capture_rule(current_player, covering_coin):
                Renderer.play_sfx("queen_cover_success")
            else:
                Renderer.play_sfx("queen_cover_fail")
    def turn_end_flow(self):
        # Any end-of-turn checks, reset striker
        current_player = self.turn_manager.get_current_player(self.players)
        Renderer.play_sfx("turn_end")
        self.board.striker.position = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2+BOARD_SIZE//2-86)
        self.board.striker.velocity = [0.0, 0.0]
        self.input_handler.power = STRIKER_MIN_POWER
        self.input_handler.aim_angle = 0.0
        self.input_handler.aiming = False
    def prepare_next_turn(self):
        self.board.striker = Striker((SCREEN_WIDTH//2, SCREEN_HEIGHT//2+BOARD_SIZE//2-86))
    def check_game_over(self):
        # Finished when all coins and queen pocketed
        coins_left = self.get_coins_left()
        if coins_left==0:
            winner = max(self.players, key=lambda p:p.score)
            self.winner = winner
            return True
        return False
    def get_coins_left(self):
        return sum(1 for c in self.board.coins if not c.is_pocketed and c.coin_type in ["white","black","queen"])
    def background_music(self, path="assets/audio/music/main_menu.ogg"):
        if self.background_music_playing:
            try:
                pygame.mixer.music.fadeout(500)
            except:
                pass
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.settings_vols[1])
            pygame.mixer.music.play(-1)
            self.background_music_playing = True
        except Exception:
            self.background_music_playing = False

def main():
    game = Game()
    try:
        game.run()
    except Exception as err:
        logging.error(f"Game crashed: {err}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()