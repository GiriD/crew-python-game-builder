import pygame
import sys
import math
import random

# Game constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
GROUND_LEVEL = SCREEN_HEIGHT - 120
DANDA_LENGTH = 100
GILLI_SIZE = 20
WIND_MIN = -5
WIND_MAX = 5
ROUNDS = 5
FPS = 60

# Initialize colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (101, 67, 33)
GREEN = (60, 179, 113)
YELLOW = (255, 236, 139)
BLUE = (135, 206, 235)
GRAY = (170, 170, 170)
RED = (220, 20, 60)

# Utility function to draw text
def draw_text(surface, text, size, x, y, color=BLACK, center=True):
    font = pygame.font.SysFont("comicsansms", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class PowerMeter:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.power = 0
        self.increasing = True
        self.active = False

    def reset(self):
        self.power = 0
        self.increasing = True
        self.active = False

    def start(self):
        self.active = True

    def update(self):
        if self.active:
            if self.increasing:
                self.power += 2
                if self.power >= 100:
                    self.power = 100
                    self.increasing = False
            else:
                self.power -= 2
                if self.power <= 0:
                    self.power = 0
                    self.increasing = True

    def stop(self):
        self.active = False
        return self.power

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height), 2)
        fill_width = (self.power / 100) * (self.width - 6)
        pygame.draw.rect(screen, RED, (self.x+3, self.y+3, fill_width, self.height-6))

class Wind:
    def __init__(self):
        self.strength = random.uniform(WIND_MIN, WIND_MAX)

    def randomize(self, difficulty=1):
        # At higher difficulties, wind variation increases
        self.strength = random.uniform(WIND_MIN * difficulty, WIND_MAX * difficulty)

    def draw(self, screen, x, y):
        wind_text = f"Wind: {'→' if self.strength > 0 else '←' if self.strength < 0 else '-'} {abs(self.strength):.1f} m/s"
        draw_text(screen, wind_text, 25, x, y, BLUE, center=False)

