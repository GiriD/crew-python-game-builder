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
    Run the crew to generate all example games.
    """
    print("## Welcome to the Game Builder Crew")
    print("## Generating ALL Example Games")
    print('-------------------------------')

    with open('src/crew_python_game_builder/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    # Filter out only the example games (keys starting with 'example')
    game_examples = {key: value for key, value in examples.items() if key.startswith('example')}
    
    total_games = len(game_examples)
    successful_games = []
    failed_games = []
    
    print(f"\nFound {total_games} games to generate:")
    for key, game in game_examples.items():
        print(f"- {game.get('name', key)}")
    print("\n" + "="*50)
    
    for i, (example_key, game_data) in enumerate(game_examples.items(), 1):
        game_name = game_data.get('name', 'unknown_game').lower().replace(' ', '_')
        
        print(f"\n[{i}/{total_games}] Generating: {game_data.get('name', example_key)}")
        print(f"Game Type: {game_data.get('type', 'Unknown')}")
        print("-" * 40)
        
        inputs = {
            'game': game_data
        }
        
        try:
            crew_builder = CrewPythonGameBuilder(game_name=game_name)
            result = crew_builder.crew().kickoff(inputs=inputs)
            
            successful_games.append({
                'name': game_data.get('name', example_key),
                'folder': crew_builder.output_folder,
                'key': example_key
            })
            
            print(f"✅ SUCCESS: {game_data.get('name', example_key)} generated!")
            print(f"   Files saved in: {crew_builder.output_folder}/")
            
        except Exception as e:
            failed_games.append({
                'name': game_data.get('name', example_key),
                'key': example_key,
                'error': str(e)
            })
            print(f"❌ FAILED: {game_data.get('name', example_key)}")
            print(f"   Error: {str(e)}")
    
    # Final summary
    print("\n" + "="*60)
    print("## BATCH GENERATION COMPLETE!")
    print("="*60)
    print(f"Total games processed: {total_games}")
    print(f"Successful: {len(successful_games)}")
    print(f"Failed: {len(failed_games)}")
    
    if successful_games:
        print(f"\n✅ SUCCESSFUL GAMES ({len(successful_games)}):")
        for game in successful_games:
            print(f"   • {game['name']}")
            print(f"     📁 Folder: {game['folder']}/")
            print(f"     🎮 Run: python {game['folder']}/generated_game.py")
            print()
    
    if failed_games:
        print(f"\n❌ FAILED GAMES ({len(failed_games)}):")
        for game in failed_games:
            print(f"   • {game['name']}: {game['error']}")
            print()
    
    print("="*60)


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
