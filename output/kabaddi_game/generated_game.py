import pygame
import sys
import random
from enum import Enum, auto

# Constants (Theme colors, court, game)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FPS = 60
TEAM_SIZE = 5
PLAYER_RADIUS = 24
COURT_MARGIN = 72
BREATH_MAX = 100
RAID_TIME_LIMIT = 15 # seconds per raid
ROUNDS_PER_MATCH = 2
SUBSTITUTIONS_PER_ROUND = 2
FONT_NAME = 'arial'
# Color palette (Accessible)
COLOR_RED = (216, 67, 21)
COLOR_BLUE = (25, 118, 210)
COLOR_SAND = (251, 233, 231)
COLOR_GOLD = (255, 214, 0)
COLOR_SLATE = (38, 50, 56)
COLOR_GRAY = (176, 190, 197)
COLOR_GREEN = (56, 142, 60)
COLOR_ORANGE = (255, 111, 0)
COLOR_CYAN = (0, 188, 212)
COLOR_WHITE = (255, 255, 255)
COLOR_DANGER = (255, 82, 82)

# Enum for Player State
class PlayerState(Enum):
    ACTIVE = auto()
    TAGGED = auto()
    OUT = auto()
    SUBBED = auto()

class GameStateEnum(Enum):
    MENU = auto()
    ROUND_START = auto()
    RAID = auto()
    TACKLE = auto()
    END_ROUND = auto()
    GAME_OVER = auto()
    PAUSE = auto()

class KabaddiException(Exception):
    pass

class Logger:
    @staticmethod
    def log(message):
        print("[KabaddiGame]", message)

# Player Class (Entity)
class Player(pygame.sprite.Sprite):
    def __init__(self, id, team_name, position, is_raider=False, jersey_num=0):
        super().__init__()
        self.id = id
        self.team_name = team_name
        self.position = position.copy()
        self.is_raider = is_raider
        self.state = PlayerState.ACTIVE
        self.breath_meter = BREATH_MAX
        self.jersey_num = jersey_num
        self.tackled = False
        self.color = COLOR_RED if team_name == "Red" else COLOR_BLUE
        self.out_timer = 0
        self.radius = PLAYER_RADIUS
        self.subbed = False
        # For rendering: create simple avatar
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(position[0], position[1]))
        self.update_avatar()
    def update_avatar(self):
        self.image.fill((0,0,0,0))
        glow = COLOR_CYAN if self.is_raider and self.breath_meter > 25 else COLOR_DANGER if self.is_raider else self.color
        pygame.draw.circle(self.image, glow, (self.radius, self.radius), self.radius+3)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius-3)
        font = pygame.font.SysFont(FONT_NAME, 24)
        text_color = COLOR_WHITE if self.color != COLOR_WHITE else COLOR_SLATE
        text = font.render(str(self.jersey_num), True, text_color)
        text_rect = text.get_rect(center=(self.radius, self.radius))
        self.image.blit(text, text_rect)
        if self.is_raider:
            rfont = pygame.font.SysFont(FONT_NAME, 16, bold=True)
            rtext = rfont.render("R", True, COLOR_CYAN)
            self.image.blit(rtext, (self.radius-15, self.radius-18))
    def move(self, dx, dy, court_rect):
        nx = self.position[0] + dx
        ny = self.position[1] + dy
        if court_rect.collidepoint(nx, ny):
            self.position[0] = nx
            self.position[1] = ny
            self.rect.center = (nx, ny)
        else:
            # Out of bounds, only allow if raider is retreating
            if self.is_raider:
                self.state = PlayerState.OUT
    def tag(self, target):
        if self.is_raider and target.state == PlayerState.ACTIVE and not target.is_raider:
            target.state = PlayerState.TAGGED
            Logger.log(f"Raider {self.jersey_num} tagged defender {target.jersey_num}")
            return True
        return False
    def tackle(self, raider):
        if not self.is_raider and self.state == PlayerState.ACTIVE:
            dist = ((self.position[0] - raider.position[0])**2 + (self.position[1] - raider.position[1])**2)**0.5
            if dist <= PLAYER_RADIUS*2:
                raider.state = PlayerState.OUT
                self.tackled = True
                Logger.log(f"Defender {self.jersey_num} tackled raider {raider.jersey_num}")
                return True
        return False
    def update_breath(self, dt):
        if self.is_raider and self.state == PlayerState.ACTIVE:
            self.breath_meter -= dt*5
            if self.breath_meter < 0:
                self.breath_meter = 0
                self.state = PlayerState.OUT
        else:
            self.breath_meter = BREATH_MAX
    def update(self):
        self.rect.center = (self.position[0], self.position[1])
        self.update_avatar()
    def sub_out(self):
        self.subbed = True
        self.state = PlayerState.SUBBED
        Logger.log(f"Player {self.jersey_num} subbed out.")
    def sub_in(self, position):
        self.subbed = False
        self.state = PlayerState.ACTIVE
        self.position = position.copy()
        self.rect.center = (self.position[0], self.position[1])
        Logger.log(f"Substitute player {self.jersey_num} in.")

