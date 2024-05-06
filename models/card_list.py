from typing import Callable
from .card import Card
from .constants import Month

class CardList(list): 

    def __str__(self):
        return "[{}]".format(", ".join([card.__str__() for card in self]))
    
    def of_month(self, month: Month): 
        # Return cards of that month 
        return self.filter(lambda card: card.month == month)
    
    def filter(self, predicate: Callable[[Card], bool]):
        """Apply the filter `predicate`."""
        return CardList(card for card in self if predicate(card))
    
    def copy(self):
        return CardList(self)
        
    def serialize(self): 
        self.sort()
        return tuple([card.serialize() for card in self])
    
    @staticmethod
    def deserialize(serialized_cardList): 
        cardList = CardList(Card.deserialize(card) for card in serialized_cardList)
        cardList.sort()
        return cardList