"""Command-line interface for the Monumenta Resource Pack Renamer."""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Iterator

from .core.operations import FileOperation, AnalysisResult, OperationType
from .core.registry import HandlerRegistry

# Import handlers to trigger registration
from . import handlers  # noqa: F401

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s' if not verbose else '%(levelname)s [%(name)s]: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def copy_source_models(input_path: Path, output_path: Path) -> int:
    """
    Copy the source_models folder from input to output.
    
    This ensures all shared models are available in the output pack.
    
    Args:
        input_path: Path to input resource pack
        output_path: Path for output
        
    Returns:
        Number of files copied
    """
    source_models_src = input_path / "assets" / "minecraft" / "optifine" / "cit" / "source_models"
    source_models_dst = output_path / "assets" / "minecraft" / "optifine" / "cit" / "source_models"
    
    if not source_models_src.exists():
        logger.warning("source_models folder not found in input pack")
        return 0
    
    # Copy the entire folder
    if source_models_dst.exists():
        shutil.rmtree(source_models_dst)
    
    shutil.copytree(source_models_src, source_models_dst)
    
    # Count files copied
    count = sum(1 for _ in source_models_dst.rglob("*") if _.is_file())
    logger.info(f"Copied {count} files from source_models")
    
    return count


def find_item_folders(cit_path: Path) -> Iterator[Path]:
    """
    Find all potential item folders in the CIT directory.
    
    An item folder is one that:
    - Contains .properties files directly, OR
    - Has icons/ and armor/ subfolders (set armor)
    
    Args:
        cit_path: Path to the optifine/cit directory
        
    Yields:
        Paths to item folders
    """
    seen_folders = set()
    
    # Find folders with .properties files
    for path in cit_path.rglob("*.properties"):
        folder = path.parent
        
        # For properties in icons/ or armor/ subfolder, yield the parent
        if folder.name in ('icons', 'armor'):
            parent = folder.parent
            if parent not in seen_folders:
                seen_folders.add(parent)
                yield parent
        elif folder not in seen_folders:
            seen_folders.add(folder)
            yield folder


def analyze_pack(
    input_path: Path,
    output_path: Path,
    handler_filter: str | None = None
) -> list[AnalysisResult]:
    """
    Analyze the resource pack and collect all operations needed.
    
    Args:
        input_path: Path to input resource pack
        output_path: Path for output
        handler_filter: Optional handler name to filter by
        
    Returns:
        List of AnalysisResult objects
    """
    cit_path = input_path / "assets" / "minecraft" / "optifine" / "cit"
    
    if not cit_path.exists():
        logger.error(f"CIT path not found: {cit_path}")
        return []
    
    results = []
    seen_folders = set()
    
    for folder in find_item_folders(cit_path):
        # Skip duplicates (folder may have multiple .properties files)
        if folder in seen_folders:
            continue
        seen_folders.add(folder)
        
        # Get appropriate handler
        handler = HandlerRegistry.get_handler(folder, output_path, input_path)
        
        if handler is None:
            logger.debug(f"No handler for: {folder.relative_to(input_path)}")
            continue
        
        # Filter by handler name if specified
        if handler_filter and handler.name != handler_filter:
            continue
        
        # Analyze the folder
        result = handler.analyze()
        results.append(result)
        
        if result.needs_changes:
            logger.debug(f"[{handler.name}] {folder.relative_to(input_path)}: {len(result.operations)} operations")
    
    return results


def execute_operations(results: list[AnalysisResult], dry_run: bool = False) -> tuple[int, int]:
    """
    Execute all operations from analysis results.
    
    Args:
        results: List of AnalysisResult objects
        dry_run: If True, only print what would be done
        
    Returns:
        Tuple of (success_count, error_count)
    """
    success_count = 0
    error_count = 0
    
    for result in results:
        if result.skipped or not result.operations:
            continue
        
        for op in result.operations:
            try:
                if dry_run:
                    print(f"  {op}")
                else:
                    execute_single_operation(op)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed: {op} - {e}")
                error_count += 1
    
    return success_count, error_count


