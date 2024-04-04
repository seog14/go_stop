from enum import Enum 

class Month(Enum): 
    JAN = 1 
    FEB = 2 
    MAR = 3 
    APR = 4 
    MAY = 5 
    JUN = 6 
    JUL = 7 
    AUG = 8 
    SEP = 9 
    OCT = 10 
    NOV = 11 
    DEC = 12 

class Type(Enum): 
    JUNK = 0 
    RIBBON = 1
    ANIMAL = 2
    BRIGHT = 3