# Team Class
class Team:
    def __init__(self, name, side):
        self.name = name
        self.side = side  # 'left' or 'right'
        self.players = []
        self.active_players = []
        self.subs = []
        self.score = 0
        self.badge_color = COLOR_RED if name == "Red" else COLOR_BLUE
    def get_active(self):
        return [p for p in self.players if p.state == PlayerState.ACTIVE]
    def substitute(self, in_player, out_player, position):
        try:
            if out_player in self.active_players and in_player in self.subs:
                out_player.sub_out()
                self.active_players.remove(out_player)
                self.subs.remove(in_player)
                in_player.sub_in(position)
                self.active_players.append(in_player)
                Logger.log(f"Substitution: {out_player.jersey_num} -> {in_player.jersey_num}")
            else:
                raise KabaddiException("Invalid substitution attempt.")
        except Exception as e:
            Logger.log(f"Substitution error: {e}")
    def reset_team(self, court_rect):
        # Reset all players and positions
        home_x = court_rect.left + COURT_MARGIN if self.side == 'left' else court_rect.right - COURT_MARGIN
        ystep = (court_rect.bottom - court_rect.top - COURT_MARGIN*2) // (TEAM_SIZE-1)
        for idx, p in enumerate(self.players):
            p.position = [home_x, court_rect.top + COURT_MARGIN + idx*ystep]
            p.rect.center = tuple(p.position)
            p.state = PlayerState.ACTIVE
            p.subbed = False
            p.tackled = False
            p.breath_meter = BREATH_MAX
            p.is_raider = False
            p.update_avatar()
        self.active_players = self.players[:TEAM_SIZE]
        self.subs = [p for p in self.players if p not in self.active_players]
    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)
            if len(self.active_players) < TEAM_SIZE:
                self.active_players.append(player)
            else:
                self.subs.append(player)

# AI Controller (for defenders as default)
class AIController:
    def __init__(self, team, court_rect):
        self.team = team
        self.court_rect = court_rect
    def decide_action(self, defenders, raider, dt):
        # Simple AI: Move toward raider, attempt tackle if close
        for defender in defenders:
            if defender.state != PlayerState.ACTIVE:
                continue
            dx = raider.position[0] - defender.position[0]
            dy = raider.position[1] - defender.position[1]
            dist = max(1, (dx**2 + dy**2)**0.5)
            # Only move if on own half
            if defender.team_name != raider.team_name:
                move_dist = 1.2 * dt * 60
                defender.move(dx/dist*move_dist, dy/dist*move_dist, self.court_rect)
                # Try tackle
                if defender.tackle(raider):
                    Logger.log(f"AI defender {defender.jersey_num} tackled raider {raider.jersey_num}")

# Input Handler for user events
class InputHandler:
    def __init__(self):
        self.actions = {'up': False, 'down': False, 'left': False, 'right': False, 'tag': False, 'retreat': False, 'tackle': False, 'pause': False}
    def process_events(self):
        ret = self.actions.copy()
        for key in self.actions.keys():
            ret[key] = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ret['up'] = True
                if event.key == pygame.K_DOWN:
                    ret['down'] = True
                if event.key == pygame.K_LEFT:
                    ret['left'] = True
                if event.key == pygame.K_RIGHT:
                    ret['right'] = True
                if event.key == pygame.K_SPACE:
                    ret['tag'] = True
                if event.key == pygame.K_RETURN:
                    ret['retreat'] = True
                if event.key == pygame.K_t:
                    ret['tackle'] = True
                if event.key == pygame.K_p:
                    ret['pause'] = True
        return ret

