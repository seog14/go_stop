from models.board import Board
from models.flags import Flags
from models.card import (Card,
                         JunkCard, 
                         RibbonCard, 
                         AnimalCard, 
                         BrightCard, 
                         SwitchCard
                         )
from models.card_list import CardList
from models.deck import Deck
from models.constants import Month, Type
from models.player import Player
from models.action import Action

from go_stop import GoStop

class SimplifiedGoStop(GoStop): 
    def __init__(self):
        super().__init__()
        p1_captured = CardList([JunkCard(month=Month(3), index=0), 
                                JunkCard(month=Month(3), index=1),
                                BrightCard(month=Month(8)), 
                                BrightCard(month=Month(3)), 
                                BrightCard(month=Month(11)), 
                                
                                RibbonCard(month=Month(3)), 
                                JunkCard(month=Month(5), index=0), 
                                JunkCard(month=Month(4), index=0),
                                JunkCard(month=Month(4), index=1), 
                                SwitchCard(month=Month(9), type=Type.JUNK), 
                                JunkCard(month=Month(9), index=0), 
                                JunkCard(month=Month(10), index=0), 
                                JunkCard(month=Month(10), index=1), 
                                JunkCard(month=Month(11), index=2, double=1), 
                                JunkCard(month=Month(8), index=0), 
                                
                                JunkCard(month=Month(5), index=1), 
                    
                                RibbonCard(month=Month(12)),
                                AnimalCard(month=Month(12)), 
        ])

        p2_captured = CardList([BrightCard(month=Month(12)), 
                                BrightCard(month=Month(1)), 
                                AnimalCard(month=Month(4)), 
                                AnimalCard(month=Month(5)), 
                                AnimalCard(month=Month(6)), 
                                AnimalCard(month=Month(8)), 
                                AnimalCard(month=Month(7)), 
                                
                                RibbonCard(month=Month(6)), 
                                RibbonCard(month=Month(1)), 
                                RibbonCard(month=Month(2)), 
                                RibbonCard(month=Month(4)), 
                                RibbonCard(month=Month(5)), 
                                JunkCard(month=Month(2), index=1), 
                                JunkCard(month=Month(8), index=1), 
                                JunkCard(month=Month(7), index=0),
                                RibbonCard(month=Month(9)),
                                JunkCard(month=Month(9), index=1),

                                JunkCard(month=Month(12), index=0, double=1)

        ])

        deck = Deck() 
        deck.deck = CardList([
                              JunkCard(month=Month(6), index=1),
                              JunkCard(month=Month(11), index=0), 
                              JunkCard(month=Month(1), index=0), 
                              JunkCard(month=Month(1), index=1), 
                              JunkCard(month=Month(11), index=1),  
                              JunkCard(month=Month(6), index=0), 
                              RibbonCard(month=Month(7)), 
                              AnimalCard(month=Month(10)), 
                              
                              JunkCard(month=Month(7), index=1), 
                              RibbonCard(month=Month(10)),

                              AnimalCard(month=Month(2)), 
                              JunkCard(month=Month(2), index=0), 

        ])
        
        p1_hand, p2_hand, center_cards = deck.specified_deal(2, 3, 2)

        p1 = Player(hand=p1_hand, number=1)
        p1.captured = p1_captured
        p1.num_go = 1
        p1.update_score()

        p2 = Player(hand=p2_hand, number=2)
        p2.captured = p2_captured
        p2.update_score()

        self.board = Board()
        self.board.deck = deck
        self.board.p1 = p1
        self.board.p2 = p2 
        self.board.curr_player = p1 
        self.board.clear_center_cards()

        self.flags = Flags() 
        self.flags.go=True

        self._append_to_center_field(center_cards)
    