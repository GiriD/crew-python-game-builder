import tkinter as tk
from tkinter import messagebox
import random

# Game constants
BOARD_SIZE = 10  # 10x10 board
NUM_SQUARES = 100
CELL_SIZE = 60
TOKEN_RADIUS = 18
BOARD_MARGIN = 60

# Snakes and ladders positions
SNAKES = {
    99: 7,
    95: 75,
    92: 36,
    89: 53,
    74: 33,
    64: 60,
    62: 19,
    49: 11,
    46: 25,
    16: 6
}

LADDERS = {
    2: 38,
    7: 14,
    8: 31,
    15: 26,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    78: 98,
    87: 94
}

TOKEN_COLORS = ["red", "blue", "green", "orange"]
PLAYER_NAMES = ["Player 1", "Player 2", "Player 3", "Player 4"]

def get_board_coords(square):
    """
    Calculate pixel coordinates for a given square (1-100).
    Indian Snakes & Ladders board is numbered bottom left to top right, alternating left/right.
    """
    n = square - 1
    row = BOARD_SIZE - 1 - n // BOARD_SIZE
    col = n % BOARD_SIZE
    if (row % 2 == BOARD_SIZE % 2):
        x = BOARD_MARGIN + (BOARD_SIZE - 1 - col) * CELL_SIZE + CELL_SIZE // 2
    else:
        x = BOARD_MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    y = BOARD_MARGIN + row * CELL_SIZE + CELL_SIZE // 2
    return x, y

class Player:
    def __init__(self, name, color, token_id):
        self.name = name
        self.color = color
        self.position = 1
        self.token_id = token_id

