from .card import Card, BrightCard, AnimalCard, RibbonCard, SwitchCard
from .card_list import CardList
from .constants import Type, Month

from typing import List

class Player(): 
    def __init__(self, hand: CardList, number: int):
        assert number == 1 or number == 2 
        self.number = number
        self.hand = hand
        self.captured = CardList()
        self.score = 0 
        # TODO: Implement Shake
        self.shaked = False 
        self.num_go = 0 
        self.num_ssa = 0 
    
    def __str__(self):
        return f"Player {self.number}\n" \
                f"Hand: {self.hand}\n" \
                f"Hand Length: {len(self.hand)}\n" \
                f"Captured: {self.captured}\n" \
                f"Score: {self.score}\n" \
                f"Num_go: {self.num_go}"
    
    def serialize(self): 
        self.sort()
        return {
            "number": self.number, 
            "hand": self.hand.serialize(), 
            "captured": self.captured.serialize(), 
            "score": self.score, 
            "num_go": self.num_go
        }
    
    @staticmethod
    def deserialize(serialized_player: dict): 
        number = int(serialized_player["number"])
        hand = CardList.deserialize(serialized_player["hand"])
        player = Player(hand, number)
        
        player.captured = CardList.deserialize(serialized_player["captured"])
        player.score = int(serialized_player["score"])
        player.num_go = int(serialized_player["num_go"])
        player.sort()

        return player

    def sort(self): 
        self.hand.sort() 
        self.captured.sort()

    def switch_card(self, card: Card, type: Type): 
        # Switch card to junk or animal
        assert isinstance(card, SwitchCard)
        card.switch_type(type)                

    # TODO: implement idea that when taking switch card, opponent can choose whether to keep as animal or give
    def take_junk(self, opponent):
        assert isinstance(opponent, Player)
        opponent_junk_cards = [card for card in opponent.captured if card.type == Type.JUNK]
        if opponent_junk_cards:
            for card in opponent_junk_cards: 
                if not card.double: # Give single point junk card 
                    self.captured.append(card)
                    opponent.captured.remove(card)
                    return 
            # Only double cards in opponent's captured
            card = opponent_junk_cards.pop() 
            self.captured.append(card)
        
    # Scoring Methods for Player 
    def update_score(self): 
        switch_card = [card for card in self.captured if isinstance(card, SwitchCard)]
        if switch_card: 
            sw_card = switch_card[0]
            # Maximize for either type 
            self.switch_card(card=sw_card, type=Type.ANIMAL)
            animal_score = self.calculate_score()
            self.switch_card(card=sw_card, type=Type.JUNK)
            junk_score = self.calculate_score() 

            if junk_score < animal_score: 
                self.switch_card(card=sw_card, type=Type.ANIMAL)
                self.score = animal_score
            else: 
                self.score = junk_score
        else: 
            self.score = self.calculate_score()

    def calculate_score(self): 
        return self.bright_points() + self.animal_points() + self.ribbon_points() + self.junk_points()
    
    def bright_points(self): 
        bright_cards = [card for card in self.captured if card.type == Type.BRIGHT]
        if len(bright_cards) < 3: 
            return 0 
        if len(bright_cards) == 3 and BrightCard(Month.DEC) in bright_cards: 
            return 2 
        if len(bright_cards) == 5: 
            return 15 
        
        return len(bright_cards)
    
    def animal_points(self): 
        points = 0 
        animal_cards = [card for card in self.captured if card.type == Type.ANIMAL]

        if len(animal_cards) >= 5: 
            points += len(animal_cards) - 4 

        # Check for Godori 
        godori_cards = [AnimalCard(Month.FEB), AnimalCard(Month.APR), AnimalCard(Month.AUG)]
        godori = all(card in animal_cards for card in godori_cards)
        if godori:
            points += 5 
        
        return points 
    
    def ribbon_points(self): 
        points = 0 
        ribbon_cards = [card for card in self.captured if card.type == Type.RIBBON]

        if len(ribbon_cards) >= 5: 
            points += len(ribbon_cards) - 4 
        
        # Check for Cheong Dan (all 3 blue)
        blue_ribbon_cards = [card for card in ribbon_cards if card.flag == RibbonCard.Flag.BLUE]
        if len(blue_ribbon_cards) == 3: 
            points += 3 
        
        # Check for Hong Dan (all 3 red w/ poetry)
        red_ribbon_cards = [card for card in ribbon_cards if card.flag == RibbonCard.Flag.RED]
        if len(red_ribbon_cards) == 3: 
            points += 3 
        
        # Check for Cho Dan (Plant flags)
        plant_ribbon_cards = [card for card in ribbon_cards if card.flag == RibbonCard.Flag.PLANT]
        if len(plant_ribbon_cards) == 3: 
            points += 3 
        
        return points 
    
    def junk_points(self): 
        total = 0 
        junk_cards = [card for card in self.captured if card.type == Type.JUNK]
        points = 0
        for card in junk_cards: 
            total += card.double + 1 
        
        if (total >= 10):
            points = total - 9
        
        return points 

    def num_junk(self):
        total = 0 
        junk_cards = [card for card in self.captured if card.type == Type.JUNK]
        for card in junk_cards: 
            total += card.double + 1 
        return total
    
    def num_bright(self): 
        bright_cards = [card for card in self.captured if card.type == Type.BRIGHT]
        return len(bright_cards)
        
        
