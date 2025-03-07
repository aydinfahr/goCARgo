from enum import Enum

class NumberOfSeats(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4

class RideStatus(str, Enum):
    past = "past"  
    upcoming = "upcoming"