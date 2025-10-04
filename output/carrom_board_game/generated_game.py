import pygame
import sys
import math
import random

# Game constants
BOARD_SIZE = 640  # Square board size in pixels
POCKET_RADIUS = 36
COIN_RADIUS = 16
STRIKER_RADIUS = 20
FRICTION = 0.99  # Friction factor for slowing movement
MAX_STRIKER_POWER = 20
STRIKER_Y_OFFSET = 70
BG_COLOR = (210, 180, 140)  # Wooden board color

WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
RED = (200, 20, 20)
GREEN = (60, 180, 60)
BORDER_COLOR = (120, 90, 50)

FPS = 60

# Coin types
WHITE_COIN = 'white'
BLACK_COIN = 'black'
RED_COIN = 'queen'

# Physics
def vec_length(vec):
    return math.hypot(vec[0], vec[1])

def vec_normalize(vec):
    l = vec_length(vec)
    return (vec[0] / l, vec[1] / l) if l != 0 else (0, 0)

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

# Coin
class Coin:
    def __init__(self, x, y, color, ctype):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = COIN_RADIUS if ctype != RED_COIN else COIN_RADIUS + 2
        self.color = color
        self.ctype = ctype
        self.pocketed = False
        self.covered = False  # Only used for queen

    def update(self):
        if not self.pocketed:
            self.x += self.vx
            self.y += self.vy
            self.vx *= FRICTION
            self.vy *= FRICTION
            if vec_length((self.vx, self.vy)) < 0.07:
                self.vx = 0
                self.vy = 0

    def draw(self, surface):
        if not self.pocketed:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Queen highlight
            if self.ctype == RED_COIN:
                pygame.draw.circle(surface, (255, 220, 120), (int(self.x), int(self.y)), self.radius - 6)

# Striker
class Striker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = STRIKER_RADIUS
        self.vx = 0
        self.vy = 0
        self.in_motion = False

    def set_position(self, x):
        # Striker can only be moved horizontally along base line
        margin = 48 + self.radius
        self.x = clamp(x, margin, BOARD_SIZE - margin)

    def shoot(self, angle, power):
        self.vx = power * math.cos(angle)
        self.vy = power * math.sin(angle)
        self.in_motion = True

    def update(self):
        if self.in_motion:
            self.x += self.vx
            self.y += self.vy
            self.vx *= FRICTION
            self.vy *= FRICTION
            if vec_length((self.vx, self.vy)) < 0.09:
                self.vx = 0
                self.vy = 0
                self.in_motion = False

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)

# Player
class Player:
    def __init__(self, name, color):
        self.name = name
        self.score = 0
        self.coins_pocketed = []
        self.color = color
        self.queen_pocketed = False
        self.queen_cover_chance = False

