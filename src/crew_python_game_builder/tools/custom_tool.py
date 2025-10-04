from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import json
import os
import ast
import subprocess
import sys


class CodeValidationInput(BaseModel):
    """Input schema for Code Validation Tool."""
    code: str = Field(..., description="Python game code to validate for syntax and basic functionality.")

class CodeValidationTool(BaseTool):
    name: str = "Code Syntax Validator"
    description: str = (
        "Validates Python game code for syntax errors, import issues, and basic functionality checks. "
        "Returns detailed validation results with specific error locations and suggestions."
    )
    args_schema: Type[BaseModel] = CodeValidationInput

    def _run(self, code: str) -> str:
        """Validate Python code for syntax and basic issues."""
        validation_results = {
            "syntax_valid": False,
            "imports_valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Check syntax
            ast.parse(code)
            validation_results["syntax_valid"] = True
            
            # Check for common pygame imports
            required_imports = ["pygame", "sys", "random"]
            missing_imports = []
            
            for imp in required_imports:
                if f"import {imp}" not in code and f"from {imp}" not in code:
                    missing_imports.append(imp)
            
            if not missing_imports:
                validation_results["imports_valid"] = True
            else:
                validation_results["warnings"].append(f"Missing recommended imports: {missing_imports}")
            
            # Check for main execution block
            if 'if __name__ == "__main__":' not in code:
                validation_results["warnings"].append("Missing main execution block")
            
            # Check for game loop
            if "while" not in code.lower():
                validation_results["warnings"].append("No game loop detected")
                
        except SyntaxError as e:
            validation_results["errors"].append(f"Syntax Error at line {e.lineno}: {e.msg}")
        except Exception as e:
            validation_results["errors"].append(f"Validation Error: {str(e)}")
        
        return json.dumps(validation_results, indent=2)


class GameArchitectureInput(BaseModel):
    """Input schema for Game Architecture Tool."""
    game_type: str = Field(..., description="Type of game to generate architecture for (e.g., 'snake', 'pong', 'tetris').")
    features: list = Field(..., description="List of required game features.")

class GameArchitectureTool(BaseTool):
    name: str = "Game Architecture Designer"
    description: str = (
        "Generates professional game architecture patterns and class structures for different game types. "
        "Provides detailed architectural recommendations, design patterns, and component organization."
    )
    args_schema: Type[BaseModel] = GameArchitectureInput

    def _run(self, game_type: str, features: list) -> str:
        """Generate game architecture recommendations."""
        architectures = {
            "snake": {
                "classes": ["Game", "Snake", "Food", "GameBoard", "ScoreManager", "InputHandler"],
                "patterns": ["State Machine", "Observer Pattern"],
                "components": ["Game Loop", "Collision Detection", "Rendering System", "Input System"]
            },
            "pong": {
                "classes": ["Game", "Paddle", "Ball", "ScoreBoard", "GameState", "PhysicsEngine"],
                "patterns": ["Component System", "State Machine"],
                "components": ["Physics System", "Collision System", "AI System", "Rendering System"]
            },
            "tetris": {
                "classes": ["Game", "Tetromino", "GameBoard", "ScoreManager", "PieceGenerator", "LineClearing"],
                "patterns": ["Factory Pattern", "State Machine", "Command Pattern"],
                "components": ["Piece System", "Grid System", "Rotation Logic", "Line Clear System"]
            }
        }
        
        arch = architectures.get(game_type.lower(), {
            "classes": ["Game", "Player", "GameState", "Renderer", "InputHandler"],
            "patterns": ["State Machine", "Component System"],
            "components": ["Game Loop", "Rendering System", "Input System", "Update System"]
        })
        
        recommendations = {
            "architecture": arch,
            "recommended_features": features,
            "performance_tips": [
                "Use sprite groups for efficient collision detection",
                "Implement object pooling for frequently created/destroyed objects",
                "Use dirty rectangle updates for better performance",
                "Implement frame rate limiting and delta time calculations"
            ],
            "code_organization": {
                "structure": "Separate classes into individual files for larger games",
                "constants": "Define game constants at the top of the file",
                "main_loop": "Keep the main game loop clean and delegate to methods"
            }
        }
        
        return json.dumps(recommendations, indent=2)


class PerformanceOptimizerInput(BaseModel):
    """Input schema for Performance Optimizer Tool."""
    code: str = Field(..., description="Python game code to analyze for performance optimization opportunities.")

class PerformanceOptimizerTool(BaseTool):
    name: str = "Game Performance Optimizer"
    description: str = (
        "Analyzes game code for performance bottlenecks and provides specific optimization recommendations. "
        "Identifies inefficient patterns and suggests pygame-specific optimizations."
    )
    args_schema: Type[BaseModel] = PerformanceOptimizerInput

    def _run(self, code: str) -> str:
        """Analyze code for performance optimization opportunities."""
        optimizations = {
            "performance_issues": [],
            "optimizations": [],
            "pygame_specific": [],
            "memory_optimizations": []
        }
        
        # Check for common performance issues
        if "pygame.image.load" in code and code.count("pygame.image.load") > 3:
            optimizations["performance_issues"].append("Multiple image loads detected - consider preloading")
            optimizations["optimizations"].append("Implement asset manager for preloading images")
        
        if "pygame.font.Font" in code and code.count("pygame.font.Font") > 1:
            optimizations["performance_issues"].append("Multiple font objects - consider reusing font instances")
        
        if ".fill(" in code and "pygame.display.flip()" in code:
            optimizations["pygame_specific"].append("Consider using pygame.display.update() with dirty rectangles instead of flip()")
        
        if "for" in code and "blit" in code:
            optimizations["pygame_specific"].append("Use sprite groups for batch rendering operations")
        
        if "pygame.time.delay" in code:
            optimizations["performance_issues"].append("pygame.time.delay() blocks execution - use Clock.tick() instead")
        
        # Memory optimization suggestions
        optimizations["memory_optimizations"].extend([
            "Use sprite groups and kill() method for automatic cleanup",
            "Implement object pooling for frequently spawned objects",
            "Use pygame.Surface.convert() for faster blitting",
            "Consider using pygame.Surface.convert_alpha() for images with transparency"
        ])
        
        return json.dumps(optimizations, indent=2)
