import pygame
import sys
import random

# Game Configuration Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 110
PADDLE_HEIGHT = 20
BALL_RADIUS = 12
BRICK_WIDTH = 60
BRICK_HEIGHT = 25
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_GAP = 5
TOP_OFFSET = 60
LEFT_OFFSET = 35
MAX_LIVES = 3
POWERUP_WIDTH = 30
POWERUP_HEIGHT = 20
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (165, 165, 165)
BLUE = (29, 155, 212)
RED = (255, 65, 54)
GREEN = (53, 220, 53)
YELLOW = (250, 229, 53)
ORANGE = (255, 140, 0)
PURPLE = (185, 53, 220)

BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

pygame.init()
pygame.font.init()

def load_font(size):
    try:
        return pygame.font.SysFont("Arial", size)
    except Exception:
        return pygame.font.Font(None, size)

class Paddle:
    def __init__(self, screen_width, screen_height):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 22
        self.speed = 8
        self.screen_width = screen_width
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, left=False, right=False, mouse_x=None):
        try:
            if mouse_x is not None:
                self.x = mouse_x - self.width // 2
            else:
                if left:
                    self.x -= self.speed
                if right:
                    self.x += self.speed
            # Clamp within screen bounds
            self.x = max(0, min(self.x, self.screen_width - self.width))
            self.rect.update(self.x, self.y, self.width, self.height)
        except Exception:
            pass

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)


class Ball:
    def __init__(self, paddle):
        self.radius = BALL_RADIUS
        self.x = paddle.x + paddle.width // 2
        self.y = paddle.y - self.radius - 1
        self.speed = 5
        self.vx = random.choice([-self.speed, self.speed])
        self.vy = -self.speed
        self.launched = False

    def launch(self):
        self.launched = True

    def update(self, paddle, bricks, powerups, score):
        try:
            if not self.launched:
                self.x = paddle.x + paddle.width // 2
                self.y = paddle.y - self.radius - 1
                return score, None
            self.x += self.vx
            self.y += self.vy

            # Collision with walls
            if self.x - self.radius <= 0:
                self.x = self.radius
                self.vx = -self.vx
            elif self.x + self.radius >= SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.radius
                self.vx = -self.vx
            if self.y - self.radius <= 0:
                self.y = self.radius
                self.vy = -self.vy

            # Collision with paddle
            paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
            ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
            if ball_rect.colliderect(paddle_rect) and self.vy > 0:
                intersect = (self.x - paddle.x) / paddle.width
                offset = (intersect - 0.5) * 2  # range [-1, 1]
                self.vx = offset * self.speed * 1.3
                self.vy = -abs(self.vy)

            # Collision with bricks
            hit_brick = None
            for brick in bricks:
                if brick.rect.colliderect(ball_rect) and brick.alive:
                    hit_brick = brick
                    brick.alive = False
                    score += brick.points
                    if brick.has_powerup:
                        powerup = PowerUp(brick.rect.x + brick.rect.width // 2,
                                          brick.rect.y + brick.rect.height // 2,
                                          random.choice(['expand', 'slow', 'life']))
                        powerups.append(powerup)

                    # Ball collision direction
                    # Determine from which side the ball hits the brick
                    overlap_left = self.x + self.radius - brick.rect.left
                    overlap_right = brick.rect.right - (self.x - self.radius)
                    overlap_top = self.y + self.radius - brick.rect.top
                    overlap_bottom = brick.rect.bottom - (self.y - self.radius)
                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    if min_overlap == overlap_left or min_overlap == overlap_right:
                        self.vx = -self.vx
                    else:
                        self.vy = -self.vy
                    break
            return score, hit_brick
        except Exception:
            return score, None

    def off_screen(self):
        return self.y - self.radius > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)


class Brick:
    def __init__(self, x, y, color, points, has_powerup=False):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.alive = True
        self.points = points
        self.has_powerup = has_powerup

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)


