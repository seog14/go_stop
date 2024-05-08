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
    
    def clear_center_cards(self): 
        self.center_cards = dict(
            (month, CardList()) for month in Month
        )

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
        result += "centercards: \n"
        for month, cards in self.center_cards.items(): 
            result += f"{month.name}:"
            for card in cards: 
                result += f" {card}"
            result += " \n"

        return result
    
    def sort(self): 
        self.p1.sort() 
        self.p2.sort()
        
    
    def serialize(self) -> dict: 
        self.sort()
        return tuple((
            
            self.deck.serialize(),
            self.p1.serialize(), 
            self.p2.serialize(), 
            tuple([
                (int(month.value), self.center_cards[month].serialize())
                for month in Month 
                if self.center_cards[month] != []
            ]),
            self.curr_player.number
        ))
    
    @staticmethod
    def deserialize(serialized_board): 

        board = Board()
        board.clear_center_cards()

        board.deck = Deck.deserialize(serialized_board[0])
        board.p1 = Player.deserialize(serialized_board[1])
        board.p2 = Player.deserialize(serialized_board[2])
        
        center_cards = serialized_board[3]

        for month, cardList in center_cards: 
            board.center_cards[Month(month)] = CardList.deserialize(cardList)

        if serialized_board[4] == 1: 
            board.curr_player = board.p1 
        else: 
            board.curr_player = board.p2
        board.sort()
        return board
    
    def get_hidden_information(self, player_num): 
        if player_num == 1: 
            return tuple((
                self.p1.serialize(), 
                self.p2.get_hidden_information(), 
                tuple([
                    (int(month.value), self.center_cards[month].serialize())
                    for month in Month 
                    if self.center_cards[month] != []
                ]),
                self.curr_player.number
            ))
        if player_num == 2: 
            return tuple((
                self.p1.get_hidden_information(), 
                self.p2.serialize(), 
                tuple([
                    (int(month.value), self.center_cards[month].serialize())
                    for month in Month 
                    if self.center_cards[month] != []
                ]),
                self.curr_player.number
            ))    

    def display_hidden_board(self, player_num):
        if player_num == 1: 
            hero = self.p1
            villain = self.p2
        else: 
            hero = self.p2 
            villain = self.p1

        hero.sort()
        villain.sort()

        result = f"Current Player: {self.curr_player.number}\n\n"
        result += f"Hero Num Go: {hero.num_go}\n"
        result += f"Hero Score: {hero.score}\n"
        result  += f"Hero Hand: {hero.hand}\n"
        result += f"Hero Captured: {hero.captured}\n\n"

        result += "centercards: \n"
        for month, cards in self.center_cards.items(): 
            result += f"\t{month.name}:"
            for card in cards: 
                result += f" {card}"
            result += " \n"
        result += "\n"
        
        result += f"Villain Num Go: {villain.num_go}\n"
        result += f"Villain Score: {villain.score}\n"
        result += f"Villain Captured: {villain.captured}\n"
        return result




