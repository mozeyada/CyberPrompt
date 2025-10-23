# CyberPrompt Project Architecture

## Overview
CyberPrompt is a research-grade evaluation platform for SOC/GRC LLM performance that benchmarks AI models for cybersecurity operations with cost-quality analysis. This platform supports RQ1 research on prompt length effects and RQ2 research on adaptive vs static benchmarking.

**Current Status**: Fully operational research platform with comprehensive dataset and validation framework.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CyberPrompt System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Frontend      │    │    Backend      │    │  Database   │  │
│  │   (React)       │◄──►│   (FastAPI)     │◄──►│  (MongoDB)  │  │
│  │   Port: 3000    │    │   Port: 8000    │    │ Port: 27017 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  External APIs  │    │   Admin UI      │                    │
│  │  OpenAI/Claude  │    │ (Mongo Express) │                    │
│  │                 │    │   Port: 8081    │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
CyberPrompt/
├── app/                    # Backend Python Application
│   ├── api/               # FastAPI Route Handlers
│   │   ├── adaptive.py    # Adaptive prompt generation endpoints
│   │   ├── analytics.py   # Cost-quality analysis endpoints
│   │   ├── documents.py   # Document upload/management
│   │   ├── export.py      # Data export functionality
│   │   ├── prompts.py     # Prompt CRUD operations
│   │   ├── research.py    # Research-specific filtering
│   │   ├── runs.py        # Experiment execution (with background tasks)
│   │   ├── stats.py       # Dashboard statistics
│   │   └── validation.py  # Validation endpoints
│   ├── core/              # Application Core
│   │   ├── config.py      # Settings & environment config
│   │   └── security.py    # API key validation
│   ├── db/                # Database Layer
│   │   ├── connection.py  # MongoDB connection management
│   │   └── repositories.py # Data access layer (CRUD)
│   ├── models/            # Pydantic Data Models
│   │   └── __init__.py    # All data schemas & enums
│   ├── services/          # Business Logic (Consolidated)
│   │   ├── analytics_service.py # Cost-quality analytics
│   │   ├── background_jobs.py   # Background task processing
│   │   ├── base.py        # Judge interface & implementations
│   │   ├── composite.py   # Rubric score calculations
│   │   ├── ensemble.py    # Ensemble evaluation system
│   │   ├── experiment.py  # Experiment orchestration
│   │   ├── fsp.py         # Focus Sentence Prompting (bias control)
│   │   ├── groq_client.py # Groq API integration for adaptive prompting
│   │   ├── llm_client.py  # LLM API integrations
│   │   ├── prompt_generator.py # Dynamic prompt creation
│   │   ├── prompts.py     # Evaluation prompt templates
│   │   ├── risk.py        # Risk assessment metrics
│   │   └── static_loader.py # Static prompt loading
│   ├── utils/             # Utilities
│   │   ├── adaptive_prompt_generator.py # Adaptive prompt generation logic
│   │   ├── mongodb.py     # ObjectId conversion helpers
│   │   ├── token_meter.py # Token counting & cost calculation
│   │   └── ulid_gen.py    # Unique ID generation
│   └── main.py            # FastAPI application entry point
├── ui/                    # Frontend React Application
│   ├── src/
│   │   ├── api/           # API Client
│   │   │   └── client.ts  # HTTP client for backend APIs
│   │   ├── components/    # React Components
│   │   │   ├── Charts/    # Data visualization components
│   │   │   ├── Filters/   # Filter UI components
│   │   │   ├── Selectors/ # Selection UI components
│   │   │   ├── Tables/    # Data table components
│   │   │   └── Step*.tsx  # Experiment wizard steps
│   │   ├── pages/         # Route Components
│   │   │   ├── About.tsx     # About page with project information
│   │   │   ├── AdaptivePrompting.tsx # Adaptive prompt generation page
│   │   │   ├── BenchmarkRunner.tsx # Experiment configuration page
│   │   │   ├── Insights.tsx   # Research analysis page
│   │   │   ├── PromptLibrary.tsx # Prompt library management
│   │   │   ├── RQ1Flow.tsx   # RQ1 research workflow
│   │   │   ├── RQ2Flow.tsx   # RQ2 research workflow
│   │   │   └── WizardLanding.tsx # Research wizard landing page
│   │   ├── state/         # State Management
│   │   │   └── useFilters.ts # Global filter state
│   │   ├── types/         # TypeScript Definitions
│   │   │   └── index.ts   # API response types
│   │   └── App.tsx        # Main application component
│   └── package.json       # Frontend dependencies
├── tests/                 # Test Suite
│   ├── conftest.py        # Test configuration
│   ├── test_evaluation.py # Evaluation logic tests
│   └── validation/        # Validation test suite
│       ├── test_ensemble_statistics.py # Statistical validation
│       ├── test_adversarial_responses.py # Quality detection tests
│       ├── test_cost_accuracy.py # Cost calculation tests
│       └── test_integration_pipeline.py # End-to-end tests
├── scripts/               # Utility Scripts
│   ├── generate_research_dataset.py # Dataset generation
│   └── import_cysecbench.py # Research data import
├── cysecbench-data/       # Research Dataset
│   └── Dataset/           # CySecBench research prompts
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # Backend container definition
└── requirements.txt       # Python dependencies
```

## Data Flow

### 1. Experiment Execution Flow
```
Frontend (Experiments Page)
    ↓ Select prompts & models
