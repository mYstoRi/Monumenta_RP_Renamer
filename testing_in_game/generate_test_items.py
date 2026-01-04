"""
Generate test items for in-game testing of the renamed resource pack.

This script creates Minecraft datapack mcfunctions that give chests containing
sample items from each handler type to verify textures are loading correctly.
"""

import os
import sys
import json
from pathlib import Path
from typing import Iterator

# Add parent src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils import parse_properties, get_base_item, get_display_name


# Datapack utilities (simplified from hopeskin_scripts)
def mkdir_and_cd(root: str, path: str) -> str:
    """Create directory if not exists and return new path."""
    new_path = os.path.join(root, path)
    os.makedirs(new_path, exist_ok=True)
    return new_path


def create_empty_datapack(root: str, pack_name: str, namespace: str) -> str:
    """Create a basic datapack structure."""
    pack_meta = {
        "pack": {
            "pack_format": 26,
            "description": "RP Renamer Test Items"
        }
    }
    
    # Create pack structure
    pack_root = mkdir_and_cd(root, pack_name)
    
    with open(os.path.join(pack_root, "pack.mcmeta"), "w") as f:
        json.dump(pack_meta, f, indent=2)
    
    data_root = mkdir_and_cd(pack_root, "data")
    ns_root = mkdir_and_cd(data_root, namespace)
    fn_root = mkdir_and_cd(ns_root, "functions")
    
    # Create empty load/tick functions
    open(os.path.join(fn_root, "load.mcfunction"), "w").close()
    open(os.path.join(fn_root, "tick.mcfunction"), "w").close()
    
    # Create minecraft tags
    mc_root = mkdir_and_cd(data_root, "minecraft")
    tags_root = mkdir_and_cd(mc_root, "tags")
    fn_tags_root = mkdir_and_cd(tags_root, "functions")
    
    load_json = {"values": [f"{namespace}:load"]}
    tick_json = {"values": [f"{namespace}:tick"]}
    
    with open(os.path.join(fn_tags_root, "load.json"), "w") as f:
        json.dump(load_json, f, indent=2)
    with open(os.path.join(fn_tags_root, "tick.json"), "w") as f:
        json.dump(tick_json, f, indent=2)
    
    return fn_root


def find_sample_items(pack_path: Path, handler_type: str, max_items: int = 9) -> list[dict]:
    """
    Find sample items of a specific handler type from the pack.
    
    Returns list of dicts with base_item and display_name.
    """
    cit_path = pack_path / "assets" / "minecraft" / "optifine" / "cit"
    items = []
    
    if not cit_path.exists():
        return items
    
    seen_names = set()
    
    for prop_file in cit_path.rglob("*.properties"):
        if len(items) >= max_items:
            break
        
        try:
            props = parse_properties(prop_file)
            base_item = get_base_item(props)
            display_name = get_display_name(props)
            
            if not base_item or not display_name:
                continue
            
            # Skip replicas for testing
            if display_name.startswith("Replica "):
                continue
            
            # Check handler type based on base item
            is_match = False
            
            if handler_type == "bow" and base_item == "bow":
                is_match = True
            elif handler_type == "crossbow" and base_item == "crossbow":
                is_match = True
            elif handler_type == "potion" and base_item in ("potion", "splash_potion", "lingering_potion"):
                is_match = True
            elif handler_type == "armor" and props.get("type") == "armor":
                is_match = True
            elif handler_type == "set_armor":
                # Check for icons/armor subfolder structure
                if prop_file.parent.name in ("icons", "armor"):
                    is_match = True
            elif handler_type == "generic":
                # Generic is everything else
                if base_item not in ("bow", "crossbow", "potion", "splash_potion", "lingering_potion"):
                    if props.get("type") != "armor":
                        is_match = True
            
            if is_match and display_name not in seen_names:
                seen_names.add(display_name)
                items.append({
                    "base_item": base_item,
                    "display_name": display_name,
                    "folder": str(prop_file.parent.relative_to(cit_path))
                })
        except Exception as e:
            continue
    
    return items


def generate_give_command(items: list[dict], slot_start: int = 0) -> str:
    """Generate a give command for a chest containing items."""
    if not items:
        return ""
    
    item_strings = []
    for i, item in enumerate(items):
        slot = slot_start + i
        base = item["base_item"]
        # Don't escape single quotes - Minecraft handles them fine
        name = item["display_name"].replace('"', '\\"')
        
        # Create the item NBT - only plain.display.Name is needed for CIT matching
        item_nbt = (
            f'{{Slot:{slot}b,id:"{base}",Count:1b,tag:{{'
            f'plain:{{display:{{Name:"{name}"}}}}'
            f'}}}}'
        )
        item_strings.append(item_nbt)
    
    return f'give @s chest{{BlockEntityTag:{{Items:[{",".join(item_strings)}]}}}}'


def main():
    # Settings
    root = Path(__file__).parent / "output"
    pack_name = "rp-renamer-test-items"
    namespace = "rptest"
    
    # Input pack path
    input_pack = Path(__file__).parent.parent / "input" / "monumenta-resourcepack"
    
    if not input_pack.exists():
        print(f"Input pack not found: {input_pack}")
        return
    
    print(f"Scanning: {input_pack}")
    
    # Handler types to test
    handler_types = [
        "bow",
        "crossbow",
        "potion",
        "armor",
        "set_armor",
        "generic"
    ]
    
    # Collect sample items
    all_items = {}
    for handler in handler_types:
        items = find_sample_items(input_pack, handler, max_items=9)
        all_items[handler] = items
        print(f"  {handler}: {len(items)} items")
    
    # Create datapack
    root.mkdir(exist_ok=True)
    fn_root = create_empty_datapack(str(root), pack_name, namespace)
    
    # Generate mcfunctions for each handler type
    for handler, items in all_items.items():
        fn_path = os.path.join(fn_root, f"get_{handler}.mcfunction")
        
        with open(fn_path, "w") as f:
            f.write(f"# Get test items for {handler} handler\n")
            f.write(f"# {len(items)} items\n\n")
            
            if items:
                cmd = generate_give_command(items)
                f.write(cmd + "\n")
            else:
                f.write("tellraw @s {\"text\":\"No items found for this handler\",\"color\":\"red\"}\n")
        
        print(f"  Created: {handler}.mcfunction")
    
    # Create a master function to get all
    with open(os.path.join(fn_root, "get_all.mcfunction"), "w") as f:
        f.write("# Get all test items (one chest per handler type)\n\n")
        for handler in handler_types:
            f.write(f"function {namespace}:get_{handler}\n")
    
    # Create an info function
    with open(os.path.join(fn_root, "info.mcfunction"), "w") as f:
        f.write("# Display available test item functions\n")
        f.write('tellraw @s {"text":"=== RP Renamer Test Items ===","color":"gold"}\n')
        f.write(f'tellraw @s {{"text":"/{namespace}:get_all - Get all test chests","color":"yellow"}}\n')
        for handler in handler_types:
            count = len(all_items.get(handler, []))
            f.write(f'tellraw @s {{"text":"/{namespace}:get_{handler} - {count} items","color":"gray"}}\n')
    
    print(f"\nDatapack created at: {root / pack_name}")
    print(f"\nIn-game usage:")
    print(f"  /function {namespace}:info")
    print(f"  /function {namespace}:get_all")


if __name__ == "__main__":
    main()
