import os
from typing import Optional
import typer
from dotenv import load_dotenv

from .use_cases.interfaces import (
    SearchClinicalNotesUseCase,
    GetResidentsUseCase, 
    GetResidentUseCase
)
from .infrastructure.gemini_service import GeminiQueryProcessor
from .infrastructure.repositories import MockResidentRepository, MockClinicalNoteRepository
from .adapters.controllers import TalkToChartController, TalkToChartPresenter


# Load environment variables
load_dotenv()

app = typer.Typer(help="Talk to the Chart - AI-powered clinical documentation search")


def create_app() -> TalkToChartController:
    """Create and configure the application with dependency injection."""
    
    # Get Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        typer.echo("Error: GEMINI_API_KEY environment variable not set")
        typer.echo("Please create a .env file with your Gemini API key:")
        typer.echo("GEMINI_API_KEY=your_api_key_here")
        raise typer.Exit(1)
    
    # Infrastructure layer
    resident_repository = MockResidentRepository()
    note_repository = MockClinicalNoteRepository()
    ai_processor = GeminiQueryProcessor(api_key)
    
    # Use cases layer  
    search_use_case = SearchClinicalNotesUseCase(note_repository, ai_processor)
    get_residents_use_case = GetResidentsUseCase(resident_repository)
    get_resident_use_case = GetResidentUseCase(resident_repository)
    
    # Interface adapters layer
    presenter = TalkToChartPresenter()
    controller = TalkToChartController(
        search_use_case, 
        get_residents_use_case,
        get_resident_use_case,
        presenter
    )
    
    return controller


@app.command()
def start() -> None:
    """Start the interactive Talk to Chart session."""
    try:
        controller = create_app()
        run_interactive_session(controller)
    except Exception as e:
        typer.echo(f"Application error: {e}")
        raise typer.Exit(1)


def run_interactive_session(controller: TalkToChartController) -> None:
    """Run the main interactive session."""
    presenter = controller._presenter
    
    # Welcome message
    presenter.display_welcome()
    
    while True:
        try:
            # Step 1: Show available residents
            residents = controller.get_residents()
            controller.display_residents(residents)
            
            # Step 2: Get resident selection
            resident_id = presenter.prompt_resident_selection()
            
            if not resident_id:
                presenter.display_info("Session ended.")
                break
            
            # Validate resident exists
            resident = next((r for r in residents if r.id == resident_id), None)
            if not resident:
                presenter.display_error(f"Resident ID '{resident_id}' not found.")
                continue
            
            # Step 3: Start chat session for this resident
            presenter.display_info(f"Starting chat session for {resident}")
            
            while True:
                # Get user query
                query = presenter.prompt_query(resident.name)
                
                if not query:
                    break
                
                # Process query
                presenter.display_info("Searching clinical notes...")
                results = controller.search_clinical_notes(resident_id, query)
                
                # Display results
                controller.display_search_results(results)
                
                # Ask if user wants to continue with this resident
                if not presenter.confirm_continue():
                    break
            
            # Ask if user wants to select another resident
            presenter.display_info("Select another resident or press Enter to exit.")
            
        except KeyboardInterrupt:
            presenter.display_info("\nSession interrupted by user.")
            break
        except Exception as e:
            presenter.display_error(f"Unexpected error: {e}")
            continue


@app.command()
def demo() -> None:
    """Run a quick demo with predefined queries."""
    try:
        controller = create_app()
        run_demo(controller)
    except Exception as e:
        typer.echo(f"Demo error: {e}")
        raise typer.Exit(1)


def run_demo(controller: TalkToChartController) -> None:
    """Run predefined demo scenarios."""
    presenter = controller._presenter
    
    presenter.display_welcome()
    presenter.display_info("Running demo with predefined queries...\n")
    
    # Demo scenarios
    demo_scenarios = [
        {
            "resident_id": "RES001",
            "resident_name": "Mary Johnson", 
            "query": "Find evidence of depression symptoms in the last 14 days"
        },
        {
            "resident_id": "RES001",
            "resident_name": "Mary Johnson",
            "query": "Find evidence of transfer assistance requirements"
        },
        {
            "resident_id": "RES002", 
            "resident_name": "Robert Williams",
            "query": "Find evidence of falls or fall risk"
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        presenter.display_info(f"Demo {i}: {scenario['resident_name']}")
        presenter.console.print(f"[bold]Query:[/bold] {scenario['query']}")
        
        # Execute search
        results = controller.search_clinical_notes(
            scenario["resident_id"], 
            scenario["query"]
        )
        
        # Display results
        controller.display_search_results(results)
        
        if i < len(demo_scenarios):
            presenter.console.input("\n[dim]Press Enter to continue to next demo...[/dim]")
            presenter.console.print("\n" + "="*60 + "\n")


@app.command()
def list_residents() -> None:
    """List all available residents."""
    try:
        controller = create_app()
        residents = controller.get_residents()
        controller.display_residents(residents)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()