Backend (runs.py)
    ↓ Create experiment runs
    ↓ Check batch size
    ├── Small batch (≤10): Synchronous execution
    └── Large batch (>10): Background task
Services (experiment.py)
    ↓ Execute LLM calls
LLM APIs (OpenAI/Claude)
    ↓ Get responses
Services (base.py - LLM Judge)
    ↓ Score responses using 7-dimension rubric
Database (MongoDB)
    ↓ Store Run + OutputBlob (linked via output_blob_id)
Services (analytics_service.py)
    ↓ Calculate cost-quality metrics
Frontend (Results/Analytics)
```

### 2. Data Models & Relationships

```
Prompt
├── prompt_id (ULID)
├── text (string)
├── scenario (SOC_INCIDENT|CTI_SUMMARY|GRC_MAPPING)
├── length_bin (XS|S|M|L|XL)
└── metadata {length_bin, word_count}

Run
├── run_id (ULID)
├── prompt_id → Prompt
├── model (gpt-4o|claude-3-5-sonnet|etc)
├── status (queued|running|succeeded|failed)
├── tokens {input, output, total}
├── economics {aud_cost, latency_ms}
├── scores {7-dimension rubric + composite}
├── output_blob_id → OutputBlob.blob_id
└── bias_controls {fsp: true}

OutputBlob
├── blob_id (hash)
├── content (LLM response text)
└── metadata
```

### 3. API Endpoints Structure

```
/prompts/
├── GET /           # List prompts with filters
├── GET /{id}       # Get specific prompt
├── POST /import    # Import prompt collections
└── POST /adaptive/generate # Generate adaptive prompts from policy documents

/export/
├── GET /csv        # Export data as CSV
└── GET /json       # Export data as JSON

/runs/
├── POST /plan      # Plan experiment matrix
├── POST /execute/batch # Execute multiple runs (background for >10 runs)
├── POST /execute/{id}  # Execute single run
├── GET /{id}       # Get run results with output content
└── GET /           # List runs with filters

/analytics/
├── GET /cost-quality-scatter # Cost vs quality data
├── GET /cost_quality        # Cost-quality frontier
├── GET /length_bias         # Length bias analysis
└── GET /risk_curves         # Risk assessment curves

/research/
├── GET /prompts/filter      # Research-specific filtering
└── GET /scenarios/stats     # Dataset statistics

/validation/
└── GET /kl-divergence      # KL divergence between adaptive and static prompts

