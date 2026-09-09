from pathlib import Path
from uuid import UUID

from app.ingestion.contracts import ParsedDocument

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def parse_raw_text(
    content: str,
    filename: str,
    source_id: UUID,
    user_id: UUID,
) -> ParsedDocument:
    """
    Normalizes raw text content and returns a ParsedDocument contract.
    """
    # Normalize Windows CRLF to standard LF
    normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")

    if not normalized_content.strip():
        raise ValueError("Source content is empty or contains only whitespace.")

    extension = Path(filename).suffix.lower()

    return ParsedDocument(
        source_id=source_id,
        user_id=user_id,
        content=normalized_content,
        metadata={
            "filename": filename,
            "extension": extension,
            "character_count": len(normalized_content),
            "line_count": len(normalized_content.splitlines()),
        },
    )


def parse_text_file(
    file_path: str | Path,
    source_id: UUID,
    user_id: UUID,
) -> ParsedDocument:
    """
    Reads a TXT or Markdown file from disk and parses it into a ParsedDocument.
    """
    path = Path(file_path)

    # 1. Existence & File Type Check
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is a directory, not a file: {path}")

    # 2. Extension Check
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported text file type: '{path.suffix}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # 3. Read with UTF-8-SIG (handles BOM) and replacement fallback
    try:
        content = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        raise ValueError(f"Failed to read file {path.name}: {exc}") from exc

    return parse_raw_text(
        content=content,
        filename=path.name,
        source_id=source_id,
        user_id=user_id,
    )