# Renderer
class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)
    def draw_court(self):
        court_rect = pygame.Rect(COURT_MARGIN, COURT_MARGIN, SCREEN_WIDTH-2*COURT_MARGIN, SCREEN_HEIGHT-2*COURT_MARGIN)
        self.screen.fill(COLOR_SAND)
        pygame.draw.rect(self.screen, COLOR_GOLD, court_rect, 8)
        pygame.draw.line(self.screen, COLOR_SLATE, (SCREEN_WIDTH//2, COURT_MARGIN), (SCREEN_WIDTH//2, SCREEN_HEIGHT-COURT_MARGIN), 6)
        return court_rect
    def draw_players(self, teams):
        sprites = pygame.sprite.Group()
        for team in teams:
            for player in team.players:
                sprites.add(player)
        sprites.draw(self.screen)
        for team in teams:
            for player in team.players:
                if player.is_raider:
                    if player.breath_meter < 25:
                        warn_txt = self.small_font.render("Breath Low! Retreat!", True, COLOR_DANGER)
                        self.screen.blit(warn_txt, (player.position[0]-50, player.position[1]-38))
    def draw_ui(self, game, state):
        # Scoreboard
        bar = pygame.Rect(SCREEN_WIDTH//2-130, 18, 260, 44)
        pygame.draw.rect(self.screen, COLOR_SLATE, bar, border_radius=12)
        tA = self.font.render(f"Red: {game.teams[0].score}", True, COLOR_WHITE)
        tB = self.font.render(f"Blue: {game.teams[1].score}", True, COLOR_WHITE)
        self.screen.blit(tA, (SCREEN_WIDTH//2-120, 26))
        self.screen.blit(tB, (SCREEN_WIDTH//2+36, 26))
        rnd_txt = self.font.render(f"Round {game.round_manager.current_round+1}/{ROUNDS_PER_MATCH}", True, COLOR_GOLD)
        self.screen.blit(rnd_txt, (SCREEN_WIDTH//2-70, 62))
        # Breath Meter
        for team in game.teams:
            raider = [p for p in team.active_players if p.is_raider]
            if raider:
                r = raider[0]
                meter_x = 48 if team.name == "Red" else SCREEN_WIDTH-200
                pygame.draw.rect(self.screen, COLOR_GRAY, (meter_x, 80, 140, 18), border_radius=8)
                breath_col = COLOR_CYAN if r.breath_meter > 25 else COLOR_DANGER
                width = int(140*r.breath_meter/BREATH_MAX)
                pygame.draw.rect(self.screen, breath_col, (meter_x, 80, width, 18), border_radius=8)
                btxt = self.small_font.render(f"Breath: {int(r.breath_meter)}", True, COLOR_SLATE)
                self.screen.blit(btxt, (meter_x+28, 82))
        # Substitution/Info panel
        info_rect = pygame.Rect(24, SCREEN_HEIGHT-70, SCREEN_WIDTH-48, 44)
        pygame.draw.rect(self.screen, COLOR_SLATE, info_rect, border_radius=12)
        txt = "Space: Tag | Enter: Retreat | T: Tackle | P: Pause"
        control_txt = self.small_font.render(txt, True, COLOR_WHITE)
        self.screen.blit(control_txt, (info_rect.left+18, info_rect.top+8))
        # Pause indication
        if state.current_state == GameStateEnum.PAUSE:
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((38, 50, 56, 160))
            self.screen.blit(pause_overlay, (0,0))
            pausetxt = self.font.render("PAUSED", True, COLOR_GOLD)
            self.screen.blit(pausetxt, (SCREEN_WIDTH//2-60, SCREEN_HEIGHT//2-30))

    def draw_menu(self):
        self.screen.fill(COLOR_SAND)
        title = pygame.font.SysFont(FONT_NAME, 54, bold=True).render("Kabaddi Game", True, COLOR_GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2-title.get_width()//2, 60))
        start_btn = pygame.font.SysFont(FONT_NAME, 36).render("Start New Match", True, COLOR_RED)
        self.screen.blit(start_btn, (SCREEN_WIDTH//2-start_btn.get_width()//2, 170))
        team_txt = pygame.font.SysFont(FONT_NAME, 24, bold=True).render("Team Red vs Team Blue", True, COLOR_SLATE)
        self.screen.blit(team_txt, (SCREEN_WIDTH//2-team_txt.get_width()//2, 226))
        info = self.small_font.render("Press Enter to Start | P: Settings | H: Help", True, COLOR_SLATE)
        self.screen.blit(info, (SCREEN_WIDTH//2-info.get_width()//2, 290))
    def draw_game_over(self, winner, game):
        self.screen.fill(COLOR_SAND)
        overtxt = pygame.font.SysFont(FONT_NAME, 54, bold=True).render("Game Over!", True, COLOR_GOLD)
        self.screen.blit(overtxt, (SCREEN_WIDTH//2-overtxt.get_width()//2, 80))
        winner_txt = pygame.font.SysFont(FONT_NAME, 36).render(f"Winner: {winner}", True, COLOR_GREEN)
        self.screen.blit(winner_txt, (SCREEN_WIDTH//2-winner_txt.get_width()//2, 164))
        sc_txt = self.font.render(f"Red: {game.teams[0].score}   Blue: {game.teams[1].score}", True, COLOR_SLATE)
        self.screen.blit(sc_txt, (SCREEN_WIDTH//2-sc_txt.get_width()//2, 220))
        btn = pygame.font.SysFont(FONT_NAME, 28, bold=True).render("Enter: Replay | Esc: Menu", True, COLOR_GOLD)
        self.screen.blit(btn, (SCREEN_WIDTH//2-btn.get_width()//2, 310))

# Round Manager (Singleton/manager)
class RoundManager:
    def __init__(self):
        self.current_round = 0
        self.round_time = 60
        self.timer = 0
        self.teams_switched = False
        self.active = False
    def start_round(self):
        self.timer = self.round_time
        self.teams_switched = False
        self.active = True
    def switch_teams(self):
        self.teams_switched = True
    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
                self.timer = 0
    def is_time_up(self):
        return self.timer <= 0

# State Machine
class GameState:
    def __init__(self):
        self.current_state = GameStateEnum.MENU
    def set_state(self, state):
        self.current_state = state
        Logger.log(f"State change: {state.name}")

# Game Class & Loop
class Game:
    def __init__(self, screen, font):
        self.state = GameState()
        self.screen = screen
        self.font = font
        self.renderer = Renderer(screen, font)
        self.input_handler = InputHandler()
        self.round_manager = RoundManager()
        # Teams
        self.teams = [Team("Red", 'left'), Team("Blue", 'right')]
        # Generate players
        court_rect = pygame.Rect(COURT_MARGIN, COURT_MARGIN, SCREEN_WIDTH-2*COURT_MARGIN, SCREEN_HEIGHT-2*COURT_MARGIN)
        for tidx, team in enumerate(self.teams):
            for pid in range(TEAM_SIZE+SUBSTITUTIONS_PER_ROUND):
                x = court_rect.left + COURT_MARGIN if team.side == 'left' else court_rect.right - COURT_MARGIN
                ystep = (court_rect.bottom-court_rect.top-COURT_MARGIN*2)//(TEAM_SIZE)
                y = court_rect.top + COURT_MARGIN + pid * ystep
                p = Player(id=f"{team.name}-{pid}", team_name=team.name, position=[x, y], is_raider=False, jersey_num=pid+1)
                team.add_player(p)
        self.ai_controller = AIController(self.teams[1], court_rect)
        self.active_team_idx = 0
        self.raider_idx = 0
        self.sub_counter = 0
        self.match_over = False
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        for team in self.teams:
            for player in team.players:
                self.all_sprites.add(player)
        self.court_rect = court_rect
        # Sound placeholders
        # self.sounds = ...
    def reset_round(self):
        for team in self.teams:
            team.reset_team(self.court_rect)
        self.active_team_idx = 0 if self.round_manager.current_round % 2 == 0 else 1
        self.raider_idx = 0
        self.sub_counter = 0
        # Set raider for attacking team
        for tidx, team in enumerate(self.teams):
            for p in team.players:
                p.is_raider = False
            if tidx == self.active_team_idx:
                team.active_players[0].is_raider = True
        Logger.log(f"Starting round {self.round_manager.current_round+1}, team {self.teams[self.active_team_idx].name} attacking.")
    def switch_round(self):
        self.round_manager.current_round += 1
        if self.round_manager.current_round < ROUNDS_PER_MATCH:
            self.round_manager.start_round()
            self.reset_round()
            self.state.set_state(GameStateEnum.ROUND_START)
        else:
            self.state.set_state(GameStateEnum.GAME_OVER)
    def calculate_score(self):
        # Points: Successful raid=1+tags, tackle=1 for defending team, out=1 to opposition
        for team in self.teams:
            raider = [p for p in team.active_players if p.is_raider]
            if raider:
                r = raider[0]
                opp_team = self.teams[1] if team == self.teams[0] else self.teams[0]
                if r.state == PlayerState.OUT:
                    opp_team.score += 1 # tackle/out
                else:
                    team.score += 1 # raid success
                    tags = sum([1 for p in opp_team.active_players if p.state == PlayerState.TAGGED])
                    team.score += tags
                    opp_team.score -= tags
                    if opp_team.score < 0: opp_team.score = 0
    def raid_end(self):
        self.calculate_score()
        self.switch_round()
    def update(self, dt):
        actions = self.input_handler.process_events()
        # State machine
        if self.state.current_state == GameStateEnum.MENU:
            if actions['retreat']:
                self.round_manager.start_round()
                self.reset_round()
                self.state.set_state(GameStateEnum.ROUND_START)
        elif self.state.current_state == GameStateEnum.ROUND_START:
            self.round_manager.start_round()
            self.state.set_state(GameStateEnum.RAID)
        elif self.state.current_state == GameStateEnum.RAID:
            self.round_manager.update(dt)
            team = self.teams[self.active_team_idx]
            opp_team = self.teams[1] if self.active_team_idx == 0 else self.teams[0]
            raider = [p for p in team.active_players if p.is_raider][0]
            # Player movement
            mv = 4*dt*60
            dx = dy = 0
            if actions['up']: dy -= mv
            if actions['down']: dy += mv
            if actions['left']: dx -= mv
            if actions['right']: dx += mv
            raider.move(dx, dy, self.court_rect)
            if actions['tag']:
                for defender in opp_team.active_players:
                    # Tag only if close
                    if ((raider.position[0]-defender.position[0])**2 + (raider.position[1]-defender.position[1])**2)**0.5 < PLAYER_RADIUS*2 and defender.state == PlayerState.ACTIVE:
                        raider.tag(defender)
            # Retreat
            if actions['retreat']:
                if (team.side == 'left' and raider.position[0] < SCREEN_WIDTH//2) or (team.side == 'right' and raider.position[0] > SCREEN_WIDTH//2):
                    self.raid_end()
            raider.update_breath(dt)
            for defender in opp_team.active_players:
                defender.update()
            self.ai_controller.decide_action(opp_team.active_players, raider, dt)
            if raider.breath_meter <= 0 or self.round_manager.is_time_up() or raider.state == PlayerState.OUT:
                self.raid_end()
        elif self.state.current_state == GameStateEnum.GAME_OVER:
            if actions['retreat']:
                # Replay
                self.round_manager.current_round = 0
                for team in self.teams:
                    team.score = 0
                self.round_manager.start_round()
                self.reset_round()
                self.state.set_state(GameStateEnum.ROUND_START)
            if actions['tag']:
                pygame.quit()
                sys.exit()
        elif self.state.current_state == GameStateEnum.PAUSE:
            if actions['pause']: # Unpause
                self.state.set_state(GameStateEnum.RAID)
        else:
            # Unhandled state
            pass
    def render(self):
        if self.state.current_state == GameStateEnum.MENU:
            self.renderer.draw_menu()
        elif self.state.current_state == GameStateEnum.GAME_OVER:
            winner = self.teams[0].name if self.teams[0].score > self.teams[1].score else self.teams[1].name if self.teams[0].score != self.teams[1].score else "Draw"
            self.renderer.draw_game_over(winner, self)
        else:
            court_rect = self.renderer.draw_court()
            self.renderer.draw_players(self.teams)
            self.renderer.draw_ui(self, self.state)
        pygame.display.flip()

# Main Entry Point
def main():
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512) # For low-latency audio (future extension)
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Kabaddi Game')
        font = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        clock = pygame.time.Clock()
        game = Game(screen, font)
        dt = 0
        while True:
            dt = clock.tick(FPS)/1000.0
            game.update(dt)
            game.render()
    except Exception as e:
        Logger.log(f"Fatal Error: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()