def execute_single_operation(op: FileOperation) -> None:
    """Execute a single file operation."""
    # Ensure destination directory exists
    op.destination.parent.mkdir(parents=True, exist_ok=True)
    
    match op.operation_type:
        case OperationType.COPY:
            if op.source:
                shutil.copy2(op.source, op.destination)
        case OperationType.RENAME:
            if op.source:
                shutil.move(str(op.source), str(op.destination))
        case OperationType.WRITE:
            if op.content is not None:
                op.destination.write_text(op.content, encoding='utf-8')
        case OperationType.DELETE:
            if op.destination.exists():
                op.destination.unlink()


def print_summary(results: list[AnalysisResult]) -> None:
    """Print a summary of the analysis results."""
    total_folders = len(results)
    folders_with_changes = sum(1 for r in results if r.needs_changes)
    total_operations = sum(len(r.operations) for r in results)
    skipped = sum(1 for r in results if r.skipped)
    with_issues = sum(1 for r in results if r.has_issues)
    
    # Count by handler
    by_handler: dict[str, int] = {}
    for r in results:
        by_handler[r.handler_name] = by_handler.get(r.handler_name, 0) + 1
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total folders analyzed: {total_folders}")
    print(f"Folders needing changes: {folders_with_changes}")
    print(f"Total operations: {total_operations}")
    print(f"Skipped: {skipped}")
    print(f"With issues: {with_issues}")
    print()
    print("By handler:")
    for handler, count in sorted(by_handler.items()):
        print(f"  {handler}: {count}")
    print("=" * 60)


def print_preview(results: list[AnalysisResult], verbose: bool = False) -> None:
    """Print a preview of what would be changed."""
    print("\n" + "=" * 60)
    print("PREVIEW MODE - No changes will be made")
    print("=" * 60 + "\n")
    
    for result in results:
        if not result.needs_changes:
            continue
        
        rel_path = result.folder_path.relative_to(result.folder_path.parents[4])  # Get relative from cit
        print(f"\n[{result.handler_name}] {rel_path}")
        print(f"  Item: {result.item_name} -> {result.reduced_name}")
        
        if result.is_replica:
            print("  (Replica)")
        
        if verbose:
            for op in result.operations:
                print(f"    {op}")
        else:
            print(f"  Operations: {len(result.operations)}")
        
        if result.issues:
            print("  Issues:")
            for issue in result.issues:
                print(f"    ⚠ {issue}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monumenta Resource Pack Renamer - Standardize item naming conventions"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to input resource pack"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Path for output resource pack"
    )
    
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Preview mode - show what would be changed without doing it"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--filter", "-f",
        type=str,
        default=None,
        help="Filter by handler name (e.g., 'bow', 'crossbow', 'generic')"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate input path
    if not args.input.exists():
        logger.error(f"Input path does not exist: {args.input}")
        return 1
    
    # Check for CIT folder
    cit_path = args.input / "assets" / "minecraft" / "optifine" / "cit"
    if not cit_path.exists():
        logger.error(f"Not a valid resource pack - missing: {cit_path}")
        return 1
    
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Mode: {'Preview' if args.preview else 'Execute'}")
    if args.filter:
        print(f"Filter: {args.filter}")
    
    # Analyze the pack
    print("\nAnalyzing resource pack...")
    results = analyze_pack(args.input, args.output, args.filter)
    
    if not results:
        print("No items found to process.")
        return 0
    
    # Print summary
    print_summary(results)
    
    if args.preview:
        # Preview mode
        print_preview(results, args.verbose)
    else:
        # Execute mode
        # First copy source_models folder
        print("\nCopying source_models...")
        models_copied = copy_source_models(args.input, args.output)
        print(f"Copied {models_copied} model files")
        
        print("\nExecuting operations...")
        success, errors = execute_operations(results, dry_run=False)
        print(f"\nCompleted: {success} operations, {errors} errors")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
