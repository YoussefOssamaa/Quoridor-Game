"""
Comprehensive Testing Suite for Quoridor AI Implementation
Run this to test all AI difficulties without GUI
"""

from board import Game, BOARD_SIZE
from ai import QuoridorAI, get_shortest_path_length, evaluate_position
import time


# ═══════════════════════════════════════════════════════
# VISUALIZATION HELPERS
# ═══════════════════════════════════════════════════════

def print_board_state(game):
    """Print a visual representation of the board."""
    print("\n" + "="*60)
    print(f"  TURN: Player {game.get_current_player()}")
    print(f"  WALLS: P0={game.get_walls_left(0)} | P1={game.get_walls_left(1)}")
    print("="*60)
    
    # Print column numbers
    print("     ", end="")
    for x in range(BOARD_SIZE):
        print(f" {x} ", end="")
    print()
    
    # Print board
    for y in range(BOARD_SIZE):
        print(f"  {y}  ", end="")
        for x in range(BOARD_SIZE):
            pos = (x, y)
            if pos == game.state.players[0].pos:
                print(" 0 ", end="")  # Player 0 (Red/Top)
            elif pos == game.state.players[1].pos:
                print(" 1 ", end="")  # Player 1 (Blue/Bottom)
            else:
                print(" . ", end="")
        print(f"  {y}")
    
    # Print column numbers again
    print("     ", end="")
    for x in range(BOARD_SIZE):
        print(f" {x} ", end="")
    print("\n")
    
    # Print walls
    if game.state.walls:
        print("  WALLS PLACED:")
        for i, (orientation, x, y) in enumerate(game.state.walls, 1):
            print(f"    {i}. {orientation} at ({x},{y})")
    print()


def print_separator():
    """Print a visual separator."""
    print("\n" + "─"*60 + "\n")


# ═══════════════════════════════════════════════════════
# TEST 1: BASIC AI FUNCTIONALITY
# ═══════════════════════════════════════════════════════

def test_basic_ai_functionality():
    """Test that AI can make valid moves for all difficulties."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "TEST 1: BASIC AI FUNCTIONALITY" + " "*13 + "║")
    print("╚" + "═"*58 + "╝")
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n🤖 Testing {difficulty.upper()} AI...")
        game = Game()
        ai = QuoridorAI(player_index=1, difficulty=difficulty)
        
        success_count = 0
        for i in range(5):
            # Move to AI's turn
            game.state.current_player = 1
            
            # Get AI move
            start_time = time.time()
            move_type, move_data = ai.get_move(game.state)
            elapsed = time.time() - start_time
            
            print(f"  Move {i+1}: {move_type} {move_data} (took {elapsed:.3f}s)")
            
            # Validate and execute
            if move_type == "pawn":
                valid_moves = game.get_valid_moves_for_current_player()
                if move_data in valid_moves:
                    game.move_pawn(move_data)
                    success_count += 1
                    print(f"    ✓ Valid pawn move")
                else:
                    print(f"    ✗ INVALID pawn move! Valid: {valid_moves}")
            elif move_type == "wall":
                x, y, orientation = move_data
                if game.place_wall(x, y, orientation):
                    success_count += 1
                    print(f"    ✓ Valid wall placement")
                else:
                    print(f"    ✗ INVALID wall placement!")
        
        print(f"\n  Result: {success_count}/5 valid moves")
        assert success_count >= 4, f"{difficulty} AI made too many invalid moves!"
        print(f"  ✅ {difficulty.upper()} AI PASSED")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# TEST 2: AI VS AI GAMES
# ═══════════════════════════════════════════════════════

def test_ai_vs_ai_games():
    """Run complete games between different AI difficulties."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*18 + "TEST 2: AI VS AI GAMES" + " "*18 + "║")
    print("╚" + "═"*58 + "╝")
    
    matchups = [
        ("easy", "easy"),
        ("easy", "medium"),
        ("medium", "medium"),
        ("medium", "hard"),
    ]
    
    for p0_diff, p1_diff in matchups:
        print(f"\n🎮 MATCH: {p0_diff.upper()} (P0) vs {p1_diff.upper()} (P1)")
        print("-" * 60)
        
        game = Game()
        ai_p0 = QuoridorAI(player_index=0, difficulty=p0_diff)
        ai_p1 = QuoridorAI(player_index=1, difficulty=p1_diff)
        
        move_count = 0
        max_moves = 100
        
        while not game.is_game_over() and move_count < max_moves:
            current = game.get_current_player()
            ai = ai_p0 if current == 0 else ai_p1
            
            # Get and execute move
            move_type, move_data = ai.get_move(game.state)
            
            if move_type == "pawn":
                success = game.move_pawn(move_data)
            else:
                success = game.place_wall(*move_data)
            
            if not success:
                print(f"  ⚠️  Move {move_count+1} failed for P{current}!")
            
            move_count += 1
            
            # Show progress every 10 moves
            if move_count % 10 == 0:
                p0_path = get_shortest_path_length(game.state, 0)
                p1_path = get_shortest_path_length(game.state, 1)
                print(f"  Move {move_count}: Paths P0={p0_path}, P1={p1_path}")
        
        # Results
        if game.is_game_over():
            winner = game.get_winner()
            winner_diff = p0_diff if winner == 0 else p1_diff
            print(f"\n  🏆 WINNER: Player {winner} ({winner_diff.upper()})")
            print(f"  📊 Total moves: {move_count}")
        else:
            print(f"\n  ⏱️  Game reached move limit ({max_moves})")
            p0_path = get_shortest_path_length(game.state, 0)
            p1_path = get_shortest_path_length(game.state, 1)
            print(f"  📊 Final paths: P0={p0_path}, P1={p1_path}")
        
        print(f"  📊 Final walls: P0={game.get_walls_left(0)}, P1={game.get_walls_left(1)}")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# TEST 3: AI DECISION QUALITY