class SnakesAndLaddersGame:
    def __init__(self, root, num_players):
        self.root = root
        self.num_players = num_players
        self.players = [Player(PLAYER_NAMES[i], TOKEN_COLORS[i], i) for i in range(num_players)]
        self.current_player_idx = 0
        self.board_canvas = tk.Canvas(root, width=BOARD_MARGIN*2 + CELL_SIZE*BOARD_SIZE,
                                      height=BOARD_MARGIN*2 + CELL_SIZE*BOARD_SIZE, bg='#f9e1b0')
        self.board_canvas.pack()
        self.dice_value = None
        self.last_dice_roll = None
        self.token_canvas_ids = {}
        self.status_label = tk.Label(root, text="", font=("Arial", 16), bg='#f3d46c')
        self.status_label.pack(fill='x')
        self.roll_button = tk.Button(root, text="Roll Dice", font=("Arial", 14), command=self.roll_dice)
        self.roll_button.pack(pady=10)
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(side='bottom', pady=6)
        self._draw_board()
        self._draw_snakes_ladders()
        self._draw_tokens()
        self.update_status()

    def _draw_board(self):
        """Draw the numbered 10x10 board grid with Indian palette"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                square_num = BOARD_SIZE * (BOARD_SIZE - 1 - row) + (col + 1) if (row % 2 == BOARD_SIZE % 2) else BOARD_SIZE * (BOARD_SIZE - 1 - row) + (BOARD_SIZE - col)
                x0 = BOARD_MARGIN + col * CELL_SIZE
                y0 = BOARD_MARGIN + row * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                # Use alternating color pattern and traditional motifs using rectangles & circles
                fill_color = "#eae4d6" if (row+col)%2==0 else "#f8c471"
                # Draw square
                self.board_canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="#b28d5f", width=3)
                # Draw square number
                self.board_canvas.create_text(x0+7, y0+10, text=str(square_num), anchor='nw',
                                              font=("Trajan Pro", 12, "bold"), fill='#5e3a00')
                # Motif - Add a circular bindi pattern on some squares
                if square_num % 13 == 0:
                    self.board_canvas.create_oval(x0+18, y0+25, x0+34, y0+41, fill="#c53b15", outline="#c53b15")

    def _draw_snakes_ladders(self):
        """Draw snakes and ladders with striking colors and shapes."""
        # Draw ladders (green/brown rectangles and yellow steps)
        for start, end in LADDERS.items():
            x1, y1 = get_board_coords(start)
            x2, y2 = get_board_coords(end)
            # Draw ladder base
            self.board_canvas.create_line(x1, y1, x2, y2, fill="#1e8449", width=12)
            # Ladder cross steps
            for i in range(6):
                xi = x1 + (x2 - x1) * (i/6)
                yi = y1 + (y2 - y1) * (i/6)
                angle = random.choice([-15,15])
                dx = angle
                dy = angle
                self.board_canvas.create_line(xi-dx, yi-dy, xi+dx, yi+dy, fill="#f9d423", width=4)
            # Decorative top
            self.board_canvas.create_oval(x2-15, y2-15, x2+15, y2+15, outline="#2ecc40", width=2)

        # Draw snakes (brown/yellow lines and ornate heads)
        for head, tail in SNAKES.items():
            x1, y1 = get_board_coords(head)
            x2, y2 = get_board_coords(tail)
            # Draw snake body -- a zigzag
            for i in range(7):
                t = i/6
                xi = x1 + (x2-x1)*t + random.choice([-16,0,16])
                yi = y1 + (y2-y1)*t + random.choice([-12,0,12])
                if i > 0:
                    self.board_canvas.create_line(prev_x, prev_y, xi, yi, fill="#b9770e", width=10, capstyle='round')
                prev_x, prev_y = xi, yi
            # Snake head (red/yellow circle, Indian cobra motif)
            self.board_canvas.create_oval(x1-20, y1-20, x1+20, y1+20, fill="#e67e22", outline="#fbfcfc", width=4)
            self.board_canvas.create_oval(x1-8, y1-10, x1+8, y1+10, fill="#d35400", outline="#2e4053", width=2)
            # Snake tail decoration (tongue)
            self.board_canvas.create_line(x2, y2, x2+14, y2+6, fill="#e74c3c", width=4)
            self.board_canvas.create_line(x2, y2, x2+10, y2-9, fill="#e74c3c", width=2)

    def _draw_tokens(self):
        """Draw every player's token at their current position."""
        for player in self.players:
            x, y = get_board_coords(player.position)
            # Spread out tokens on the same square
            dx = (player.token_id % 2) * TOKEN_RADIUS*1.2 - TOKEN_RADIUS*0.6
            dy = (player.token_id // 2) * TOKEN_RADIUS*1.1 - TOKEN_RADIUS*0.5
            token = self.board_canvas.create_oval(x-TOKEN_RADIUS+dx, y-TOKEN_RADIUS+dy,
                                                  x+TOKEN_RADIUS+dx, y+TOKEN_RADIUS+dy,
                                                  fill=player.color, outline="black", width=2)
            self.token_canvas_ids[player.token_id] = token
            # Draw symbol in token (Indian style)
            self.board_canvas.create_text(x+dx, y+dy, text="●", fill="white", font=("Helvetica", 18, 'bold'))

    def _move_token(self, player, new_position):
        """Move the player's token to the new position."""
        try:
            # Remove existing token
            token_id = self.token_canvas_ids[player.token_id]
            self.board_canvas.delete(token_id)
        except Exception:
            pass
        player.position = new_position
        # Redraw token
        x, y = get_board_coords(player.position)
        dx = (player.token_id % 2) * TOKEN_RADIUS*1.2 - TOKEN_RADIUS*0.6
        dy = (player.token_id // 2) * TOKEN_RADIUS*1.1 - TOKEN_RADIUS*0.5
        token = self.board_canvas.create_oval(x-TOKEN_RADIUS+dx, y-TOKEN_RADIUS+dy,
                                              x+TOKEN_RADIUS+dx, y+TOKEN_RADIUS+dy,
                                              fill=player.color, outline="black", width=2)
        self.token_canvas_ids[player.token_id] = token
        self.board_canvas.create_text(x+dx, y+dy, text="●", fill="white", font=("Helvetica", 18, 'bold'))

    def update_status(self):
        """Update status label to show current player and board info."""
        info = f"{self.players[self.current_player_idx].name}'s turn ({self.players[self.current_player_idx].color.capitalize()})"
        if self.last_dice_roll:
            info += f" - Last dice: {self.last_dice_roll}"
        self.status_label.config(text=info)

    def roll_dice(self):
        """Roll dice, animate, and process move."""
        # Prevent rolling after win
        for p in self.players:
            if p.position == 100:
                self.roll_button.config(state='disabled')
                return
        dice = random.randint(1,6)
        self.last_dice_roll = dice
        self.update_status()
        self.root.after(350, lambda: self.handle_move(dice))

    def handle_move(self, dice):
        """Move token, apply snake/ladder, check for win, next turn."""
        player = self.players[self.current_player_idx]
        new_pos = player.position + dice
        # Cannot move beyond 100
        if new_pos > 100:
            new_pos = player.position  # stay in place
        # Animate movement (step by step)
        def animate_pos(pos_list, idx=0):
            if idx >= len(pos_list):
                self._move_token(player, pos_list[-1])
                self.after_move(player)
                return
            self._move_token(player, pos_list[idx])
            self.root.after(150, lambda: animate_pos(pos_list, idx+1))
        if new_pos != player.position:
            steps = list(range(player.position+1, new_pos+1))
            animate_pos(steps)
        else:
            self.after_move(player)

    def after_move(self, player):
        # Check for snake or ladder
        pos = player.position
        moved = False
        # Ladder check
        if pos in LADDERS:
            dest = LADDERS[pos]
            self._move_token(player, dest)
            self.status_label.config(text=f"Ladder! {player.name} climbs up to {dest}")
            moved = True
            pos = dest
        # Snake check
        elif pos in SNAKES:
            dest = SNAKES[pos]
            self._move_token(player, dest)
            self.status_label.config(text=f"Snake! {player.name} slides down to {dest}")
            moved = True
            pos = dest
        # Check for win
        if pos == 100:
            self.celebrate_win(player)
            self.roll_button.config(state='disabled')
            return
        # Next player's turn
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players
        self.update_status()
        self.roll_button.config(state='normal')

    def celebrate_win(self, player):
        """Celebration for win with popup and board sparkle."""
        self.status_label.config(text=f"{player.name} Wins! 🎉")
        self.flash_win_tokens(player)
        messagebox.showinfo("Congratulations!", f"{player.name} ({player.color.capitalize()}) Wins! \n\nJai Ho!")
        self.roll_button.config(state='disabled')

    def flash_win_tokens(self, player, count=0):
        """Flash winning token with colors and bindi."""
        if count > 14:
            return
        x, y = get_board_coords(100)
        dx = (player.token_id % 2) * TOKEN_RADIUS*1.2 - TOKEN_RADIUS*0.6
        dy = (player.token_id // 2) * TOKEN_RADIUS*1.1 - TOKEN_RADIUS*0.5
        color_cycle = ["red", "gold", "green", "orange", "yellow"]
        token_color = color_cycle[count % len(color_cycle)]
        # Remove old
        try:
            self.board_canvas.delete(self.token_canvas_ids[player.token_id])
        except Exception:
            pass
        token = self.board_canvas.create_oval(x-TOKEN_RADIUS+dx, y-TOKEN_RADIUS+dy,
                                              x+TOKEN_RADIUS+dx, y+TOKEN_RADIUS+dy,
                                              fill=token_color, outline="white", width=3)
        self.token_canvas_ids[player.token_id] = token
        self.board_canvas.create_text(x+dx, y+dy, text="★", fill="white", font=("Helvetica", 20, 'bold'))
        self.root.after(130, lambda: self.flash_win_tokens(player, count+1))

def choose_players_dialog():
    """Dialog to choose player count at startup."""
    win = tk.Tk()
    win.title("Snakes and Ladders - Choose Players")
    win.configure(bg='#f3d46c')
    label = tk.Label(win, text="Choose Number of Players (2-4)", font=("Arial", 16, "bold"), bg='#f3d46c')
    label.pack(pady=18)
    chosen = tk.IntVar(value=2)
    def start_game():
        win.destroy()
    for i in range(2,5):
        b = tk.Radiobutton(win, text=f"{i} Players", variable=chosen, value=i, font=('Arial', 15),
                           indicatoron=0, width=12, pady=8, bg="#f9e1b0", selectcolor="#f9e1b0",
                           fg=TOKEN_COLORS[i-2])
        b.pack(pady=3)
    btn = tk.Button(win, text="Start Game", font=("Arial", 13, "bold"), command=start_game, bg='#e67e22', fg='white')
    btn.pack(pady=14)
    win.mainloop()
    return chosen.get()

def main():
    """Entry point for the Snakes and Ladders game."""
    num_players = choose_players_dialog()
    root = tk.Tk()
    root.title("Snakes and Ladders - Classic Indian Board Game")
    root.configure(bg='#f9e1b0')
    try:
        game = SnakesAndLaddersGame(root, num_players)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Something went wrong!\n{e}")

if __name__ == "__main__":
    main()