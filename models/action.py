from .card import Card 

from abc import ABC
from typing import Literal, Tuple

Kind = Literal[
    "throw",
    "go",
    "select match", 
    "select matches"
]

class Action(ABC):
    def __init__(self, kind, arg):
        self.kind = kind
        self.arg = arg 

    def __eq__(self, obj):
        return isinstance(obj, Action) and obj.kind == self.kind and obj.arg == self.arg 
    
class ActionThrow(Action):

    def __init__(self, card: Card): 
        super().__init__("throw", card)
        self.card = card

# One Match List
class ActionSelectMatch(Action): 

    def __init__(self, og_card: Card , match: Card): 
        super().__init__("select match", (og_card, match))
        self.og_card = og_card
        self.match = match 

# Two Match Lists 
class ActionSelectMatches(Action): 
    def __init__(self, og_cards: Tuple[Card], matches: Tuple[Card]): 
        super().__init__("select matches", (og_cards, matches))
        self.og_cards = og_cards
        self.matches = matches

class ActionGo(Action): 

    def __init__(self, option: bool): 
        super().__init__("go", option)
        self.option = option 