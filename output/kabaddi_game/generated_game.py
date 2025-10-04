import pygame
import sys
import random
import time

# Constants for game setup
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 600
COURT_MARGIN = 60
COURT_WIDTH = SCREEN_WIDTH - 2 * COURT_MARGIN
COURT_HEIGHT = SCREEN_HEIGHT - 2 * COURT_MARGIN

TEAM_SIZE = 5
PLAYER_RADIUS = 18
RAIDER_COLOR = (255, 0, 0)
DEFENDER_COLOR = (0, 0, 200)
SELECTED_COLOR = (255, 255, 0)
SUB_COLOR = (120, 120, 120)

BREATH_MAX = 8  # seconds that raider can raid
ROUND_TIME = 45  # seconds per round
NUM_ROUNDS = 2

FONT_NAME = 'arial'
FPS = 60

# Exception for game-related errors
class KabaddiGameException(Exception):
    pass

# Player Type Enum
class PlayerType:
    DEFENDER = 0
    RAIDER = 1
    SUB = 2

# Player class
class Player:
    def __init__(self, x, y, team, idx, player_type=PlayerType.DEFENDER):
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.team = team
        self.idx = idx
        self.player_type = player_type
        self.selected = False
        self.active = True
        self.tagged = False
        self.tackled = False

    def move(self, dx, dy, bounds):
        # Move player within given bounds
        try:
            nx = self.x + dx
            ny = self.y + dy
            if bounds.left + PLAYER_RADIUS <= nx <= bounds.right - PLAYER_RADIUS and \
               bounds.top + PLAYER_RADIUS <= ny <= bounds.bottom - PLAYER_RADIUS:
                self.x = nx
                self.y = ny
        except Exception as e:
            raise KabaddiGameException("Player movement error!") from e

    def reset(self):
        # Reset player to initial position
        self.x = self.initial_x
        self.y = self.initial_y
        self.selected = False
        self.tagged = False
        self.tackled = False
        self.active = True
        self.player_type = PlayerType.DEFENDER

    def draw(self, surface):
        # Draw player
        if not self.active:
            color = SUB_COLOR
        elif self.player_type == PlayerType.RAIDER:
            color = RAIDER_COLOR
        else:
            color = DEFENDER_COLOR
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), PLAYER_RADIUS)
        if self.selected:
            pygame.draw.circle(surface, SELECTED_COLOR, (int(self.x), int(self.y)), PLAYER_RADIUS + 3, 3)
        # Show tag/tackle status
        if self.tagged or self.tackled:
            font = pygame.font.SysFont(FONT_NAME, 18)
            txt = 'T' if self.tackled else 'X'
            surface.blit(font.render(txt, True, (0, 0, 0)), (self.x-6, self.y-12))

