"""Core modules for the resource pack renamer."""

from .utils import reduce_name, parse_properties
from .operations import FileOperation, OperationType
from .base_handler import BaseHandler
from .registry import HandlerRegistry

__all__ = [
    "reduce_name",
    "parse_properties", 
    "FileOperation",
    "OperationType",
    "BaseHandler",
    "HandlerRegistry",
]
