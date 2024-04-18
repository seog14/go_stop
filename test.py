from go_stop import GoStop
import random 

def run_game(game): 
    while not game.terminal: 
        # print(f"cards left: {len(game.board.deck)}")
        # game.display()
        actions = game.actions() 
        if not actions: 
            break
        random_action =  random.choice(actions)
        game.play(random_action)

    return game.calculate_winnings()

p1_winnings = []
p2_winnings = []
for _ in range(1000): 
    game = GoStop() 
    p1, p2 = run_game(game) 
    p1_winnings.append(p1)
    p2_winnings.append(p2)
print(sum(p1_winnings) / len(p1_winnings))
print(sum(p2_winnings)/len(p2_winnings))