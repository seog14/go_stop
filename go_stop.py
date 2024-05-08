from models.board import Board
from models.flags import Flags
from models.card import Card
from models.card_list import CardList
from models.action import (Action,
                           ActionGo,
                           ActionSelectMatch,
                           ActionSelectMatches,
                           ActionThrow, 
                           ActionFlip)
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
        self.winner: Union[None, int] = None
        # (player_num, action)
        self.history : List[Tuple[int, Action]] = []
    
    def is_terminal(self): 
        if self.actions() == []:
            return True 
        return False

    def actions(self) -> List[Action]: 

        # Gives all possible actions given board state 

        if self.terminal: 
            return []
        if self.board.deck == []: 
            self.terminal = True 
            return []

        # If Go flag is set, player must choose to Go or not 
        if self.flags.go: 
            return [ActionGo(option) for option in {True, False}]
        
        # If select match flag is set, return actions to choose which card to select 
        if self.flags.select_match: 
            assert self.select_match is not None
            # One match
            if len(self.select_match) == 2: 
                og_card = self.select_match[0]
                matches = self.select_match[1]
                return [ActionSelectMatch(og_card, match) for match in matches]
            # Two match lists
            else: 
                og_cards = (self.select_match[0], self.select_match[2])
                first_matches = self.select_match[1]
                second_matches = self.select_match[3]
                return [ActionSelectMatches(og_cards, (match_one, match_two)) for match_one in first_matches
                        for match_two in second_matches]
                
        # Otherwise, can throw card from hand 
        return [ActionThrow(card) for card in self.board.curr_player.hand]
    
    def play(self, action: Action): 
        self.history.append((self.get_current_player_number(), action))
        if action.kind == "go":
            action = cast(ActionGo, action)

            self.flags.go = False 

            if action.option: 
                self._go()
                return

            self._stop() 
            return 
        
        if action.kind == "throw": 
            action = cast(ActionThrow, action)
            self._throw_and_flip(action.card)
            return
        
        if action.kind == "select match":
            action = cast(ActionSelectMatch, action)
            self._select_match(action.og_card, action.match)
            return 
        
        if action.kind == "select matches": 
            action = cast(ActionSelectMatches, action)
            self._select_matches(action.og_cards, action.matches)
            return 
                
    def _throw_and_flip(self, thrown_card: Card): 

        num_steal_junk = 0 

        # Remove card from player hand
        self.board.curr_player.hand.remove(thrown_card)
        # Add card into center 
        self._append_to_center_field(CardList([thrown_card]))
        matched_cards = self.board.center_cards[thrown_card.month]

        if len(matched_cards) == 4: 
            num_steal_junk += 1 
            self.board.center_cards[thrown_card.month] = CardList() # Clear center cards of that month 
            self.board.curr_player.captured.extend(matched_cards)

            num_steal_junk += self._flip()
        else: 
            # Will deal with every other situation in flip 
            num_steal_junk += self._flip(thrown_card) 

        # Check to see if center cards were cleared 
        if(
            all(field == [] for field in self.board.center_cards.values())
            and self.board.curr_player.hand != CardList()
        ):
            num_steal_junk += 1 

        # Take Junk 
        opponent = self.board.get_opponent() 
        if num_steal_junk: 
            for _ in range(num_steal_junk):
                self.board.curr_player.take_junk(opponent)
        
        # See if current player has racked enough points to Go 
        # Only do this if current player is not waiting to select a match 
        if not self.flags.select_match: 
            if self.board.curr_player.num_go == 0: 
                self.board.curr_player.update_score() 
                score = self.board.curr_player.score 
                if score >= 7: 
                    # Check to see if opponent has already go'd 
                    if opponent.num_go > 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    # Check if own hand is empty then won 
                    if len(self.board.curr_player.hand) == 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return
                    self.flags.go = True 
            else: 
                old_score = self.board.curr_player.score 
                self.board.curr_player.update_score() 
                new_score = self.board.curr_player.score 
                if new_score > old_score: 
                    if len(self.board.curr_player.hand) == 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    self.flags.go = True 
            
            # Switch turns if no go flag 
            if not self.flags.go: 
                self.board.switch_turn()
        
    def _flip(self, thrown_card: Optional[Card] = None): 

        num_steal_junk = 0 
        thrown_match_select = False
        flip_match_select = False

        flipped_card = self.board.deck.flip() 
        flip_matched_cards = self.board.center_cards[flipped_card.month]

        # Add to action history
        action_flip = ActionFlip(card=flipped_card)
        self.history.append((self.get_current_player_number(), action_flip))

        if thrown_card: 
            if flipped_card.month == thrown_card.month: 
                # Captured Entire Suit 
                if len(flip_matched_cards) == 3: 
                    num_steal_junk += 1 
                    self.board.center_cards[flipped_card.month] = CardList() 
                    self.board.curr_player.captured.extend(flip_matched_cards + CardList([flipped_card]))
                elif len(flip_matched_cards) == 2: 
                    # ssa 
                    self.board.curr_player.num_ssa += 1 
                    self._append_to_center_field(CardList([flipped_card]))
                elif len(flip_matched_cards) == 1: 
                    # ghost 
                    num_steal_junk += 1 
                    self.board.center_cards[thrown_card.month].remove(thrown_card)
                    self.board.curr_player.captured.extend(CardList([thrown_card, flipped_card]))
                # return here as everything is done
                return num_steal_junk
            else: 
                # Deal with Thrown Matchings 
                thrown_matched_cards = self.board.center_cards[thrown_card.month] # this includes thrown card 
                if len(thrown_matched_cards) == 3: 
                    # print(f"thrown matched cards: {thrown_matched_cards}")
                    thrown_match_select = True 
                elif len(thrown_matched_cards) == 2: 
                    self.board.center_cards[thrown_card.month] = CardList() # Clear that suit 
                    self.board.curr_player.captured.extend(thrown_matched_cards)

        # Deal with Flipped Matchings 
        # Captured Entire Suit of Different Suit from Thrown 
        if len(flip_matched_cards) == 3: 
            num_steal_junk += 1 
            self.board.center_cards[flipped_card.month] = CardList() 
            self.board.curr_player.captured.extend(flip_matched_cards + CardList([flipped_card]))
        elif len(flip_matched_cards) == 2: 
            flip_match_select = True 
        elif len(flip_matched_cards) == 1: 
            self.board.center_cards[flipped_card.month] = CardList() # Clear that suit 
            self.board.curr_player.captured.extend(flip_matched_cards + CardList([flipped_card]))
        else: 
            self._append_to_center_field(CardList([flipped_card]))

        # Handle Match Selects 
        if thrown_match_select and flip_match_select: 
            self.flags.select_match = True 
            self.select_match = (flipped_card, flip_matched_cards, thrown_card, thrown_matched_cards)
        elif thrown_match_select: 
            self.flags.select_match = True 
            self.select_match = (thrown_card, thrown_matched_cards)
            # Remove thrown card from board 
            self.board.center_cards[thrown_card.month].remove(thrown_card)

        elif flip_match_select: 
            self.flags.select_match = True 
            self.select_match = (flipped_card, flip_matched_cards)
            # Remove flipped card from board 
            self.board.center_cards[flipped_card.month].remove(flipped_card)

        return num_steal_junk
    
    def _select_match(self, og_card: Card, match: Card): 

        # Remove match from center
        # print(f"before sel match: {self.board.center_cards[match.month]}")
        self.board.center_cards[match.month].remove(match)
        # print(f"after after sel match: {self.board.center_cards[match.month]}")

        # Add to captured 
        self.board.curr_player.captured.extend(CardList([og_card, match]))

        opponent = self.board.get_opponent()
        # Check For Go 
        if len(self.board.curr_player.hand) != 0:
            if self.board.curr_player.num_go == 0: 
                self.board.curr_player.update_score() 
                score = self.board.curr_player.score 
                if score >= 7: 
                    if opponent.num_go > 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    self.flags.go = True 
            else: 
                old_score = self.board.curr_player.score 
                self.board.curr_player.update_score() 
                new_score = self.board.curr_player.score 
                # If this is the last turn, no cards in hand determines winner
                if new_score > old_score: 
                    if len(self.board.curr_player.hand) == 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    self.flags.go = True 
        
        # Switch turns if cannot go 
        if not self.flags.go: 
            self.board.switch_turn()

        # Set select_match flag to false 
        self.flags.select_match = False 

    def _select_matches(self, og_cards: Tuple[Card], matches: Tuple[Card]): 

        # Remove match from center
        for card in matches: 
            self.board.center_cards[card.month].remove(card)

        # Add to captured 
        self.board.curr_player.captured.extend(CardList([og_cards[0], og_cards[1], matches[0], matches[1]]))

        # Check for Go 
        opponent = self.board.get_opponent()
        if len(self.board.curr_player.hand) != 0:
            if self.board.curr_player.num_go == 0: 
                self.board.curr_player.update_score() 
                score = self.board.curr_player.score 
                if score >= 7: 
                    if opponent.num_go > 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    self.flags.go = True 
            else: 
                old_score = self.board.curr_player.score 
                self.board.curr_player.update_score() 
                new_score = self.board.curr_player.score 
                if new_score > old_score: 
                    if len(self.board.curr_player.hand) == 0: 
                        self.terminal = True 
                        self.winner = self.board.curr_player.number
                        return 
                    self.flags.go = True 

         # Switch turns if cannot go 
        if not self.flags.go: 
            self.board.switch_turn()

        # Set select_match flag to false 
        self.flags.select_match = False 


    def _append_to_center_field(self, cards: CardList): 
        for card in cards: 
            if self.board.center_cards[card.month] != CardList():
                self.board.center_cards[card.month].append(card)
            else: 
                self.board.center_cards[card.month] = CardList([card])

    def _go(self): 
        curr_player = self.board.curr_player

        curr_player.num_go += 1 
        curr_player.update_score()
        self.curr_go_score = curr_player.score

        self.board.switch_turn() 
        return 
    
    def _stop(self): 

        self.terminal = True 
        self.winner = self.board.curr_player.number
        self.board.curr_player.update_score()

        return 
    
    def calculate_winnings(self): 
        if not self.winner: 
            return (0, 0)
        if self.winner == 1: 
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
            if p1.junk_points() > 0: 
                if p2.num_junk() < 6: 
                    winnings *= 2 

            # Guang-bak
            if p1.bright_points() > 0: 
                if p2.num_bright() == 0: 
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
            if p2.junk_points() > 0: 
                if p1.num_junk() < 6: 
                    winnings *= 2 

            # Guang-bak
            if p2.bright_points() > 0: 
                if p1.num_bright() == 0: 
                    winnings *= 2 
            
            return (-winnings, winnings)
        
    def get_utility(self, player_num): 
        player_one_utility, player_two_utility = self.calculate_winnings() 
        if player_num == 1: 
            return player_one_utility
        else: 
            return player_two_utility

    def display(self): 
        print(self.board)
        for player_num, action in self.history:
            print(f"{(player_num, action.serialize())}\n" )

    def display_game(self, hero): 
        print(f"{self.board.display_hidden_board(hero)}\n")


    def serialize(self): 
        # preprocess history  
        serialized_history = tuple([(player_num, action.serialize()) for player_num, action in self.history])
        # preprocess select_match
        serialized_select_match = None
        if self.select_match: 
            if len(self.select_match) == 2: 

                card_thrown_or_flipped = self.select_match[0]
                serialized_card_thrown_or_flipped = card_thrown_or_flipped.serialize()

                matches = self.select_match[1]
                serialized_matches = matches.serialize()

                serialized_select_match = tuple((serialized_card_thrown_or_flipped, serialized_matches))

            if len(self.select_match) == 4: 

                card_thrown = self.select_match[0]
                serialized_card_thrown = card_thrown.serialize()

                thrown_matches = self.select_match[1]
                serialized_thrown_matches = thrown_matches.serialize()

                card_flipped = self.select_match[2]
                serialized_card_flipped = card_flipped.serialize()

                flipped_matches = self.select_match[3]
                serialized_flipped_matches = flipped_matches.serialize() 

                serialized_select_match = tuple((serialized_card_thrown, 
                                                 serialized_thrown_matches, 
                                                 serialized_card_flipped, 
                                                 serialized_flipped_matches))
        return tuple((
            self.board.serialize(),
            self.flags.serialize(), 
            serialized_select_match,
            self.terminal,
            self.curr_go_score, 
            self.winner, 
            serialized_history
        ))
    
    @staticmethod
    def deserialize(serialized_game: tuple): 
        game = GoStop()

        # Deserialize select_match
        serialized_select_match = serialized_game[2]
        
        select_match = None
        if serialized_select_match:
            if len(serialized_select_match) == 2: 
                deserialized_card_thrown_flipped = Card.deserialize(serialized_select_match[0])
                deserialized_matches = CardList.deserialize(serialized_select_match[1])
                select_match = tuple((deserialized_card_thrown_flipped, deserialized_matches))
            if len(serialized_select_match) == 4: 
                deserialized_card_thrown = Card.deserialize(serialized_select_match[0])
                deserialized_thrown_matches = CardList.deserialize(serialized_select_match[1])
                deserialized_card_flipped = Card.deserialize(serialized_select_match[2])
                deserialized_flipped_matches = CardList.deserialize(serialized_select_match[3])
                select_match = tuple((deserialized_card_thrown, deserialized_thrown_matches,
                                    deserialized_card_flipped, deserialized_flipped_matches))


        # Deserialize history 
        serialized_history = serialized_game[6]
        history = [(int(player_num), Action.deserialize(action)) for player_num, action in serialized_history]

        game.board = Board.deserialize(serialized_game[0])
        game.flags = Flags.deserialize(serialized_game[1])
        game.select_match = select_match
        game.terminal = serialized_game[3]
        game.curr_go_score = serialized_game[4]
        game.winner = serialized_game[5]
        game.history = history

        return game
    
    def get_current_player_number(self): 
        return self.board.curr_player.number
    
    def get_infoSet(self) -> tuple: 
        serialized_history = tuple([(player_num, action.serialize()) for player_num, action in self.history])

        serialized_select_match = None
        if self.select_match: 
            if len(self.select_match) == 2: 

                card_thrown_or_flipped = self.select_match[0]
                serialized_card_thrown_or_flipped = card_thrown_or_flipped.serialize()

                matches = self.select_match[1]
                serialized_matches = matches.serialize()

                serialized_select_match = tuple((serialized_card_thrown_or_flipped, serialized_matches))

            if len(self.select_match) == 4: 

                card_thrown = self.select_match[0]
                serialized_card_thrown = card_thrown.serialize()

                thrown_matches = self.select_match[1]
                serialized_thrown_matches = thrown_matches.serialize()

                card_flipped = self.select_match[2]
                serialized_card_flipped = card_flipped.serialize()

                flipped_matches = self.select_match[3]
                serialized_flipped_matches = flipped_matches.serialize() 

                serialized_select_match = tuple((serialized_card_thrown, 
                                                 serialized_thrown_matches, 
                                                 serialized_card_flipped, 
                                                 serialized_flipped_matches))
                
        player_num = self.get_current_player_number() 
        return tuple((
            self.board.get_hidden_information(player_num=player_num),
            self.flags.serialize(),
            serialized_select_match,
            self.terminal,
            self.curr_go_score, 
            self.winner, 
            serialized_history
        ))
        