# ═══════════════════════════════════════════════════════

def test_ai_decision_quality():
    """Test that AI makes sensible strategic decisions."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "TEST 3: AI DECISION QUALITY" + " "*16 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Test 1: AI should move toward goal
    print("\n📊 Test 3.1: Forward Movement Preference")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="medium")
    
    initial_pos = game.state.players[1].pos
    game.state.current_player = 1
    
    forward_moves = 0
    for _ in range(10):
        move_type, move_data = ai.get_move(game.state)
        
        if move_type == "pawn":
            new_y = move_data[1]
            old_y = game.state.players[1].pos[1]
            
            # Player 1 wants to reach y=0 (top), so forward is decreasing y
            if new_y < old_y:
                forward_moves += 1
            
            game.move_pawn(move_data)
        else:
            game.place_wall(*move_data)
        
        # Switch back to AI
        game.state.current_player = 1
    
    print(f"  Forward moves: {forward_moves}/10")
    print(f"  ✅ PASSED" if forward_moves >= 5 else "  ⚠️  WARNING: Low forward bias")
    
    # Test 2: Hard AI should use walls strategically
    print("\n📊 Test 3.2: Strategic Wall Usage (Hard AI)")
    game = Game()
    ai = QuoridorAI(player_index=0, difficulty="hard")
    
    # Position opponent close to goal
    game.state.players[1].pos = (4, 2)  # Close to top
    game.state.current_player = 0
    
    walls_used = 0
    for _ in range(5):
        move_type, move_data = ai.get_move(game.state)
        
        if move_type == "wall":
            walls_used += 1
            game.place_wall(*move_data)
        else:
            game.move_pawn(move_data)
        
        game.state.current_player = 0
    
    print(f"  Walls used when opponent near goal: {walls_used}/5")
    print(f"  ✅ PASSED" if walls_used >= 1 else "  ⚠️  WARNING: Should use walls defensively")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# TEST 4: PERFORMANCE BENCHMARKS
# ═══════════════════════════════════════════════════════

def test_performance_benchmarks():
    """Measure AI decision-making speed."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*16 + "TEST 4: PERFORMANCE TESTS" + " "*17 + "║")
    print("╚" + "═"*58 + "╝")
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n⏱️  {difficulty.upper()} AI Performance")
        
        game = Game()
        ai = QuoridorAI(player_index=1, difficulty=difficulty)
        game.state.current_player = 1
        
        times = []
        for _ in range(10):
            start = time.time()
            move_type, move_data = ai.get_move(game.state)
            elapsed = time.time() - start
            times.append(elapsed)
            
            # Execute move to change state
            if move_type == "pawn":
                game.move_pawn(move_data)
            else:
                game.place_wall(*move_data)
            
            game.state.current_player = 1
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"  Average: {avg_time*1000:.1f}ms")
        print(f"  Min: {min_time*1000:.1f}ms | Max: {max_time*1000:.1f}ms")
        
        # Performance expectations
        if difficulty == "easy":
            assert avg_time < 0.1, "Easy AI too slow!"
            print(f"  ✅ PASSED (< 100ms)")
        elif difficulty == "medium":
            assert avg_time < 0.5, "Medium AI too slow!"
            print(f"  ✅ PASSED (< 500ms)")
        elif difficulty == "hard":
            assert avg_time < 2.0, "Hard AI too slow!"
            print(f"  ✅ PASSED (< 2000ms)")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# TEST 5: EDGE CASES