# Team class
class Team:
    def __init__(self, name, side):
        self.name = name
        self.side = side  # 'left' or 'right'
        self.players = []
        self.on_field = []
        self.subs = []
        self.score = 0

    def setup_players(self):
        # Position players on their half
        MarginY = COURT_MARGIN + COURT_HEIGHT // 2
        if self.side == 'left':
            half_rect = pygame.Rect(COURT_MARGIN, COURT_MARGIN, COURT_WIDTH // 2, COURT_HEIGHT)
            x_start = COURT_MARGIN + COURT_WIDTH // 6
        else:
            half_rect = pygame.Rect(COURT_MARGIN + COURT_WIDTH // 2, COURT_MARGIN, COURT_WIDTH // 2, COURT_HEIGHT)
            x_start = COURT_MARGIN + COURT_WIDTH * 5 // 6

        y_gap = COURT_HEIGHT // (TEAM_SIZE + 1)
        for i in range(TEAM_SIZE):
            x = x_start
            y = COURT_MARGIN + (i + 1) * y_gap
            p = Player(x, y, self, i)
            self.players.append(p)
            self.on_field.append(p)
        # Add two subs
        for i in range(2):
            x = x_start
            y = SCREEN_HEIGHT - COURT_MARGIN - (i + 1) * 40
            sub_p = Player(x, y, self, TEAM_SIZE + i, PlayerType.SUB)
            sub_p.active = False
            self.players.append(sub_p)
            self.subs.append(sub_p)

    def draw(self, surface):
        # Draw all players
        for p in self.players:
            p.draw(surface)

    def reset_positions(self):
        # Reset all players to their initial positions
        for p in self.players:
            p.reset()

# Kabaddi Match class
class KabaddiMatch:
    def __init__(self, surface):
        self.surface = surface
        self.teams = []
        self.current_round = 0
        self.round_start_time = time.time()
        self.round_end_time = self.round_start_time + ROUND_TIME
        self.active_team = 0
        self.defending_team = 1
        self.raider = None
        self.breath_start = None
        self.breath_meter = BREATH_MAX
        self.game_over = False
        self.in_raid = False
        self.raider_selected = False
        self.tackle_attempted = False
        self.status_msg = ""
        self.selected_defender = None
        self.switch_locked = False
        self.sub_candidate = None
        self.score_flash_time = 0
        self.flash_team = None
        self.last_score_time = 0
        self.font = pygame.font.SysFont(FONT_NAME, 22)
        self.bigfont = pygame.font.SysFont(FONT_NAME, 32)

    def setup(self):
        # Setup two teams and their players
        try:
            team1 = Team("Team Blue", 'left')
            team2 = Team("Team Red", 'right')
            team1.setup_players()
            team2.setup_players()
            self.teams = [team1, team2]
            self.current_round = 1
            self.active_team = 0  # team 0 raids first
            self.defending_team = 1
            self.raider_selected = False
            self.raider = None
            self.in_raid = False
            self.breath_meter = BREATH_MAX
            self.breath_start = None
            self.tackle_attempted = False
            self.round_start_time = time.time()
            self.round_end_time = self.round_start_time + ROUND_TIME
            self.status_msg = "Select a Raider with mouse"
            self.selected_defender = None
            self.switch_locked = False
            self.sub_candidate = None
            self.flash_team = None
            self.last_score_time = 0
            for t in self.teams:
                t.reset_positions()
        except Exception as e:
            raise KabaddiGameException("KabaddiMatch setup error!") from e

    def draw_court(self):
        # Draw the kabaddi court split into halves
        pygame.draw.rect(self.surface, (180, 180, 180), (COURT_MARGIN, COURT_MARGIN, COURT_WIDTH, COURT_HEIGHT), 0)
        pygame.draw.rect(self.surface, (90, 90, 90), (COURT_MARGIN, COURT_MARGIN, COURT_WIDTH, COURT_HEIGHT), 4)
        mid_line = COURT_MARGIN + COURT_WIDTH // 2
        pygame.draw.line(
            self.surface, (30, 30, 30),
            (mid_line, COURT_MARGIN),
            (mid_line, COURT_MARGIN + COURT_HEIGHT),
            5
        )
        # Show round/time
        round_txt = f"Round {self.current_round}/{NUM_ROUNDS}"
        txt = self.font.render(round_txt, True, (0, 70, 0))
        self.surface.blit(txt, (SCREEN_WIDTH // 2 - 70, 20))

    def draw_status(self):
        # Draw scores, time, and status
        left_score = self.teams[0].score
        right_score = self.teams[1].score
        txt = f"{self.teams[0].name}: {left_score}   |   {self.teams[1].name}: {right_score}"
        scoretxt = self.bigfont.render(txt, True, (0, 0, 100))
        self.surface.blit(scoretxt, (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 48))
        time_left = int(self.round_end_time - time.time())
        timer_color = (200, 0, 0) if time_left <= 7 else (0, 0, 0)
        timertxt = self.font.render(f"Time Left: {max(0, time_left)}s", True, timer_color)
        self.surface.blit(timertxt, (SCREEN_WIDTH // 2 - 50, 54))

        # Flash score on recent event
        if self.flash_team is not None and time.time() < self.score_flash_time + 0.7:
            txt = f"+1 Point!"
            team_idx = self.flash_team
            color = (180, 0, 0) if team_idx == 1 else (60, 90, 255)
            stxt = self.bigfont.render(txt, True, color)
            sx = 160 if team_idx == 0 else SCREEN_WIDTH - 230
            self.surface.blit(stxt, (sx, SCREEN_HEIGHT // 2 - 44))
        # Status
        status = self.status_msg
        if status:
            st = self.font.render(status, True, (10, 80, 30))
            self.surface.blit(st, (SCREEN_WIDTH // 2 - 170, COURT_MARGIN // 2))

        # Breath meter
        if self.in_raid and self.breath_start:
            breath_left = max(0, BREATH_MAX - (time.time() - self.breath_start))
            bar_w = int(220 * (breath_left / BREATH_MAX))
            pygame.draw.rect(self.surface, (80, 200, 70), (SCREEN_WIDTH // 2 - 110, COURT_MARGIN // 2 + 30, bar_w, 22))
            txtbreath = self.font.render(f"Breath: {breath_left:.1f}s", True, (0, 60, 0))
            self.surface.blit(txtbreath, (SCREEN_WIDTH // 2 - 60, COURT_MARGIN // 2 + 32))

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            try:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.raider_selected:
                        # Select raider from active team
                        for p in self.teams[self.active_team].on_field:
                            if p.active and (mx - p.x) ** 2 + (my - p.y) ** 2 < PLAYER_RADIUS ** 2:
                                self.set_raider(p)
                                break
                    elif self.in_raid and not self.tackle_attempted:
                        # Defender selection for tackling
                        for p in self.teams[self.defending_team].on_field:
                            if p.active and (mx - p.x) ** 2 + (my - p.y) ** 2 < PLAYER_RADIUS ** 2:
                                self.selected_defender = p
                                self.selected_defender.selected = True
                                self.status_msg = "Defender selected. Press SPACE to attempt tackle."
                                break
                    elif not self.in_raid and not self.switch_locked:
                        # Substitution selection
                        self.sub_candidate = None
                        for p in self.teams[self.active_team].on_field:
                            if (mx - p.x) ** 2 + (my - p.y) ** 2 < PLAYER_RADIUS ** 2:
                                self.sub_candidate = p
                                break
                        for p in self.teams[self.active_team].subs:
                            if (mx - p.x) ** 2 + (my - p.y) ** 2 < PLAYER_RADIUS ** 2:
                                if self.sub_candidate:
                                    self.do_substitution(self.active_team, self.sub_candidate.idx, p.idx)
                                    break
                elif event.type == pygame.KEYDOWN:
                    if self.in_raid and self.raider:
                        # Raider controls (arrow keys)
                        if self.raider.team.side == 'left':
                            half_rect = pygame.Rect(COURT_MARGIN, COURT_MARGIN, COURT_WIDTH, COURT_HEIGHT)
                        else:
                            half_rect = pygame.Rect(COURT_MARGIN, COURT_MARGIN, COURT_WIDTH, COURT_HEIGHT)
                        speed = 7 if event.mod & pygame.KMOD_SHIFT else 4
                        if event.key == pygame.K_UP:
                            self.raider.move(0, -speed, half_rect)
                        elif event.key == pygame.K_DOWN:
                            self.raider.move(0, speed, half_rect)
                        elif event.key == pygame.K_LEFT:
                            self.raider.move(-speed, 0, half_rect)
                        elif event.key == pygame.K_RIGHT:
                            self.raider.move(speed, 0, half_rect)
                        # Tag defender
                        elif event.key == pygame.K_SPACE:
                            for p in self.teams[self.defending_team].on_field:
                                if p.active and ((p.x - self.raider.x) ** 2 + (p.y - self.raider.y) ** 2 < (PLAYER_RADIUS*2) ** 2):
                                    p.tagged = True
                                    self.status_msg = "Defender tagged! Return to own half!"
                                    self.tackle_attempted = False
                                    break
                    if self.in_raid and self.selected_defender and not self.tackle_attempted:
                        # Tackle attempt by defender (space key)
                        if event.key == pygame.K_SPACE:
                            if ((self.selected_defender.x - self.raider.x) ** 2 + (self.selected_defender.y - self.raider.y) ** 2 < (PLAYER_RADIUS*2) ** 2):
                                self.selected_defender.tackled = True
                                self.tackle_attempted = True
                                self.status_msg = "Raider tackled!"
                            else:
                                self.status_msg = "Missed tackle!"
                            self.selected_defender.selected = False
                            self.selected_defender = None
                    # Substitution confirmation
                    if event.key == pygame.K_s and not self.in_raid and not self.switch_locked and self.sub_candidate is not None:
                        if not self.sub_candidate.active:
                            # Must select in-field then sub
                            for p in self.teams[self.active_team].on_field:
                                if p.selected:
                                    self.do_substitution(self.active_team, p.idx, self.sub_candidate.idx)
                                    break
                        else:
                            self.sub_candidate.selected = not self.sub_candidate.selected
            except Exception as e:
                raise KabaddiGameException("Error handling event!") from e

    def set_raider(self, player):
        # Set the selected player as raider for this raid
        try:
            player.player_type = PlayerType.RAIDER
            player.selected = True
            self.raider_selected = True
            self.raider = player
            self.in_raid = True
            self.breath_start = time.time()
            self.status_msg = "Raider selected! Use arrow keys to raid. SPACE to tag."
            for p in self.teams[self.active_team].on_field:
                if p != player:
                    p.selected = False
        except Exception as e:
            raise KabaddiGameException("Could not assign raider!") from e

    def process_raid(self):
        # Main raid process: Check breath, tagging, return, tackle
        try:
            if not self.raider or not self.in_raid:
                return
            now = time.time()
            # Breath meter check
            breath_left = BREATH_MAX - (now - self.breath_start)
            if breath_left <= 0:
                self.status_msg = "Out of breath! Raid failed."
                self.teams[self.defending_team].score += 1
                self.flash_team = self.defending_team
                self.score_flash_time = now
                self.end_raid()
                return
            # If raider crosses mid-line into defender half
            mid_line = COURT_MARGIN + COURT_WIDTH // 2
            raider_side = self.raider.x < mid_line if self.active_team == 0 else self.raider.x > mid_line
            if not raider_side:
                # In opponent's half
                # If tagged defender, try returning
                if any(p.tagged for p in self.teams[self.defending_team].on_field):
                    self.status_msg = "Return to own half!"
                # If tackled
                if any(p.tackled for p in self.teams[self.defending_team].on_field):
                    self.status_msg = "Raider tackled! No points."
                    self.teams[self.defending_team].score += 1
                    self.flash_team = self.defending_team
                    self.score_flash_time = now
                    self.end_raid()
                    return
            else:
                # In own half
                tagged = [p for p in self.teams[self.defending_team].on_field if p.tagged]
                if tagged:
                    # Tagged defenders, successful raid!
                    self.teams[self.active_team].score += len(tagged)
                    self.status_msg = f"Raid successful! +{len(tagged)} pts."
                    self.flash_team = self.active_team
                    self.score_flash_time = now
                    self.end_raid(successful=True)
                    return
                else:
                    # No tag on raid
                    self.status_msg = "Safe return, no points."
                    self.end_raid()
                    return
        except Exception as e:
            raise KabaddiGameException("Raid processing error!") from e

    def end_raid(self, successful=False):
        # Ends current raid, resets necessary variables
        try:
            self.in_raid = False
            self.raider_selected = False
            self.raider.player_type = PlayerType.DEFENDER
            self.raider.selected = False
            self.raider = None
            self.breath_start = None
            self.breath_meter = BREATH_MAX
            self.tackle_attempted = False
            self.switch_locked = True
            self.status_msg += " Press ENTER to next raid."
            # Remove tagged defenders temporarily
            for p in self.teams[self.defending_team].on_field:
                if p.tagged and successful:
                    p.active = False  # Out for next raid
                p.tagged = False
                p.tackled = False
            self.selected_defender = None
            self.last_score_time = time.time()
        except Exception as e:
            raise KabaddiGameException("Error ending raid!") from e

    def do_substitution(self, team_idx, out_idx, in_idx):
        # Substitution: swap player-out with sub-in
        try:
            team = self.teams[team_idx]
            p_out = None
            p_in = None
            for p in team.players:
                if p.idx == out_idx:
                    p_out = p
                if p.idx == in_idx:
                    p_in = p
            if p_out and p_in and p_out.active and not p_in.active:
                p_out.active = False
                p_in.active = True
                team.on_field.remove(p_out)
                team.on_field.append(p_in)
                team.subs.remove(p_in)
                team.subs.append(p_out)
                p_in.x, p_in.y = p_out.x, p_out.y
                self.status_msg = "Substitution complete."
            else:
                self.status_msg = "Invalid substitution."
        except Exception as e:
            raise KabaddiGameException("Substitution error") from e

    def round_over(self):
        # Round timer finished
        return time.time() > self.round_end_time

    def next_round(self):
        # Set up for new round
        try:
            self.current_round += 1
            self.active_team, self.defending_team = self.defending_team, self.active_team
            for t in self.teams:
                t.reset_positions()
            self.raider_selected = False
            self.raider = None
            self.in_raid = False
            self.breath_meter = BREATH_MAX
            self.breath_start = None
            self.tackle_attempted = False
            self.round_start_time = time.time()
            self.round_end_time = self.round_start_time + ROUND_TIME
            self.status_msg = f"Round {self.current_round} - {self.teams[self.active_team].name} raids."
            self.selected_defender = None
            self.switch_locked = False
            self.sub_candidate = None
            self.flash_team = None
        except Exception as e:
            raise KabaddiGameException("Next round error!") from e

    def draw(self):
        # Draw everything onto surface
        self.draw_court()
        for t in self.teams:
            t.draw(self.surface)
        self.draw_status()

    def update(self):
        # Main per-frame update: check raid status, round end
        try:
            if self.in_raid:
                self.process_raid()
            if self.round_over():
                if self.current_round < NUM_ROUNDS:
                    self.status_msg = "Round over! Press ENTER for next round."
                    self.in_raid = False
                    self.switch_locked = True
                else:
                    self.game_over = True
                    winner = None
                    if self.teams[0].score > self.teams[1].score:
                        winner = self.teams[0].name
                        color = (50, 90, 255)
                    elif self.teams[0].score < self.teams[1].score:
                        winner = self.teams[1].name
                        color = (180, 10, 10)
                    else:
                        winner = 'Draw!'
                        color = (180, 180, 40)
                    win_txt = f"Game Over! Winner: {winner}"
                    txt = self.bigfont.render(win_txt, True, color)
                    self.surface.blit(txt, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 40))
        except Exception as e:
            raise KabaddiGameException("Update error!") from e

# Main game loop
def main():
    pygame.init()
    pygame.display.set_caption("Kabaddi Game")
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = KabaddiMatch(surface)
    game.setup()
    running = True

    while running:
        surface.fill((90, 130, 80))
        events = pygame.event.get()
        game.handle_events(events)
        game.update()
        game.draw()
        pygame.display.update()

        # Keyboard shortcuts and controls
        keys = pygame.key.get_pressed()
        if game.game_over:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Restart game
                    game.setup()
                    game.game_over = False
        else:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Next raid or next round
                        if not game.in_raid:
                            if game.switch_locked and not game.round_over():
                                # Next raid
                                game.switch_locked = False
                                game.status_msg = "Select a Raider with mouse"
                            elif game.round_over() and game.current_round < NUM_ROUNDS:
                                game.next_round()
                                game.switch_locked = False

        clock.tick(FPS)

if __name__ == "__main__":
    try:
        main()
    except KabaddiGameException as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Unexpected error: {e}")
        pygame.quit()
        sys.exit()