---
# Kabaddi Game – Professional Software Architecture Blueprint

## 1. UML Class Diagram (Text-Based)

```
+-----------------+
|     Game        |<>------>[GameState]
+-----------------+
| - state         |
| - teams         |
| - score         |
| - round         |
| - court         |
| - timer         |
+-----------------+
| +run()          |
| +update()       |
| +switch_round() |
| +calculate_score()|
+-----------------+

+------------------+         +---------------------+
|     Team         |<>------>|   Player            |
+------------------+         +---------------------+
| - name           |         | - id                |
| - players        |         | - position          |
| - active_players |         | - state (Enum)      |
| - subs           |         | - breath_meter      |
| +substitute()    |         | - is_raider         |
| +get_active()    |         | - tag()             |
+------------------+         | - tackle()          |
                             | - move()            |
                             | - update_breath()   |
                             +---------------------+

+------------------+         +---------------------+       +------------------+
|GameState         |         |Renderer             |       |InputHandler      |
+------------------+         +---------------------+       +------------------+
| - current_state  |         | - screen            |       | - inputs         |
| +set_state()     |         +---------------------+       +------------------+
| +update()        |         | +draw_players()     |       | +handle_input()  |
| +handle_events() |         | +draw_court()       |       | +get_action()    |
+------------------+         | +draw_ui()          |       +------------------+
                             +---------------------+

+------------------+         +---------------------+
|AIController      |         |RoundManager         |
+------------------+         +---------------------+
| - team           |         | - rounds            |
| +decide_action() |         | - current_round     |
+------------------+         | +start_round()      |
                             | +switch_teams()     |
                             +---------------------+
```

**Relationships**:
- `Game` holds `GameState`, two `Team` instances, `RoundManager`, `Renderer`, `InputHandler`.
- `Team` manages a set of `Player` objects and subs.
- `GameState` drives transitions using a State Machine pattern.
- `Renderer` is responsible for all visuals.
- `InputHandler` manages user and AI input.

---

## 2. Design Pattern Specifications

1. **State Machine Pattern**  
   - Manages game states: `Menu`, `RoundStart`, `Raid`, `Tackle`, `EndRound`, `GameOver`.
   - Implements state transitions and encapsulates logic for each phase.

2. **Entity-Component System (ECS)**
   - *Player*: Composed of components (`Movement`, `Breath`, `Taggable`, `Tacklable`), allowing for flexible extension (e.g., power-ups).
   - Facilitates scalable team/player features.

3. **Observer Pattern**
   - Score updates notify HUD/UI elements.
   - Events (tag/tackle) notify respective subsystems (sound, animation).

4. **Singleton/Manager Patterns**
   - `RoundManager`, `InputHandler`, and `Renderer` implemented as singletons/managers for unified access.

---

## 3. Component System Design

**Core Components:**

- **Game Loop**: Master update method calls `update()` and `render()` methods per frame.
- **Renderer**: Draws court, players, breath meters, UI overlays.
- **Input System**: Handles both keyboard and (optionally) AI decisions through abstractions.
- **Update System**: Manages physics, collisions, breath countdown.
- **Team Management**: Substitution, active-players, switching raider/defender roles.
- **Scoring System**: Point calculation on events, persistent round scoring.

**Extensible Components:**

- Player states (e.g. `Active`, `Tagged`, `Out`, `Subbed`)
- AI modules for defender/raider logic
- Configuration loader for game settings (court size, team size, rules)

---

## 4. Performance Optimization Plan

- **Sprite Groups**: Use pygame sprite groups for batch updates/draws and collision detection.
- **Dirty Rects Rendering**: Update only changed areas of the screen.
- **Object Pooling**: For animation effects (tags/tackles), reuse object instances to minimize GC overhead.
- **Delta Time Calculation**: Ensure frame-rate independence for smooth movement and timers.
- **Frame Rate Limiting**: Cap FPS (60+) using pygame’s clock object.
- **Data-Oriented Structures**: Prefer numpy arrays or lightweight structures for player positions, optimizing batch operations.
- **Memoization**: Cache frequently used calculations (e.g., scoring tables).

