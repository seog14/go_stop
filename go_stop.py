from .models.board import Board
from .models.flags import Flags
from .models.card import Card
from .models.card_list import CardList
from.models.action import (Action,
                           ActionGo,
                           ActionSelectMatch,
                           ActionSelectMatches,
                           ActionThrow)
from .models.player import Player
from typing import List, Union, Tuple, cast, Optional

class GoStop():
    def __init__(self):
        self.board = Board()
        self.flags = Flags() 
        self.select_match: Union[
            None, 
            Tuple[
                Card, # Card Thrown/Flipped
                CardList # Matches 
            ], 
            Tuple[
                Card, # Card Thrown 
                CardList, # Matches 
                Card, # Card Flipped
                CardList # Matches
            ]
        ] = None
        self.terminal = False
        self.curr_go_score = 0 
        self.winner = Union[None, Player] 


    def actions(self) -> List[Action]: 

        board = self.board 
        flags = self.flags

        # Gives all possible actions given board state 

        if self.terminal: 
            return []
        
        if board.deck == []: 
            self.terminal = True 
            return []

        # If Go flag is set, player must choose to Go or not 
        if flags.go: 
            return [ActionGo(option) for option in {True, False}]
        
        # If select match flag is set, return actions to choose which card to select 
        if flags.select_match: 
            assert self.select_match is not None
            # One match
            if len(self.select_match) == 2: 
                og_card = self.select_match[0]
                matches = self.select_match[1]
                return [ActionSelectMatch(og_card, match) for match in matches]
            # Two match lists
            else: 
                og_cards = Tuple(self.select_match[0], self.select_match[2])
                first_matches = self.select_match[1]
                second_matches = self.select_match[3]
                return [ActionSelectMatch(og_cards, Tuple(match_one, match_two)) for match_one in first_matches
                        for match_two in second_matches]
                
        # Otherwise, can throw card from hand 
        return [ActionThrow(card) for card in board.curr_player.hand]
    
    def play(self, action: Action): 
        
        board = self.board 
        flags = self.flags 
        
        if action.kind == "go":
            action = cast(ActionGo, action)

            flags.go = False 

            if action.option: 
                self._go()

            self._stop() 
            return 
        
        if action.kind == "throw": 
            action = cast(ActionThrow, action)
            self._throw_and_flip(action.card)
            return
        
        if action.kind == "select_match":
            action = cast(ActionSelectMatch, action)
            self._select_match(action.og_card, action.match)
            return 
        
        if action.kind == "select_matches": 
            action = cast(ActionSelectMatches, action)
            self._select_matches(action.og_cards, action.matches)
            return 
        
    def _throw_and_flip(self, thrown_card: Card): 
        board = self.board 
        flags = self.flags 
        center_cards = board.center_cards

        num_steal_junk = 0 

        # Remove card from player hand
        board.curr_player.hand.remove(thrown_card)
        # Add card into center 
        self._append_to_center_field(CardList(thrown_card))
        matched_cards = center_cards[thrown_card.month]

        if len(matched_cards) == 4: 
            num_steal_junk += 1 
            center_cards[thrown_card.month] = CardList() # Clear center cards of that month 
            board.curr_player.captured.extend(matched_cards + CardList[thrown_card])

            num_steal_junk += self._flip()
        else: 
            # Will deal with every other situation in flip 
            num_steal_junk += self._flip(thrown_card) 

        # Check to see if center cards were cleared 
        if(
            all(field == [] for field in center_cards.values())
            and board.curr_player.hand
        ):
            num_steal_junk += 1 

        # Take Junk 
        opponent = board.get_opponent() 
        board.curr_player.take_junk(opponent)
        
    
        # See if current player has racked enough points to Go 
        # Only do this if current player is not waiting to select a match 
        if not flags.select_match: 
            if board.curr_player.num_go == 0: 
                board.curr_player.update_score() 
                score = board.curr_player.score 
                if score >= 7: 
                    # Check to see if opponent has already go'd 
                    if opponent.num_go > 0: 
                        self.terminal = True 
                        self.winner = board.curr_player
                        return 
                    flags.go = True 
            else: 
                old_score = board.curr_player.score 
                board.curr_player.update_score() 
                new_score = board.curr_player.score 
                if new_score > old_score: 
                    if not board.curr_player.hand: 
                        self.terminal = True 
                        self.winner = board.curr_player
                        return 
                    flags.go = True 
            
            # Switch turns if no go flag 
            if not flags.go: 
                board.switch_turn()
        
    def _flip(self, thrown_card: Optional[Card]): 
        board = self.board 
        flags = self.flags 
        center_cards = board.center_cards

        num_steal_junk = 0 

        flipped_card = board.deck.flip() 
        flip_matched_cards = board.center_cards[flipped_card.month]

        if thrown_card: 
            if flipped_card.month == thrown_card.month: 
                # Captured Entire Suit 
                if len(flip_matched_cards) == 3: 
                    num_steal_junk += 1 
                    center_cards[flipped_card.month] = CardList() 
                    board.curr_player.captured.extend(flip_matched_cards + CardList(flipped_card))
                elif len(flip_matched_cards) == 2: 
                    # ssa 
                    board.curr_player.num_ssa += 1 
                    self._append_to_center_field(CardList(flipped_card))
                elif len(flip_matched_cards) == 1: 
                    # ghost 
                    num_steal_junk += 1 
                    center_cards[thrown_card.month].remove(thrown_card)
                    board.curr_player.captured.extend(CardList(thrown_card, flipped_card))
                # return here as everything is done
                return num_steal_junk
            else: 
                # Deal with Thrown Matchings 
                thrown_matched_cards = board.center_cards[thrown_card.month] # this includes thrown card 
                if len(thrown_matched_cards) == 3: 
                    thrown_match_select = True 
                elif len(thrown_matched_cards) == 2: 
                    center_cards[thrown_card.month] = CardList() # Clear that suit 
                    board.curr_player.captured.extend(thrown_matched_cards)

        # Deal with Flipped Matchings 
        # Captured Entire Suit of Different Suit from Thrown 
        if len(flip_matched_cards) == 3: 
            num_steal_junk += 1 
            center_cards[flipped_card.month] = CardList() 
            board.curr_player.extend(flip_matched_cards + CardList(flipped_card))
        elif len(flip_matched_cards) == 2: 
            flip_match_select = True 
        elif len(flip_matched_cards) == 1: 
            center_cards[flipped_card.month] = CardList() # Clear that suit 
            board.curr_player.captured.extend(flip_matched_cards + CardList(flipped_card))
        else: 
            self._append_to_center_field(CardList(flipped_card))

        # Handle Match Selects 
        if thrown_match_select and flip_match_select: 
            flags.select_match = True 
            self.select_match = (flipped_card, flip_matched_cards, thrown_card, thrown_matched_cards)
        elif thrown_match_select: 
            flags.select_match = True 
            self.select_match = (thrown_card, thrown_matched_cards)
            # Remove thrown card from board 
            board.center_cards[thrown_card.month].remove(thrown_card)
        elif flip_match_select: 
            flags.select_match = True 
            self.select_match = (flipped_card, flip_matched_cards)

        return num_steal_junk
    
    def _select_match(self, og_card: Card, match: Card): 
        board = self.board 
        flags = self.flags 
        center_cards = board.center_cards 

        # Remove match and og_card from center
        center_cards[og_card.month].remove(og_card)
        center_cards[match.month].remove(match)

        # Add to captured 
        board.curr_player.capture.extend(CardList(og_card, match))

        opponent = board.get_opponent()
        # Check For Go 
        if board.curr_player.num_go == 0: 
            board.curr_player.update_score() 
            score = board.curr_player.score 
            if score >= 7: 
                if opponent.num_go > 0: 
                    self.terminal = True 
                    self.winner = board.curr_player
                    return 
                flags.go = True 
        else: 
            old_score = board.curr_player.score 
            board.curr_player.update_score() 
            new_score = board.curr_player.score 
            # If this is the last turn, no cards in hand determines winner
            if new_score > old_score: 
                if not board.curr_player.hand: 
                    self.terminal = True 
                    self.winner = board.curr_player
                    return 
                flags.go = True 
        
        # Switch turns if cannot go 
        if not flags.go: 
            board.switch_turn()

        # Set select_match flag to false 
        flags.select_match = False 

    def _select_matches(self, og_cards: Tuple[Card], matches: Tuple[Card]): 
        board = self.board 
        flags = self.flags 
        center_cards = board.center_cards 

        # Remove match and og_card from center
        for card in og_cards: 
            center_cards[card.month].remove(card)
        
        for card in matches: 
            center_cards[card.month].remove(card)

        # Add to captured 
        board.curr_player.capture.extend(CardList(og_cards[0], og_cards[1], matches[0], matches[1]))

        # Check for Go 
        opponent = board.get_opponent()

        if board.curr_player.num_go == 0: 
            board.curr_player.update_score() 
            score = board.curr_player.score 
            if score >= 7: 
                if opponent.num_go > 0: 
                    self.terminal = True 
                    self.winner = board.curr_player
                    return 
                flags.go = True 
        else: 
            old_score = board.curr_player.score 
            board.curr_player.update_score() 
            new_score = board.curr_player.score 
            if new_score > old_score: 
                if not board.curr_player.hand: 
                    self.terminal = True 
                    self.winner = board.curr_player
                    return 
                flags.go = True 

         # Switch turns if cannot go 
        if not flags.go: 
            board.switch_turn()

        # Set select_match flag to false 
        flags.select_match = False 


    def _append_to_center_field(self, cards: CardList): 
        for card in cards: 
            if self.board.center_cards[card.month]:
                self.board.center_cards[card.month].append(card)
            else: 
                self.board.center_cards[card.month] = CardList(card)

    def _go(self): 
        board = self.board
        curr_player = board.curr_player

        curr_player.num_go += 1 
        curr_player.update_score()
        self.curr_go_score = curr_player.score

        board.switch_turn() 
        return 
    
    def _stop(self): 
        board = self.board

        self.terminal = True 
        self.winner = board.curr_player

        self.winner.update_score() 

        return 
    
    def calculate_winnings(self): 
        if not self.winner: 
            return (0, 0)
        if self.winner == self.board.p1: 
            p1 = self.board.p1 
            p2 = self.board.p2
            p1.update_score()
            winnings = p1.score
            # Calculate Penalties 

            # Go - Penalties
            if p1.num_go < 3: 
                winnings += p1.num_go
            else: 
                times_doubled = p1.num_go - 2 
                winnings = winnings * pow(2, times_doubled)
            
            # Pi-bak 
            if p1.junk_points > 0: 
                if p2.num_junk < 6: 
                    winnings *= 2 

            # Guang-bak
            if p1.bright_points > 0: 
                if p2.num_bright == 0: 
                    winnings *= 2 
            
            return (winnings, -winnings)
        else: 
            p1 = self.board.p1 
            p2 = self.board.p2
            p2.update_score()
            winnings = p2.score
            # Calculate Penalties 

            # Go - Penalties
            if p2.num_go < 3: 
                winnings += p2.num_go
            else: 
                times_doubled = p2.num_go - 2 
                winnings = winnings * pow(2, times_doubled)
            
            # Pi-bak 
            if p2.junk_points > 0: 
                if p1.num_junk < 6: 
                    winnings *= 2 

            # Guang-bak
            if p2.bright_points > 0: 
                if p1.num_bright == 0: 
                    winnings *= 2 
            
            return (-winnings, winnings)
