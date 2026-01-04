"""Handler for crossbow items with pulling and loaded states."""

from pathlib import Path
from typing import ClassVar
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, is_replica

logger = logging.getLogger(__name__)


@HandlerRegistry.register
class CrossbowHandler(BaseHandler):
    """
    Handler for crossbows with pulling and loaded state animations.
    
    Expected files:
    - base texture (idle/standby)
    - pulling_0 through pulling_2 textures
    - arrow loaded texture
    - firework loaded texture
    - Emissive versions (_e.png) optional
    """
    
    name: ClassVar[str] = "crossbow"
    priority: ClassVar[int] = 10  # Same as bow
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """Check if this folder contains a crossbow item."""
        for props in properties_list:
            base_item = get_base_item(props)
            if base_item == 'crossbow':
                return True
        return False
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """
        Analyze a crossbow folder and generate operations.
        
        Crossbow naming convention:
        - {name}.png (idle)
        - {name}_pulling_0.png through {name}_pulling_2.png
        - {name}_arrow.png (loaded with arrow)
        - {name}_firework.png (loaded with firework)
        """
        operations = []
        issues = []
        
        if not self.item_name:
            issues.append("Could not determine item name")
            return operations, issues
        
        # Track texture mappings
        texture_mapping = {}  # old_name -> new_name
        
        # Process properties files
        for prop_file, props in self.properties.items():
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            
            # Parse texture references
            base_texture = props.get('texture', '')
            if base_texture.endswith('.png'):
                base_texture = base_texture[:-4]
            
            # Pulling textures (0-2 for crossbow)
            pulling_textures = {}
            for i in range(3):
                key = f'texture.crossbow_pulling_{i}'
                if key in props:
                    tex = props[key]
                    if tex.endswith('.png'):
                        tex = tex[:-4]
                    pulling_textures[i] = tex
            
            # Arrow and firework textures
            arrow_texture = props.get('texture.crossbow_arrow', '')
            if arrow_texture.endswith('.png'):
                arrow_texture = arrow_texture[:-4]
                
            firework_texture = props.get('texture.crossbow_firework', '')
            if firework_texture.endswith('.png'):
                firework_texture = firework_texture[:-4]
            
            # Build texture mapping
            if base_texture:
                texture_mapping[base_texture] = self.reduced_name
            
            for i, tex in pulling_textures.items():
                texture_mapping[tex] = f"{self.reduced_name}_pulling_{i}"
            
            if arrow_texture:
                texture_mapping[arrow_texture] = f"{self.reduced_name}_arrow"
            
            if firework_texture:
                texture_mapping[firework_texture] = f"{self.reduced_name}_firework"
            
            # Generate new properties
            new_prop_name = f"{prefix}{self.reduced_name}.properties"
            new_content = self._generate_properties(props, is_rep)
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
    
    def _generate_properties(self, original: dict[str, str], is_replica: bool) -> str:
        """Generate standardized crossbow properties file content."""
        lines = []
        
        lines.append("type=item")
        lines.append("matchItems=crossbow")
        
        # Model (if present)
        model = original.get('model')
        if model:
            lines.append(f"model={model}")
        
        # Base texture
        lines.append(f"texture={self.reduced_name}")
        
        # Pulling textures (0-2)
        for i in range(3):
            lines.append(f"texture.crossbow_pulling_{i}={self.reduced_name}_pulling_{i}")
        
        # Arrow and firework
        lines.append(f"texture.crossbow_arrow={self.reduced_name}_arrow")
        lines.append(f"texture.crossbow_firework={self.reduced_name}_firework")
        
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
