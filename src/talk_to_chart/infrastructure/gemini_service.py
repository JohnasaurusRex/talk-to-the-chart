import re
from typing import List
import google.generativeai as genai

from ..domain.entities import ClinicalNote, QueryResult
from ..use_cases.interfaces import AIQueryProcessor


class GeminiQueryProcessor(AIQueryProcessor):
    """Gemini-powered implementation of AI query processing."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        """Initialize Gemini AI service."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def process_query(
        self, 
        query: str, 
        clinical_notes: List[ClinicalNote]
    ) -> List[QueryResult]:
        """Process natural language query against clinical notes."""
        # Prepare context with all clinical notes
        context = self._prepare_context(clinical_notes)
        
        # Create prompt for finding relevant snippets
        prompt = self._create_search_prompt(query, context)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_search_response(response.text, clinical_notes)
        except Exception as e:
            print(f"Error processing query with Gemini: {e}")
            return []
    
    def generate_summary(self, query: str, results: List[QueryResult]) -> str:
        """Generate a summary of the search results."""
        if not results:
            return "No relevant clinical evidence found for your query."
        
        count = len(results)
        evidence_type = self._extract_evidence_type(query)
        
        if evidence_type:
            return f"I found {count} notes that may indicate {evidence_type}:"
        else:
            return f"I found {count} relevant notes for your query:"
    
    def _prepare_context(self, clinical_notes: List[ClinicalNote]) -> str:
        """Prepare clinical notes as context for the AI model."""
        context_parts = []
        for i, note in enumerate(clinical_notes):
            context_parts.append(
                f"NOTE_{i}:\n"
                f"Type: {note.note_type.value}\n"
                f"Author: {note.author}\n"
                f"Date: {note.created_at.strftime('%m/%d/%Y %H:%M')}\n"
                f"Content: {note.content}\n"
                f"---"
            )
        return "\n".join(context_parts)
    
    def _create_search_prompt(self, query: str, context: str) -> str:
        """Create a prompt for finding relevant clinical evidence."""
        return f"""
You are an expert MDS coordinator assistant. Your task is to find relevant clinical evidence from nursing home documentation.

QUERY: {query}

CLINICAL NOTES:
{context}

Instructions:
1. Find direct quotes from the clinical notes that are relevant to the query
2. Return ONLY the most relevant sentences or phrases (not entire paragraphs)
3. Include the NOTE_X identifier for each relevant snippet
4. Format your response as:
   SNIPPET: "exact quote from note"
   NOTE_ID: NOTE_X
   RELEVANCE: score from 1-10
   
5. Return up to 5 most relevant snippets
6. Only include snippets that directly answer or relate to the query

Response format:
SNIPPET: "quote here"
NOTE_ID: NOTE_0
RELEVANCE: 8

SNIPPET: "another quote"
NOTE_ID: NOTE_2  
RELEVANCE: 7
"""

    def _parse_search_response(
        self, 
        response_text: str, 
        clinical_notes: List[ClinicalNote]
    ) -> List[QueryResult]:
        """Parse Gemini response into QueryResult objects."""
        results = []
        
        # Split response into sections
        sections = response_text.split("SNIPPET:")
        
        for section in sections[1:]:  # Skip first empty section
            try:
                # Extract snippet text (between quotes)
                snippet_match = re.search(r'"([^"]+)"', section)
                if not snippet_match:
                    continue
                snippet = snippet_match.group(1)
                
                # Extract note ID
                note_id_match = re.search(r'NOTE_ID:\s*NOTE_(\d+)', section)
                if not note_id_match:
                    continue
                note_index = int(note_id_match.group(1))
                
                # Extract relevance score
                relevance_match = re.search(r'RELEVANCE:\s*(\d+)', section)
                relevance_score = float(relevance_match.group(1)) / 10.0 if relevance_match else 0.5
                
                # Validate note index
                if note_index >= len(clinical_notes):
                    continue
                
                results.append(QueryResult(
                    snippet=snippet,
                    source_note=clinical_notes[note_index],
                    relevance_score=relevance_score
                ))
                
            except (ValueError, IndexError, AttributeError):
                continue
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def _extract_evidence_type(self, query: str) -> str | None:
        """Extract the type of evidence being searched for."""
        query_lower = query.lower()
        
        # Map common MDS-related terms
        evidence_mapping = {
            "depression": "symptoms of depression",
            "mood": "mood-related symptoms", 
            "fall": "fall risk or incidents",
            "assist": "assistance requirements",
            "transfer": "transfer assistance needs",
            "cognitive": "cognitive impairment",
            "behavior": "behavioral symptoms",
            "pain": "pain indicators",
            "medication": "medication-related issues"
        }
        
        for keyword, description in evidence_mapping.items():
            if keyword in query_lower:
                return description
        
        return None