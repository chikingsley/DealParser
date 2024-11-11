# Affiliate Deal Processing Bot - Development Plan

## Project Overview
A Telegram bot that processes affiliate deal messages using Mistral API to extract and standardize deal information according to the specified template format.  The bot will support bulk processing of deals from a single message.

## Project Structure
```
affiliate_bot/
├── .env                    # Environment variables (including NOTION_TOKEN, MISTRAL_TOKEN)
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                 # Application entry point
│
├── config/
│   ├── __init__.py
│   ├── settings.py        # Configuration management
│   ├── constants.py       # Shared constants and enums
│   └── notion.py         # Notion database configuration
│
├── core/
│   ├── __init__.py
│   ├── mistral/
│   │   ├── __init__.py
│   │   ├── client.py     # Mistral API integration
│   │   ├── prompts.py    # System and user prompts
│   │   └── parser.py     # Response parsing utilities
│   │
│   ├── notion/
│   │   ├── __init__.py
│   │   ├── client.py     # Notion API client
│   │   ├── database.py   # Database operations
│   │   └── mapper.py     # Deal to Notion property mapper
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── deal.py       # Deal data models
│   │   └── state.py      # User state models
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py  # Input validation
│       └── formatters.py  # Output formatting
│
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── message.py    # Message handling
│   │   ├── callback.py   # Callback query handling
│   │   └── error.py      # Error handling
│   │
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── review.py     # Deal review keyboards
│   │   └── edit.py       # Deal editing keyboards
│   │
│   └── states/
│       ├── __init__.py
│       └── manager.py     # State management
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_mistral/
    ├── test_handlers/
    └── test_validators/
```

## Development Phases

### Phase 1: Project Setup 
1. Initialize project structure
2. Set up environment configuration
3. Install dependencies:
   - python-telegram-bot
   - mistralai
   - pydantic
   - python-dotenv
4. Create basic documentation

### Phase 2: Core Components 

#### Mistral Integration
1. Implement Mistral client wrapper
2. Design system prompt based on deal formatting template
3. Create response parser for standardized output
4. Implement error handling and retry logic

#### Data Models
1. Create Pydantic models for:
   - Deal structure
   - User state
   - Bot configuration
   - Validation rules

### Phase 3: Notion Integration 

#### Notion Setup
1. Create Notion integration and get API token
2. Set up database with appropriate properties matching deal structure:
   - Region (select)
   - Partner (text)
   - GEO (multi-select)
   - Language (select)
   - Source (multi-select)
   - Model (select)
   - CPA (number)
   - CRG (number)
   - CPL (number)
   - Funnels (multi-select)
   - CR (number)
   - Deduction Limit (number)

#### Notion Client Implementation
1. Implement Notion API client wrapper
2. Create database operations module
3. Implement property mapping system
4. Add error handling and retry logic
5. Create validation for database schema
6. Implement bulk operations for multiple deals (supports processing multiple deals simultaneously)

### Phase 4: Bot Implementation 

#### Message Handling
1. Implement basic message reception
2. Create deal extraction pipeline (handles single and multiple deals)
3. Implement validation system (handles single and multiple deals)
4. Add error handling and user feedback (provides feedback for each deal in bulk processing)

#### Interactive Interface
1. Create review interface (supports review of multiple deals)
2. Implement navigation for multiple deals
3. Build editing interface (supports editing multiple deals)
4. Add confirmation/rejection handling (handles confirmation/rejection for multiple deals)

#### State Management
1. Implement user session handling
2. Create deal state tracking (handles multiple deals)
3. Add conversation flow management (handles multiple deals)
4. Implement data persistence


### Phase 5: Testing & Refinement (2-3 days)
1. Write unit tests
2. Implement integration tests
3. Add logging system
4. Create monitoring setup

## Key Considerations

### Mistral API Integration
- Start with system prompt engineering
- Implement proper rate limiting
- Add retry logic for API failures
- Cache common patterns
- Monitor token usage

### Data Processing
- Validate all input against template rules
- Handle multiple deals in single message
- Implement proper error handling
- Add feedback loop for failed parsing

### User Experience
- Clear error messages
- Intuitive navigation
- Quick response times
- Progress indicators
- Helpful feedback

### Security
- Input sanitization
- Rate limiting per user
- Error logging
- Data validation

## Testing Strategy

### Unit Tests
- Mistral client responses
- Deal parsing logic
- Validation rules
- State management
- Keyboard generation
- Notion integration
- Property mapping
- Database operations

### Integration Tests
- Full message processing
- User interaction flows
- Error handling
- State transitions

### Performance Tests
- Response times
- API usage optimization
- Memory usage
- State management efficiency

## Deployment Considerations
1. Environment configuration
2. Rate limiting setup
3. Error monitoring
4. Backup strategy
5. Scaling plan

## Documentation Requirements
1. Setup guide
2. API documentation
3. User guide updates
4. Troubleshooting guide
5. Development guide
