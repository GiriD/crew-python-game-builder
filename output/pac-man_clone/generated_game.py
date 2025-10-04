import pygame
import sys
import random

# Game constants
SCREEN_WIDTH = 608
SCREEN_HEIGHT = 672
TILE_SIZE = 32
MAZE_ROWS = 21
MAZE_COLS = 19
FPS = 60
PLAYER_SPEED = 4
GHOST_SPEED = 2

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
DOT_COLOR = (255, 255, 255)
WALL_COLOR = (0, 0, 128)

# Maze layout using ASCII: '#' = wall, '.' = dot, ' ' = empty, 'P' = player start, 'G' = ghost start
MAZE_LAYOUT = [
    "###################",
    "#........#........#",
    "#.###.###.#.###.###",
    "#G###.###.#.###.G##",
    "#.................#",
    "#.###.#.#####.#.###",
    "#.....#...#...#...#",
    "#####.### # ###.###",
    "    #.#       #.#  ",
    "#####.# ## ## #.###",
    "     .  #P#  .     ",
    "#####.# ##### #.###",
    "    #.#       #.#  ",
    "#####.# ##### #.###",
    "#........#........#",
    "#.###.###.#.###.###",
    "#G..#..... .....G.#",
    "###.#.#.#####.#.###",
    "#.....#...#...#...#",
    "#.######### ########",
    "###################"
]