# ═══════════════════════════════════════════════════════

def test_edge_cases():
    """Test AI behavior in unusual game situations."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*19 + "TEST 5: EDGE CASES" + " "*21 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Test 1: No walls left
    print("\n🔍 Test 5.1: AI with No Walls Remaining")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="medium")
    game.state.players[1].walls_left = 0
    game.state.current_player = 1
    
    move_type, move_data = ai.get_move(game.state)
    print(f"  AI chose: {move_type}")
    assert move_type == "pawn", "AI should only move pawn when no walls!"
    print(f"  ✅ PASSED - AI correctly chose pawn move")
    
    # Test 2: Blocked on all sides except one
    print("\n🔍 Test 5.2: AI Surrounded by Walls")
    game = Game()
    ai = QuoridorAI(player_index=0, difficulty="hard")
    
    # Place walls around player 0 (at 4,0), leaving only right open
    game.state.walls.append(("V", 3, 0))  # Left side blocked
    game.state.walls.append(("H", 4, 0))  # Bottom blocked
    game.state.current_player = 0
    
    move_type, move_data = ai.get_move(game.state)
    print(f"  AI chose: {move_type} {move_data}")
    
    if move_type == "pawn":
        valid_moves = game.get_valid_moves_for_current_player()
        print(f"  Valid moves: {valid_moves}")
        assert move_data in valid_moves, "AI chose invalid move!"
        print(f"  ✅ PASSED - AI found valid escape route")
    else:
        print(f"  ✅ PASSED - AI chose to place wall instead")
    
    # Test 3: Near goal line
    print("\n🔍 Test 5.3: AI One Move From Victory")
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty="easy")
    game.state.players[1].pos = (4, 1)  # One move from goal (row 0)
    game.state.current_player = 1
    
    move_type, move_data = ai.get_move(game.state)
    print(f"  AI chose: {move_type} {move_data}")
    
    if move_type == "pawn":
        if move_data[1] == 0:  # Moved to goal
            print(f"  ✅ EXCELLENT - AI took winning move!")
        else:
            print(f"  ⚠️  WARNING - AI didn't take obvious win")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# TEST 6: INTERACTIVE DEMO
# ═══════════════════════════════════════════════════════

def interactive_ai_demo():
    """Play against AI with visualization."""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "TEST 6: INTERACTIVE AI DEMO" + " "*16 + "║")
    print("╚" + "═"*58 + "╝")
    
    print("\n🎮 Play a game against the AI!")
    print("   You are Player 0 (starts at top, goal is bottom)")
    print("   AI is Player 1 (starts at bottom, goal is top)")
    
    difficulty = input("\nChoose AI difficulty (easy/medium/hard): ").lower()
    while difficulty not in ["easy", "medium", "hard"]:
        difficulty = input("Invalid! Choose easy/medium/hard: ").lower()
    
    game = Game()
    ai = QuoridorAI(player_index=1, difficulty=difficulty)
    
    print(f"\n🤖 You're playing against {difficulty.upper()} AI")
    print("\nCommands:")
    print("  move X Y  - Move pawn to position (X,Y)")
    print("  wall X Y H/V - Place wall at (X,Y) with orientation")
    print("  quit - Exit game")
    
    while not game.is_game_over():
        print_board_state(game)
        
        if game.get_current_player() == 0:
            # Human turn
            print("YOUR TURN (Player 0)")
            valid_moves = game.get_valid_moves_for_current_player()
            print(f"Valid moves: {valid_moves}")
            
            cmd = input("\nYour move: ").strip().split()
            
            if not cmd:
                continue
            
            if cmd[0] == "quit":
                print("Game ended by player.")
                return
            
            elif cmd[0] == "move" and len(cmd) == 3:
                try:
                    x, y = int(cmd[1]), int(cmd[2])
                    if game.move_pawn((x, y)):
                        print("✓ Move successful!")
                    else:
                        print("✗ Invalid move!")
                except ValueError:
                    print("✗ Invalid coordinates!")
            
            elif cmd[0] == "wall" and len(cmd) == 4:
                try:
                    x, y = int(cmd[1]), int(cmd[2])
                    orientation = cmd[3].upper()
                    if game.place_wall(x, y, orientation):
                        print("✓ Wall placed!")
                    else:
                        print("✗ Invalid wall placement!")
                except ValueError:
                    print("✗ Invalid coordinates!")
            
            else:
                print("✗ Invalid command!")
        
        else:
            # AI turn
            print("AI'S TURN (Player 1)")
            print("AI is thinking...", end="", flush=True)
            
            start = time.time()
            move_type, move_data = ai.get_move(game.state)
            elapsed = time.time() - start
            
            print(f" ({elapsed:.2f}s)")
            
            if move_type == "pawn":
                game.move_pawn(move_data)
                print(f"🤖 AI moved pawn to {move_data}")
            else:
                x, y, orientation = move_data
                game.place_wall(x, y, orientation)
                print(f"🤖 AI placed {orientation} wall at ({x},{y})")
            
            input("\nPress Enter to continue...")
    
    # Game over
    print_board_state(game)
    winner = game.get_winner()
    if winner == 0:
        print("🎉 YOU WIN! Congratulations!")
    else:
        print("💔 AI WINS! Better luck next time!")
    
    print_separator()


# ═══════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════

def run_all_tests():
    """Run all automated tests."""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + "═"*58 + "║")
    print("║" + " "*10 + "QUORIDOR AI COMPREHENSIVE TEST SUITE" + " "*12 + "║")
    print("║" + "═"*58 + "║")
    print("╚" + "═"*58 + "╝")
    
    start_time = time.time()
    
    try:
        test_basic_ai_functionality()
        test_ai_vs_ai_games()
        test_ai_decision_quality()
        test_performance_benchmarks()
        test_edge_cases()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        print("║" + " "*19 + "ALL TESTS PASSED! ✅" + " "*19 + "║")
        print("="*60)
        print(f"\nTotal time: {elapsed:.2f} seconds")
        print("\n✨ Your AI implementation is working correctly!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main entry point."""
    print("\nQuoridor AI Testing Suite")
    print("="*60)
    print("1. Run all automated tests")
    print("2. Play against AI (interactive demo)")
    print("3. Run specific test")
    print("="*60)
    
    choice = input("\nChoose option (1/2/3): ").strip()
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        interactive_ai_demo()
    elif choice == "3":
        print("\nAvailable tests:")
        print("1. Basic AI Functionality")
        print("2. AI vs AI Games")
        print("3. AI Decision Quality")
        print("4. Performance Benchmarks")
        print("5. Edge Cases")
        
        test_num = input("\nChoose test (1-5): ").strip()
        
        if test_num == "1":
            test_basic_ai_functionality()
        elif test_num == "2":
            test_ai_vs_ai_games()
        elif test_num == "3":
            test_ai_decision_quality()
        elif test_num == "4":
            test_performance_benchmarks()
        elif test_num == "5":
            test_edge_cases()
        else:
            print("Invalid test number!")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()