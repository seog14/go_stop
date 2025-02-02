from .card import (
    AnimalCard, 
    BrightCard,
    RibbonCard,
    JunkCard,
    SwitchCard
)
from .card_list import CardList
from .constants import Month

import random
import copy

class Deck(): 
    def __init__(self, deck: CardList = None):

        bright_cards = CardList(BrightCard(month) for month in BrightCard.months)
        animal_cards = CardList(AnimalCard(month) for month in AnimalCard.months)
        ribbon_cards = CardList(RibbonCard(month) for month in RibbonCard.months)
        junk_cards = CardList([JunkCard(month, index) for month in Month if month.value < 11 for index in range(0,2)] + 
                              [JunkCard(Month.NOV, index=0), JunkCard(Month.NOV, index=1), JunkCard(Month.NOV, index=2, double=1)] + 
                              [JunkCard(Month.DEC, index=0, double=1)])
        switch_card = CardList(SwitchCard(month) for month in SwitchCard.month)

        self.full_deck = CardList(bright_cards + animal_cards + ribbon_cards + junk_cards + switch_card)
        self.max_cards = 48
        if not deck: 
            self.deck = CardList(bright_cards + animal_cards + ribbon_cards + junk_cards + switch_card)
        else: 
            self.deck = deck

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
        return (CardList(sorted(player_one_hand)), 
                CardList(sorted(player_two_hand)),
                CardList(sorted(open_cards)))
    
    def specified_deal(self, num_playerOne_cards, num_playerTwo_cards, num_center_cards): 
        while True:
            copy_deck = self.deck.copy()
            random.shuffle(copy_deck)
            num_cards = 0 
            player_one_hand = copy_deck[:num_cards + num_playerOne_cards]
            num_cards += num_playerOne_cards
            player_two_hand = copy_deck[num_cards:num_cards + num_playerTwo_cards]
            num_cards += num_playerTwo_cards
            center_cards = copy_deck[num_cards: num_cards + num_center_cards]
            num_cards += num_center_cards
            del copy_deck[:num_cards]
            if center_cards[0].month != center_cards[1].month:
                break
        
        self.deck = copy_deck
        return (CardList(sorted(player_one_hand)), 
                CardList(sorted(player_two_hand)), 
                CardList(sorted(center_cards)))

    def sort(self):
        self.deck.sort()

    def serialize(self) -> list: 
        self.deck.sort()
        return CardList.serialize(self.deck)

    @staticmethod
    def deserialize(serialized_deck): 
        deck = CardList.deserialize(serialized_cardList=serialized_deck)
        deck.sort()
        return Deck(deck)
    