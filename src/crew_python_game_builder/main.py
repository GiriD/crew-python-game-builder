#!/usr/bin/env python
import sys
import warnings
import yaml

from crew_python_game_builder.crew import CrewPythonGameBuilder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    print("## Welcome to the Game Builder Crew")
    print('-------------------------------')

    with open('src/crew_python_game_builder/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    # Default to example2_snake if no argument provided, or use the argument
    game_key = 'example9_kabaddi'  # Default game
    if len(sys.argv) > 1:
        # Check if the argument is a valid game key
        arg_game_key = sys.argv[1]
        if arg_game_key in examples:
            game_key = arg_game_key
        else:
            # Try to find by name matching
            for key, game in examples.items():
                if key.startswith('example') and arg_game_key.lower() in game.get('name', '').lower():
                    game_key = key
                    break

    inputs = {
        'game': examples[game_key]
    }
    
    # Extract game name for folder organization
    game_name = inputs['game'].get('name', 'unknown_game').lower().replace(' ', '_')
    
    try:
        crew_builder = CrewPythonGameBuilder(game_name=game_name)
        result = crew_builder.crew().kickoff(inputs=inputs)
        
        print("\n\n########################")
        print("## Game Builder Crew Completed!")
        print("########################\n")
        print(f"Generated files saved in the '{crew_builder.output_folder}' folder:")
        print("- generated_game.py (The complete Python game)")
        print("- architecture_design.md (Software architecture)")
        print("- ui_design_specs.md (UI/UX design specifications)")
        print("- audio_design_specs.md (Audio design specifications)")
        print("- code_review.md (Code review report)")
        print("- final_evaluation.md (Final evaluation report)")
        print(f"\nTo run the generated game:")
        print(f"python {crew_builder.output_folder}/generated_game.py")
        print(f"\nCrew execution result: {result}")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    with open('src/crew_python_game_builder/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    inputs = {
        'game': examples['example1_pacman']
    }
    
    # Extract game name for folder organization
    game_name = inputs['game'].get('name', 'unknown_game').lower().replace(' ', '_')
    
    try:
        CrewPythonGameBuilder(game_name=game_name).crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CrewPythonGameBuilder().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    with open('src/crew_python_game_builder/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    inputs = {
        'game': examples['example3_pong']
    }
    
    # Extract game name for folder organization
    game_name = inputs['game'].get('name', 'unknown_game').lower().replace(' ', '_')
    
    try:
        CrewPythonGameBuilder(game_name=game_name).crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
