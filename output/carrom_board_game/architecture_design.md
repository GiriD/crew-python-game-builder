Professional Software Architecture Document for Carrom Board Game

---

**I. UML Class Diagrams (Text-Based)**

```
+------------------------------------------------------------------+
|                          Carrom Board Game                       |
+------------------------------------------------------------------+
| Game                                                             |
|  - state: GameState                                              |
|  - players: List[Player]                                         |
|  - board: Board                                                  |
|  - turn_manager: TurnManager                                     |
|  - physics_engine: PhysicsEngine                                 |
|  - renderer: Renderer                                            |
|  - input_handler: InputHandler                                   |
|  - scorer: Scorer                                                |
|  + run()                                                         |
|  + update(dt)                                                    |
|  + render()                                                      |
|  + handle_input(event)                                           |
+------------------------------------------------------------------+

| Player                                                           |
|  - name: str                                                     |
|  - score: int                                                    |
|  - coins_pocketed: List[Coin]                                    |
|  - has_covered_queen: bool                                       |
+------------------------------------------------------------------+

| GameState                                                        |
|  - current_state: Enum (INIT, AIM, SHOOT, PHYSICS, TURN_END, GAME_OVER)   |
|  + change_state(new_state)                                       |
|  + update(dt)                                                    |
+------------------------------------------------------------------+

| Board                                                            |
|  - coins: List[Coin]                                             |
|  - queen: Coin (Special)                                         |
|  - striker: Striker                                              |
|  - pockets: List[Pocket]                                         |
|  - boundaries: Rect                                              |
+------------------------------------------------------------------+

| Coin (base class)                                                |
|  - position: Vector2                                             |
|  - velocity: Vector2                                             |
|  - color: Enum (White, Black, Red)                               |
|  - is_pocketed: bool                                             |
+------------------------------------------------------------------+

| Striker (inherits Coin)                                          |
|  - controlled_by_player: bool                                    |
|  + set_direction(power, angle)                                   |
+------------------------------------------------------------------+

| Pocket                                                          |
|  - position: Vector2                                             |
|  - radius: float                                                 |
|  + check_collision(coin)                                         |
+------------------------------------------------------------------+

| PhysicsEngine                                                    |
|  + update_coin_positions(dt)                                     |
|  + resolve_collisions()                                          |
|  + apply_friction()                                              |
+------------------------------------------------------------------+

| Renderer                                                         |
|  + draw_board()                                                  |
|  + draw_coins()                                                  |
|  + draw_striker()                                                |
|  + draw_ui()                                                     |
+------------------------------------------------------------------+

| InputHandler                                                     |
|  + handle_mouse_event(event)                                     |
|  + handle_keyboard_event(event)                                  |
+------------------------------------------------------------------+

| TurnManager                                                      |
|  - current_player_index: int                                     |
|  + next_turn()                                                   |
|  + get_current_player()                                          |
+------------------------------------------------------------------+

| Scorer                                                           |
|  + update_score(player, coins_pocketed)                          |
|  + queen_capture_rule(player, queen, covering_coin)              |
+------------------------------------------------------------------+
```

---

**II. Design Pattern Specifications**

1. **State Machine Pattern**
   - Used in the `GameState` class to manage transitions (AIM, SHOOT, PHYSICS, etc).
   - Clean separation of logic for each phase of a turn or gameplay.
2. **Component System**
   - Each entity (`Coin`, `Striker`, etc.) can be extended with components for physics, rendering, input, etc.
   - Enables modularity and code reuse.
3. **Observer Pattern**
   - Use for turn change notifications and game events broadcast (e.g., pocketed coin triggers scorer update).
4. **Singleton Pattern**
   - Could be used for `Game` instance and maybe `Renderer` or `PhysicsEngine`.

---

**III. Component System Design**

