# 🎮 CrewAI Python Game Builder

An AI-powered game development system that uses **CrewAI** multi-agent collaboration to automatically generate complete Python games with professional UI/UX design. This project leverages multiple AI agents working together to create, review, and evaluate games with stunning visual designs and modern gameplay mechanics.

## ✨ Features

- 🤖 **Enhanced Multi-Agent AI System**: Uses CrewAI with 5 specialized agents (Senior Engineer, UI/UX Designer, Audio Engineer, QA Engineer, Chief QA Engineer)
- 🎨 **Professional UI/UX**: Generates games with stunning visual design, particle effects, and smooth animations
- 🏗️ **Comprehensive Documentation**: Each game includes architecture design, UI specs, audio design, code review, and evaluation
- 🎲 **Diverse Game Collection**: 10 games including classic arcade games + traditional Indian games
- ⚡ **Simple Usage**: Single command with optional game argument - `crewai run [game]`
- 🔧 **Advanced Tools**: Custom validation, architecture design, and performance optimization tools
- 🔍 **Quality Assurance**: Multi-layer code review and comprehensive quality evaluation

## 🎮 Available Games

### Classic Arcade Games
- 🟡 **Pac-Man Clone** - Navigate mazes, collect dots, avoid ghosts
- 🐍 **Snake Game** - Modern neon-style snake with particle effects  
- 🏓 **Pong Game** - Retro-futuristic design with 3D effects
- 🧱 **Breakout Game** - Destroy bricks with enhanced physics
- 🔲 **Tetris** - Classic puzzle game with smooth animations

### Traditional Indian Games (2000s Era)
- 🐍 **Snakes and Ladders** - Digital version of the classic board game
- 🎯 **Carrom Board Game** - Physics-based coin-flicking game
- 🏃 **Kabaddi Game** - Simplified version of India's national sport
- 🥌 **Pithu (Seven Stones)** - Traditional street game with physics
- 🏏 **Gilli Danda** - Classic rural game with trajectory mechanics

## 🚀 Quick Start

### Prerequisites
- Python >=3.10 <3.14  
- OpenAI API Key or Azure OpenAI Service

### Installation

1. **Install UV** (if not already installed):
```bash
pip install uv
```

2. **Install Dependencies**:
```bash
crewai install
```

3. **Setup Environment**:
Create a `.env` file and add your API configuration:

**For OpenAI:**
```env
OPENAI_API_KEY=your_api_key_here
```

**For Azure OpenAI:**
```env
AZURE_API_KEY=your_azure_api_key
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-12-01-preview
```

4. **Generate Your First Game**:
```bash
# Generate the default game
crewai run

# Or generate a specific game
crewai run pong
```

5. **Run the Generated Game**:
```bash
# Install pygame (required for running games)
pip install pygame

# Run the game
python output/snake_game/generated_game.py
```

## 🎯 Usage

### 🎮 Generate Games

**Basic Usage:**
```bash
# Generate default game
crewai run

# Generate specific game
crewai run snake
crewai run pong
```

**Game Selection:**
```bash
# Generate specific game by key
crewai run example1_pacman
crewai run example2_snake
crewai run example3_pong

# Generate by name (partial matching)
crewai run snake
crewai run tetris
crewai run carrom
```

### 🎲 Available Game Keys
- `example1_pacman` - Pac-Man Clone
- `example2_snake` - Snake Game
- `example3_pong` - Pong Game  
- `example4_breakout` - Breakout Game
- `example5_tetris` - Simple Tetris
- `example7_snakes_ladders` - Snakes and Ladders
- `example8_carrom` - Carrom Board Game
- `example9_kabaddi` - Kabaddi Game
- `example10_pithu` - Pithu (Seven Stones)
- `example11_gilli_danda` - Gilli Danda

Each game is generated in its own folder in the `output/` directory:
```
output/
├── pac-man_clone/
├── snake_game/
├── pong_game/
├── breakout_game/
├── simple_tetris/
├── snakes_and_ladders/
├── carrom_board_game/
├── kabladdi_game/
├── pithu_(seven_stones)/
└── gilli_danda/
```

### 🎮 Run Generated Games
Navigate to any game folder and run:
```bash
python output/[game_folder]/generated_game.py
```

Examples:
```bash
python output/snake_game/generated_game.py
python output/pong_game/generated_game.py
python output/pac-man_clone/generated_game.py
```

### 📁 Generated Files Structure
Each game folder contains comprehensive documentation:
- `generated_game.py` - Complete playable Python game
- `architecture_design.md` - Professional software architecture 
- `ui_design_specs.md` - UI/UX design specifications
- `audio_design_specs.md` - Audio system design
- `code_review.md` - Detailed code review and analysis  
- `final_evaluation.md` - Quality assessment and recommendations

### 🎯 Command Reference
```bash
# Generate specific games
crewai run                          # Default game (Snake)
crewai run example1_pacman          # Generate Pac-Man
crewai run pong                     # Generate Pong (by name)
crewai run tetris                   # Generate Tetris (by name)

# Training and testing
crewai train 5 training_data.txt    # Train the crew
crewai test 3 gpt-4                 # Test the crew
crewai replay task_123              # Replay a task
```

