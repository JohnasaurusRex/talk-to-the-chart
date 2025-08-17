from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class NoteType(Enum):
    """Types of clinical notes."""
    NURSING = "Nursing"
    THERAPY = "Therapy"  
    CNA = "CNA"
    SOCIAL_WORK = "Social Work"
    PHYSICIAN = "Physician"


@dataclass(frozen=True)
class Author:
    """Value object representing a clinical note author."""
    name: str
    title: str
    
    def __str__(self) -> str:
        return f"{self.name}, {self.title}"


@dataclass(frozen=True)
class ClinicalNote:
    """Entity representing a clinical note in the patient chart."""
    id: str
    resident_id: str
    content: str
    note_type: NoteType
    author: Author
    created_at: datetime
    
    @property
    def source_description(self) -> str:
        """Get formatted source description for display."""
        date_str = self.created_at.strftime("%m/%d/%Y")
        time_str = self.created_at.strftime("%H:%M")
        return f"Source: {self.note_type.value} Note, {self.author} — {date_str}, {time_str}"


@dataclass(frozen=True)
class Resident:
    """Entity representing a nursing home resident."""
    id: str
    name: str
    room_number: str
    admission_date: datetime
    
    def __str__(self) -> str:
        return f"{self.name} (Room {self.room_number})"


@dataclass(frozen=True)
class QueryResult:
    """Value object representing a search result snippet."""
    snippet: str
    source_note: ClinicalNote
    relevance_score: float
    
    @property
    def quoted_snippet(self) -> str:
        """Get snippet wrapped in quotes."""
        return f'"{self.snippet}"'


@dataclass(frozen=True)
class SearchResults:
    """Aggregate representing the complete search results."""
    query: str
    resident: Resident
    results: List[QueryResult]
    summary: str
    
    @property
    def count(self) -> int:
        """Get number of results found."""
        return len(self.results)
    
    def filter_by_note_type(self, note_type: NoteType) -> "SearchResults":
        """Filter results by note type."""
        filtered_results = [
            result for result in self.results 
            if result.source_note.note_type == note_type
        ]
        return SearchResults(
            query=self.query,
            resident=self.resident,
            results=filtered_results,
            summary=f"Filtered results for {note_type.value}: {len(filtered_results)} notes found"
        )