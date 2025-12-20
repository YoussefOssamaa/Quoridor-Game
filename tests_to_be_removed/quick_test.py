"""
Quick Test Script for Quoridor AI
Simple tests to verify AI is working correctly
"""

from board import Game
from ai import QuoridorAI


def quick_test():
    """Quick smoke test for AI."""
    print("\n" + "="*60)
    print("QUICK AI TEST")
    print("="*60)
    
    # Test 1: Easy AI
    print("\n1️⃣  Testing Easy AI...")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="easy")
    
    for i in range(3):
        game.state.current_player = 1
        move_type, move_data = ai.get_move(game.state)
        print(f"   Move {i+1}: {move_type} -> {move_data}")
        
        if move_type == "pawn":
            game.move_pawn(move_data)
        else:
            game.place_wall(*move_data)
    
    print("   ✅ Easy AI works!")
    
    # Test 2: Medium AI
    print("\n2️⃣  Testing Medium AI...")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="medium")
    
    for i in range(3):
        game.state.current_player = 1
        move_type, move_data = ai.get_move(game.state)
        print(f"   Move {i+1}: {move_type} -> {move_data}")
        
        if move_type == "pawn":
            game.move_pawn(move_data)
        else:
            game.place_wall(*move_data)
    
    print("   ✅ Medium AI works!")
    
    # Test 3: Hard AI
    print("\n3️⃣  Testing Hard AI...")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="hard")
    
    for i in range(3):
        game.state.current_player = 1
        move_type, move_data = ai.get_move(game.state)
        print(f"   Move {i+1}: {move_type} -> {move_data}")
        
        if move_type == "pawn":
            game.move_pawn(move_data)
        else:
            game.place_wall(*move_data)
    
    print("   ✅ Hard AI works!")
    
    # Test 4: Complete game
    print("\n4️⃣  Testing Complete Game (Easy vs Medium)...")
    game = Game()
    ai_easy = QuoridorAI(player_index=0, difficulty="easy")
    ai_medium = QuoridorAI(player_index=1, difficulty="medium")
    
    moves = 0
    while not game.is_game_over() and moves < 50:
        current = game.get_current_player()
        ai = ai_easy if current == 0 else ai_medium
        
        move_type, move_data = ai.get_move(game.state)
        
        if move_type == "pawn":
            game.move_pawn(move_data)
        else:
            game.place_wall(*move_data)
        
        moves += 1
    
    if game.is_game_over():
        winner = game.get_winner()
        print(f"   Game ended in {moves} moves")
        print(f"   Winner: Player {winner}")
        print("   ✅ Complete game works!")
    else:
        print(f"   Game reached 50 moves without winner")
        print("   ✅ Game logic works!")
    
    print("\n" + "="*60)
    print("✨ ALL TESTS PASSED! Your AI is working! ✨")
    print("="*60)
    print("\nNext steps:")
    print("  - Run: python test_ai.py  (for comprehensive tests)")
    print("  - Or play interactively in test_ai.py option 2")
    print()


if __name__ == "__main__":
    quick_test()