## 🤖 AI Agent System

The system uses **five specialized AI agents** working collaboratively:

### 👨‍💻 Senior Engineer Agent
- **Role**: Lead game developer and architect
- **Responsibilities**: 
  - Designs game architecture and core mechanics
  - Implements professional UI/UX with modern visual effects
  - Creates complete, playable Python games using Pygame
  - Focuses on code quality, performance, and user experience

### 🔍 QA Engineer Agent  
- **Role**: Code reviewer and quality analyst
- **Responsibilities**:
  - Reviews generated game code for bugs and issues
  - Analyzes code structure, readability, and best practices
  - Provides detailed feedback on improvements
  - Ensures game functionality and performance standards

### 👔 Chief QA Engineer Agent
- **Role**: Final evaluator and project manager
- **Responsibilities**:
  - Conducts final quality assessment of the complete game
  - Evaluates user experience and gameplay mechanics
  - Provides strategic recommendations for enhancements
  - Ensures project meets professional standards

## 🎨 Design Philosophy

### Visual Excellence
- **Modern UI/UX**: Professional interfaces with contemporary design principles
- **Advanced Effects**: Particle systems, smooth animations, glow effects
- **3D-Style Elements**: Realistic lighting, shadows, and depth
- **Responsive Design**: Smooth 60+ FPS gameplay with fluid interactions

### Code Quality
- **Clean Architecture**: Well-structured, maintainable code
- **Performance Optimization**: Efficient algorithms and resource management  
- **Error Handling**: Robust error management and edge case handling
- **Documentation**: Clear comments and comprehensive documentation

## ⚙️ Customization

### Adding New Games
Edit `src/crew_python_game_builder/config/gamedesign.yaml` to add new game specifications:

```yaml
example12_your_game:
  name: "Your Game Name"
  type: "Game Category"
  description: >
    Detailed game description with visual and gameplay requirements...
  requirements:
    - "Specific technical requirements"
    - "UI/UX design specifications"
    - "Performance and quality standards"
```

### Modifying Agents
- **Agents**: `src/crew_python_game_builder/config/agents.yaml`
- **Tasks**: `src/crew_python_game_builder/config/tasks.yaml` 
- **Crew Logic**: `src/crew_python_game_builder/crew.py`
- **Main Runner**: `src/crew_python_game_builder/main.py`

## 🛠️ Technical Requirements

### System Requirements
- **Python**: 3.10 - 3.13
- **Dependencies**: CrewAI, Pygame, PyYAML
- **API**: OpenAI API access
- **Storage**: ~100MB for all generated games

### Game Requirements
- **Graphics**: Pygame-based rendering
- **Performance**: 60+ FPS target
- **Controls**: Keyboard/mouse input
- **Resolution**: Scalable window sizes
- **Platform**: Cross-platform (Windows, macOS, Linux)

## 🎮 Game Features

### Visual Design Elements
- ✨ Particle effects and animations
- 🌈 Gradient backgrounds and modern UI
- 💫 Glow effects and professional lighting  
- 🎯 Smooth transitions and responsive controls
- 🎨 Consistent color schemes and typography

### Gameplay Mechanics
- 🎲 Physics simulation and collision detection
- 🏆 Scoring systems and win conditions
- ⚡ Progressive difficulty and speed scaling
- 🔄 Game state management (menu, play, game over)
- 💾 High score tracking and persistence

## 📁 Project Structure

```
crew_python_game_builder/
├── src/crew_python_game_builder/
│   ├── config/
│   │   ├── agents.yaml          # AI agent configurations
│   │   ├── tasks.yaml           # Task definitions
│   │   ├── gamedesign.yaml      # Game specifications
│   │   └── system_config.yaml   # Advanced system settings
│   ├── tools/
│   │   └── custom_tool.py       # Custom validation and optimization tools
│   ├── crew.py                  # Main crew orchestration
│   └── main.py                  # Simple entry point
├── output/                      # Generated games (auto-created)
│   ├── [game_name]/
│   │   ├── generated_game.py    # Playable game
│   │   ├── architecture_design.md # Software architecture
│   │   ├── ui_design_specs.md   # UI/UX specifications
│   │   ├── audio_design_specs.md # Audio design
│   │   ├── code_review.md       # Code analysis
│   │   └── final_evaluation.md  # Quality assessment
├── knowledge/                   # Additional context files
└── tests/                       # Test files
```

## 🤝 Support & Resources

### CrewAI Resources
- 📖 [CrewAI Documentation](https://docs.crewai.com)
- 🐙 [CrewAI GitHub](https://github.com/joaomdmoura/crewai)
- 💬 [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- 💬 [Chat with CrewAI Docs](https://chatg.pt/DWjSBZn)

### Game Development
- 🎮 [Pygame Documentation](https://www.pygame.org/docs/)
- 🐍 [Python Game Development](https://realpython.com/pygame-a-primer/)

---

**🚀 Ready to create amazing games with AI?** Run `crewai run` and watch as multiple AI agents collaborate to build professional-quality games with stunning visual designs!
