from .card import Card 
from .card_list import CardList

from abc import ABC, abstractmethod
from typing import Literal, Tuple

Kind = Literal[
    "throw",
    "go",
    "select match", 
    "select matches",
    "flip"
]

class Action(ABC):
    def __init__(self, kind, arg):
        self.kind = kind
        self.arg = arg 

    def __eq__(self, obj):
        return isinstance(obj, Action) and obj.kind == self.kind and obj.arg == self.arg 

    def __str__(self): 
        return f"Action: {self.kind} with args: {self.arg}"
    
    @abstractmethod
    def serialize(self): 
        pass

    @staticmethod
    def deserialize(serialized_action: dict): 
        kind = serialized_action[0]
        if kind == "throw": 
            card = serialized_action[1]
            return ActionThrow(card=Card.deserialize(card))
        
        if kind == "select match": 
            og_card = serialized_action[1]
            match = serialized_action[2]
            return ActionSelectMatch(og_card=Card.deserialize(og_card),
                                     match=Card.deserialize(match))
        
        if kind == "select matches": 
            og_cards = CardList.deserialize(serialized_action[1])
            matches = CardList.deserialize(serialized_action[2])
            # Change Cardlist to tuple 
            return ActionSelectMatches(og_cards=tuple(og_cards),
                                       matches=tuple(matches)) 
        
        if kind == "go": 
            option = bool(serialized_action[1])
            return ActionGo(option=option)

        if kind == "flip": 
            card = serialized_action[1]
            return ActionFlip(card=Card.deserialize(card))
        
class ActionThrow(Action):

    def __init__(self, card: Card): 
        super().__init__("throw", card)
        self.card = card

    def serialize(self): 
        return tuple([
            self.kind,
            self.card.serialize()
        ])

# One Match List
class ActionSelectMatch(Action): 

    def __init__(self, og_card: Card , match: Card): 
        super().__init__("select match", (og_card, match))
        self.og_card = og_card
        self.match = match 

    def serialize(self): 
        return tuple([
            self.kind, 
            self.og_card.serialize(),
            self.match.serialize()
        ])

# Two Match Lists 
class ActionSelectMatches(Action): 
    def __init__(self, og_cards: Tuple[Card], matches: Tuple[Card]): 
        super().__init__("select matches", (og_cards, matches))
        self.og_cards = og_cards
        self.matches = matches
    
    def serialize(self): 
        og_cards = CardList(self.og_cards)
        og_cards.sort()
        matches = CardList(self.matches)
        matches.sort()
        return tuple([
            self.kind, 
            tuple(og_cards.serialize()),
            tuple(matches.serialize())
        ])

class ActionGo(Action): 

    def __init__(self, option: bool): 
        super().__init__("go", option)
        self.option = option 
    
    def serialize(self): 
        return tuple([
            self.kind, 
            self.option
        ])
    
class ActionFlip(Action):
    def __init__(self, card: Card): 
        super().__init__("flip", card)
        self.card = card 
    
    def serialize(self): 
        return tuple([
            self.kind, 
            self.card.serialize()
        ])