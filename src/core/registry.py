"""Handler registry for automatic handler discovery and selection."""

from pathlib import Path
from typing import Type
import logging

from .base_handler import BaseHandler
from .utils import parse_properties

logger = logging.getLogger(__name__)


class HandlerRegistry:
    """
    Registry for item type handlers.
    
    Handlers register themselves and the registry selects the appropriate
    handler for each folder based on the can_handle() method.
    """
    
    _handlers: list[Type[BaseHandler]] = []
    
    @classmethod
    def register(cls, handler_class: Type[BaseHandler]) -> Type[BaseHandler]:
        """
        Register a handler class.
        
        Can be used as a decorator:
            @HandlerRegistry.register
            class BowHandler(BaseHandler):
                ...
        
        Args:
            handler_class: The handler class to register
            
        Returns:
            The handler class (for decorator usage)
        """
        if handler_class not in cls._handlers:
            cls._handlers.append(handler_class)
            # Sort by priority (highest first)
            cls._handlers.sort(key=lambda h: h.priority, reverse=True)
            logger.debug(f"Registered handler: {handler_class.name}")
        return handler_class
    
    @classmethod
    def get_handler(
        cls,
        folder_path: Path,
        output_base: Path,
        input_base: Path
    ) -> BaseHandler | None:
        """
        Get the appropriate handler for a folder.
        
        Args:
            folder_path: Path to the item folder
            output_base: Base path for output
            input_base: Base path of input pack
            
        Returns:
            An instantiated handler, or None if no handler matches
        """
        # Load properties files for detection
        properties_list = []
        for prop_file in folder_path.glob("*.properties"):
            try:
                properties_list.append(parse_properties(prop_file))
            except Exception as e:
                logger.warning(f"Failed to parse {prop_file}: {e}")
        
        # Try each handler in priority order
        for handler_class in cls._handlers:
            try:
                if handler_class.can_handle(folder_path, properties_list):
                    return handler_class(folder_path, output_base, input_base)
            except Exception as e:
                logger.warning(f"Error checking handler {handler_class.name}: {e}")
        
        return None
    
    @classmethod
    def get_all_handlers(cls) -> list[Type[BaseHandler]]:
        """Get all registered handler classes."""
        return cls._handlers.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers (mainly for testing)."""
        cls._handlers.clear()
