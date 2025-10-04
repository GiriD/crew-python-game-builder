import pygame
import sys
import math
import random

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
STONE_WIDTH = 40
STONE_HEIGHT = 12
STONE_GAP = 3
NUM_STONES = 7
BALL_RADIUS = 16
PLAYER_RADIUS = 28
PLAYER_SPEED = 4
BALL_THROWS = 1  # Number of throws per turn
STACK_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)
STACK_REBUILD_TIME = 10  # Seconds to rebuild stack
TEAM_ONE_COLOR = (249, 213, 101)  # Traditional yellow clothing
TEAM_TWO_COLOR = (79, 192, 223)   # Traditional blue clothing
BG_COLOR = (215, 215, 175)
UI_COLOR = (35, 35, 35)
FONT_NAME = 'comicsansms'

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(FONT_NAME, 32)
small_font = pygame.font.SysFont(FONT_NAME, 22)

def clamp(x, mini, maxi):
    return max(mini, min(x, maxi))

class Stone(pygame.sprite.Sprite):
    """Each stone in the stack"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((STONE_WIDTH, STONE_HEIGHT))
        self.image.fill((128, 99, 63))
        edge_light = pygame.Surface((STONE_WIDTH, STONE_HEIGHT))
        edge_light.set_colorkey((0, 0, 0))
        pygame.draw.rect(edge_light, (180, 148, 97), (0, 0, STONE_WIDTH, 4))
        self.image.blit(edge_light, (0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.active = True  # Is stone visible in stack
        self.vx = 0
        self.vy = 0
        self.gravity = 0.7
        self.angle = 0

    def update(self):
        if not self.active:
            # If hit, apply physics
            self.vy += self.gravity
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)
            self.angle += self.vx * 0.8
            # Out of screen removes stone
            if self.rect.y > SCREEN_HEIGHT:
                self.kill()

    def draw(self, surface):
        if self.active:
            rotated = pygame.transform.rotate(self.image, self.angle)
            surface.blit(rotated, rotated.get_rect(center=self.rect.center))
        else:
            rotated = pygame.transform.rotate(self.image, self.angle)
            surface.blit(rotated, rotated.get_rect(center=self.rect.center))

class Ball(pygame.sprite.Sprite):
    """Game Ball"""
    def __init__(self, x, y, team_color):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS
        self.active = False
        self.throwing = False
        self.thrown_by = None
        self.color = (220, 80, 80)
        self.team_color = team_color

    def throw(self, angle, power):
        # Throw with given angle and power
        rad = math.radians(angle)
        self.vx = math.cos(rad) * power
        self.vy = math.sin(rad) * power
        self.active = True
        self.throwing = True

    def update(self):
        if self.active:
            self.vy += 0.48  # Gravity
            self.x += self.vx
            self.y += self.vy
            # Bounce off floor
            if self.y + self.radius > SCREEN_HEIGHT:
                self.vy = -abs(self.vy) * 0.58
                self.y = SCREEN_HEIGHT - self.radius
                # Slow down
                self.vx *= 0.72
                if abs(self.vy) < 1 and abs(self.vx) < 1:
                    self.active = False
            if self.x < 0 or self.x > SCREEN_WIDTH:
                self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.team_color, (int(self.x), int(self.y)), self.radius - 2, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Player(pygame.sprite.Sprite):
    """A player (either rebuilding or throwing)"""
    def __init__(self, x, y, team, player_id, is_ai=False):
        super().__init__()
        self.x = x
        self.y = y
        self.team = team
        self.player_id = player_id
        self.radius = PLAYER_RADIUS
        self.color = TEAM_ONE_COLOR if team == 1 else TEAM_TWO_COLOR
        self.is_ai = is_ai
        self.alive = True
        self.target_stack_idx = 0
        self.rebuilding = False
        self.speed = PLAYER_SPEED
        self.hit = False
        self.throw_angle = 0

    def move(self, dx, dy):
        if not self.alive:
            return
        self.x = clamp(self.x + dx * self.speed, self.radius, SCREEN_WIDTH - self.radius)
        self.y = clamp(self.y + dy * self.speed, self.radius, SCREEN_HEIGHT - self.radius)

    def update(self, ball, stones, stack_status):
        if not self.alive:
            self.y += 2  # Drift down as knocked out
            return
        if self.is_ai:
            self.ai_action(ball, stones, stack_status)

    def ai_action(self, ball, stones, stack_status):
        # AI movement for team 2 (throwers): Move to aim and throw ball, intercept rebuilders
        if self.team == 2:
            if ball and not ball.active:
                # Aim for nearest re-builder
                target = None
                min_dist = 99999
                for p in stack_status['players']:
                    if p.team == 1 and p.alive and not p.hit:
                        d = math.hypot(p.x - self.x, p.y - self.y)
                        if d < min_dist:
                            min_dist = d
                            target = p
                if target and min_dist < 550:
                    dx = clamp(target.x - self.x, -self.speed, self.speed)
                    dy = clamp(target.y - self.y, -self.speed, self.speed)
                    self.move(dx//self.speed, dy//self.speed)
            # try throw
            if ball and not ball.active and random.random() < 0.03:
                try:
                    throw_angle = self.compute_throw_angle(stack_status['players'])
                    ball.x = self.x
                    ball.y = self.y
                    ball.team_color = self.color
                    ball.throw(throw_angle, random.randint(13, 18))
                    ball.thrown_by = self
                except Exception:
                    pass
        # AI for team 1 (stack rebuilders): Move to stack and rebuild
        elif self.team == 1 and self.rebuilding and not self.hit:
            stack_x, stack_y = STACK_CENTER
            dx = clamp(stack_x - self.x, -self.speed, self.speed)
            dy = clamp(stack_y - self.y, -self.speed, self.speed)
            self.move(dx//self.speed, dy//self.speed)

    def compute_throw_angle(self, players):
        # Compute the angle to nearest stack builder
        target = None
        min_dist = 99999
        for p in players:
            if p.team == 1 and p.alive and not p.hit:
                d = math.hypot(p.x - self.x, p.y - self.y)
                if d < min_dist:
                    min_dist = d
                    target = p
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            angle = math.degrees(math.atan2(dy, dx))
            return angle
        return random.randint(60, 110)

    def draw(self, surface):
        if not self.alive:
            pygame.draw.circle(surface, (70, 70, 70), (int(self.x), int(self.y)), self.radius)
            return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius-5, 2)
        # Face for fun
        mouth_y = int(self.y + self.radius//3)
        mouth_x = int(self.x)
        pygame.draw.arc(surface, UI_COLOR, (mouth_x-8, mouth_y, 16, 10), math.pi*0.12, math.pi*0.92, 2)
        pygame.draw.circle(surface, UI_COLOR, (int(self.x-7), int(self.y-8)), 2)
        pygame.draw.circle(surface, UI_COLOR, (int(self.x+7), int(self.y-8)), 2)
        # Rebuilding hand
        if self.rebuilding and self.alive:
            pygame.draw.line(surface, (145, 91, 64), (self.x, self.y), (self.x+13, self.y-11), 4)
        if self.hit:
            pygame.draw.line(surface, (200, 0, 0), (self.x-10, self.y+20), (self.x+10, self.y+20), 3)

class Button:
    """Simple clickable button"""
    def __init__(self, rect, text, color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font
        self.hovered = False

    def draw(self, surface):
        fill = self.color if not self.hovered else tuple(clamp(c+40, 0, 255) for c in self.color)
        pygame.draw.rect(surface, fill, self.rect, border_radius=7)
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2, self.rect.centery - text_surf.get_height()//2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    """Main Game class"""
    def __init__(self, multiplayer=False):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pithu (Seven Stones) - Traditional Indian Game")
        self.clock = pygame.time.Clock()
        self.multiplayer = multiplayer
        self.running = True
        self.state = 'menu'  # menu, playing, result
        self.stones = pygame.sprite.Group()
        self.ball = Ball(0, 0, TEAM_TWO_COLOR)
        self.timer = STACK_REBUILD_TIME
        self.score = {'Team 1': 0, 'Team 2': 0}
        self.turn = 1  # 1 = Team 1 building, 2 = Team 2 throwing
        self.thrower_idx = 0
        self.rebuilders_idx = 0
        self.players = []
        self.throw_count = 0
        self.result_text = ''
        self.last_time = 0

        self.init_buttons()
        self.init_game()

    def init_buttons(self):
        # Main menu buttons
        self.start_btn = Button((SCREEN_WIDTH//2-145, SCREEN_HEIGHT//2-70, 290, 60), "Start Game (1P vs AI)", (109, 141, 65), (255,255,255))
        self.mp_btn = Button((SCREEN_WIDTH//2-145, SCREEN_HEIGHT//2+10, 290, 60), "Multiplayer (2P Local)", (91, 153, 211), (255,255,255))
        self.quit_btn = Button((SCREEN_WIDTH//2-145, SCREEN_HEIGHT//2+90, 290, 60), "Quit", (166, 59, 70), (255,255,255))

    def init_game(self):
        self.state = 'playing'
        self.stones.empty()
        self.players = []
        stack_x, stack_y = STACK_CENTER
        # Stack stones vertically
        curr_y = stack_y
        for i in range(NUM_STONES):
            stone = Stone(stack_x, curr_y)
            self.stones.add(stone)
            curr_y -= STONE_HEIGHT + STONE_GAP
        # Place players
        self.ball = Ball(0, 0, TEAM_TWO_COLOR)
        self.timer = STACK_REBUILD_TIME
        self.throw_count = 0
        # Team 1 (stack rebuilders)
        for i in range(2):
            self.players.append(Player(stack_x-80-60*i, stack_y+120, 1, i, is_ai=not self.multiplayer or i==1))
        # Team 2 (throwers)
        for i in range(2):
            self.players.append(Player(stack_x+80+60*i, stack_y-160, 2, i, is_ai=not self.multiplayer or i==0))
        for p in self.players:
            p.rebuilding = False
            p.hit = False
            p.alive = True
            p.x = clamp(p.x, PLAYER_RADIUS, SCREEN_WIDTH-PLAYER_RADIUS)
            p.y = clamp(p.y, PLAYER_RADIUS, SCREEN_HEIGHT-PLAYER_RADIUS)
        if self.turn == 1:  # Team 1 starts rebuilding
            for p in self.players:
                if p.team == 1:
                    p.rebuilding = True
        else:
            for p in self.players:
                if p.team == 2:
                    p.rebuilding = False

    def reset_stack(self):
        # Re-create the stack at center
        self.stones.empty()
        stack_x, stack_y = STACK_CENTER
        curr_y = stack_y
        for i in range(NUM_STONES):
            stone = Stone(stack_x, curr_y)
            self.stones.add(stone)
            curr_y -= STONE_HEIGHT + STONE_GAP

    def stack_status(self):
        # Get stack status (for AI)
        return {
            'stones': self.stones,
            'players': self.players,
            'stack_center': STACK_CENTER,
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if self.state == 'menu':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.start_btn.is_clicked(pos):
                        self.multiplayer = False
                        self.turn = 1
                        self.init_game()
                    elif self.mp_btn.is_clicked(pos):
                        self.multiplayer = True
                        self.turn = 1
                        self.init_game()
                    elif self.quit_btn.is_clicked(pos):
                        self.running = False
                        pygame.quit()
                        sys.exit()
            elif self.state == 'playing':
                # Gameplay input events
                if event.type == pygame.KEYDOWN:
                    try:
                        self.handle_player_inputs(event)
                    except Exception:
                        pass
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(event)

    def handle_player_inputs(self, event):
        """Handle keyboard for player(s).

        Controls:
        Team 1 (Rebuilder): WASD (move), E (rebuild stack)
        Team 2 (Thrower): Arrow keys (move), SPACE (throw ball)
        """
        # Team 1 - Human controlled
        p1 = self.get_player(team=1, idx=0)
        if p1 and not p1.is_ai and p1.alive and not p1.hit:
            dx, dy = 0, 0
            if event.key == pygame.K_a:
                dx = -1
            elif event.key == pygame.K_d:
                dx = 1
            elif event.key == pygame.K_w:
                dy = -1
            elif event.key == pygame.K_s:
                dy = 1
            if dx or dy:
                p1.move(dx, dy)
            if event.key == pygame.K_e and self.turn == 1:
                self.try_rebuild_stack(p1)
        # Team 2 - Human controlled
        p2 = self.get_player(team=2, idx=0)
        if p2 and not p2.is_ai and p2.alive:
            dx, dy = 0, 0
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            if dx or dy:
                p2.move(dx, dy)
            if event.key == pygame.K_SPACE and self.turn == 2 and not self.ball.active:
                mx, my = pygame.mouse.get_pos()
                angle = math.degrees(math.atan2(my-p2.y, mx-p2.x))
                power = 18 - random.randint(0, 6)
                self.ball.x = p2.x
                self.ball.y = p2.y
                self.ball.team_color = p2.color
                self.ball.throw(angle, power)
                self.ball.thrown_by = p2

    def handle_mouse(self, event):
        # Mouse for aiming ball if Team 2's player
        if self.turn == 2 and not self.ball.active:
            # Only for multiplayer, player 2
            p2 = self.get_player(team=2, idx=0)
            if p2 and not p2.is_ai and p2.alive:
                mx, my = pygame.mouse.get_pos()
                angle = math.degrees(math.atan2(my-p2.y, mx-p2.x))
                power = random.randint(15, 19)
                self.ball.x = p2.x
                self.ball.y = p2.y
                self.ball.team_color = p2.color
                self.ball.throw(angle, power)
                self.ball.thrown_by = p2

    def get_player(self, team, idx):
        for p in self.players:
            if p.team == team and p.player_id == idx:
                return p
        return None

    def try_rebuild_stack(self, player):
        """Player tries to rebuild stack if standing near."""
        if not player.alive or player.hit or not player.rebuilding:
            return
        stack_x, stack_y = STACK_CENTER
        dist = math.hypot(stack_x - player.x, stack_y - player.y)
        if dist < PLAYER_RADIUS + 18:
            # Place stones back; only when not being hit
            stones_off = [s for s in self.stones if not s.active]
            if stones_off:
                count = 2 if len(stones_off) > 3 else 1
                placed = 0
                for s in stones_off:
                    s.active = True
                    s.rect.center = (stack_x, stack_y - (NUM_STONES - placed-1) * (STONE_HEIGHT + STONE_GAP))
                    placed += 1
                    if placed >= count:
                        break

    def update(self):
        if self.state == 'playing':
            self.update_play()

    def update_play(self):
        # Ball physics and collision
        self.ball.update()
        for stone in self.stones:
            stone.update()
            if stone.active and self.ball.active:
                # Collision
                if self.ball.get_rect().colliderect(stone.rect):
                    stone.active = False
                    stone.vx = self.ball.vx * random.uniform(0.8, 1.4) + random.randint(-3, 3)
                    stone.vy = self.ball.vy * random.uniform(0.5, 1.2) + random.randint(-2, 3)
                    self.ball.vy *= 0.52
                    self.ball.vx *= 0.45
        for p in self.players:
            p.update(self.ball, self.stones, self.stack_status())
        if self.ball.active:
            # Ball hits player (only team 1; rebuilding)
            for p in self.players:
                if p.team == 1 and not p.hit and p.alive:
                    px, py = p.x, p.y
                    bx, by = self.ball.x, self.ball.y
                    d = math.hypot(px-bx, py-by)
                    if d < BALL_RADIUS + PLAYER_RADIUS - 8:
                        p.hit = True
                        p.alive = False
                        self.ball.active = False
                        self.ball.vx *= 0.58
                        self.ball.vy *= 0.58
        self.check_rebuilding()
        self.check_timer()

    def check_rebuilding(self):
        # Detect if stack is rebuilt
        stones_placed = [s for s in self.stones if s.active]
        if len(stones_placed) == NUM_STONES and self.turn == 1:
            self.score['Team 1'] += 1
            self.result_text = 'Team 1 rebuilt! +1'
            pygame.time.set_timer(pygame.USEREVENT + 1, 1400)
            self.state = 'result'

    def check_timer(self):
        # Timer for rebuilding
        now = pygame.time.get_ticks()
        if self.last_time == 0:
            self.last_time = now
        dt = (now - self.last_time) / 1000.0
        if self.turn == 1 and self.state == 'playing':
            self.timer -= dt
            self.last_time = now
            if self.timer <= 0:
                self.result_text = 'Team 2 stopped rebuilding!'
                self.score['Team 2'] += 1
                pygame.time.set_timer(pygame.USEREVENT + 2, 1400)
                self.state = 'result'
        else:
            self.last_time = now

    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'result':
            self.draw_game()
            self.draw_result()

    def draw_menu(self):
        self.screen.fill((204, 183, 120))
        title_text = font.render("Pithu (Seven Stones)", True, (140, 58, 16))
        self.screen.blit(title_text, (SCREEN_WIDTH//2-title_text.get_width()//2, 120))
        desc1 = small_font.render("A traditional Indian street game!", True, (61, 39, 18))
        self.screen.blit(desc1, (SCREEN_WIDTH//2-desc1.get_width()//2, 160))
        self.start_btn.hovered = self.start_btn.rect.collidepoint(pygame.mouse.get_pos())
        self.mp_btn.hovered = self.mp_btn.rect.collidepoint(pygame.mouse.get_pos())
        self.quit_btn.hovered = self.quit_btn.rect.collidepoint(pygame.mouse.get_pos())
        self.start_btn.draw(self.screen)
        self.mp_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def draw_game(self):
        self.screen.fill(BG_COLOR)
        # Center area
        pygame.draw.rect(self.screen, (166, 134, 55), (STACK_CENTER[0]-70, STACK_CENTER[1]-120, 140, 260), border_radius=8)
        # Stack shadow
        pygame.draw.ellipse(self.screen, (86, 75, 43), (STACK_CENTER[0]-70, STACK_CENTER[1]+90, 140, 22))
        for stone in self.stones:
            stone.draw(self.screen)
        for p in self.players:
            p.draw(self.screen)
        self.ball.draw(self.screen)
        self.draw_ui()

    def draw_ui(self):
        # Info bars, score, timer
        pygame.draw.rect(self.screen, (172, 138, 55), (0, 0, SCREEN_WIDTH, 54))
        score_text = small_font.render(
            f"Team 1 (Rebuilders): {self.score['Team 1']}  |  Team 2 (Throwers): {self.score['Team 2']}", True, (5,5,5))
        self.screen.blit(score_text, (SCREEN_WIDTH//2-score_text.get_width()//2, 10))
        if self.turn == 1:
            act_text = small_font.render("Team 1: Rebuild the stack! (WASD + E)", True, (21,44,90))
        else:
            act_text = small_font.render("Team 2: Throw the ball! (Arrows + Space)", True, (218,46,35))
        self.screen.blit(act_text, (SCREEN_WIDTH//2-act_text.get_width()//2, 32))
        # Timer
        pygame.draw.rect(self.screen, UI_COLOR, (30, 14, 150, 30), border_radius=5)
        timer_val = max(0, int(self.timer))
        timer_text = small_font.render(f"Time left: {timer_val}s", True, (255,255,255))
        self.screen.blit(timer_text, (40, 17))
        # Show how to rebuild stack
        rebuild_tip = small_font.render("Tip: Stand near the stack & press 'E'!", True, (31, 24, 22))
        self.screen.blit(rebuild_tip, (SCREEN_WIDTH//2-rebuild_tip.get_width()//2, SCREEN_HEIGHT-36))

    def draw_result(self):
        # Result overlay
        rect = pygame.Rect(SCREEN_WIDTH//2-160, SCREEN_HEIGHT//2-58, 320, 115)
        pygame.draw.rect(self.screen, (225, 218, 152), rect, border_radius=10)
        text = font.render(self.result_text, True, (90,31,13))
        self.screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2 - 12))
        next_text = small_font.render("Next Round in 2s...", True, (99, 76, 40))
        self.screen.blit(next_text, (rect.centerx - next_text.get_width()//2, rect.centery + 28))

    def round_over(self):
        # Prepare for next round
        self.reset_stack()
        self.timer = STACK_REBUILD_TIME
        self.last_time = pygame.time.get_ticks()
        for p in self.players:
            p.hit = False
            p.alive = True
            p.rebuilding = False
        self.ball.active = False
        self.ball.throwing = False
        self.ball.x = 0
        self.ball.y = 0
        self.turn = 1 if self.turn == 2 else 2
        if self.turn == 1:
            for p in self.players:
                if p.team == 1:
                    p.rebuilding = True
        else:
            for p in self.players:
                if p.team == 2:
                    p.rebuilding = False
        self.state = 'playing'
        self.result_text = ''

    def main_loop(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            # Event to auto-handle next round
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1 or event.type == pygame.USEREVENT + 2:
                    self.round_over()

def main():
    try:
        g = Game(multiplayer=False)
        g.main_loop()
    except Exception as e:
        print(f"Error running Pithu: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()