# Carrom Main Game Class
class CarromGame:
    def __init__(self, player_names):
        pygame.init()
        self.surface = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        pygame.display.set_caption("Carrom Board Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('comicsansms', 22)
        self.running = True

        self.players = [Player(player_names[i], [BLACK, WHITE, (70, 70, 220), (220, 120, 40)][i]) for i in range(len(player_names))]
        self.current_player = 0
        self.striker = None
        self.aiming = True
        self.shooting = False
        self.aim_angle = 0
        self.aim_power = 0

        self.coins = []
        self.pockets = []
        self.turn_has_pocket = False
        self.scratch = False

        self.queen_needs_cover = None  # Player index
        self.queen_unlock_queue = None  # True for next shot, None otherwise

        self.init_board()
        self.reset_striker()

    def init_board(self):
        self.coins.clear()
        # Place coins in central formation: 6 white, 6 black, 1 red
        center = BOARD_SIZE // 2
        radius = 52
        positions = []
        count = 0
        for layer in range(3):
            for i in range(0, 8, 2):
                angle = math.pi / 4 * i + (layer % 2) * (math.pi / 8)
                r = radius * (layer + 1) * 0.8
                x = center + r * math.cos(angle)
                y = center + r * math.sin(angle)
                positions.append((x, y))
                count += 1

        # Place queen
        self.coins.append(Coin(center, center, RED, RED_COIN))
        # Place 6 white and 6 black in positions
        for i in range(12):
            ctype = WHITE_COIN if i % 2 == 0 else BLACK_COIN
            clr = WHITE if ctype == WHITE_COIN else BLACK
            x, y = positions[i]
            self.coins.append(Coin(x, y, clr, ctype))

        # Set pocket positions
        offset = POCKET_RADIUS - 4
        self.pockets = [(offset, offset),
                        (BOARD_SIZE - offset, offset),
                        (BOARD_SIZE - offset, BOARD_SIZE - offset),
                        (offset, BOARD_SIZE - offset)]

    def reset_striker(self):
        # Striker starts at the base side of the current player
        margin = 48
        if len(self.players) == 2:
            base_y = BOARD_SIZE - STRIKER_Y_OFFSET if self.current_player == 0 else STRIKER_Y_OFFSET
        else:
            base = [(BOARD_SIZE - STRIKER_Y_OFFSET, True),
                    (STRIKER_Y_OFFSET, True),
                    (BOARD_SIZE - STRIKER_Y_OFFSET, False),
                    (STRIKER_Y_OFFSET, False)][self.current_player % 4]
            base_y = base[0]
        self.striker = Striker(BOARD_SIZE // 2, base_y)
        self.aiming = True
        self.shooting = False
        self.aim_angle = -math.pi / 2 if base_y > BOARD_SIZE // 2 else math.pi / 2
        self.aim_power = 1

    def coins_in_motion(self):
        # Returns True if any coin or striker is moving
        for c in self.coins:
            if not c.pocketed and (abs(c.vx) > 0.04 or abs(c.vy) > 0.04):
                return True
        if self.striker and (abs(self.striker.vx) > 0.04 or abs(self.striker.vy) > 0.04):
            return True
        return False

    def pocket_detect(self, coin):
        # Check if the coin is in any pocket
        for px, py in self.pockets:
            if vec_length((coin.x - px, coin.y - py)) < POCKET_RADIUS - 2:
                return True
        return False

    def update(self):
        # Physics update on coins and striker
        for c in self.coins:
            c.update()

        self.striker.update()

        # Handle collisions - coins with striker and coins with coins
        # Simple elastic collision model
        for c in self.coins:
            if c.pocketed: continue
            # With striker
            dx = c.x - self.striker.x
            dy = c.y - self.striker.y
            dist = math.hypot(dx, dy)
            if dist < c.radius + self.striker.radius:
                overlap = (c.radius + self.striker.radius) - dist + 1
                nx, ny = vec_normalize((dx, dy))
                # Push out
                c.x += nx * overlap / 2
                self.striker.x -= nx * overlap / 2
                # Transfer momentum
                dvx = self.striker.vx - c.vx
                dvy = self.striker.vy - c.vy
                c.vx += nx * dvx * 0.25
                c.vy += ny * dvy * 0.25
                self.striker.vx -= nx * dvx * 0.20
                self.striker.vy -= ny * dvy * 0.20

            # Coins with coins
            for other in self.coins:
                if other == c or other.pocketed: continue
                dx = c.x - other.x
                dy = c.y - other.y
                dist = math.hypot(dx, dy)
                if dist < c.radius + other.radius:
                    overlap = (c.radius + other.radius) - dist + 1
                    nx, ny = vec_normalize((dx, dy))
                    c.x += nx * overlap / 2
                    c.y += ny * overlap / 2
                    other.x -= nx * overlap / 2
                    other.y -= ny * overlap / 2
                    # Exchange velocities (elastic)
                    c.vx, other.vx = other.vx, c.vx
                    c.vy, other.vy = other.vy, c.vy

        # Handle coins pocketed
        pocketed_this_turn = []
        scratch_this_turn = False
        for c in self.coins:
            if not c.pocketed and self.pocket_detect(c):
                c.pocketed = True
                pocketed_this_turn.append(c)
        # Handle striker pocketed
        if not self.striker.in_motion and self.pocket_detect(self.striker):
            scratch_this_turn = True
            self.striker.in_motion = False
            # Place striker at base

        # Return results for this update
        return pocketed_this_turn, scratch_this_turn

    def handle_pocketed(self, pocketed_list, scratch):
        player = self.players[self.current_player]
        pocket_types = [c.ctype for c in pocketed_list]
        # Queen logic
        queen_in_list = RED_COIN in pocket_types
        player_coins = WHITE_COIN if self.current_player % 2 == 0 else BLACK_COIN
        opponent_coins = BLACK_COIN if player_coins == WHITE_COIN else WHITE_COIN
        covered = False

        for c in pocketed_list:
            if c.ctype == player_coins:
                player.score += 10
                player.coins_pocketed.append(c)
                covered = True
            elif c.ctype == opponent_coins:
                self.players[(self.current_player+1)%len(self.players)].score += 10
                self.players[(self.current_player+1)%len(self.players)].coins_pocketed.append(c)
            elif c.ctype == RED_COIN:
                # Queen must be covered by pocketing own color same turn or next allowed shot
                player.queen_pocketed = True
                self.queen_needs_cover = self.current_player
                self.queen_unlock_queue = True
                player.queen_cover_chance = True
        # Queen covering conditions
        if player.queen_pocketed and covered:
            player.score += 50
            player.queen_cover_chance = False
            player.queen_pocketed = False
            self.queen_needs_cover = None
            self.queen_unlock_queue = None
        elif player.queen_pocketed and not covered:
            if self.queen_unlock_queue and not covered:
                # Queen not covered in allowed shot
                # Place queen back to center
                for coin in self.coins:
                    if coin.ctype == RED_COIN:
                        coin.pocketed = False
                        coin.x = BOARD_SIZE // 2
                        coin.y = BOARD_SIZE // 2
                        coin.vx = coin.vy = 0
                player.queen_pocketed = False
                player.queen_cover_chance = False
                self.queen_needs_cover = None
                self.queen_unlock_queue = None
            elif self.queen_unlock_queue:
                self.queen_unlock_queue = False

        # Handle scratch
        if scratch:
            player.score -= 10
            # Return one own coin to board if any
            if player.coins_pocketed:
                coin = player.coins_pocketed.pop()
                coin.pocketed = False
                coin.x = random.randint(BOARD_SIZE//2-30, BOARD_SIZE//2+30)
                coin.y = random.randint(BOARD_SIZE//2-30, BOARD_SIZE//2+30)
            self.scratch = True

        # Set flag for turn extension
        self.turn_has_pocket = len(pocketed_list) > 0 and not scratch

    def next_player(self):
        # Go to next player, unless turn is extended for successful pocketing
        if self.turn_has_pocket and not self.scratch:
            pass
        else:
            self.current_player = (self.current_player + 1) % len(self.players)
        self.scratch = False
        self.turn_has_pocket = False
        self.reset_striker()

    def all_coins_pocketed(self):
        # End condition
        non_striker_coins_left = [c for c in self.coins if not c.pocketed and c.ctype != RED_COIN]
        return len(non_striker_coins_left) == 0

    def draw_board(self):
        # Draw board background
        self.surface.fill(BG_COLOR)
        # Draw border and frame
        pygame.draw.rect(self.surface, BORDER_COLOR, (24, 24, BOARD_SIZE - 48, BOARD_SIZE - 48), 30)
        pygame.draw.rect(self.surface, (160, 110, 50), (24, 24, BOARD_SIZE - 48, BOARD_SIZE - 48), 6)

        # Draw pockets
        for px, py in self.pockets:
            pygame.draw.circle(self.surface, BLACK, (int(px), int(py)), POCKET_RADIUS)
            pygame.draw.circle(self.surface, (80, 40, 10), (int(px), int(py)), POCKET_RADIUS, 5)

        # Draw base lines (for striker position)
        margin = 44
        pygame.draw.line(self.surface, BLACK, (margin, BOARD_SIZE - STRIKER_Y_OFFSET), (BOARD_SIZE - margin, BOARD_SIZE - STRIKER_Y_OFFSET), 4)
        pygame.draw.line(self.surface, BLACK, (margin, STRIKER_Y_OFFSET), (BOARD_SIZE - margin, STRIKER_Y_OFFSET), 4)

        # Coin circles
        for c in self.coins:
            c.draw(self.surface)
        self.striker.draw(self.surface)

        # Draw aim
        if self.aiming:
            start = (int(self.striker.x), int(self.striker.y))
            end = (int(self.striker.x + math.cos(self.aim_angle) * 70 * self.aim_power),
                   int(self.striker.y + math.sin(self.aim_angle) * 70 * self.aim_power))
            pygame.draw.line(self.surface, RED, start, end, 3)
            pygame.draw.circle(self.surface, RED, end, 7)
            # Power bar
            pygame.draw.rect(self.surface, (180, 40, 40), (BOARD_SIZE - 118, BOARD_SIZE - 62, 22, -int(56 * self.aim_power / MAX_STRIKER_POWER)))
            # Draw text "Power"
            fnt = pygame.font.SysFont(None, 18)
            self.surface.blit(fnt.render("Power", True, (0, 0, 0)), (BOARD_SIZE-120, BOARD_SIZE-80))

        # Draw scores and turn
        yoff = 30
        for i, p in enumerate(self.players):
            clr = p.color
            title = ("► " if i == self.current_player else "   ") + p.name
            txt = f"{title}: {p.score} pts"
            render = self.font.render(txt, True, clr)
            self.surface.blit(render, (32, yoff))
            yoff += 38

        # Queen covering info
        if self.queen_needs_cover is not None:
            info = self.font.render("Queen needs covering!", True, RED)
            self.surface.blit(info, (BOARD_SIZE//2 - 100, 18))

        # End game
        if self.all_coins_pocketed():
            winner_score = max([p.score for p in self.players])
            winners = [p.name for p in self.players if p.score == winner_score]
            txt = "Winner: " + ", ".join(winners)
            render = self.font.render(txt, True, GREEN)
            self.surface.blit(render, (BOARD_SIZE//2 - 100, BOARD_SIZE//2 - 12))

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            pocketed = []
            scratch_this_turn = False
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.aiming and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Set aim direction and power
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - self.striker.x
                    dy = my - self.striker.y
                    angle = math.atan2(dy, dx)
                    # Only allow shooting away from base line
                    if len(self.players) == 2:
                        if (self.striker.y > BOARD_SIZE // 2 and -math.pi < angle < 0) or (self.striker.y < BOARD_SIZE // 2 and 0 < angle < math.pi):
                            self.aim_angle = angle
                            self.shooting = True
                    else:
                        # Any direction allowed for 4-player (simplify)
                        self.aim_angle = angle
                        self.shooting = True

                elif self.aiming and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    # Move striker horizontally
                    mx, my = pygame.mouse.get_pos()
                    self.striker.set_position(mx)

                elif self.aiming and event.type == pygame.MOUSEMOTION and self.shooting:
                    # Drag for power (mouse move while shooting)
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - self.striker.x
                    dy = my - self.striker.y
                    dist = vec_length((dx, dy))
                    self.aim_power = clamp(dist / 40, 1, MAX_STRIKER_POWER)

                elif self.aiming and event.type == pygame.MOUSEBUTTONUP and self.shooting:
                    # Release to shoot
                    self.striker.shoot(self.aim_angle, self.aim_power)
                    self.aiming = False
                    self.shooting = False
                    self.aim_power = 1

                elif self.aiming and event.type == pygame.KEYDOWN:
                    # Keyboard controls for striker move
                    if event.key == pygame.K_LEFT:
                        self.striker.set_position(self.striker.x - 15)
                    elif event.key == pygame.K_RIGHT:
                        self.striker.set_position(self.striker.x + 15)

            # Update physics if coins are moving
            if not self.aiming:
                pl, scratch = self.update()
                if pl or scratch:
                    pocketed = pl
                    scratch_this_turn = scratch

                # When everyone stopped, handle pockets and switch turn
                if not self.coins_in_motion():
                    if self.all_coins_pocketed():
                        self.draw_board()
                        pygame.display.update()
                        pygame.time.wait(1800)
                        self.running = False
                        continue
                    self.handle_pocketed(pocketed, scratch_this_turn)
                    self.next_player()
                    pocketed.clear()

            self.draw_board()
            pygame.display.update()

        pygame.quit()
        sys.exit()

def main():
    try:
        # Prompt for players
        pygame.init()
        screen = pygame.display.set_mode((420, 220))
        pygame.display.set_caption("Enter Player Names")
        font = pygame.font.SysFont('comicsansms', 26)
        smallf = pygame.font.SysFont('comicsansms', 20)
        clock = pygame.time.Clock()
        input_boxes = []
        player_names = ["", "", "", ""]
        num_players = 2
        selected = 0
        active_box = 0
        running = True
        while running:
            screen.fill((190, 170, 110))
            label = font.render('Carrom: Enter Player Names', True, (0, 0, 0))
            screen.blit(label, (30, 18))
            screen.blit(smallf.render("Number of players: [2-4] (Up/Down to change)", True, (0,0,0)), (34, 54))
            np_render = smallf.render(str(num_players), True, GREEN)
            screen.blit(np_render, (285, 54))
            yoff = 88
            for i in range(num_players):
                rect = pygame.Rect(46, yoff + 48*i, 210, 36)
                pygame.draw.rect(screen, (220, 210, 170), rect)
                pygame.draw.rect(screen, GREEN if active_box == i else BLACK, rect, 2)
                txt_render = smallf.render(player_names[i], True, BLACK)
                screen.blit(txt_render, (rect.x+8, rect.y+8))
                nm = f"Player {i+1}:"
                screen.blit(smallf.render(nm, True, BLACK), (rect.x - 88, rect.y + 8))
            screen.blit(smallf.render("Press Enter to Start", True, (20,60,140)), (128, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_KP_PLUS:
                        num_players = clamp(num_players + 1, 2, 4)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_KP_MINUS:
                        num_players = clamp(num_players - 1, 2, 4)
                    if event.key == pygame.K_TAB:
                        active_box = (active_box + 1) % num_players
                    if event.key == pygame.K_RETURN:
                        if all(player_names[:num_players]):
                            running = False
                            break
                    elif event.key == pygame.K_BACKSPACE:
                        player_names[active_box] = player_names[active_box][:-1]
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(player_names[active_box]) < 14:
                            player_names[active_box] += ch

            pygame.display.update()
            clock.tick(30)
        pygame.quit()
        g = CarromGame(player_names[:num_players])
        g.run()
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()