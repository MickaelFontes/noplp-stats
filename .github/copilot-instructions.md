# NOPLP Stats Development Instructions

## Project Overview

**noplp-stats** is a data visualization platform for statistics about the French TV show *N'oubliez Pas Les Paroles* (NOPLP).

- **Website**: https://noplp-stats.fr
- **Tech Stack**: Python 3.14+, Dash 4.1.0, Pandas, Gunicorn
- **Data Source**: Fandom Wiki (with show verification)
- **Repository**: github.com/MickaelFontes/noplp-stats
- **Default Branch**: `main`

---

## Development Workflow

### 1. Environment Setup
- **Python Version**: 3.14+ (configured via Poetry)
- **Package Manager**: Poetry (see `pyproject.toml`)
- **Dev Dependencies**: Black, Pylint, Flake8, Pytest, Selenium, BeautifulSoup4
- **Command Prefix**: Use `poetry run` for executing commands in the Python environment

### 2. Code Style & Standards
- **Formatting**: Black (automatic via pre-commit recommended)
- **Linting**: Pylint and Flake8
- **Import Format**: Follow Python conventions (stdlib, third-party, local)
- **Naming**: 
  - Snake_case for variables and functions
  - PascalCase for classes
  - UPPER_CASE for constants
- **Docstrings**: Include for all public functions and classes

### 3. Project Structure
```
noplp-stats/
├── app.py                 # Main Dash application entry point
├── noplp/                 # Core business logic
│   ├── scrapper.py       # Fandom Wiki scraping
│   ├── create_database.py # Database creation & management
│   ├── song.py           # Song data model
│   ├── main.py           # Main orchestration
│   └── compare_changes.py # Data comparison utilities
├── pages/                 # Dash pages (multi-page app)
│   ├── home.py           # Homepage
│   ├── global.py         # Global statistics
│   ├── by_singer.py      # Singer-specific stats
│   ├── by_song.py        # Song-specific stats
│   ├── by_category.py    # Category breakdowns
│   ├── training.py       # Training mode
│   ├── my_stats.py       # User statistics
│   ├── new_training.py   # New training features
│   ├── utils.py          # Page utilities
│   └── assets/           # CSS, images
├── data/                  # CSV datasets
├── tests/                 # Test suite
├── deploy/               # Kubernetes configs
└── docs/                 # Documentation
```

---

## Dash Development Guidelines

### Creating/Modifying Pages
1. **Location**: All pages go in `pages/` directory
2. **Structure**: Use `register_page()` for multi-page routing
3. **Components**: Use Dash Bootstrap Components (`dbc`) for UI
4. **Styling**: Add CSS to `pages/assets/css/`
5. **Callbacks**: Handle interactivity with `@callback` decorator

### Component Best Practices
- Use `dbc.Container` for layout structure
- Leverage Bootstrap grid system (12-column)
- Keep callbacks focused and well-documented
- Use State/Input/Output appropriately in callbacks
- Store session/user data in `dcc.Store` components

### Responsive Design
- Test on mobile, tablet, and desktop
- Use Bootstrap breakpoints (sm, md, lg, xl)
- Ensure all charts are responsive
- Test with Bootstrap theme variables

---

## Data & Analytics Guidelines

