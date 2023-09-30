from typing import List, Optional


from .garden import GardenRead
from .bed import BedRead


class GardenReadWithBeds(GardenRead):
    """Garden model used to get an instance of a garden\
        with associated garden beds."""
    beds: List[BedRead] = []


class BedReadWithGarden(BedRead):
    """Garden bed model used to get an instance of a garden bed\
        with associated garden."""
    garden: Optional[GardenRead] = None
