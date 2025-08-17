"""
Example tests demonstrating how Clean Architecture enables easy testing.
Business logic can be tested without external dependencies.
"""
import pytest
from datetime import datetime, timedelta
from typing import List

from talk_to_chart.domain.entities import (
    ClinicalNote, Author, NoteType, QueryResult, Resident
)
from talk_to_chart.use_cases.interfaces import (
    ClinicalNoteRepository, AIQueryProcessor, SearchClinicalNotesUseCase
)


class MockNoteRepository(ClinicalNoteRepository):
    """Mock repository for testing."""
    
    def __init__(self, notes: List[ClinicalNote]) -> None:
        self._notes = notes
    
    def find_by_resident_id(
        self, 
        resident_id: str, 
        since_date: datetime | None = None
    ) -> List[ClinicalNote]:
        filtered_notes = [n for n in self._notes if n.resident_id == resident_id]
        if since_date:
            filtered_notes = [n for n in filtered_notes if n.created_at >= since_date]
        return filtered_notes


class MockAIProcessor(AIQueryProcessor):
    """Mock AI processor for testing."""
    
    def __init__(self, mock_results: List[QueryResult]) -> None:
        self._mock_results = mock_results
    
    def process_query(
        self, 
        query: str, 
        clinical_notes: List[ClinicalNote]
    ) -> List[QueryResult]:
        return self._mock_results
    
    def generate_summary(self, query: str, results: List[QueryResult]) -> str:
        return f"Found {len(results)} results for test query"


@pytest.fixture
def sample_notes() -> List[ClinicalNote]:
    """Create sample clinical notes for testing."""
    base_date = datetime.now()
    author = Author("Test Nurse", "RN")
    
    return [
        ClinicalNote(
            id="NOTE_001",
            resident_id="RES001", 
            content="Resident appears sad and withdrawn",
            note_type=NoteType.NURSING,
            author=author,
            created_at=base_date - timedelta(days=2)
        ),
        ClinicalNote(
            id="NOTE_002",
            resident_id="RES001",
            content="Required two-person assist for transfer",
            note_type=NoteType.NURSING, 
            author=author,
            created_at=base_date - timedelta(days=1)
        ),
        ClinicalNote(
            id="NOTE_003",
            resident_id="RES002",
            content="Different resident's note",
            note_type=NoteType.NURSING,
            author=author, 
            created_at=base_date - timedelta(days=1)
        )
    ]


@pytest.fixture
def search_use_case(sample_notes: List[ClinicalNote]) -> SearchClinicalNotesUseCase:
    """Create search use case with mocked dependencies."""
    mock_results = [
        QueryResult(
            snippet="Resident appears sad and withdrawn",
            source_note=sample_notes[0],
            relevance_score=0.9
        )
    ]
    
    note_repository = MockNoteRepository(sample_notes)
    ai_processor = MockAIProcessor(mock_results)
    
    return SearchClinicalNotesUseCase(note_repository, ai_processor)


def test_search_filters_by_resident_id(
    search_use_case: SearchClinicalNotesUseCase,
    sample_notes: List[ClinicalNote]
) -> None:
    """Test that search only returns notes for the specified resident."""
    
    # Execute search for RES001
    results = search_use_case.execute("RES001", "test query")
    
    # Verify results contain only RES001 notes
    assert results.count == 1
    assert results.results[0].snippet == "Resident appears sad and withdrawn"


def test_search_filters_by_date_range(
    sample_notes: List[ClinicalNote]
) -> None:
    """Test that repository correctly filters by date range."""
    repository = MockNoteRepository(sample_notes)
    
    # Search with date filter
    cutoff_date = datetime.now() - timedelta(days=1, hours=12)
    recent_notes = repository.find_by_resident_id("RES001", cutoff_date)
    
    # Should only return the most recent note
    assert len(recent_notes) == 1
    assert recent_notes[0].id == "NOTE_002"


def test_search_handles_no_results(
    sample_notes: List[ClinicalNote]
) -> None:
    """Test search behavior when no notes are found."""
    note_repository = MockNoteRepository([])  # Empty repository
    ai_processor = MockAIProcessor([])  # No results
    
    use_case = SearchClinicalNotesUseCase(note_repository, ai_processor)
    results = use_case.execute("NONEXISTENT", "test query")
    
    assert results.count == 0
    assert "No clinical notes found" in results.summary


def test_query_result_formatting() -> None:
    """Test QueryResult value object formatting."""
    author = Author("Test Author", "RN")
    note = ClinicalNote(
        id="TEST_001",
        resident_id="RES001",
        content="Test content",
        note_type=NoteType.NURSING,
        author=author,
        created_at=datetime(2025, 8, 15, 14, 30)
    )
    
    result = QueryResult(
        snippet="Test snippet",
        source_note=note,
        relevance_score=0.8
    )
    
    assert result.quoted_snippet == '"Test snippet"'
    assert "Test Author, RN" in result.source_note.source_description
    assert "08/15/2025, 14:30" in result.source_note.source_description


def test_resident_string_representation() -> None:
    """Test Resident entity string formatting."""
    resident = Resident(
        id="RES001",
        name="Test Patient", 
        room_number="101A",
        admission_date=datetime.now()
    )
    
    assert str(resident) == "Test Patient (Room 101A)"


if __name__ == "__main__":
    pytest.main([__file__])