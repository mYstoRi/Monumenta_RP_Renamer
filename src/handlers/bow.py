"""Handler for bow items with pulling animations."""

from pathlib import Path
from typing import ClassVar
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, is_replica

logger = logging.getLogger(__name__)


@HandlerRegistry.register
class BowHandler(BaseHandler):
    """
    Handler for bows with pulling animations.
    
    Expected files:
    - standby texture (or base texture)
    - pulling_0 through pulling_4 textures
    - Emissive versions (_e.png) optional
    - Animation files (.png.mcmeta) optional
    """
    
    name: ClassVar[str] = "bow"
    priority: ClassVar[int] = 10  # Higher than generic
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """Check if this folder contains a bow item."""
        for props in properties_list:
            base_item = get_base_item(props)
            if base_item == 'bow':
                return True
        return False
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """
        Analyze a bow folder and generate operations.
        
        Bow naming convention:
        - {name}.png (standby/idle)
        - {name}_pulling_0.png through {name}_pulling_4.png
        """
        operations = []
        issues = []
        
        if not self.item_name:
            issues.append("Could not determine item name")
            return operations, issues
        
        # Track which textures we've seen
        texture_mapping = {}  # old_name -> new_name
        
        # Process properties files
        for prop_file, props in self.properties.items():
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            
            # Parse texture references from properties
            base_texture = props.get('texture', '')
            if base_texture.endswith('.png'):
                base_texture = base_texture[:-4]
            
            pulling_textures = {}
            for i in range(5):
                key = f'texture.bow_pulling_{i}'
                if key in props:
                    tex = props[key]
                    if tex.endswith('.png'):
                        tex = tex[:-4]
                    pulling_textures[i] = tex
            
            # Map old texture names to new names
            if base_texture:
                texture_mapping[base_texture] = self.reduced_name
            
            for i, tex in pulling_textures.items():
                texture_mapping[tex] = f"{self.reduced_name}_pulling_{i}"
            
            # Generate new properties filename
            new_prop_name = f"{prefix}{self.reduced_name}.properties"
            
            # Generate new properties content
            new_content = self._generate_properties(props, is_rep, pulling_textures)
            operations.append(self._create_write_operation(
                new_prop_name,
                new_content,
                f"{'Replica ' if is_rep else ''}Properties: {prop_file.name} -> {new_prop_name}"
            ))
        
        # Copy texture files with new names
        processed_textures = set()
        for old_name, new_name in texture_mapping.items():
            if old_name in processed_textures:
                continue
            processed_textures.add(old_name)
            
            texture_path = self.folder_path / f"{old_name}.png"
            if texture_path.exists():
                operations.extend(self._copy_with_rename(
                    texture_path,
                    new_name,
                    f"Texture"
                ))
            else:
                issues.append(f"Missing texture: {old_name}.png")
        
        return operations, issues
    
    def _generate_properties(
        self, 
        original: dict[str, str], 
        is_replica: bool,
        pulling_textures: dict[int, str]
    ) -> str:
        """Generate standardized bow properties file content."""
        lines = []
        
        lines.append("type=item")
        lines.append("matchItems=bow")
        
        # Model (if present)
        model = original.get('model')
        if model:
            lines.append(f"model={model}")
        
        # Base texture (no _standby suffix per README convention)
        lines.append(f"texture={self.reduced_name}")
        
        # Pulling textures
        for i in range(5):
            lines.append(f"texture.bow_pulling_{i}={self.reduced_name}_pulling_{i}")
        
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
