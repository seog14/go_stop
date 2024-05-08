from simplified_go_stop import SimplifiedGoStop
from models.action import Action
import numpy as np 
import pickle
from tqdm import tqdm

class GoStopNode(): 
    def __init__(self, num_actions, infoSet: tuple):
        self.infoSet = infoSet
        self.regretSum = np.zeros(shape=num_actions)
        self.strategySum = np.zeros(shape=num_actions)
        self.strategy = np.zeros(shape=num_actions)

    def get_strategy(self, realizationWeight): 
        self.strategy = np.maximum(self.regretSum, 0)
        normalizingSum = np.sum(self.strategy)

        if normalizingSum > 0: 
            self.strategy /= normalizingSum
        else: 
            self.strategy = np.ones_like(self.strategy)/(self.strategy.shape[0])
        
        self.strategySum += realizationWeight * self.strategy

        return self.strategy
    
    def get_average_strategy(self): 
        normalizingSum = np.sum(self.strategySum)
        average_strategy = np.copy(self.strategySum)
        if normalizingSum > 0: 
            average_strategy /= normalizingSum
        else: 
            average_strategy = np.ones_like(self.strategy) / len(self.strategy)

        return average_strategy 
    
    def __str__(self): 
        return f'{self.infoSet}: {self.get_average_strategy()}'


class GoStopAI(): 
    def __init__(self):
        self.nodeMap = dict()

    def save_nodeMap(self, filename="saved_Nodemaps/simple"): 
        with open(filename, "wb") as f:
            pickle.dump(self.nodeMap, f)

    def load_nodeMap(self, filename="saved_Nodemaps/simple"):
        with open(filename, "rb") as f:
            self.nodeMap = pickle.load(f)  

    def train(self, iterations: int): 
        util = 0
        # game = SimplifiedGoStop()
        # self.game = game 
        for _ in tqdm(range(iterations)):
            game = SimplifiedGoStop()
            # Starts random game of simplified go stop 
            util += self.cfr(1, game.serialize(), None, 1, 1)
            util += self.cfr(2, game.serialize(), None, 1, 1)
        print(f"Avg game value: {util/iterations}")
            

    def cfr(self, player_num, serialized_game_state: tuple, action_to_play: Action, pr_1, pr_2): 
        # Load in current game state 
        game = SimplifiedGoStop.deserialize(serialized_game_state)
        if action_to_play:
            game.play(action_to_play)
        if game.terminal: 
            # print(game.winner)
            # print(player_num)
            # print(game.get_utility(player_num))
            return game.get_utility(player_num)
        
        # Get Information Set Node or Create if Inexistant
        num_actions = len(game.actions())
        infoSet = game.get_infoSet()
        curr_node = self.nodeMap.get(infoSet)
        if curr_node == None: 
            curr_node = GoStopNode(num_actions, infoSet)
            self.nodeMap[infoSet] = curr_node
        
        #Get current strategies for this info set 
        current_player_number = game.get_current_player_number()
        strategy = curr_node.get_strategy(pr_1 if player_num == 1 else pr_2)
        utils = np.zeros(num_actions)
        nodeUtil = 0 
        for index, action in enumerate(game.actions()): 
            if current_player_number == 1: 
                utils[index] = self.cfr(player_num, game.serialize(), action, pr_1 * strategy[index], pr_2)
            else:
                utils[index] = self.cfr(player_num, game.serialize(), action, pr_1, pr_2 * strategy[index])

            nodeUtil += strategy[index] * utils[index]
        
        if current_player_number == player_num: 
            for index, action in enumerate(game.actions()): 
                regret = utils[index] - nodeUtil 
                curr_node.regretSum[index] += regret * pr_1 if player_num == 2 else regret * pr_2
            
        return nodeUtil
    