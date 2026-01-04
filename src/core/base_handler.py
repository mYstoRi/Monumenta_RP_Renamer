"""Abstract base class for item type handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar
import logging

from .operations import FileOperation, AnalysisResult, OperationType
from .utils import parse_properties, get_base_item, get_item_name, reduce_name, is_replica

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """
    Abstract base class for all item type handlers.
    
    Each handler is responsible for:
    1. Detecting if it can handle a given folder (can_handle)
    2. Analyzing the folder contents and determining what needs to change (analyze)
    3. Generating file operations for preview mode (get_operations via analyze)
    
    Subclasses must implement:
    - name: Class variable with handler name
    - can_handle: Static method to detect if handler applies
    - _analyze_folder: Method to analyze and generate operations
    """
    
    # Class variable - each handler must define its name
    name: ClassVar[str] = "base"
    
    # Priority for handler selection (higher = checked first)
    # This allows more specific handlers to take precedence
    priority: ClassVar[int] = 0
    
    def __init__(self, folder_path: Path, output_base: Path, input_base: Path):
        """
        Initialize the handler.
        
        Args:
            folder_path: Path to the item folder to process
            output_base: Base path for output (e.g., ./output/monumenta-resourcepack)
            input_base: Base path of input pack (e.g., ./input/monumenta-resourcepack)
        """
        self.folder_path = folder_path
        self.output_base = output_base
        self.input_base = input_base
        
        # Calculate the relative path from input base
        self.relative_path = folder_path.relative_to(input_base)
        self.output_folder = output_base / self.relative_path
        
        # These will be populated during analysis
        self.properties_files: list[Path] = []
        self.properties: dict[Path, dict[str, str]] = {}
        self.item_name: str = ""
        self.reduced_name: str = ""
        self.is_replica: bool = False
    
    @staticmethod
    @abstractmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """
        Determine if this handler can process the given folder.
        
        Args:
            folder_path: Path to the folder to check
            properties_list: List of parsed properties from .properties files in folder
            
        Returns:
            True if this handler should process this folder
        """
        pass
    
    def analyze(self) -> AnalysisResult:
        """
        Analyze the folder and determine what operations are needed.
        
        This is the main entry point. It:
        1. Loads all properties files
        2. Extracts item information
        3. Calls the subclass _analyze_folder to generate operations
        
        Returns:
            AnalysisResult containing operations and any issues
        """
        result = AnalysisResult(
            folder_path=self.folder_path,
            handler_name=self.name,
        )
        
        try:
            # Find and parse all properties files
            self._load_properties()
            
            if not self.properties:
                result.skipped = True
                result.skip_reason = "No properties files found"
                return result
            
            # Extract item info from first non-replica properties
            self._extract_item_info()
            
            result.item_name = self.item_name
            result.reduced_name = self.reduced_name
            result.is_replica = self.is_replica
            
            # Let the subclass do the actual analysis
            operations, issues = self._analyze_folder()
            result.operations = operations
            result.issues = issues
            
        except Exception as e:
            logger.exception(f"Error analyzing {self.folder_path}")
            result.issues.append(f"Error during analysis: {str(e)}")
        
        return result
    
    def _load_properties(self) -> None:
        """Load all .properties files in the folder."""
        self.properties_files = list(self.folder_path.glob("*.properties"))
        
        for prop_file in self.properties_files:
            try:
                self.properties[prop_file] = parse_properties(prop_file)
            except Exception as e:
                logger.warning(f"Failed to parse {prop_file}: {e}")
    
    def _extract_item_info(self) -> None:
        """Extract item name and other info from properties."""
        # Find the first non-replica properties file to get the canonical name
        for prop_file, props in self.properties.items():
            name = get_item_name(props)
            if name:
                self.item_name = name
                self.reduced_name = reduce_name(name)
                self.is_replica = is_replica(props)
                
                # Prefer non-replica as the source of truth
                if not self.is_replica:
                    break
    
    @abstractmethod
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """
        Analyze the folder and generate file operations.
        
        This is where subclasses implement their specific logic.
        
        Returns:
            Tuple of (list of FileOperations, list of issue strings)
        """
        pass
    
    # Helper methods for subclasses
    
    def _create_copy_operation(
        self, 
        source: Path, 
        dest_name: str,
        description: str = ""
    ) -> FileOperation:
        """Create a copy operation from source to output folder."""
        return FileOperation(
            operation_type=OperationType.COPY,
            source=source,
            destination=self.output_folder / dest_name,
            description=description or f"Copy {source.name} -> {dest_name}"
        )
    
    def _create_write_operation(
        self,
        dest_name: str,
        content: str,
        description: str = ""
    ) -> FileOperation:
        """Create a write operation for new/modified content."""
        return FileOperation(
            operation_type=OperationType.WRITE,
            destination=self.output_folder / dest_name,
            content=content,
            description=description or f"Write {dest_name}"
        )
    
    def _copy_with_rename(
        self,
        source: Path,
        new_stem: str,
        description: str = ""
    ) -> list[FileOperation]:
        """
        Create copy operations for a texture and its associated files.
        
        Handles:
        - Main texture (.png)
        - Emissive texture (_e.png)
        - Animation file (.png.mcmeta)
        - Emissive animation file (_e.png.mcmeta)
        
        Args:
            source: Path to the source .png file
            new_stem: New filename stem (without extension)
            description: Optional description prefix
            
        Returns:
            List of FileOperations for all associated files
        """
        operations = []
        folder = source.parent
        old_stem = source.stem
        
        # Main texture
        if source.exists():
            operations.append(self._create_copy_operation(
                source,
                f"{new_stem}.png",
                f"{description}: {old_stem}.png -> {new_stem}.png" if description else ""
            ))
        
        # Emissive
        emissive = folder / f"{old_stem}_e.png"
        if emissive.exists():
            operations.append(self._create_copy_operation(
                emissive,
                f"{new_stem}_e.png"
            ))
        
        # Animation
        mcmeta = folder / f"{old_stem}.png.mcmeta"
        if mcmeta.exists():
            operations.append(self._create_copy_operation(
                mcmeta,
                f"{new_stem}.png.mcmeta"
            ))
        
        # Emissive animation
        e_mcmeta = folder / f"{old_stem}_e.png.mcmeta"
        if e_mcmeta.exists():
            operations.append(self._create_copy_operation(
                e_mcmeta,
                f"{new_stem}_e.png.mcmeta"
            ))
        
        return operations
