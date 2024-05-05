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
                return True         
            
        return False

    def get_opponent(self): 
        if self.curr_player == self.p1: 
            return self.p2 
        else: 
            return self.p1
    
    def __str__(self):
        result = f"curr player: {self.curr_player}\n"
        result += f"opp player: {self.get_opponent()}\n"
        for month, cards in self.center_cards.items(): 
            result += f"{month.name}:"
            for card in cards: 
                result += f" {card}"
            result += " "
        return result
    
    def sort(self): 
        self.p1.sort() 
        self.p2.sort()
        
    
    def serialize(self) -> dict: 
        self.sort()
        return {
            
            "deck": self.deck.serialize(),
            "p1": Player.serialize(self.p1), 
            "p2": Player.serialize(self.p2), 
            "center_cards": dict(
                (int(month.value), self.center_cards[month].serialize())
                for month in Month 
                if self.center_cards[month] != []
            ),
            "curr_player": self.curr_player.number
    
        }
    
    @staticmethod
    def deserialize(serialized_board): 

        board = Board()

        board.deck = Deck.deserialize(serialized_board["deck"])
        board.p1 = Player.deserialize(serialized_board["p1"])
        board.p2 = Player.deserialize(serialized_board["p2"])
        
        center_cards = serialized_board["center_cards"]

        board.center_cards = dict(
            (
                month, 
                CardList.deserialize(center_cards[month])
                if month.value in center_cards
                else CardList([])
            )
            for month in Month
        )

        if serialized_board["curr_player"] == 1: 
            board.curr_player = board.p1 
        else: 
            board.curr_player = board.p2
        
        return board.sort() 
