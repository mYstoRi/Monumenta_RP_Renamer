"""File operation definitions for the resource pack renamer."""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class OperationType(Enum):
    """Types of file operations that can be performed."""
    COPY = auto()       # Copy file from source to destination
    RENAME = auto()     # Rename/move file (within output)
    WRITE = auto()      # Write new content to file
    DELETE = auto()     # Delete a file (rarely used)


@dataclass
class FileOperation:
    """
    Represents a single file operation to be performed.
    
    This is used for preview mode - we collect all operations first,
    then either display them (preview) or execute them.
    
    Attributes:
        operation_type: The type of operation (copy, rename, write, delete)
        source: Source path (for copy/rename operations)
        destination: Destination path
        content: Content to write (for write operations)
        description: Human-readable description of what this operation does
    """
    operation_type: OperationType
    destination: Path
    source: Path | None = None
    content: str | None = None
    description: str = ""
    
    def __post_init__(self):
        """Validate the operation."""
        if self.operation_type == OperationType.COPY and self.source is None:
            raise ValueError("COPY operation requires a source path")
        if self.operation_type == OperationType.RENAME and self.source is None:
            raise ValueError("RENAME operation requires a source path")
        if self.operation_type == OperationType.WRITE and self.content is None:
            raise ValueError("WRITE operation requires content")
    
    def __str__(self) -> str:
        """Human-readable representation of the operation."""
        if self.description:
            return self.description
            
        match self.operation_type:
            case OperationType.COPY:
                return f"COPY: {self.source} -> {self.destination}"
            case OperationType.RENAME:
                return f"RENAME: {self.source} -> {self.destination}"
            case OperationType.WRITE:
                preview = self.content[:50] + "..." if self.content and len(self.content) > 50 else self.content
                return f"WRITE: {self.destination} ({preview})"
            case OperationType.DELETE:
                return f"DELETE: {self.destination}"
            case _:
                return f"{self.operation_type}: {self.destination}"


@dataclass
class AnalysisResult:
    """
    Result of analyzing an item folder.
    
    Attributes:
        folder_path: Path to the analyzed folder
        handler_name: Name of the handler that processed this folder
        item_name: Display name of the item
        reduced_name: File-system compatible name
        is_replica: Whether this is a replica item
        operations: List of file operations to perform
        issues: List of issues/warnings found during analysis
        skipped: Whether this folder was skipped (and why)
    """
    folder_path: Path
    handler_name: str
    item_name: str = ""
    reduced_name: str = ""
    is_replica: bool = False
    operations: list[FileOperation] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""
    
    @property
    def needs_changes(self) -> bool:
        """Check if any changes are needed."""
        return len(self.operations) > 0
    
    @property  
    def has_issues(self) -> bool:
        """Check if there are any issues."""
        return len(self.issues) > 0
