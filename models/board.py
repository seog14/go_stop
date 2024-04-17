from .player import Player
from .deck import Deck
from .card import Card
from .card_list import CardList
from .constants import Month
from typing import List, Dict

class Board(): 
    def __init__(self):
        while(True):
            self.deck = Deck()
            player_one_hand, player_two_hand, center_cards = self.deck.deal()
            if not self.reset(player_one_hand, player_two_hand, center_cards): 
                break
        self.p1 = Player(player_one_hand, 1)
        self.p2 = Player(player_two_hand, 2)
        self.center_cards: Dict[Month, CardList] = dict( 
            ((month, center_cards.of_month(month)) for month in Month)
        )
        self.curr_player = self.p1 

    def switch_turn(self):
        if self.curr_player == self.p1: 
            self.curr_player = self.p2
        else: 
            self.curr_player = self.p1

    def reset(self, player_one_hand, player_two_hand, center_cards):
        # Either player has 4 of same month or the center cards have 4 of same month
        return (self.same_four_month(player_one_hand) or 
                self.same_four_month(player_two_hand) or 
                self.same_four_month(center_cards))

    def same_four_month(self, cards: List[Card]):
        consecutive_months = 0 
        curr_month = cards[0].month
        for card in cards: 
            if card.month == curr_month: 
                consecutive_months += 1
            else: 
                curr_month = card.month
                consecutive_months = 1 
            if consecutive_months == 4: 
                print(cards)
                return True         
            
        return False

    def get_opponent(self): 
        if self.curr_player == self.p1: 
            return self.p2 
        else: 
            return self.p1
        