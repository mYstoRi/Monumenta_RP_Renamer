"""Handler for single armor pieces (non-set armor)."""

from pathlib import Path
from typing import ClassVar
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, is_replica

logger = logging.getLogger(__name__)


@HandlerRegistry.register
class ArmorHandler(BaseHandler):
    """
    Handler for individual armor pieces (not part of a set).
    
    Expected structure:
    - Icon properties (type=item)
    - Armor properties (type=armor)
    - Icon texture + overlay (for leather)
    - Armor layer texture + overlay (for leather)
    """
    
    name: ClassVar[str] = "armor"
    priority: ClassVar[int] = 5  # Between generic and set armor
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """
        Check if this folder contains a single armor piece.
        
        Criteria:
        - Has type=armor property
        - Not a set (doesn't have icons/ and armor/ subfolders)
        """
        has_armor_type = False
        armor_pieces = set()
        
        for props in properties_list:
            if props.get('type') == 'armor':
                has_armor_type = True
            
            base_item = get_base_item(props)
            if base_item:
                for piece in ['helmet', 'chestplate', 'leggings', 'boots']:
                    if piece in base_item:
                        armor_pieces.add(piece)
        
        if not has_armor_type:
            return False
        
        # If it has icons/ and armor/ subfolders, it's a set
        if (folder_path / "icons").exists() and (folder_path / "armor").exists():
            return False
        
        # Single armor piece (not multiple pieces = set)
        return len(armor_pieces) <= 1
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """Analyze a single armor piece folder."""
        operations = []
        issues = []
        
        if not self.item_name:
            issues.append("Could not determine item name")
            return operations, issues
        
        # Determine material and piece type
        material = None
        piece_type = None
        is_leather = False
        
        for props in self.properties.values():
            base_item = get_base_item(props)
            if base_item:
                parts = base_item.split('_')
                if len(parts) >= 2:
                    material = parts[0]
                    piece_type = parts[1] if len(parts) == 2 else '_'.join(parts[1:])
                    is_leather = material == 'leather'
                    if material == 'golden':
                        material = 'gold'
                break
        
        if not material or not piece_type:
            issues.append("Could not determine armor material/piece type")
            return operations, issues
        
        # Track processed properties to avoid duplicates
        processed_icon = False
        processed_armor = False
        
        for prop_file, props in self.properties.items():
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            prop_type = props.get('type', 'item')
            
            if prop_type == 'armor' and not processed_armor:
                # Armor layer properties
                new_prop_name = f"{prefix}{self.reduced_name}_armor.properties"
                new_content = self._generate_armor_properties(props, is_rep, material, piece_type, is_leather)
                operations.append(self._create_write_operation(
                    new_prop_name, new_content,
                    f"Armor properties: {prop_file.name} -> {new_prop_name}"
                ))
                
                # Copy armor textures
                layer_num = "2" if "leggings" in piece_type else "1"
                layer_key = f"texture.{material}_layer_{layer_num}"
                
                if is_leather:
                    base_tex = props.get(layer_key, '')
                    overlay_tex = props.get(f"{layer_key}_overlay", '')
                    
                    if base_tex:
                        tex_path = self.folder_path / f"{base_tex}.png"
                        if tex_path.exists():
                            operations.extend(self._copy_with_rename(
                                tex_path, f"{self.reduced_name}_armor"
                            ))
                    
                    if overlay_tex:
                        overlay_path = self.folder_path / f"{overlay_tex}.png"
                        if overlay_path.exists():
                            operations.extend(self._copy_with_rename(
                                overlay_path, f"{self.reduced_name}_armor_overlay"
                            ))
                else:
                    tex_name = props.get(layer_key, '')
                    if tex_name:
                        tex_path = self.folder_path / f"{tex_name}.png"
                        if tex_path.exists():
                            operations.extend(self._copy_with_rename(
                                tex_path, f"{self.reduced_name}_armor"
                            ))
                
                processed_armor = True
                
            elif prop_type == 'item' and not processed_icon:
                # Icon properties
                new_prop_name = f"{prefix}{self.reduced_name}_icon.properties"
                new_content = self._generate_icon_properties(props, is_rep, is_leather)
                operations.append(self._create_write_operation(
                    new_prop_name, new_content,
                    f"Icon properties: {prop_file.name} -> {new_prop_name}"
                ))
                
                # Copy icon textures
                if is_leather:
                    base_item = get_base_item(props)
                    base_tex = props.get(f"texture.{base_item}", '')
                    overlay_tex = props.get(f"texture.{base_item}_overlay", '')
                    
                    if base_tex:
                        tex_path = self.folder_path / f"{base_tex}.png"
                        if tex_path.exists():
                            operations.extend(self._copy_with_rename(
                                tex_path, f"{self.reduced_name}_icon"
                            ))
                    
                    if overlay_tex:
                        overlay_path = self.folder_path / f"{overlay_tex}.png"
                        if overlay_path.exists():
                            operations.extend(self._copy_with_rename(
                                overlay_path, f"{self.reduced_name}_icon_overlay"
                            ))
                else:
                    tex_name = props.get('texture', '')
                    if tex_name:
                        if tex_name.endswith('.png'):
                            tex_name = tex_name[:-4]
                        tex_path = self.folder_path / f"{tex_name}.png"
                        if tex_path.exists():
                            operations.extend(self._copy_with_rename(
                                tex_path, f"{self.reduced_name}_icon"
                            ))
                
                processed_icon = True
        
        return operations, issues
    
    def _generate_icon_properties(
        self, 
        original: dict[str, str], 
        is_replica: bool,
        is_leather: bool
    ) -> str:
        """Generate standardized icon properties."""
        lines = []
        base_item = get_base_item(original)
        
        lines.append("type=item")
        lines.append(f"matchItems={base_item}")
        
        if is_leather:
            lines.append(f"texture.{base_item}={self.reduced_name}_icon")
            lines.append(f"texture.{base_item}_overlay={self.reduced_name}_icon_overlay")
        else:
            lines.append(f"texture={self.reduced_name}_icon")
        
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {self.item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={self.item_name}")
        
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
    
    def _generate_armor_properties(
        self,
        original: dict[str, str],
        is_replica: bool,
        material: str,
        piece_type: str,
        is_leather: bool
    ) -> str:
        """Generate standardized armor layer properties."""
        lines = []
        base_item = get_base_item(original)
        layer_num = "2" if "leggings" in piece_type else "1"
        
        lines.append("type=armor")
        lines.append(f"matchItems={base_item}")
        
        lines.append(f"texture.{material}_layer_{layer_num}={self.reduced_name}_armor")
        if is_leather:
            lines.append(f"texture.{material}_layer_{layer_num}_overlay={self.reduced_name}_armor_overlay")
        
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {self.item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={self.item_name}")
        
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
