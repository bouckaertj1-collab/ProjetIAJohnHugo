from games.PixelKart.game_model.types import Pixel
from games.PixelKart.game_model.kart import Kart
from math import floor

def compute_effective_speed(pixel,kart: Kart) -> int:
        """Return the speed used for this turn after terrain effects."""
        if pixel == Pixel.GRASS:
            return floor(kart.pixels_per_turn / 2)
        return kart.pixels_per_turn