class PowerUp:
    def __init__(self, x, y, type_):
        self.rect = pygame.Rect(x - POWERUP_WIDTH // 2, y - POWERUP_HEIGHT // 2, POWERUP_WIDTH, POWERUP_HEIGHT)
        self.type = type_
        self.speed = 3
        self.active = True

    def update(self):
        try:
            self.rect.y += self.speed
            if self.rect.y > SCREEN_HEIGHT:
                self.active = False
        except Exception:
            self.active = False

    def draw(self, surface):
        color = YELLOW if self.type == 'expand' else GREEN if self.type == 'life' else PURPLE
        label = '+' if self.type == 'life' else '<<' if self.type == 'expand' else 'S'
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        font = load_font(18)
        label_surf = font.render(label, True, BLACK)
        label_rect = label_surf.get_rect(center=self.rect.center)
        surface.blit(label_surf, label_rect)


class Level:
    def __init__(self, number):
        self.number = number
        self.bricks = []
        self.powerup_rate = 0.14 + 0.025 * number  # Increase powerup drop rate per level
        self.layout = self.generate_layout(number)
        self.create_bricks()

    def generate_layout(self, number):
        layout = []
        # Increase randomness and brick strength as levels progress
        for row in range(BRICK_ROWS):
            layout_row = []
            for col in range(BRICK_COLS):
                if random.random() < 0.8 - 0.06 * number:
                    # There's a brick here
                    layout_row.append(1)
                else:
                    layout_row.append(0)
            layout.append(layout_row)
        return layout

    def create_bricks(self):
        try:
            self.bricks.clear()
            for row_idx, row in enumerate(self.layout):
                for col_idx, brick_present in enumerate(row):
                    if brick_present:
                        x = LEFT_OFFSET + col_idx * (BRICK_WIDTH + BRICK_GAP)
                        y = TOP_OFFSET + row_idx * (BRICK_HEIGHT + BRICK_GAP)
                        color = BRICK_COLORS[row_idx % len(BRICK_COLORS)]
                        points = 50 + (row_idx * 20)
                        has_powerup = random.random() < self.powerup_rate
                        brick = Brick(x, y, color, points, has_powerup)
                        self.bricks.append(brick)
        except Exception:
            pass

    def is_cleared(self):
        return not any(brick.alive for brick in self.bricks)

    def draw(self, surface):
        for brick in self.bricks:
            brick.draw(surface)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout Game")
        self.clock = pygame.time.Clock()
        self.font = load_font(24)
        self.big_font = load_font(56)
        self.level_number = 1
        self.score = 0
        self.lives = MAX_LIVES
        self.high_score = 0
        self.game_over = False
        self.paddle = Paddle(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ball = Ball(self.paddle)
        self.powerups = []
        self.load_highscore()
        self.start_level(self.level_number)
        self.left_pressed = False
        self.right_pressed = False

    def load_highscore(self):
        try:
            with open("breakout_highscore.txt", "r") as f:
                self.high_score = int(f.read().strip())
        except Exception:
            self.high_score = 0

    def save_highscore(self):
        try:
            with open("breakout_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def start_level(self, level_number):
        try:
            self.level = Level(level_number)
            self.ball = Ball(self.paddle)
            self.powerups.clear()
        except Exception:
            pass

    def reset_game(self):
        self.level_number = 1
        self.score = 0
        self.lives = MAX_LIVES
        self.game_over = False
        self.paddle = Paddle(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ball = Ball(self.paddle)
        self.powerups.clear()
        self.start_level(self.level_number)

    def update(self):
        # Handle paddle movement
        keys = pygame.key.get_pressed()
        self.left_pressed = keys[pygame.K_LEFT]
        self.right_pressed = keys[pygame.K_RIGHT]

        # Mouse paddle movement
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_x, _ = pygame.mouse.get_pos()
        if mouse_buttons[0]:
            self.paddle.move(mouse_x=mouse_x)
        else:
            self.paddle.move(left=self.left_pressed, right=self.right_pressed)

        # Update ball
        self.score, _ = self.ball.update(self.paddle, self.level.bricks, self.powerups, self.score)

        # Update powerups
        for powerup in self.powerups:
            powerup.update()

        # Powerup collision with paddle
        for powerup in self.powerups:
            if powerup.active and powerup.rect.colliderect(self.paddle.rect):
                if powerup.type == 'expand':
                    self.paddle.width = min(self.paddle.width + 50, SCREEN_WIDTH // 2)
                elif powerup.type == 'slow':
                    self.ball.vx *= 0.7
                    self.ball.vy *= 0.7
                elif powerup.type == 'life':
                    if self.lives < MAX_LIVES:
                        self.lives += 1
                powerup.active = False

        # Remove inactive powerups
        self.powerups = [p for p in self.powerups if p.active]

        # Ball falls below the screen
        if self.ball.off_screen():
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_highscore()
            else:
                self.ball = Ball(self.paddle)
                self.powerups.clear()

        # Level cleared
        if self.level.is_cleared():
            self.level_number += 1
            self.start_level(self.level_number)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_highscore()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.ball.launched and not self.game_over:
                    self.ball.launch()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN and not self.ball.launched and not self.game_over:
                self.ball.launch()

    def draw_hud(self):
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        hs_surf = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
        level_surf = self.font.render(f"Level: {self.level_number}", True, WHITE)
        self.screen.blit(lives_surf, (10, 10))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - 60, 10))
        self.screen.blit(hs_surf, (SCREEN_WIDTH - 220, 10))
        self.screen.blit(level_surf, (SCREEN_WIDTH // 2 + 70, 10))
        instr_surf = self.font.render("←/→ or Mouse to move. SPACE/MOUSE to launch ball.", True, GRAY)
        self.screen.blit(instr_surf, (SCREEN_WIDTH // 2 - instr_surf.get_width() // 2, SCREEN_HEIGHT - 38))

    def draw(self):
        self.screen.fill(BLACK)
        self.level.draw(self.screen)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        self.draw_hud()
        if self.game_over:
            over_surf = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(over_surf, (SCREEN_WIDTH // 2 - over_surf.get_width() // 2, SCREEN_HEIGHT // 2 - over_surf.get_height()))
            rest_surf = self.font.render("Press 'R' to restart or close window.", True, GRAY)
            self.screen.blit(rest_surf, (SCREEN_WIDTH // 2 - rest_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        elif self.level.is_cleared():
            win_surf = self.font.render("Level Cleared! Get ready for next level...", True, GREEN)
            self.screen.blit(win_surf, (SCREEN_WIDTH // 2 - win_surf.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

    def run(self):
        try:
            while True:
                self.clock.tick(FPS)
                self.handle_events()
                if not self.game_over and not self.level.is_cleared():
                    self.update()
                self.draw()
        except Exception:
            pygame.quit()
            sys.exit()


def main():
    try:
        game = Game()
        game.run()
    except Exception:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()