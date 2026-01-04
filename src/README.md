# Monumenta RP Renamer - Refactored

A tool for standardizing file naming conventions in the Monumenta Minecraft server resource pack.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Preview Mode (Recommended First)

See what would be changed without actually modifying anything:

```bash
python -m src.cli --input ./input/monumenta-resourcepack --output ./output --preview
```

### Execute Rename

```bash
python -m src.cli --input ./input/monumenta-resourcepack --output ./output
```

### Verbose Output

```bash
python -m src.cli --input ./input/monumenta-resourcepack --output ./output -v
```

## Project Structure

```
src/
├── cli.py              # Command-line interface
├── core/
│   ├── utils.py        # Utility functions (reduce, parse_properties)
│   ├── operations.py   # FileOperation dataclass
│   ├── base_handler.py # Abstract handler base class
│   └── registry.py     # Handler auto-registration
└── handlers/
    ├── generic.py      # Simple single-texture items
    ├── bow.py          # Bows with pulling animations
    ├── crossbow.py     # Crossbows
    ├── armor.py        # Single armor pieces
    ├── set_armor.py    # Armor sets
    └── potion.py       # Potions with JSON models
```
