"""Item type handlers for the resource pack renamer."""

# Import all handlers to trigger registration
from .generic import GenericHandler
from .bow import BowHandler
from .crossbow import CrossbowHandler
from .armor import ArmorHandler
from .set_armor import SetArmorHandler
from .potion import PotionHandler

__all__ = [
    "GenericHandler",
    "BowHandler",
    "CrossbowHandler",
    "ArmorHandler",
    "SetArmorHandler",
    "PotionHandler",
]