class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.dots = []
        self.walls = []
        self.player_start = None
        self.ghost_starts = []
        self.parse_maze()

    def parse_maze(self):
        # Parse maze layout, populate dots, walls, player and ghost start positions
        for row_idx, row in enumerate(self.layout):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if cell == '#':
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif cell == '.':
                    self.dots.append(Dot(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                elif cell == 'P':
                    self.player_start = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif cell == 'G':
                    self.ghost_starts.append((x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                elif cell == ' ':
                    continue

    def draw(self, screen):
        # Draw the maze walls and dots
        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)
        for dot in self.dots:
            dot.draw(screen)

    def get_tile(self, x, y):
        # Get cell content at given (x,y) maze tile
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
            return self.layout[row][col]
        return '#'

    def is_wall(self, x, y):
        # Return True if given position is a wall
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
            return self.layout[row][col] == '#'
        return True

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 4
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        pygame.draw.circle(screen, DOT_COLOR, (self.x, self.y), self.radius)

class Player:
    def __init__(self, x, y, maze):
        self.x = x
        self.y = y
        self.maze = maze
        self.radius = TILE_SIZE // 2 - 2
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        # Handle direction change when available
        if self.can_move(*self.next_direction):
            self.direction = self.next_direction
        if self.can_move(*self.direction):
            self.x += self.direction[0] * PLAYER_SPEED
            self.y += self.direction[1] * PLAYER_SPEED
        # Update rect
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        # Wrap around
        self.x = self.x % SCREEN_WIDTH
        self.y = self.y % SCREEN_HEIGHT

    def can_move(self, dx, dy):
        # Predict next position and check collision with wall
        next_x = self.x + dx * PLAYER_SPEED
        next_y = self.y + dy * PLAYER_SPEED
        bbox = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius * 2, self.radius * 2)
        for wall in self.maze.walls:
            if bbox.colliderect(wall):
                return False
        return True

    def set_next_direction(self, direction):
        self.next_direction = direction

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class Ghost:
    COLORS = [RED, PINK, CYAN, ORANGE]
    def __init__(self, x, y, maze, color_idx):
        self.x = x
        self.y = y
        self.maze = maze
        self.radius = TILE_SIZE // 2 - 3
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = Ghost.COLORS[color_idx % len(Ghost.COLORS)]
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.move_counter = 0

    def update(self, player_pos):
        # Simple AI: try to move toward player, but randomly change directions
        self.move_counter += 1
        if self.move_counter % 13 == 0:
            options = self.possible_directions()
            # Prefer direction toward player if possible
            px, py = player_pos
            dx = px - self.x
            dy = py - self.y
            preferred = []
            if abs(dx) > abs(dy):
                if dx > 0:
                    preferred.append((1, 0))
                else:
                    preferred.append((-1, 0))
            if dy > 0:
                preferred.append((0, 1))
            else:
                preferred.append((0, -1))
            # Pick preferred if not blocked
            for pref in preferred:
                if pref in options:
                    self.direction = pref
                    break
            else:
                if options:
                    self.direction = random.choice(options)

        if self.can_move(*self.direction):
            self.x += self.direction[0] * GHOST_SPEED
            self.y += self.direction[1] * GHOST_SPEED
        else:
            options = self.possible_directions()
            if options:
                self.direction = random.choice(options)
        # Update rect
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        # Wrap around
        self.x = self.x % SCREEN_WIDTH
        self.y = self.y % SCREEN_HEIGHT

    def can_move(self, dx, dy):
        next_x = self.x + dx * GHOST_SPEED
        next_y = self.y + dy * GHOST_SPEED
        bbox = pygame.Rect(next_x - self.radius, next_y - self.radius, self.radius * 2, self.radius * 2)
        for wall in self.maze.walls:
            if bbox.colliderect(wall):
                return False
        return True

    def possible_directions(self):
        directions = []
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            if self.can_move(*d):
                directions.append(d)
        return directions

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Eye white
        pygame.draw.circle(screen, WHITE, (int(self.x-8), int(self.y-2)), 6)
        pygame.draw.circle(screen, WHITE, (int(self.x+8), int(self.y-2)), 6)
        # Eye pupils toward player's direction
        pygame.draw.circle(screen, BLACK, (int(self.x-8), int(self.y-2)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x+8), int(self.y-2)), 2)
        # Little trailing squiggles using lines
        for i in range(4):
            pygame.draw.line(screen, self.color, (int(self.x-12+6*i), int(self.y+12)), (int(self.x-10+6*i), int(self.y+16)), 3)

def draw_text(screen, text, x, y, size=32, color=WHITE, center=True):
    # Render text to the screen
    font = pygame.font.SysFont("arial", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Clone")
        self.clock = pygame.time.Clock()
        self.maze = Maze(MAZE_LAYOUT)
        self.score = 0
        self.game_over = False
        self.win = False
        self.restart_delay = 0
        self.init_entities()

    def init_entities(self):
        # Start positions from maze
        player_pos = self.maze.player_start if self.maze.player_start else (TILE_SIZE * MAZE_COLS // 2, TILE_SIZE * (MAZE_ROWS // 2))
        self.player = Player(player_pos[0], player_pos[1], self.maze)
        self.ghosts = []
        color_idx = 0
        if not self.maze.ghost_starts:
            # Default ghosts if none specified
            self.maze.ghost_starts = [
                (TILE_SIZE*1 + TILE_SIZE//2, TILE_SIZE*1 + TILE_SIZE//2),
                (TILE_SIZE*(MAZE_COLS-2) + TILE_SIZE//2, TILE_SIZE*1 + TILE_SIZE//2)
            ]
        for gx, gy in self.maze.ghost_starts:
            self.ghosts.append(Ghost(gx, gy, self.maze, color_idx))
            color_idx += 1
        self.score = 0
        self.game_over = False
        self.win = False
        self.restart_delay = 0

    def handle_input(self):
        # Handle keyboard events for movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over or self.win:
                    if event.key == pygame.K_SPACE and self.restart_delay == 0:
                        self.maze = Maze(MAZE_LAYOUT)
                        self.init_entities()
                        continue
                if event.key == pygame.K_UP:
                    self.player.set_next_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.player.set_next_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.player.set_next_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.player.set_next_direction((1, 0))

    def update(self):
        if self.game_over or self.win:
            if self.restart_delay > 0:
                self.restart_delay -= 1
            return

        self.player.update()
        for ghost in self.ghosts:
            ghost.update((self.player.x, self.player.y))

        # Collisions with dots
        player_rect = pygame.Rect(self.player.x - self.player.radius, self.player.y - self.player.radius, self.player.radius * 2, self.player.radius * 2)
        dots_to_remove = []
        for dot in self.maze.dots:
            if player_rect.colliderect(dot.rect):
                dots_to_remove.append(dot)
                self.score += 10
        for dot in dots_to_remove:
            if dot in self.maze.dots:
                self.maze.dots.remove(dot)

        # Win condition
        if not self.maze.dots:
            self.win = True
            self.restart_delay = FPS * 2

        # Collisions with ghosts
        for ghost in self.ghosts:
            ghost_rect = pygame.Rect(ghost.x - ghost.radius, ghost.y - ghost.radius, ghost.radius * 2, ghost.radius * 2)
            if player_rect.colliderect(ghost_rect):
                self.game_over = True
                self.restart_delay = FPS * 2

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        # Draw score
        draw_text(self.screen, f"Score: {self.score}", 100, SCREEN_HEIGHT - 24, size=24, color=YELLOW, center=False)

        if self.win:
            draw_text(self.screen, "YOU WIN!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, size=48, color=YELLOW)
            draw_text(self.screen, "Press SPACE to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, size=32, color=WHITE)
        elif self.game_over:
            draw_text(self.screen, "GAME OVER!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, size=48, color=RED)
            draw_text(self.screen, "Press SPACE to restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, size=32, color=WHITE)

        pygame.display.flip()

    def run(self):
        # Main game loop with error handling
        try:
            while True:
                self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            pygame.quit()
            print("An error occurred:", e)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()