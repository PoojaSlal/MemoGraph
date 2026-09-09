from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class ParsedDocument:
    """Normalized document produced by a parser."""

    source_id: UUID
    user_id: UUID
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractedMemory:
    """Semantic memory extracted from document content."""

    source_id: UUID
    user_id: UUID
    summary: str
    memory_type: str
    memory_id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class DocumentChunk:
    """Retrieval-level text segment produced by the chunker."""

    source_id: UUID
    user_id: UUID
    content: str
    chunk_index: int
    token_count: int
    memory_id: UUID | None = None
    chunk_id: UUID = field(default_factory=uuid4)
    embedding: list[float] | None = None
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_version: str = "v1"


@dataclass(slots=True)
class ExtractedEntity:
    """Canonical entity extracted from a memory."""

    user_id: UUID
    name: str
    entity_type: str
    entity_id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        # Enforce canonical lowercase string matching DB constraint
        self.name = self.name.strip().lower()


@dataclass(slots=True)
class ExtractedRelationship:
    """Directed relationship between two entities."""

    user_id: UUID
    source_id: UUID
    memory_id: UUID
    subject_entity_id: UUID
    predicate: str
    object_entity_id: UUID
    weight: float = 1.0
    relationship_id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        # Enforce uppercase predicate matching Memgraph controlled vocabulary
        self.predicate = self.predicate.strip().upper()


@dataclass(slots=True)
class IngestionBatch:
    """Container holding all artifacts extracted from a source document."""

    source_id: UUID
    user_id: UUID
    memories: list[ExtractedMemory] = field(default_factory=list)
    chunks: list[DocumentChunk] = field(default_factory=list)
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)