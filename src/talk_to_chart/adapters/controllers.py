from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..domain.entities import Resident, SearchResults, NoteType
from ..use_cases.interfaces import (
    SearchClinicalNotesUseCase, 
    GetResidentsUseCase, 
    GetResidentUseCase
)


class TalkToChartController:
    """Main controller for the Talk to Chart application."""
    
    def __init__(
        self,
        search_use_case: SearchClinicalNotesUseCase,
        get_residents_use_case: GetResidentsUseCase,
        get_resident_use_case: GetResidentUseCase,
        presenter: "TalkToChartPresenter"
    ) -> None:
        self._search_use_case = search_use_case
        self._get_residents_use_case = get_residents_use_case
        self._get_resident_use_case = get_resident_use_case
        self._presenter = presenter
    
    def get_residents(self) -> List[Resident]:
        """Get all available residents."""
        return self._get_residents_use_case.execute()
    
    def search_clinical_notes(self, resident_id: str, query: str) -> SearchResults:
        """Search clinical notes for a resident."""
        # Execute search
        results = self._search_use_case.execute(resident_id, query)
        
        # Get resident info to complete the results
        resident = self._get_resident_use_case.execute(resident_id)
        
        # Update results with resident info
        return SearchResults(
            query=results.query,
            resident=resident,
            results=results.results,
            summary=results.summary
        )
    
    def display_residents(self, residents: List[Resident]) -> None:
        """Display available residents."""
        self._presenter.display_residents(residents)
    
    def display_search_results(self, results: SearchResults) -> None:
        """Display search results."""
        self._presenter.display_search_results(results)


class TalkToChartPresenter:
    """Presenter for formatting and displaying application output."""
    
    def __init__(self) -> None:
        self.console = Console()
    
    def display_welcome(self) -> None:
        """Display welcome message."""
        welcome_text = """
[bold blue]🏥 Talk to the Chart[/bold blue]
[dim]AI-powered clinical documentation search for MDS coordinators[/dim]

This tool helps you find specific clinical evidence from resident charts using natural language queries.
        """
        self.console.print(Panel(welcome_text.strip(), title="Welcome", border_style="blue"))
    
    def display_residents(self, residents: List[Resident]) -> None:
        """Display available residents in a formatted table."""
        if not residents:
            self.console.print("[red]No residents found.[/red]")
            return
        
        table = Table(title="Available Residents", show_header=True, header_style="bold blue")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Room", justify="center")
        table.add_column("Admission Date", justify="center")
        
        for resident in residents:
            table.add_row(
                resident.id,
                resident.name,
                resident.room_number,
                resident.admission_date.strftime("%m/%d/%Y")
            )
        
        self.console.print(table)
    
    def display_search_results(self, results: SearchResults) -> None:
        """Display search results in a formatted, easy-to-scan layout."""
        if not results.results:
            self.console.print(f"\n[yellow]No results found for: '{results.query}'[/yellow]")
            return
        
        # Display header
        self.console.print(f"\n[bold]Query:[/bold] {results.query}")
        if results.resident:
            self.console.print(f"[bold]Resident:[/bold] {results.resident}")
        
        # Display summary
        self.console.print(f"\n[green]{results.summary}[/green]\n")
        
        # Display each result
        for i, result in enumerate(results.results, 1):
            self._display_single_result(i, result)
        
        # Display filter options
        self._display_filter_options(results)
    
    def _display_single_result(self, index: int, result) -> None:
        """Display a single search result."""
        # Create the quote panel
        quote_text = Text(result.quoted_snippet)
        quote_text.stylize("italic")
        
        # Source information
        source_info = result.source_note.source_description
        
        # Action buttons (simulated)
        actions = "[dim][Copy Text] [View Full Note][/dim]"
        
        # Combine all elements
        content = f"{quote_text}\n\n{source_info}\n{actions}"
        
        # Create panel with numbered title
        panel_title = f"Result {index}"
        color = self._get_note_type_color(result.source_note.note_type)
        
        self.console.print(Panel(
            content,
            title=panel_title,
            border_style=color,
            padding=(0, 1)
        ))
        self.console.print()  # Add spacing
    
    def _get_note_type_color(self, note_type: NoteType) -> str:
        """Get color scheme for different note types."""
        color_map = {
            NoteType.NURSING: "green",
            NoteType.THERAPY: "blue", 
            NoteType.CNA: "yellow",
            NoteType.SOCIAL_WORK: "purple",
            NoteType.PHYSICIAN: "red"
        }
        return color_map.get(note_type, "white")
    
    def _display_filter_options(self, results: SearchResults) -> None:
        """Display available filter options."""
        note_types = set(result.source_note.note_type for result in results.results)
        
        if len(note_types) > 1:
            filter_chips = " ".join([
                f"[dim][[/dim][blue]{nt.value}[/blue][dim]][/dim]" 
                for nt in sorted(note_types, key=lambda x: x.value)
            ])
            self.console.print(f"[dim]Filter by:[/dim] [blue][All][/blue] {filter_chips}")
    
    def display_error(self, message: str) -> None:
        """Display error message."""
        self.console.print(f"[red]Error: {message}[/red]")
    
    def display_info(self, message: str) -> None:
        """Display info message."""
        self.console.print(f"[blue]ℹ {message}[/blue]")
    
    def prompt_resident_selection(self) -> str:
        """Prompt user to select a resident."""
        return self.console.input("\n[bold]Enter Resident ID:[/bold] ")
    
    def prompt_query(self, resident_name: str) -> str:
        """Prompt user for their query."""
        prompt = f"\n[bold]Ask a question about {resident_name}'s chart:[/bold] "
        return self.console.input(prompt)
    
    def confirm_continue(self) -> bool:
        """Ask user if they want to continue."""
        response = self.console.input("\n[dim]Continue? (y/n):[/dim] ").lower()
        return response in ['y', 'yes', '']