### Data Sources
- **Primary**: Fandom Wiki (https://n-oubliez-pas-les-paroles.fandom.com/fr/)
- **Validation**: All data must be cross-referenced with show air dates
- **Verified Lyrics**: Mark with bold in UI when verified on-air
- **Categories**: Understand show scoring categories (Points, Maestro, Même chanson, etc.)

### Working with Datasets
- CSV files stored in `data/` directory
- Key files:
  - `db_songs.csv` - Song master data
  - `db_lyrics.csv` - Song lyrics (with verification status)
  - `global_ranking.csv` - Overall popularity rankings
  - `coverage_graph.csv` - Coverage scores
  - `songs.csv` - Aggregated song data
- Use Pandas for data manipulation
- Validate data integrity before committing

### Analytics Calculations
- **Coverage Score**: Number of songs needed to complete a category
- **Popularity**: Based on show air frequency
- **Rankings**: By category and time period
- Always provide context (time window, sample size, etc.)

---

## Testing Requirements

### Test Structure
- **Location**: `tests/` directory
- **Framework**: Pytest
- **UI Testing**: Selenium for integration tests
- **Test Files**:
  - `test_all.py` - General functionality
  - `test_interactions_timings.py` - Performance/timing tests
  - Use `conftest.py` for fixtures and shared setup

### Testing Standards
1. Write tests for new features before merging
2. Maintain >80% code coverage target
3. Test edge cases and error handling
4. Include data validation tests
5. Test responsive UI behavior

### Running Tests
```bash
pytest tests/
pytest tests/test_all.py -v
```

---

## Code Quality & Tools

### Pre-Commit Checks
Run before committing:
```bash
black noplp/ pages/ tests/
flake8 noplp/ pages/ tests/ --max-line-length=100
pylint noplp/ pages/ tests/
```

### Imports
- Remove unused imports (use Pylint guidance)
- Organize: stdlib → third-party → local imports
- Use explicit imports (avoid `import *`)

### Documentation
- Add docstrings to all public functions/classes
- Include type hints where possible
- Update README if adding major features
- Document breaking changes

---

## Deployment & Configuration

### Environment Variables
- `DASH_DEBUG`: Set to enable debug mode in production (behind Gunicorn)
- Default: `False` for production safety

### Containerization
- **Dev Container**: `Dockerfile.dev`
- **GCP App Engine**: `deploy/app.yaml` (production configuration)
- **Server**: Gunicorn (see `pyproject.toml` for version)

### Build & Run Commands
```bash
# Install dependencies
poetry install

# Run development server
poetry run python app.py

# Run with Gunicorn
poetry run gunicorn --workers 4 app:server

# Build Docker image
docker build -f Dockerfile.dev -t noplp-stats .
```

---

## Domain Knowledge: NOPLP Show

### Understanding the Show
- **Format**: Contestants guess song lyrics
- **Categories**: Different scoring rules (Points, Maestro, etc.)
- **Coverage**: Knowing top songs in each category ensures strong performance
- **Fandom Wiki**: Primary source of truth for lyrics and song data

### Key Metrics
- **Popular Songs**: Most frequently played on the show
- **Coverage Score**: Percentage of category covered by learning top N songs
- **Singer Stats**: Frequency of each artist's songs appearing
- **Temporal Analysis**: Trends over time, seasonal patterns

### Data Integrity Checks
- Verify song data against actual show episodes
- Cross-reference Fandom Wiki with broadcast dates
- Flag discrepancies and missing data
- Document any manual corrections

---

## Agent Capabilities

When working with AI agents on this project, emphasize these capabilities:

### Dash Development
- ✓ Create new pages with multi-page routing
- ✓ Build interactive components with callbacks
- ✓ Style using Bootstrap components and CSS
- ✓ Implement responsive layouts
- ✓ Manage application state (callbacks, stores)

### Data Processing
- ✓ Scrape and validate Fandom Wiki data
- ✓ Process song/singer statistics
- ✓ Calculate coverage scores and rankings
- ✓ Validate data integrity against sources
- ✓ Query and update CSV files with Pandas

### Testing
- ✓ Write Pytest unit tests
- ✓ Create Selenium UI tests
- ✓ Test interaction timings
- ✓ Validate data accuracy

### Code Quality
- ✓ Apply Black formatting
- ✓ Run Pylint/Flake8 linting
- ✓ Optimize imports
- ✓ Follow project conventions

### Deployment
- ✓ Update Kubernetes YAML configs
- ✓ Manage containerization
- ✓ Configure environment variables
- ✓ Handle multi-environment setups

---

## Common Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v

# Format code
poetry run black .

# Lint code
poetry run flake8 . --max-line-length=100
poetry run pylint noplp/ pages/ tests/

# Run dev server
poetry run python app.py

# Docker build
docker build -f Dockerfile.dev -t noplp-stats .

# Check poetry lock
poetry lock --check
```

---

## Git Workflow

- **Branch Naming**: `feature/*`, `bugfix/*`, `hotfix/*`, `docs/*`
- **Commit Messages**: Clear, descriptive, reference issues when applicable
- **PR Process**: 
  1. Create feature branch from `main`
  2. Make changes with descriptive commits
  3. Run tests locally
  4. Push and create PR
  5. Address review comments
  6. Merge to `main`

---

## Quick Reference

| Task | Command/File |
|------|-------------|
| View dependencies | `pyproject.toml` |
| Add new package | `poetry add <package>` |
| Run app | `python app.py` |
| Format code | `black .` |
| Run tests | `pytest tests/` |
| Check types | `pylint noplp/` |
| Build Docker | `docker build -f Dockerfile.dev .` |

---

## Need Help?

- **Project Structure**: See `noplp/`, `pages/` directories
- **Dash Docs**: https://dash.plotly.com
- **Bootstrap Components**: https://dash-bootstrap-components.opensource.faculty/
- **Poetry**: https://python-poetry.org/docs/
- **Contributing**: Follow code style and always write tests

