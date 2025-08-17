from datetime import datetime, timedelta
from typing import List
import json

from ..domain.entities import Resident, ClinicalNote, Author, NoteType
from ..use_cases.interfaces import ResidentRepository, ClinicalNoteRepository


class MockResidentRepository(ResidentRepository):
    """Mock implementation of resident repository with sample data."""
    
    def __init__(self) -> None:
        self._residents = self._create_mock_residents()
    
    def find_all(self) -> List[Resident]:
        """Get all residents."""
        return list(self._residents.values())
    
    def find_by_id(self, resident_id: str) -> Resident | None:
        """Find resident by ID."""
        return self._residents.get(resident_id)
    
    def _create_mock_residents(self) -> dict[str, Resident]:
        """Create mock resident data."""
        residents = {}
        
        # Sample residents for demo
        resident_data = [
            {
                "id": "RES001", 
                "name": "Mary Johnson", 
                "room": "101A",
                "admission_date": datetime.now() - timedelta(days=30)
            },
            {
                "id": "RES002", 
                "name": "Robert Williams", 
                "room": "102B", 
                "admission_date": datetime.now() - timedelta(days=45)
            },
            {
                "id": "RES003", 
                "name": "Dorothy Smith", 
                "room": "103A",
                "admission_date": datetime.now() - timedelta(days=20)
            }
        ]
        
        for data in resident_data:
            resident = Resident(
                id=data["id"],
                name=data["name"],
                room_number=data["room"],
                admission_date=data["admission_date"]
            )
            residents[resident.id] = resident
        
        return residents


class MockClinicalNoteRepository(ClinicalNoteRepository):
    """Mock implementation of clinical note repository with sample data."""
    
    def __init__(self) -> None:
        self._notes = self._create_mock_notes()
    
    def find_by_resident_id(
        self, 
        resident_id: str, 
        since_date: datetime | None = None
    ) -> List[ClinicalNote]:
        """Find all notes for a resident, optionally filtered by date."""
        resident_notes = [
            note for note in self._notes 
            if note.resident_id == resident_id
        ]
        
        if since_date:
            resident_notes = [
                note for note in resident_notes
                if note.created_at >= since_date
            ]
        
        # Sort by date (most recent first)
        resident_notes.sort(key=lambda x: x.created_at, reverse=True)
        return resident_notes
    
    def _create_mock_notes(self) -> List[ClinicalNote]:
        """Create comprehensive mock clinical notes for demo scenarios."""
        notes = []
        base_date = datetime.now()
        
        # Mary Johnson (RES001) - Depression and mobility issues
        mary_notes = [
            {
                "content": "Resident stated 'I just don't feel like getting out of bed anymore.' Tearful during conversation. Declined to participate in activities. Appetite appears decreased.",
                "note_type": NoteType.NURSING,
                "author": Author("A. Smith", "RN"),
                "days_ago": 3
            },
            {
                "content": "Refused to participate in morning group activities, stating 'what's the point?' Remained in room most of the day. Observed staring out window for extended periods.",
                "note_type": NoteType.CNA,
                "author": Author("D. Jones", "CNA"),
                "days_ago": 5
            },
            {
                "content": "Family reports resident seems 'more withdrawn and sad than usual' since last week. Daughter concerned about mother's mood changes.",
                "note_type": NoteType.SOCIAL_WORK,
                "author": Author("M. Chen", "LSW"),
                "days_ago": 7
            },
            {
                "content": "Transfer from bed to wheelchair required assistance of 2 staff members due to weakness and unsteady gait. Resident cooperative but needed significant support.",
                "note_type": NoteType.NURSING,
                "author": Author("B. Rodriguez", "RN"),
                "days_ago": 2
            },
            {
                "content": "Ambulation assessment: Resident able to walk 10 feet with walker and standby assistance. Gait unsteady, requires verbal cues for safety.",
                "note_type": NoteType.THERAPY,
                "author": Author("J. Thompson", "PT"),
                "days_ago": 4
            }
        ]
        
        for note_data in mary_notes:
            notes.append(ClinicalNote(
                id=f"NOTE_{len(notes)+1:03d}",
                resident_id="RES001",
                content=note_data["content"],
                note_type=note_data["note_type"],
                author=note_data["author"],
                created_at=base_date - timedelta(days=note_data["days_ago"])
            ))
        
        # Robert Williams (RES002) - Fall risk and cognitive issues
        robert_notes = [
            {
                "content": "Resident found on floor next to bed at 0230. No apparent injury. States he was trying to get to bathroom independently. Vitals stable.",
                "note_type": NoteType.NURSING,
                "author": Author("C. Davis", "RN"),
                "days_ago": 1
            },
            {
                "content": "Confusion noted during medication administration. Resident asked same question multiple times and did not recognize evening CNA.",
                "note_type": NoteType.CNA,
                "author": Author("L. Wilson", "CNA"),
                "days_ago": 2
            },
            {
                "content": "Cognitive assessment shows decline in short-term memory. Mini-Mental State Exam score decreased from 24 to 19 over past month.",
                "note_type": NoteType.NURSING,
                "author": Author("A. Smith", "RN"),
                "days_ago": 6
            },
            {
                "content": "Fall risk assessment completed. Score indicates high risk due to impaired judgment and history of falls. Bed alarm activated.",
                "note_type": NoteType.NURSING,
                "author": Author("E. Martinez", "RN"),
                "days_ago": 1
            }
        ]
        
        for note_data in robert_notes:
            notes.append(ClinicalNote(
                id=f"NOTE_{len(notes)+1:03d}",
                resident_id="RES002",
                content=note_data["content"],
                note_type=note_data["note_type"],
                author=note_data["author"],
                created_at=base_date - timedelta(days=note_data["days_ago"])
            ))
        
        # Dorothy Smith (RES003) - Pain management and behavioral issues
        dorothy_notes = [
            {
                "content": "Resident reports pain level 8/10 in lower back. Became agitated when asked to participate in physical therapy. Requested additional pain medication.",
                "note_type": NoteType.NURSING,
                "author": Author("F. Brown", "RN"),
                "days_ago": 1
            },
            {
                "content": "Exhibited aggressive behavior during personal care. Verbally abusive to staff, stating 'leave me alone' repeatedly. Required de-escalation techniques.",
                "note_type": NoteType.CNA,
                "author": Author("G. Taylor", "CNA"),
                "days_ago": 3
            },
            {
                "content": "Pain management consultation requested. Current regimen appears inadequate for controlling chronic back pain. Considering adjustment to medication schedule.",
                "note_type": NoteType.PHYSICIAN,
                "author": Author("Dr. H. Patel", "MD"),
                "days_ago": 4
            },
            {
                "content": "Behavioral triggers appear related to pain episodes. Implemented comfort measures and scheduled pain assessment every 4 hours.",
                "note_type": NoteType.NURSING,
                "author": Author("A. Smith", "RN"),
                "days_ago": 2
            }
        ]
        
        for note_data in dorothy_notes:
            notes.append(ClinicalNote(
                id=f"NOTE_{len(notes)+1:03d}",
                resident_id="RES003",
                content=note_data["content"],
                note_type=note_data["note_type"],
                author=note_data["author"],
                created_at=base_date - timedelta(days=note_data["days_ago"])
            ))
        
        return notes