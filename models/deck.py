from .card import (
    AnimalCard, 
    BrightCard,
    RibbonCard,
    JunkCard,
    SwitchCard
)
from .constants import Month

import random

class Deck(): 
    def __init__(self):

        bright_cards = [BrightCard(month) for month in BrightCard.months]
        animal_cards = [AnimalCard(month) for month in AnimalCard.months]
        ribbon_cards = [RibbonCard(month) for month in RibbonCard.months]
        junk_cards = [JunkCard(month, index) for month in Month if month.value < 11 for index in range(0,2)] + [JunkCard(Month.NOV, index=0), JunkCard(Month.NOV, index=1), JunkCard(Month.NOV, index=2, double=1)] + [JunkCard(Month.DEC, index=0, double=1)]
        switch_cards = [SwitchCard(month) for month in SwitchCard.months]

        self.deck = bright_cards + animal_cards + ribbon_cards + junk_cards + switch_cards 
        self.max_cards = len(self.deck)
        self.shuffle() 

    def shuffle(self): 
        random.shuffle(self.deck)

    def __len__(self):
        return len(self.deck)

    def flip(self): 
        # Returns None if no more cards left in deck
        if len(self) == 0: 
            return None
        return self.deck.pop()
    
    def deal(self): 
        assert len(self) == self.max_cards 
        player_one_hand = self.deck[:10]
        player_two_hand = self.deck[10:20]
        open_cards = self.deck[20:28]
        del self.deck[:28]
        return player_one_hand, player_two_hand, open_cards
