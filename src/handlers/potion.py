"""Handler for potion items with custom models."""

from pathlib import Path
from typing import ClassVar
import json
import logging

from ..core.base_handler import BaseHandler
from ..core.registry import HandlerRegistry
from ..core.operations import FileOperation, OperationType
from ..core.utils import get_base_item, is_replica

logger = logging.getLogger(__name__)


@HandlerRegistry.register
class PotionHandler(BaseHandler):
    """
    Handler for potions that use custom JSON models.
    
    Expected files:
    - properties file referencing a model
    - potion texture (layer1)
    - potion overlay texture (layer0)
    - JSON model in source_models/potions/
    """
    
    name: ClassVar[str] = "potion"
    priority: ClassVar[int] = 10
    
    @staticmethod
    def can_handle(folder_path: Path, properties_list: list[dict[str, str]]) -> bool:
        """Check if this folder contains a potion item."""
        for props in properties_list:
            base_item = get_base_item(props)
            if base_item in ('potion', 'splash_potion', 'lingering_potion'):
                # Check that it has a model (potions typically need models)
                if 'model' in props:
                    return True
        return False
    
    def _analyze_folder(self) -> tuple[list[FileOperation], list[str]]:
        """Analyze a potion folder and generate operations."""
        operations = []
        issues = []
        
        if not self.item_name:
            issues.append("Could not determine item name")
            return operations, issues
        
        for prop_file, props in self.properties.items():
            is_rep = is_replica(props)
            prefix = "replica_" if is_rep else ""
            
            base_item = get_base_item(props)
            model_path = props.get('model', '')
            
            # Clean up model path
            if model_path.endswith('.json'):
                model_path = model_path[:-5]
            
            # Generate new properties
            new_prop_name = f"{prefix}{self.reduced_name}.properties"
            
            # Calculate new model path
            model_parts = model_path.split('/')
            if len(model_parts) > 1:
                new_model_path = '/'.join(model_parts[:-1]) + '/' + self.reduced_name
            else:
                new_model_path = self.reduced_name
            
            new_content = self._generate_properties(props, is_rep, base_item, new_model_path)
            operations.append(self._create_write_operation(
                new_prop_name,
                new_content,
                f"{'Replica ' if is_rep else ''}Properties: {prop_file.name} -> {new_prop_name}"
            ))
            
            # Handle textures
            # Potions have layer0 (overlay) and layer1 (base)
            # Find textures in folder
            for png_file in self.folder_path.glob("*.png"):
                if png_file.stem.endswith("_e"):
                    continue  # Skip emissive for now
                
                old_stem = png_file.stem
                
                # Determine new name
                if "overlay" in old_stem.lower():
                    new_stem = f"{self.reduced_name}_overlay"
                elif old_stem == "potion":
                    new_stem = self.reduced_name
                elif old_stem == "potion_overlay":
                    new_stem = f"{self.reduced_name}_overlay"
                else:
                    new_stem = self.reduced_name
                
                if old_stem != new_stem:
                    operations.extend(self._copy_with_rename(
                        png_file,
                        new_stem,
                        "Potion texture"
                    ))
                else:
                    operations.extend(self._copy_with_rename(
                        png_file,
                        new_stem
                    ))
            
            # Handle model file if it exists
            if model_path:
                full_model_path = self._find_model_file(model_path)
                if full_model_path and full_model_path.exists():
                    # Read and update model content
                    try:
                        model_content = json.loads(full_model_path.read_text(encoding='utf-8'))
                        updated_model = self._update_model_textures(model_content)
                        
                        # Calculate output model path
                        new_model_name = f"{self.reduced_name}.json"
                        model_dir = full_model_path.parent
                        rel_model_dir = model_dir.relative_to(self.input_base)
                        output_model_path = self.output_base / rel_model_dir / new_model_name
                        
                        operations.append(FileOperation(
                            operation_type=OperationType.WRITE,
                            destination=output_model_path,
                            content=json.dumps(updated_model, indent=4),
                            description=f"Model: {full_model_path.name} -> {new_model_name}"
                        ))
                    except Exception as e:
                        issues.append(f"Failed to process model {model_path}: {e}")
        
        return operations, issues
    
    def _find_model_file(self, model_path: str) -> Path | None:
        """Find the full path to a model file."""
        # Models are typically in assets/minecraft/optifine/cit/source_models/
        # The path in properties is relative like optifine/cit/source_models/potions/xxx
        
        # Try direct path from input base
        if model_path.startswith("optifine/"):
            full_path = self.input_base / "assets" / "minecraft" / model_path
            if not full_path.suffix:
                full_path = full_path.with_suffix('.json')
            if full_path.exists():
                return full_path
        
        # Try with assets/minecraft prefix
        full_path = self.input_base / "assets" / "minecraft" / model_path
        if not full_path.suffix:
            full_path = full_path.with_suffix('.json')
        if full_path.exists():
            return full_path
        
        return None
    
    def _update_model_textures(self, model: dict) -> dict:
        """Update texture references in a model to use new names."""
        if "textures" not in model:
            return model
        
        textures = model["textures"]
        
        # Update layer0 and layer1
        for layer in ["layer0", "layer1"]:
            if layer in textures:
                old_path = textures[layer]
                path_parts = old_path.split('/')
                
                if layer == "layer0":
                    # Overlay
                    path_parts[-1] = f"{self.reduced_name}_overlay"
                else:
                    # Base texture
                    path_parts[-1] = self.reduced_name
                
                textures[layer] = '/'.join(path_parts)
        
        model["textures"] = textures
        return model
    
    def _generate_properties(
        self,
        original: dict[str, str],
        is_replica: bool,
        base_item: str,
        new_model_path: str
    ) -> str:
        """Generate standardized potion properties."""
        lines = []
        
        lines.append("type=item")
        lines.append(f"matchItems={base_item}")
        lines.append(f"model={new_model_path}")
        
        if is_replica:
            lines.append(f"nbt.plain.display.Name=Replica {self.item_name}")
        else:
            lines.append(f"nbt.plain.display.Name={self.item_name}")
        
        weight = original.get('weight')
        if weight:
            lines.append(f"weight={weight}")
        
        return '\n'.join(lines) + '\n'