class Gilli:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0  # velocity X
        self.vy = 0  # velocity Y
        self.angle = 0  # launch angle in degrees
        self.flying = False
        self.distance = 0
        self.time = 0

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.flying = False
        self.distance = 0
        self.time = 0

    def launch(self, power, angle, wind):
        # Translate power to initial velocity (max 30 m/s)
        v_init = 10 + (power/100)*20
        self.vx = v_init * math.cos(math.radians(angle)) + wind.strength
        self.vy = -v_init * math.sin(math.radians(angle))
        self.angle = angle
        self.flying = True
        self.time = 0
        self.start_x = self.x

    def update(self):
        if self.flying:
            dt = 1 / FPS
            # Gravity
            g = 9.8 * 30  # scale gravity for screen pixels
            # Update time
            self.time += dt
            # Compute new positions
            self.x += self.vx
            self.vy += g * dt
            self.y += self.vy * dt
            # Check if it landed
            if self.y > GROUND_LEVEL-GILLI_SIZE//2:
                self.y = GROUND_LEVEL-GILLI_SIZE//2
                self.flying = False
                self.distance = int(self.x - self.start_x)
                return True
        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, YELLOW, (int(self.x)-GILLI_SIZE//2, int(self.y)-GILLI_SIZE//2, GILLI_SIZE, GILLI_SIZE))
        pygame.draw.ellipse(screen, BLACK, (int(self.x)-GILLI_SIZE//2, int(self.y)-GILLI_SIZE//2, GILLI_SIZE, GILLI_SIZE), 2)

class Danda:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = -45  # Default resting angle

    def draw(self, screen, hitting=False):
        angle = self.angle if not hitting else self.angle - 60
        rad = math.radians(angle)
        x2 = self.x + DANDA_LENGTH * math.cos(rad)
        y2 = self.y - DANDA_LENGTH * math.sin(rad)
        pygame.draw.line(screen, BROWN, (self.x, self.y), (x2, y2), 10)
        pygame.draw.circle(screen, BROWN, (self.x, self.y), 12)

class LevelManager:
    def __init__(self):
        self.round = 1
        self.max_round = ROUNDS
        self.difficulty = 1

    def next_round(self):
        self.round += 1
        self.difficulty = 1 + 0.5 * (self.round - 1)

    def reset(self):
        self.round = 1
        self.difficulty = 1

    def draw(self, screen):
        draw_text(screen, f"Round {self.round}/{self.max_round}", 25, 110, 80, RED, center=False)

class ScoreBoard:
    def __init__(self):
        self.distances = []
        self.total_score = 0

    def add_shot(self, distance):
        self.distances.append(distance)
        self.total_score += max(0, int(distance * 0.1))  # Score is proportional to distance

    def reset(self):
        self.distances = []
        self.total_score = 0

    def draw(self, screen):
        draw_text(screen, f"Score: {self.total_score}", 28, SCREEN_WIDTH-180, 70, BLACK, center=False)
        if len(self.distances) > 0:
            draw_text(screen, f"Last Distance: {self.distances[-1]} px", 23, SCREEN_WIDTH-180, 102, GRAY, center=False)

class VillageBackground:
    def draw(self, screen):
        screen.fill(BLUE)
        pygame.draw.rect(screen, GREEN, (0, GROUND_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT-GROUND_LEVEL))  # Ground
        # Draw huts
        for i in range(2):
            hut_x = 150 + i*500
            pygame.draw.rect(screen, BROWN, (hut_x, GROUND_LEVEL-80, 100, 60))
            pygame.draw.polygon(screen, GRAY, [(hut_x-10, GROUND_LEVEL-80), (hut_x+50, GROUND_LEVEL-120), (hut_x+110, GROUND_LEVEL-80)])
            pygame.draw.rect(screen, BLACK, (hut_x+35, GROUND_LEVEL-65, 30, 35))
        # Draw trees
        for tree_x in [400, 700]:
            pygame.draw.rect(screen, BROWN, (tree_x, GROUND_LEVEL-60, 14, 60))
            pygame.draw.circle(screen, GREEN, (tree_x+7, GROUND_LEVEL-70), 30)
        # Draw some clouds
        for cx, cy in [(200, 70), (400, 120), (600, 90)]:
            pygame.draw.circle(screen, WHITE, (cx, cy), 22)
            pygame.draw.circle(screen, WHITE, (cx+25, cy-5), 17)
            pygame.draw.circle(screen, WHITE, (cx-20, cy+8), 12)
        # Village border fence
        for i in range(0, SCREEN_WIDTH, 18):
            pygame.draw.rect(screen, GRAY, (i, GROUND_LEVEL+40, 6, 32))

class GilliDandaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gilli Danda - Traditional Indian Game")
        self.clock = pygame.time.Clock()
        self.background = VillageBackground()
        self.danda = Danda(240, GROUND_LEVEL-15)
        self.gilli = Gilli(240+105, GROUND_LEVEL-20)
        self.power_meter = PowerMeter(120, SCREEN_HEIGHT-60, 220, 35)
        self.wind = Wind()
        self.level = LevelManager()
        self.score_board = ScoreBoard()
        self.state = 'aim'  # Can be 'aim', 'power', 'hit', 'fly', 'score', 'end'
        self.angle = 45
        self.aiming_left = False
        self.aiming_right = False
        self.hitting_animation = False
        self.timer = 0
        self.error_message = ""
        self.round_finished = False

    def reset_round(self):
        self.danda = Danda(240, GROUND_LEVEL-15)
        self.gilli = Gilli(240+105, GROUND_LEVEL-20)
        self.power_meter.reset()
        self.state = 'aim'
        self.angle = 45
        self.wind.randomize(self.level.difficulty)
        self.hitting_animation = False
        self.timer = 0
        self.round_finished = False

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if self.state == 'end':
                        if event.key == pygame.K_RETURN:
                            self.level.reset()
                            self.score_board.reset()
                            self.reset_round()
                            return
                    if self.state == 'aim':
                        if event.key == pygame.K_LEFT:
                            self.aiming_left = True
                        elif event.key == pygame.K_RIGHT:
                            self.aiming_right = True
                        elif event.key == pygame.K_SPACE:
                            self.state = 'power'
                            self.power_meter.start()
                    if self.state == 'power':
                        if event.key == pygame.K_SPACE:
                            self.state = 'hit'
                            self.power_meter.stop()
                            self.hitting_animation = True
                            self.timer = 0
                    if self.state == 'score' and not self.round_finished:
                        if event.key == pygame.K_RETURN:
                            if self.level.round < self.level.max_round:
                                self.level.next_round()
                                self.reset_round()
                            else:
                                self.state = 'end'
                            self.round_finished = True
                elif event.type == pygame.KEYUP:
                    if self.state == 'aim':
                        if event.key == pygame.K_LEFT:
                            self.aiming_left = False
                        elif event.key == pygame.K_RIGHT:
                            self.aiming_right = False
        except Exception as ex:
            self.error_message = f"Event Error: {ex}"

    def update(self):
        try:
            if self.state == 'aim':
                if self.aiming_left:
                    self.angle = max(15, self.angle - 2)
                if self.aiming_right:
                    self.angle = min(75, self.angle + 2)
                self.danda.angle = -self.angle
            elif self.state == 'power':
                self.power_meter.update()
            elif self.state == 'hit':
                self.timer += 1
                if self.timer > 10:
                    # Launch the Gilli after hitting animation
                    power = self.power_meter.power
                    angle = self.angle
                    self.gilli.launch(power, angle, self.wind)
                    self.state = 'fly'
                    self.hitting_animation = False
                    self.timer = 0
            elif self.state == 'fly':
                finished = self.gilli.update()
                if finished:
                    self.state = 'score'
                    # Register shot score
                    self.score_board.add_shot(max(0, self.gilli.distance))
            elif self.state == 'score':
                pass
            elif self.state == 'end':
                pass
        except Exception as ex:
            self.error_message = f"Update Error: {ex}"

    def draw(self):
        try:
            self.background.draw(self.screen)
            self.level.draw(self.screen)
            self.wind.draw(self.screen, 20, 20)
            self.score_board.draw(self.screen)

            if self.state in ('aim', 'power'):
                # Draw Danda, Gilli (not flying)
                hitting = self.hitting_animation and self.state == 'hit'
                self.danda.draw(self.screen, hitting=hitting)
                self.gilli.draw(self.screen)
                # Draw angle indicator
                draw_text(self.screen, f"Angle: {self.angle}°", 24, SCREEN_WIDTH//2-62, SCREEN_HEIGHT-50)
            elif self.state == 'hit':
                # Danda is animated
                self.danda.draw(self.screen, hitting=True)
                self.gilli.draw(self.screen)
            elif self.state == 'fly':
                # Draw flying Gilli
                self.danda.draw(self.screen)
                self.gilli.draw(self.screen)
                # Draw flying distance
                draw_text(self.screen, f"Gilli Flying...", 22, SCREEN_WIDTH//2+40, SCREEN_HEIGHT-50)
            elif self.state == 'score':
                self.danda.draw(self.screen)
                self.gilli.draw(self.screen)
                # Show distance and prompt for next round
                draw_text(self.screen, f"Distance: {max(0, self.gilli.distance)} px", 28, SCREEN_WIDTH//2-20, SCREEN_HEIGHT//2-35, BLACK)
                draw_text(self.screen, "Press Enter for Next Round!", 23, SCREEN_WIDTH//2-20, SCREEN_HEIGHT//2+12, RED)
            elif self.state == 'end':
                draw_text(self.screen, "GAME OVER", 52, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-60, RED)
                draw_text(self.screen, f"Your Score: {self.score_board.total_score}", 38, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BLACK)
                draw_text(self.screen, "Press Enter to Play Again", 23, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+50, BLUE)
            # Power meter
            if self.state in ('aim', 'power', 'hit'):
                draw_text(self.screen, "Power Meter", 18, 235, SCREEN_HEIGHT-80, BLACK)
                self.power_meter.draw(self.screen)
            # Error messages
            if self.error_message:
                draw_text(self.screen, self.error_message, 18, SCREEN_WIDTH//2, 18, RED)
            pygame.display.flip()
        except Exception as ex:
            self.error_message = f"Draw Error: {ex}"

def main():
    try:
        game = GilliDandaGame()
        game.run()
    except Exception as e:
        print(f"Critical Error: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()