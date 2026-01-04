"""Handler for armor sets (multiple pieces with shared textures)."""

from pathlib import Path
from typing import ClassVar
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, get_item_name, reduce_name, is_replica, parse_properties

logger = logging.getLogger(__name__)


@HandlerRegistry.register  
class SetArmorHandler(BaseHandler):
    """
    Handler for armor sets with icons/ and armor/ subfolders.
    
    Expected structure:
    set_folder/
    ├── icons/
    │   ├── {name}_helmet_icon.properties
    │   ├── {name}_chestplate_icon.properties
    │   ├── {name}_leggings_icon.properties
    │   ├── {name}_boots_icon.properties
    │   └── *.png (icon textures)
    └── armor/
        ├── {name}_armor.properties (or per-piece properties)
        ├── {name}_layer_1.png (helmet, chest, boots)
        └── {name}_layer_2.png (leggings)
    """
    
    name: ClassVar[str] = "set_armor"
    priority: ClassVar[int] = 15  # Higher than single armor
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """
        Check if this folder contains an armor set.
        
        Criteria:
        - Has icons/ and armor/ subfolders
        """
        icons_path = folder_path / "icons"
        armor_path = folder_path / "armor"
        
        return icons_path.exists() and armor_path.exists()
    
    def __init__(self, folder_path: Path, output_base: Path, input_base: Path):
        """Initialize with set-specific paths."""
        super().__init__(folder_path, output_base, input_base)
        self.icons_path = folder_path / "icons"
        self.armor_path = folder_path / "armor"
        self.output_icons = self.output_folder / "icons"
        self.output_armor = self.output_folder / "armor"
        
        # Set name derived from folder name
        self.set_name = folder_path.name
        self.reduced_set_name = reduce_name(self.set_name)
    
    def _load_properties(self) -> None:
        """Load properties from both icons/ and armor/ subfolders."""
        # Load icon properties
        for prop_file in self.icons_path.glob("*.properties"):
            try:
                self.properties[prop_file] = parse_properties(prop_file)
                self.properties_files.append(prop_file)
            except Exception as e:
                logger.warning(f"Failed to parse {prop_file}: {e}")
        
        # Load armor properties
        for prop_file in self.armor_path.glob("*.properties"):
            try:
                self.properties[prop_file] = parse_properties(prop_file)
                self.properties_files.append(prop_file)
            except Exception as e:
                logger.warning(f"Failed to parse {prop_file}: {e}")
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """Analyze an armor set folder."""
        operations = []
        issues = []
        
        # Determine material from properties
        material = None
        is_leather = False
        
        for props in self.properties.values():
            base_item = get_base_item(props)
            if base_item:
                parts = base_item.split('_')
                material = parts[0]
                is_leather = material == 'leather'
                if material == 'golden':
                    material = 'gold'
                break
        
        if not material:
            issues.append("Could not determine armor material")
            return operations, issues
        
        # Process icons
        icon_ops, icon_issues = self._process_icons(is_leather)
        operations.extend(icon_ops)
        issues.extend(icon_issues)
        
        # Process armor layers
        armor_ops, armor_issues = self._process_armor_layers(material, is_leather)
        operations.extend(armor_ops)
        issues.extend(armor_issues)
        
        return operations, issues
    
    def _process_icons(self, is_leather: bool) -> tuple[list[FileOperation], list[str]]:
        """Process icon properties and textures."""
        operations = []
        issues = []
        
        pieces = ['helmet', 'chestplate', 'leggings', 'boots']
        
        for prop_file, props in self.properties.items():
            if prop_file.parent != self.icons_path:
                continue
            
            base_item = get_base_item(props)
            if not base_item:
                continue
            
            # Determine which piece this is
            piece = None
            for p in pieces:
                if p in base_item:
                    piece = p
                    break
            
            if not piece:
                continue
            
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            item_name = get_item_name(props) or self.set_name
            reduced_item = reduce_name(item_name)
            
            # Generate new properties filename
            new_prop_name = f"{prefix}{reduced_item}_icon.properties"
            new_content = self._generate_icon_properties(props, is_rep, base_item, reduced_item, is_leather)
            
            operations.append(FileOperation(
                operation_type=OperationType.WRITE,
                destination=self.output_icons / new_prop_name,
                content=new_content,
                description=f"Icon properties: {prop_file.name} -> {new_prop_name}"
            ))
            
            # Copy icon textures
            if is_leather:
                base_tex = props.get(f"texture.{base_item}", '')
                overlay_tex = props.get(f"texture.{base_item}_overlay", '')
                
                if base_tex:
                    tex_path = self.icons_path / f"{base_tex}.png"
                    if tex_path.exists():
                        operations.extend(self._copy_icon_texture(tex_path, f"{reduced_item}_icon"))
                    else:
                        issues.append(f"Missing icon texture: {base_tex}.png")
                
                if overlay_tex:
                    overlay_path = self.icons_path / f"{overlay_tex}.png"
                    if overlay_path.exists():
                        operations.extend(self._copy_icon_texture(overlay_path, f"{reduced_item}_icon_overlay"))
            else:
                tex_name = props.get('texture', '')
                if tex_name:
                    if tex_name.endswith('.png'):
                        tex_name = tex_name[:-4]
                    tex_path = self.icons_path / f"{tex_name}.png"
                    if tex_path.exists():
                        operations.extend(self._copy_icon_texture(tex_path, f"{reduced_item}_icon"))
        
        return operations, issues
    
    def _copy_icon_texture(self, source: Path, new_stem: str) -> list[FileOperation]:
        """Copy icon texture and its variants to output icons folder."""
        operations = []
        old_stem = source.stem
        folder = source.parent
        
        # Main texture
        if source.exists():
            operations.append(FileOperation(
                operation_type=OperationType.COPY,
                source=source,
                destination=self.output_icons / f"{new_stem}.png"
            ))
        
        # Emissive
        emissive = folder / f"{old_stem}_e.png"
        if emissive.exists():
            operations.append(FileOperation(
                operation_type=OperationType.COPY,
                source=emissive,
                destination=self.output_icons / f"{new_stem}_e.png"
            ))
        
        return operations
    
    def _process_armor_layers(self, material: str, is_leather: bool) -> tuple[list[FileOperation], list[str]]:
        """Process armor layer properties and textures."""
        operations = []
        issues = []
        
        for prop_file, props in self.properties.items():
            if prop_file.parent != self.armor_path:
                continue
            
            if props.get('type') != 'armor':
                continue
            
            base_item = get_base_item(props)
            if not base_item:
                continue
            
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            item_name = get_item_name(props) or self.set_name
            reduced_item = reduce_name(item_name)
            
            # Determine piece type for layer number
            layer_num = "2" if "leggings" in base_item else "1"
            piece = "leggings" if "leggings" in base_item else "other"
            
            # Generate properties
            new_prop_name = f"{prefix}{reduced_item}_layer.properties"
            new_content = self._generate_armor_properties(props, is_rep, material, layer_num, is_leather, reduced_item)
            
            operations.append(FileOperation(
                operation_type=OperationType.WRITE,
                destination=self.output_armor / new_prop_name,
                content=new_content,
                description=f"Armor properties: {prop_file.name} -> {new_prop_name}"
            ))
        
        # Copy layer textures (shared across set pieces)
        layer_textures = self._find_layer_textures(material, is_leather)
        for old_name, new_name in layer_textures.items():
            tex_path = self.armor_path / f"{old_name}.png"
            if tex_path.exists():
                operations.extend(self._copy_armor_texture(tex_path, new_name))
        
        return operations, issues
    
    def _find_layer_textures(self, material: str, is_leather: bool) -> dict[str, str]:
        """Find all layer textures and map to new names."""
        mapping = {}
        
        for prop_file, props in self.properties.items():
            if prop_file.parent != self.armor_path:
                continue
            
            # Check for layer_1 and layer_2 textures
            for layer in ['1', '2']:
                key = f"texture.{material}_layer_{layer}"
                tex = props.get(key, '')
                if tex and tex not in mapping:
                    mapping[tex] = f"{self.reduced_set_name}_layer_{layer}"
                
                if is_leather:
                    overlay_key = f"{key}_overlay"
                    overlay_tex = props.get(overlay_key, '')
                    if overlay_tex and overlay_tex not in mapping:
                        mapping[overlay_tex] = f"{self.reduced_set_name}_layer_{layer}_overlay"
        
        return mapping
    
    def _copy_armor_texture(self, source: Path, new_stem: str) -> list[FileOperation]:
        """Copy armor texture to output armor folder."""
        operations = []
        old_stem = source.stem
        folder = source.parent
        
        if source.exists():
            operations.append(FileOperation(
                operation_type=OperationType.COPY,
                source=source,
                destination=self.output_armor / f"{new_stem}.png"
            ))
        
        # Emissive
        emissive = folder / f"{old_stem}_e.png"
        if emissive.exists():
            operations.append(FileOperation(
                operation_type=OperationType.COPY,
                source=emissive,
                destination=self.output_armor / f"{new_stem}_e.png"
            ))
        
        return operations
    
    def _generate_icon_properties(
        self,
        original: dict[str, str],
        is_replica: bool,
        base_item: str,
        reduced_name: str,
        is_leather: bool
    ) -> str:
        """Generate standardized icon properties."""
        lines = []
        
        lines.append("type=item")
        lines.append(f"matchItems={base_item}")
        
        if is_leather:
            lines.append(f"texture.{base_item}={reduced_name}_icon")
            lines.append(f"texture.{base_item}_overlay={reduced_name}_icon_overlay")
        else:
            lines.append(f"texture={reduced_name}_icon")
        
        item_name = get_item_name(original) or self.set_name
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={item_name}")
        
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
    
    def _generate_armor_properties(
        self,
        original: dict[str, str],
        is_replica: bool,
        material: str,
        layer_num: str,
        is_leather: bool,
        reduced_name: str
    ) -> str:
        """Generate standardized armor layer properties."""
        lines = []
        base_item = get_base_item(original)
        
        lines.append("type=armor")
        lines.append(f"matchItems={base_item}")
        
        lines.append(f"texture.{material}_layer_{layer_num}={self.reduced_set_name}_layer_{layer_num}")
        if is_leather:
            lines.append(f"texture.{material}_layer_{layer_num}_overlay={self.reduced_set_name}_layer_{layer_num}_overlay")
        
        item_name = get_item_name(original) or self.set_name
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={item_name}")
        
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
