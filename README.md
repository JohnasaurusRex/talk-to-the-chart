# Talk to the Chart

AI-powered clinical documentation search system for MDS coordinators. A Proof of Concept (POC) application that enables natural language querying of nursing home resident charts to find clinical evidence for MDS coding.

## 🏥 Business Context

The Minimum Data Set (MDS) is a federally mandated clinical assessment that determines Medicare reimbursement rates for nursing homes under the Patient Driven Payment Model (PDPM). MDS coordinators must review extensive clinical documentation to find evidence supporting higher reimbursement codes. This application streamlines that process using AI.

## 🏗️ Architecture

Built following **Clean Architecture** and **SOLID principles**:

```
src/talk_to_chart/
├── domain/              # Business entities and rules
│   └── entities.py
├── use_cases/           # Application business logic  
│   └── interfaces.py
├── infrastructure/      # External services and data
│   ├── gemini_service.py
│   └── repositories.py
├── adapters/           # Interface adapters
│   └── controllers.py
└── main.py            # Application entry point
```

### Architecture Layers

- **Domain**: Core business entities (Resident, ClinicalNote, QueryResult)
- **Use Cases**: Application services (SearchClinicalNotes, GetResidents)  
- **Infrastructure**: External services (Gemini AI, Mock repositories)
- **Interface Adapters**: Controllers and presenters for user interaction

## ⚡ Features

- **Natural Language Search**: Ask questions like "Find evidence of depression symptoms in the last 14 days"
- **Source Attribution**: Every result shows exact source, author, date, and time
- **Multiple Note Types**: Supports Nursing, Therapy, CNA, Social Work, and Physician notes
- **Rich CLI Interface**: Beautiful, scannable results with color coding by note type
- **Mock Data**: Comprehensive sample clinical notes for realistic demos

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Poetry
- Google Gemini API key

### Installation

1. **Clone and setup the project:**
```bash
git clone https://github.com/JohnasaurusRex/talk-to-the-chart
cd talk-to-chart
poetry install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

3. **Get Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

### Usage

**Interactive Mode:**
```bash
poetry run talk-to-chart start
```

**Quick Demo:**
```bash
poetry run talk-to-chart demo
```

**List Available Residents:**
```bash
poetry run talk-to-chart list-residents
```

## 💡 Example Queries

The system understands MDS-specific terminology:

- "Find evidence of depression symptoms in the last 14 days"
- "Show me transfer assistance requirements"  
- "Find fall incidents or fall risk assessments"
- "Look for signs of cognitive impairment"
- "Find evidence of behavioral symptoms"
- "Show pain-related documentation"

## 🏥 Sample Data

The POC includes three mock residents with realistic clinical scenarios:

- **Mary Johnson (RES001)**: Depression and mobility issues
- **Robert Williams (RES002)**: Fall risk and cognitive decline  
- **Dorothy Smith (RES003)**: Pain management and behavioral issues

Each resident has multiple note types spanning 14 days with clinically relevant content.

## 🎯 Example Output

```
Query: Find evidence of depression symptoms in the last 14 days
Resident: Mary Johnson (Room 101A)

I found 3 notes that may indicate symptoms of depression:

┌─ Result 1 ─────────────────────────────────────────────────────┐
│ "Resident stated 'I just don't feel like getting out of bed    │
│ anymore.' Tearful during conversation."                        │
│                                                                │
│ Source: Nursing Note, A. Smith, RN — 08/11/2025, 14:30       │
│ [Copy Text] [View Full Note]                                  │
└────────────────────────────────────────────────────────────────┘
```

## 🔧 Development

**Install dependencies:**
```bash
poetry install
```

**Run tests:**
```bash
poetry run pytest
```

**Code formatting:**
```bash
poetry run black .
poetry run isort .
```

**Type checking:**
```bash
poetry run mypy .
```

## 🏛️ Design Principles Applied

### Clean Architecture
- **Independence**: Business logic independent of frameworks and UI
- **Testability**: Core logic can be tested without external dependencies
- **Flexibility**: Easy to swap implementations (e.g., different AI providers)

### SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Interfaces can be swapped without breaking code
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Domain-Driven Design (DDD)
- **Bounded Context**: Clinical evidence discovery
- **Entities**: Resident, ClinicalNote with business identity
- **Value Objects**: Immutable QueryResult, Author
- **Aggregates**: SearchResults as consistency boundary
- **Domain Services**: AI query processing

## 🔒 Security & Compliance

- **HIPAA Compliant**: All mock data is synthetic and contains no real PHI
- **API Security**: Gemini API key stored in environment variables
- **Data Isolation**: Each query scoped to single resident

## 🚧 Current Limitations (POC Scope)

- **Mock Data Only**: No live EMR integration
- **Simple Search**: No complex date filtering or cross-resident queries  
- **CLI Interface**: No web UI (easily extensible due to clean architecture)
- **No Persistence**: Results not saved between sessions

## 🎯 Production Roadmap

For production deployment, consider:

- **EMR Integration**: Replace mock repositories with real data adapters
- **Web Interface**: Add React/Vue frontend using existing controllers
- **Advanced Search**: Complex filtering, date ranges, multiple residents
- **Audit Logging**: Track all searches for compliance
- **Performance**: Caching, indexing, and optimized retrieval
- **Security**: Authentication, authorization, and audit trails

## 📚 Dependencies

- **Core**: Python 3.9+, Poetry
- **AI**: Google Generative AI (Gemini)
- **CLI**: Typer, Rich (beautiful terminal interfaces)
- **Validation**: Pydantic
- **Development**: pytest, black, isort, mypy

## 🤝 Contributing

1. Follow Clean Architecture principles
2. Maintain SOLID design patterns
3. Add tests for new features
4. Use type hints throughout
5. Follow existing code style

---

**Built with Clean Architecture principles for maintainable, testable, and scalable healthcare software.**
