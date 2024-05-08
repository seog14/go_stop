from simplified_go_stop import SimplifiedGoStop
from go_stop_ai import GoStopAI
import random 
import numpy as np 

# Initialize AI 
ai = GoStopAI()
ai.load_nodeMap()

continue_game = True

def get_action(strategy): 
    rr = random.random()
    cum_strategy = np.cumsum(strategy)
    return np.searchsorted(cum_strategy, rr)


while(continue_game):
    # Select which player you want to be 
    player_num = int(input("Enter 1 for player one or 2 for player 2: "))
    simplified_game = SimplifiedGoStop()

    while not simplified_game.terminal: 
        # Show the Current board 
        simplified_game.display_game(player_num)

        if simplified_game.get_current_player_number() == int(player_num): 
            
            has_infoSet = False
            # Show AI's decision
            if ai.nodeMap.get(simplified_game.get_infoSet()):
                curr_strategy = ai.nodeMap[simplified_game.get_infoSet()].get_average_strategy()
                has_infoSet = True
            prompt = "What action do you want to take?\n"
            prompt += str([action.serialize() for action in simplified_game.actions()])
            if  has_infoSet: 
                prompt += f"\nAI has following strategy: {curr_strategy}\n"
            prompt += "\nChoose number for action: "

            action_num = int(input(prompt))

            action = simplified_game.actions()[action_num - 1]

            simplified_game.play(action)
        
        else: 
            if ai.nodeMap.get(simplified_game.get_infoSet()):
                curr_strategy = ai.nodeMap[simplified_game.get_infoSet()].get_average_strategy()
            else: 
                print("RANDOM ACTION\n")
                num_actions = len(simplified_game.actions())
                curr_strategy = np.ones(num_actions) / num_actions
            action = get_action(curr_strategy)
            selected_action = simplified_game.actions()[action]
            print(f"Villain's selected action is: {selected_action}\n")
            simplified_game.play(selected_action)
        print(simplified_game.get_current_player_number())
        input("Click anything for Next game state")

    print(f"Finished game state: {simplified_game.display()}")
    print(simplified_game.get_utility(player_num))
    
    continue_game = input("type True if you want to playe new game, false otherwise")


        