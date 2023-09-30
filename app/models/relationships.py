from typing import List, Optional


from .garden import GardenRead
from .bed import BedRead
from .planting import PlantingRead
from .plant import PlantRead


class GardenReadWithBeds(GardenRead):
    """Garden model used to get an instance of a garden\
        with associated garden beds."""
    beds: List[BedRead] = []


class BedReadWithGarden(BedRead):
    """Garden bed model used to get an instance of a garden bed\
        with associated garden."""
    garden: Optional[GardenRead] = None


class BedReadWithPlantings(BedRead):
    """Garden bed model used to get an instance of a garden bed\
        with associated plantings."""
    plantings: List[PlantingRead] = []


class PlantingReadWithBed(PlantingRead):
    """Planting model used to get an instance of a planting\
        with associated garden bed."""
    bed: Optional[BedRead] = None


class PlantingReadWithPlants(PlantingRead):
    """Planting model used to get an instance of a planting\
        with associated plants."""
    plants: List[PlantRead] = []


class PlantReadWithPlanting(PlantRead):
    """Plant model used to get an instance of a plant\
        with associated planting."""
    planting: Optional[PlantingRead] = None
