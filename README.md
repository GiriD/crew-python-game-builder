# 🎮 CrewAI Python Game Builder

An AI-powered game development system that uses **CrewAI** multi-agent collaboration to automatically generate complete Python games with professional UI/UX design. This project leverages multiple AI agents working together to create, review, and evaluate games with stunning visual designs and modern gameplay mechanics.

## ✨ Features

- 🤖 **Multi-Agent AI System**: Uses CrewAI with specialized agents (Senior Engineer, QA Engineer, Chief QA Engineer)
- 🎨 **Professional UI/UX**: Generates games with modern visual design, particle effects, and smooth animations
- 🏗️ **Organized Output**: Each game is generated in its own dedicated folder with complete documentation
- 🎲 **Multiple Game Types**: Classic arcade games + traditional Indian games
- 📦 **Batch Generation**: Generate all games at once or individual games
- 🔍 **Quality Assurance**: Automatic code review and evaluation for each generated game

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
- OpenAI API Key

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
Create a `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

4. **Install Pygame** (required for running games):
```bash
pip install pygame
```

## 🎯 Usage

### Generate All Games (Batch Mode)
Generate all available games at once:
```bash
crewai run
```

This will create individual folders for each game in the `output/` directory:
```
output/
├── pac-man_clone/
├── snake_game/
├── pong_game/
├── breakout_game/
├── simple_tetris/
├── snakes_and_ladders/
├── carrom_board_game/
├── kabaddi_game/
├── pithu_(seven_stones)/
└── gilli_danda/
```

### Run Generated Games
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

### Generated Files Structure
Each game folder contains:
- `generated_game.py` - Complete playable Python game
- `code_review.md` - Detailed code review and analysis  
- `final_evaluation.md` - Quality assessment and recommendations

## 🤖 AI Agent System

The system uses **three specialized AI agents** working collaboratively:

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
│   │   └── gamedesign.yaml      # Game specifications
│   ├── crew.py                  # Main crew orchestration
│   └── main.py                  # Entry point and batch processing
├── output/                      # Generated games (auto-created)
│   ├── [game_name]/
│   │   ├── generated_game.py    # Playable game
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