/documents/
├── POST /                   # Upload documents
├── GET /                    # List documents
└── POST /generate-prompts/{id} # Generate prompts from docs
```

## Key Technologies

### Backend Stack
- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **MongoDB**: Document database with Motor (async driver)
- **Pydantic**: Data validation and serialization
- **ULID**: Unique identifiers for all entities
- **Background Tasks**: FastAPI BackgroundTasks for async processing
- **Docker**: Containerization for consistent deployment

### Frontend Stack
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **TanStack Query**: Data fetching and caching
- **Recharts**: Data visualization library

### External Integrations
- **OpenAI API**: GPT models (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- **Anthropic API**: Claude models (claude-3-5-sonnet, claude-3-opus)
- **Groq API**: Llama models (llama-3.3-70b-versatile) for cost-effective adaptive prompting
- **Token Counting**: tiktoken for accurate token measurement
- **Cost Calculation**: Real-time AUD pricing per 1K tokens

## Core Features

### 1. 7-Dimension SOC/GRC Rubric
Every LLM response is evaluated across:
1. **Technical Accuracy**: Factual correctness in cybersecurity context
2. **Actionability**: Can analysts act on the response?
3. **Completeness**: Covers all aspects of the prompt
4. **Compliance Alignment**: Aligns with regulatory frameworks
5. **Risk Awareness**: Acknowledges risks and limitations
6. **Relevance**: Stays on-task without digressions
7. **Clarity**: Clear, structured, unambiguous writing

### 2. Bias Mitigation (FSP)
- **Focus Sentence Prompting**: Reduces verbosity bias in evaluation
- **Length Normalization**: Ensures fair comparison regardless of response length
- **Granularity Control**: Consistent evaluation criteria across models

### 3. Cost-Quality Analysis
- **Token-level Tracking**: Precise input/output token counting
- **Real-time Pricing**: AUD cost calculation per API call
- **Quality Frontiers**: Identify optimal cost-performance trade-offs
- **Budget Optimization**: Find best value models for SOC/GRC tasks

### 4. Scalable Experiment Processing
- **Background Tasks**: Large experiments (>10 runs) execute asynchronously
- **Immediate Feedback**: Small experiments execute synchronously
- **Progress Tracking**: Real-time status updates for long-running tasks
- **Concurrent Execution**: Configurable parallelism (1-10 concurrent runs)

### 5. Research Capabilities
- **Adaptive Benchmarking**: Generate prompts from live documents using Groq API
- **KL Divergence Validation**: Statistical validation of adaptive vs static prompt distributions
- **Length Bias Analysis**: Study prompt length vs quality correlation with FSP bias mitigation
- **Scenario Comparison**: Compare performance across SOC/GRC contexts
- **Reproducible Experiments**: Fixed seeds and versioned datasets

## Development Workflow

### 1. Local Development
```bash
# Start all services
make dev

# Individual services
docker compose up -d        # Backend + database
cd ui && npm run dev       # Frontend dev server
```

### 2. Testing
```bash
# Backend tests
docker compose exec api pytest

# Frontend tests
cd ui && npm test
```

### 3. Data Management
```bash
# Import research dataset (300 prompts)
make import-cysecbench
```

## Security & Configuration

### Environment Variables (.env)
```bash
APP_ENV=dev
MONGO_URI=mongodb://mongo:27017
MONGO_DB=genai_bench

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Pricing (AUD per 1K tokens)
PRICE_INPUT.gpt4=0.03
PRICE_OUTPUT.gpt4=0.06
```

### API Security
- **API Key Authentication**: All endpoints require x-api-key header
- **CORS Configuration**: Allows frontend access from localhost:3000
- **Input Validation**: Pydantic models validate all request/response data
- **Error Handling**: Structured error responses with proper HTTP status codes

## Deployment Architecture

### Development (Docker Compose)
- **API Container**: Python FastAPI application
- **MongoDB Container**: Database with persistent volume
- **Mongo Express**: Database admin interface
- **Frontend**: Vite dev server (local)

### Production Considerations
- **Container Orchestration**: Kubernetes or Docker Swarm
- **Database**: MongoDB Atlas or self-hosted cluster
- **Load Balancing**: Nginx or cloud load balancer
- **Monitoring**: Application and infrastructure monitoring
- **Secrets Management**: Secure API key storage

This architecture provides a scalable, maintainable platform for evaluating LLM performance in cybersecurity contexts with comprehensive cost-quality analysis.