from abc import ABC, abstractmethod
from .constants import Month, Type
from enum import Enum 


class Card(ABC): 
    def __init__(self, type: Type, month: Month):
        self.type = type 
        self.month = month 

    @abstractmethod
    def __str__(self):
        pass

    def __eq__(self, object) -> bool:
        return (
            isinstance(object, Card)
            and object.type == self.type 
            and object.month == self.month
        )
    
    def __lt__(self, obj):
        assert isinstance(obj, Card)
        return self._sort_value() < obj._sort_value()
    
    def _sort_value(self) -> int: 
        return(self.month.value * 1000 + self.type.value * 100)

class BrightCard(Card): 
    
    months = [Month.JAN, Month.MAR, Month.AUG, Month.NOV, Month.DEC]

    def __init__(self, month: Month):
        assert month in self.months
        super().__init__(type=Type.BRIGHT, month=month)

    def __str__(self):
        return f"Bright: {self.month.name}"
    
class AnimalCard(Card): 
    
    months = [Month.FEB, Month.APR, Month.JUN, Month.JUL, Month.AUG, Month.OCT, Month.DEC]

    def __init__(self, month: Month):
        assert month in self.months
        super().__init__(type=Type.ANIMAL, month=month)

    def __str__(self):
        return f"Animal: {self.month.name}"

class RibbonCard(Card):
    
    class Flag(Enum):
        RED = 0 
        PLANT = 1
        BLUE = 2
        NULL = 3 

    months = [Month.JAN, Month.FEB, Month.MAR, Month.APR, Month.MAY, Month.JUN, Month.JUL, Month.SEP, Month.OCT, Month.DEC]

    def __init__(self, month: Month):
        assert month in self.months
        super().__init__(type=Type.RIBBON, month=month)
        if month in [Month.JAN, Month.FEB, Month.MAR]:
            self.flag = self.Flag.RED
        elif month in [Month.APR, Month.MAY, Month.JUL]:
            self.flag = self.Flag.PLANT
        elif month in [Month.JUN, Month.SEP, Month.OCT]: 
            self.flag = self.Flag.BLUE
        else:
            self.flag = self.Flag.NULL 
    
    def __str__(self):
        return f"Ribbon: {self.month.name} {self.flag.name}"
        

class JunkCard(Card):

    def __init__(self, month: Month, index: int, double: int=0):
        assert double == 0 or double == 1
        if month == Month.NOV and double == 1:
            assert index==2
        elif month == Month.DEC: 
            assert double==1 and index==0
        else: 
            assert double == 0 
            assert index < 2 
        super().__init__(type=Type.JUNK, month=month)
        self.index = index 
        self.double = double # 1 if ssang-pi

    def __str__(self):
        return "{}Junk: {} {}".format(
            "Double " if self.double else "",
            self.month.name, 
            self.index
        )
    
    def __eq__(self, object) -> bool:
        return (
            super().__eq__(object)
            and object.index == self.index
        )
    
    def _sort_value(self) -> int:
        return super()._sort_value() + self.index

class SwitchCard(Card):

    month = [Month.SEP]

    def __init__(self, month: Month, type: Type = Type.ANIMAL):
        assert type == Type.ANIMAL or type == Type.JUNK
        assert month in self.month
        super().__init__(type=type, month=month)
        self.double = 1 
        self.index = 2 
    
    def switch_type(self, type: Type): 
        assert type == Type.ANIMAL or type == Type.JUNK
        self.type = type

    def __str__(self):
        if self.type == Type.JUNK:
            return "{}Junk: {} {}".format(
            "Double " if self.double else "",
            self.month.name, 
            self.index
        )
        else: 
            return f"Animal: {self.month.name}"
    
    def __eq__(self, object) -> bool:
        return (
            super().__eq__(object)
            and object.index == self.index
        )