- **Entities**: Coins, Striker, Players, Board
- **Components**:
  - PhysicsComponent: Handles velocity, acceleration, collisions
  - RenderComponent: Handles drawing on screen
  - InputComponent (for Striker): Handles user control
  - ScoreComponent: Handles scoring logic (coin pocketed, queen rule)
  - StateComponent: Handles current game and entity state

- **Systems**:
  - PhysicsEngine: Updates all entities with PhysicsComponent
  - RenderingSystem: Draws entities with RenderComponent
  - InputSystem: Handles all user inputs, especially for striker aiming/shooting
  - TurnSystem: Manages player turns and game flow

---

**IV. Performance Optimization Plan**

- Use `pygame.sprite.Group` for coins and striker, enabling batch collision checks and draw calls.
- Implement **Object Pooling** for coins: Reuse coin objects instead of deleting/recreating after pocket events.
- Apply **Dirty Rectangles**: Only redraw changed screen areas for efficient rendering.
- Use **Frame Rate Limiting** and **Delta Time Calculations** in main loop for smooth and consistent movement.
- Optimize physics: Use spatial partitioning (e.g., grid-based) if coin count per frame increases.
- Minimize resource usage: Preload images, avoid runtime file read in game loop, cache computations.

---

**V. Code Structure Recommendations**

- `/game/`
  - `main.py` (entry point & main loop)
  - `game.py` (Game, GameState)
  - `player.py` (Player)
  - `board.py` (Board, Coin, Striker, Pocket)
  - `physics.py` (PhysicsEngine)
  - `renderer.py` (Renderer)
  - `input.py` (InputHandler)
  - `turn.py` (TurnManager)
  - `score.py` (Scorer)
  - `/assets/` (Images, sounds)
  - `/config/` (Settings, rules)
- Use config files for board, physics parameters, and rules.
- Logging and error handling in each subsystem (e.g. physics, input, scoring).
- Separate test suites for critical systems (physics, scoring).

---

**VI. Scalability Roadmap**

- **Modular Entities/Components**: Using ECS allows more coin types, power-ups, customization (extendable Coin, Player classes).
- **Network Play Ready**: Design turn system and input handling to be extendable for online multiplayer.
- **Board/Asset Customization**: Board visuals, sound packs, and coin skins are decoupled from logic.
- **Configurable Physics**: Use external config files (JSON/YAML) for friction, pocket strength, rules, making balancing easier.
- **Memory Management**: Object pooling for coins, cache for surfaces/sounds, lazy loading for assets.
- **Event Queues**: For complex interactions, queue up events to be processed by systems.
- **Plugin-Friendly**: Structure for adding new rules/modes (e.g., solo practice, AI opponent, tournaments).

---

**VII. Error Handling Strategies**

- Centralized exception handler in game loop; log all errors to file.
- Physics and scoring: Validate all movement and scoring events, log suspicious or edge-case outcomes.
- UI: Validate input ranges and sanity-check striker movement and coin launches.
- Configuration: Validate config files at load time; fall back to defaults and log errors.
- Turn/state logic: Assert valid state transitions, gracefully recover from unexpected states.

---

**VIII. Summary Table**

| Module        | Key Classes        | Patterns Applied     | Main Responsibility                   |
|---------------|-------------------|---------------------|---------------------------------------|
| game.py       | Game, GameState   | State Machine       | Controls flow, manages game state     |
| player.py     | Player            | Component           | Player data and scoring logic         |
| board.py      | Board, Coin, ...  | ECS                 | Board layout, coin positions          |
| physics.py    | PhysicsEngine     | Component           | Updates positions, resolves collisions|
| renderer.py   | Renderer          | Singleton           | Draws board and game UI               |
| input.py      | InputHandler      | Component           | Handles mouse/touch for striker       |
| turn.py       | TurnManager       | Observer            | Manages player turns and phases       |
| score.py      | Scorer            | Component           | Scoring and queen logic               |

---

This architecture blueprint provides scalable, maintainable, and performant foundations for a professional Carrom board game implementation in Python with pygame, following industry standards.