---

## 5. Code Structure Recommendations

```
kabaddi_game/
    main.py                # Game entry point, main loop
    game.py                # Game class and loop management
    team.py                # Team and player management
    player.py              # Player class and components
    gamestate.py           # State machine implementation
    renderer.py            # All scene and UI drawing
    input_handler.py       # Processing player/AI input
    ai_controller.py       # AI logic for defenders/raiders
    round_manager.py       # Manages round transitions
    config.py              # Game configs, settings loader/saver
    assets/
        images/            # Player/court sprites
        sounds/            # Effects, music
    utils.py               # Logger, error handler, shared constants
    tests/
        test_player.py     # Unit tests for critical classes
        test_team.py
        test_game.py
```

- Use **modules** for separation and maintainability.
- Centralized **error logger** in `utils.py`, uncaught exceptions route here.
- Settings & save system isolated in `config.py`.

---

## 6. Scalability Roadmap

- **Modular ECS**: Add new player abilities/components without breaking core.
- **Configurable Team Sizes & Rules**: Expand game modes/simple rule toggles via external config files.
- **Online Multiplayer Option**: Introduce networking layer; architecture preps for player/controller abstraction.
- **Plug-and-Play AI**: Develop new AI strategies and swap via dependency injection.
- **Extensible Renderer**: Easy upgrade to animated sprites, effects, or different UI layouts.

---

## 7. Memory Management Patterns

- Use **object pooling** for frequently created/destroyed animation or event objects.
- Dispose of inactive player/sprites by removing from sprite groups and nullifying references.
- Lazy load images/sounds as needed, cache currently active assets.
- Handle all errors centrally via `utils.py`, use try/except to guard file I/O, input handling, and state transitions.

---

## 8. Error Handling Strategies

- Validate player/team configs on load; fallback to safe defaults.
- State machine enforces legal transitions (cannot start raid unless round is active, etc.).
- Input events buffered; invalid controls safely ignored/logged.
- All game-critical functions wrap in try/except blocks; fatal errors route to logger/UI dialog.
- Periodic save-states for crash recovery.
- Use assertion and log warnings during development, suppress/route errors in production.

---

## 9. Example Class Skeletons

```python
class Game:
    def __init__(self, config):
        self.state = GameState()
        self.teams = [Team("Red"), Team("Blue")]
        self.round_manager = RoundManager()
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.score = {team.name: 0 for team in self.teams}
        # ...other inits

    def run(self):
        while self.state.current_state != "GameOver":
            self.update()
            self.renderer.render(self.state, self.teams)
            self.input_handler.process_input()
        # Log/game over

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []
        self.subs = []

    def substitute(self, in_player, out_player):
        # error handling & swap logic

class Player:
    def __init__(self, id, position, is_raider=False):
        self.id = id
        self.position = position
        self.state = "Active"
        self.is_raider = is_raider
        self.breath_meter = 100

    def tag(self, target):
        # tagging logic
    def tackle(self, raider):
        # tackle logic
    def move(self, direction, delta_time):
        # move logic

class GameState:
    # Implements the State Machine
    def __init__(self):
        self.current_state = "Menu"
    def set_state(self, state):
        # transition logic

class Renderer:
    def render(self, state, teams):
        # draw court, players, UI

class InputHandler:
    def process_input(self):
        # handle keyboard and (optionally) AI
```

---

## 10. Summary of Blueprint Strengths

- Uses proven, scalable design patterns for a sports game.
- Ready for AI, multiplayer, and new rules/components via ECS/state machine.
- Separation of concerns for clean maintenance and performance.
- Robust error/memory management for reliability.
- Modular codebase for testing, expansion, and easy refactoring.

---

This blueprint is ready for development and supports clean, professional, high-performance Kabaddi game implementation in Python/pygame.