"""Handler for generic/simple items with a single texture."""

from pathlib import Path
from typing import ClassVar
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, get_display_name, is_replica

logger = logging.getLogger(__name__)


@HandlerRegistry.register
class GenericHandler(BaseHandler):
    """
    Handler for simple items with:
    - One texture file
    - One properties file (or two if replica exists)
    - Uses a model from source_models folder (not subfolders)
    
    This is the fallback handler with lowest priority.
    """
    
    name: ClassVar[str] = "generic"
    priority: ClassVar[int] = 0  # Lowest priority - fallback handler
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """
        Check if this folder contains a simple generic item.
        
        Criteria:
        - Has exactly 1 or 2 properties files
        - Not a bow, crossbow, armor, or potion
        - Uses model from source_models (not subfolders) OR no model
        """
        if not properties_list:
            return False
        
        # Check property count (1 for non-replica, 2 if has replica)
        if len(properties_list) > 2:
            return False
        
        for props in properties_list:
            base_item = get_base_item(props)
            if not base_item:
                continue
                
            # Exclude specific item types that have dedicated handlers
            if base_item in ('bow', 'crossbow'):
                return False
            if base_item in ('potion', 'splash_potion', 'lingering_potion'):
                return False
            if props.get('type') == 'armor':
                return False
            
            # Check if it's armor-related
            armor_items = ['helmet', 'chestplate', 'leggings', 'boots']
            if any(armor in base_item for armor in armor_items):
                # Could be armor - check if there's a type=armor property
                if props.get('type') == 'armor':
                    return False
        
        # Count texture files (non-emissive .png files)
        png_files = [f for f in folder_path.glob("*.png") if not f.stem.endswith("_e")]
        
        # Generic items typically have 1-2 textures
        if len(png_files) > 2:
            return False
        
        return True
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """
        Analyze a generic item folder and generate operations.
        
        Returns:
            Tuple of (operations list, issues list)
        """
        operations = []
        issues = []
        
        if not self.item_name:
            issues.append("Could not determine item name")
            return operations, issues
        
        # Process each properties file
        for prop_file, props in self.properties.items():
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            
            # Generate new properties filename
            new_prop_name = f"{prefix}{self.reduced_name}.properties"
            
            # Check if rename is needed
            if prop_file.name != new_prop_name:
                # Generate new properties content
                new_content = self._generate_properties(props, is_rep)
                operations.append(self._create_write_operation(
                    new_prop_name,
                    new_content,
                    f"Rewrite properties: {prop_file.name} -> {new_prop_name}"
                ))
            else:
                # Just copy the existing file
                operations.append(self._create_copy_operation(
                    prop_file,
                    new_prop_name
                ))
            
            # Handle texture file
            texture_name = props.get('texture', '')
            if texture_name:
                # Remove .png extension if present
                if texture_name.endswith('.png'):
                    texture_name = texture_name[:-4]
                
                texture_path = self.folder_path / f"{texture_name}.png"
                
                if texture_path.exists():
                    # Determine new texture name
                    new_texture_stem = self.reduced_name
                    
                    if texture_name != new_texture_stem:
                        # Need to rename - copy with new name
                        operations.extend(self._copy_with_rename(
                            texture_path,
                            new_texture_stem,
                            "Rename texture"
                        ))
                    else:
                        # Just copy as-is
                        operations.extend(self._copy_with_rename(
                            texture_path,
                            new_texture_stem
                        ))
                else:
                    issues.append(f"Texture file not found: {texture_name}.png")
        
        return operations, issues
    
    def _generate_properties(self, original: dict[str, str], is_replica: bool) -> str:
        """
        Generate standardized properties file content.
        
        Args:
            original: Original properties dictionary
            is_replica: Whether this is a replica item
            
        Returns:
            Properties file content as string
        """
        lines = []
        
        # Type
        lines.append(f"type=item")
        
        # Base item
        base_item = get_base_item(original)
        if base_item:
            lines.append(f"matchItems={base_item}")
        
        # Model (if present)
        model = original.get('model')
        if model:
            lines.append(f"model={model}")
        
        # Texture
        lines.append(f"texture={self.reduced_name}")
        
        # Display name
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {self.item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={self.item_name}")
        
        # Weight (if present)
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
