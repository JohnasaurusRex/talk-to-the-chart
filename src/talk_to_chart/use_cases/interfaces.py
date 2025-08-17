from abc import ABC, abstractmethod
from typing import List, Protocol
from datetime import datetime, timedelta

from ..domain.entities import Resident, ClinicalNote, SearchResults, QueryResult


class ResidentRepository(Protocol):
    """Repository interface for resident data access."""
    
    def find_all(self) -> List[Resident]:
        """Get all residents."""
        pass
    
    def find_by_id(self, resident_id: str) -> Resident | None:
        """Find resident by ID."""
        pass


class ClinicalNoteRepository(Protocol):
    """Repository interface for clinical note data access."""
    
    def find_by_resident_id(
        self, 
        resident_id: str, 
        since_date: datetime | None = None
    ) -> List[ClinicalNote]:
        """Find all notes for a resident, optionally filtered by date."""
        pass


class AIQueryProcessor(Protocol):
    """Interface for AI-powered query processing."""
    
    def process_query(
        self, 
        query: str, 
        clinical_notes: List[ClinicalNote]
    ) -> List[QueryResult]:
        """Process natural language query against clinical notes."""
        pass
    
    def generate_summary(self, query: str, results: List[QueryResult]) -> str:
        """Generate a summary of the search results."""
        pass


class SearchClinicalNotesUseCase:
    """Use case for searching clinical notes using natural language."""
    
    def __init__(
        self,
        note_repository: ClinicalNoteRepository,
        ai_processor: AIQueryProcessor,
        lookback_days: int = 14
    ) -> None:
        self._note_repository = note_repository
        self._ai_processor = ai_processor
        self._lookback_days = lookback_days
    
    def execute(self, resident_id: str, query: str) -> SearchResults:
        """Execute the search use case."""
        # Calculate lookback date
        since_date = datetime.now() - timedelta(days=self._lookback_days)
        
        # Get clinical notes for the resident
        notes = self._note_repository.find_by_resident_id(resident_id, since_date)
        
        if not notes:
            return SearchResults(
                query=query,
                resident=None,  # Will need to fetch this separately
                results=[],
                summary="No clinical notes found for the specified time period."
            )
        
        # Process query with AI
        results = self._ai_processor.process_query(query, notes)
        
        # Generate summary
        summary = self._ai_processor.generate_summary(query, results)
        
        return SearchResults(
            query=query,
            resident=None,  # Will be populated by the controller
            results=results,
            summary=summary
        )


class GetResidentsUseCase:
    """Use case for retrieving all residents."""
    
    def __init__(self, resident_repository: ResidentRepository) -> None:
        self._resident_repository = resident_repository
    
    def execute(self) -> List[Resident]:
        """Get all available residents."""
        return self._resident_repository.find_all()


class GetResidentUseCase:
    """Use case for retrieving a specific resident."""
    
    def __init__(self, resident_repository: ResidentRepository) -> None:
        self._resident_repository = resident_repository
    
    def execute(self, resident_id: str) -> Resident | None:
        """Get a specific resident by ID."""
        return self._resident_repository.find_by_id(resident_id)