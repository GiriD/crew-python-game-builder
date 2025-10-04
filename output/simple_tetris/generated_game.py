import pygame
import sys
import random
import time

# Game configuration constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
TOP_MARGIN = 60
RIGHT_PANEL = 140

FPS = 60
START_SPEED = 500  # ms between drops
SPEEDUP_STEP = 1000  # points per speed up

# Tetromino shapes and rotations
TETROMINOS = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]]
    ]
}

# Tetromino colors
TETROMINO_COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0)
}

# Line clear animation color
ANIM_COLOR = (255, 255, 255)

class Tetromino:
    def __init__(self, shape, grid):
        self.shape_key = shape
        self.rot = 0
        self.shapes = TETROMINOS[self.shape_key]
        self.color = TETROMINO_COLORS[self.shape_key]
        self.size = len(self.shapes[0])
        self.x = GRID_WIDTH // 2 - self.size // 2
        self.y = 0
        self.grid = grid  # allows access to grid for collision

    def get_blocks(self, x_offset=0, y_offset=0, rot_idx=None):
        blocks = []
        r = rot_idx if rot_idx is not None else self.rot
        shape = self.shapes[r]
        for dy in range(self.size):
            for dx in range(self.size):
                if dy < len(shape) and dx < len(shape[dy]) and shape[dy][dx]:
                    blocks.append((self.x + dx + x_offset, self.y + dy + y_offset))
        return blocks

    def can_move(self, dx, dy, rot_change=0):
        try:
            new_rot = (self.rot + rot_change) % len(self.shapes)
            for x, y in self.get_blocks(dx, dy, new_rot):
                if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                    return False
                if self.grid[y][x]:
                    return False
            return True
        except Exception as ex:
            return False

    def move(self, dx, dy):
        if self.can_move(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        if self.can_move(0, 0, 1):
            self.rot = (self.rot + 1) % len(self.shapes)
            return True
        else:
            # Wall kick: try moving left or right
            if self.can_move(-1, 0, 1):
                self.x -= 1
                self.rot = (self.rot + 1) % len(self.shapes)
                return True
            elif self.can_move(1, 0, 1):
                self.x += 1
                self.rot = (self.rot + 1) % len(self.shapes)
                return True
        return False

class TetrisGame:
    def __init__(self):
        # Initialize pygame and window
        pygame.init()
        pygame.display.set_caption('Simple Tetris')
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH + RIGHT_PANEL, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        # Setup font
        self.font = pygame.font.SysFont('Calibri', 24, True)
        self.small_font = pygame.font.SysFont('Calibri', 18)
        # Game state
        self.reset()

    def reset(self):
        # Initialize playfield (empty grid)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        # Score, level, speed
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = START_SPEED
        self.last_drop_time = pygame.time.get_ticks()
        self.game_over = False
        self.animating = False
        self.anim_lines = []
        self.anim_time = 0
        # Generate tetrominoes
        self.bag = []
        self.next_piece = self.get_next_piece()
        self.tetromino = self.get_next_piece()
        self.hold = None
        self.hold_locked = False

    def get_next_piece(self):
        # 7-bag randomization: ensures more balanced distribution
        if not self.bag:
            self.bag = list(TETROMINOS.keys())
            random.shuffle(self.bag)
        shape = self.bag.pop()
        return Tetromino(shape, self.grid)

    def lock_tetromino(self):
        # Place current tetromino on grid
        for x, y in self.tetromino.get_blocks():
            if y < 0:
                continue  # Ignore blocks above visible grid
            self.grid[y][x] = self.tetromino.color
        self.tetromino = None

    def line_clear_check(self):
        # Find complete rows
        full_rows = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                full_rows.append(y)
        return full_rows

    def animate_line_clear(self, lines):
        # Start line clear animation
        self.animating = True
        self.anim_lines = lines[:]
        self.anim_time = pygame.time.get_ticks()

    def perform_line_clear(self):
        # Clear lines and shift above down
        for y in sorted(self.anim_lines):
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        # Update score and level
        line_count = len(self.anim_lines)
        self.lines_cleared += line_count
        base_points = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.score += base_points.get(line_count, 0) * self.level
        self.level = self.lines_cleared // 10 + 1
        self.speed = max(100, START_SPEED - (self.level - 1) * 35)
        self.animating = False
        self.anim_lines = []

    def soft_drop(self):
        if not self.game_over and self.tetromino:
            if not self.tetromino.move(0, 1):
                self.lock_tetromino()
                self.process_post_lock()

    def hard_drop(self):
        if not self.game_over and self.tetromino:
            while self.tetromino.move(0, 1):
                pass
            self.lock_tetromino()
            self.process_post_lock()

    def process_post_lock(self):
        # Check finished block for completed lines
        lines = self.line_clear_check()
        if lines:
            self.animate_line_clear(lines)
        else:
            self.spawn_new_tetromino()
            self.hold_locked = False

    def spawn_new_tetromino(self):
        self.tetromino = self.next_piece
        self.tetromino.grid = self.grid
        self.next_piece = self.get_next_piece()
        # Check for game over (if spawn collides)
        if not self.tetromino.can_move(0, 0):
            self.game_over = True

    def update(self):
        # If animating line clear, pause dropping
        if self.animating:
            elapsed = pygame.time.get_ticks() - self.anim_time
            if elapsed > 200:
                self.perform_line_clear()
                self.spawn_new_tetromino()
                self.hold_locked = False
            return
        # Drop tetromino by speed timing
        now = pygame.time.get_ticks()
        if self.tetromino and now - self.last_drop_time > self.speed:
            if not self.tetromino.move(0, 1):
                self.lock_tetromino()
                self.process_post_lock()
            self.last_drop_time = now

    def handle_events(self):
        # Keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not self.game_over and event.type == pygame.KEYDOWN:
                if not self.animating:
                    try:
                        if event.key == pygame.K_LEFT:
                            self.tetromino.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.tetromino.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.soft_drop()
                        elif event.key == pygame.K_UP:
                            self.tetromino.rotate()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                    except Exception as ex:
                        pass
            if self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset()

    def draw_grid(self, surf, offset_x, offset_y):
        # Draw grid lines
        for y in range(GRID_HEIGHT + 1):
            py = offset_y + y * BLOCK_SIZE
            pygame.draw.line(
                surf, (30, 30, 30),
                (offset_x, py), (offset_x + GRID_WIDTH * BLOCK_SIZE, py))
        for x in range(GRID_WIDTH + 1):
            px = offset_x + x * BLOCK_SIZE
            pygame.draw.line(
                surf, (30, 30, 30),
                (px, offset_y), (px, offset_y + GRID_HEIGHT * BLOCK_SIZE))

    def draw_playfield(self):
        px = 20
        py = TOP_MARGIN
        # Draw playfield background
        play_rect = pygame.Rect(px, py, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(self.screen, (18, 18, 28), play_rect)
        # Draw locked blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x]
                if color:
                    self.draw_block(x, y, color, px, py)
        # Animate cleared lines (flash white)
        if self.animating:
            for y in self.anim_lines:
                for x in range(GRID_WIDTH):
                    self.draw_block(x, y, ANIM_COLOR, px, py)
        # Draw falling tetromino
        if self.tetromino and not self.animating:
            for x, y in self.tetromino.get_blocks():
                if y >= 0:
                    self.draw_block(x, y, self.tetromino.color, px, py)
        # Draw grid
        self.draw_grid(self.screen, px, py)

    def draw_block(self, x, y, color, px_off, py_off):
        # Draw single block with border
        r = pygame.Rect(
            px_off + x * BLOCK_SIZE, py_off + y * BLOCK_SIZE,
            BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, color, r)
        pygame.draw.rect(self.screen, (240, 240, 240), r, 2)

    def draw_next_piece(self):
        # Draw "Next" panel
        px = WINDOW_WIDTH + 20
        py = TOP_MARGIN
        pygame.draw.rect(
            self.screen, (18, 18, 28),
            (px, py, RIGHT_PANEL - 40, 110))
        label = self.small_font.render("Next:", True, (230, 230, 230))
        self.screen.blit(label, (px + 12, py + 5))
        # Draw next tetromino in panel
        tet = self.next_piece
        shape = tet.shapes[0]
        color = tet.color
        size = len(shape)
        for dy in range(size):
            for dx in range(size):
                if dy < len(shape) and dx < len(shape[dy]) and shape[dy][dx]:
                    self.draw_block(dx, dy, color,
                                    px + 22, py + 32)

    def draw_score_level(self):
        # Display score, level, and lines
        s = self.font.render(f"Score: {self.score}", True, (245, 245, 245))
        l = self.font.render(f"Level: {self.level}", True, (210, 210, 245))
        lines = self.small_font.render(f"Lines: {self.lines_cleared}", True, (210, 210, 245))
        self.screen.blit(s, (WINDOW_WIDTH + 24, TOP_MARGIN + 140))
        self.screen.blit(l, (WINDOW_WIDTH + 24, TOP_MARGIN + 170))
        self.screen.blit(lines, (WINDOW_WIDTH + 24, TOP_MARGIN + 200))

    def draw_title(self):
        # Game title
        logo = self.font.render("Simple Tetris", True, (220, 240, 255))
        self.screen.blit(logo, (WINDOW_WIDTH // 2 - 65, 10))

    def draw_game_over(self):
        # Game over overlay
        surface = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
        surface.fill((40, 10, 10, 140))
        px = 20
        py = TOP_MARGIN
        self.screen.blit(surface, (px, py))
        msg = self.font.render("GAME OVER!", True, (255, 70, 70))
        self.screen.blit(msg, (px + 45, py + 240))
        press = self.small_font.render("Press Enter to Restart", True, (255, 255, 240))
        self.screen.blit(press, (px + 33, py + 272))

    def run(self):
        # Main game loop
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.game_over:
                self.update()
            self.render()

    def render(self):
        self.screen.fill((10, 15, 22))
        self.draw_title()
        self.draw_playfield()
        self.draw_next_piece()
        self.draw_score_level()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

def main():
    try:
        game = TetrisGame()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()