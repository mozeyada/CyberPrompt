# CyberPrompt Platform - Code Overview

**Research Project**: Benchmarking Generative AI Token Use in Cybersecurity Operations  
**Student**: Mohamed Zeyada (11693860)  
**Date**: October 2025

---

## Code Samples Included

This directory contains representative code samples from the CyberPrompt platform that demonstrate the research implementation and technical architecture.

### Core Platform Files

#### `generate_research_dataset.py`
- **Purpose**: Generates the 300-prompt academic dataset for RQ1 research
- **Key Features**: 
  - Controlled experiment design with S/M/L length variants
  - BOTSv3 dataset integration for authentic cybersecurity data
  - Token counting and validation using tiktoken
  - Academic reproducibility with fixed seed (42)
- **Research Relevance**: Demonstrates dataset creation methodology for controlled experiments

#### `import_cysecbench.py`
- **Purpose**: Imports the generated dataset into MongoDB for experimental execution
- **Key Features**:
  - MongoDB integration with AsyncIOMotor
  - Dataset validation and metadata preservation
  - Academic dataset structure maintenance
- **Research Relevance**: Shows data management for experimental infrastructure

#### `main.py`
- **Purpose**: FastAPI application entry point and core server configuration
- **Key Features**:
  - FastAPI application setup with CORS and middleware
  - Database connection management
  - API route registration and configuration
  - Development and production environment handling
- **Research Relevance**: Demonstrates platform architecture and API foundation

#### `data_models.py`
- **Purpose**: Pydantic data models for type safety and validation
- **Key Features**:
  - Prompt data structure with metadata
  - Experiment run tracking models
  - Quality assessment rubric definitions
  - API request/response schemas
- **Research Relevance**: Shows data structure design for research experiments

### Infrastructure Files

#### `docker-compose.yml`
- **Purpose**: Container orchestration for development and deployment
- **Key Features**:
  - Multi-service architecture (app, database, frontend, admin)
  - Environment variable configuration
  - Volume management for data persistence
  - Network configuration for service communication
- **Research Relevance**: Demonstrates reproducible deployment for research platform

#### `requirements.txt`
- **Purpose**: Python dependencies and version specifications
- **Key Features**:
  - FastAPI and async database drivers
  - LLM integration libraries (OpenAI, Anthropic)
  - Data processing and analysis tools
  - Development and testing dependencies
- **Research Relevance**: Shows technical dependencies for AI research platform

## Code Architecture Highlights

### Backend Structure
```
app/
├── api/           # REST API endpoints
├── core/          # Application configuration
├── db/            # Database layer
├── models/        # Data models and schemas
├── services/      # Business logic
└── utils/         # Utility functions
```

### Key Design Patterns
- **Async/Await**: Full asynchronous programming for performance
- **Dependency Injection**: FastAPI dependency system for modularity
- **Repository Pattern**: Data access abstraction for testability
- **Service Layer**: Business logic separation from API endpoints

### Research Integration
- **Academic Dataset**: Structured prompt management with metadata
- **Experimental Framework**: Controlled experiment execution
- **Quality Assessment**: Automated evaluation pipeline
- **Statistical Analysis**: Cost-quality trade-off calculations

## Research Methodology Implementation

### Controlled Experiment Design
The code implements a controlled experimental framework where:
- **Independent Variable**: Prompt length (isolated through S/M/L variants)
- **Controlled Variables**: Task requirements, role assignments, scenario types
- **Dependent Variables**: Quality scores, cost efficiency, processing time

### Data Integrity
- **Reproducibility**: Fixed random seed (42) for consistent results
- **Validation**: Automated checking of token counts and task consistency
- **Versioning**: Dataset version tracking for academic reproducibility
- **Metadata**: Comprehensive research metadata for transparency

### Quality Assurance
- **Automated Validation**: Token count and task requirement checking
- **Statistical Power**: Sample size calculations for robust findings
- **Error Handling**: Graceful fallbacks and comprehensive logging
- **Testing**: Unit tests for critical functionality

## External Dependencies

### AI/ML Libraries
- **tiktoken**: Token counting for LLM compatibility
- **OpenAI**: GPT model integration
- **Anthropic**: Claude model integration

### Database and API
- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database for flexible data storage
- **AsyncIOMotor**: Asynchronous MongoDB driver

### Data Processing
- **Pydantic**: Data validation and serialization
- **pandas**: Data analysis and manipulation
- **numpy**: Numerical computations

## Research Applications

### Academic Use Cases
- **Prompt Engineering Research**: Systematic optimization studies
- **Cost-Benefit Analysis**: Economic evaluation of AI deployment
- **Quality Assessment**: Standardized evaluation frameworks
- **Comparative Studies**: Cross-model performance analysis

### Industry Applications
- **SOC Operations**: Optimized incident response workflows
- **GRC Processes**: Efficient compliance assessment
- **CTI Analysis**: Enhanced threat intelligence synthesis
- **Training Programs**: Educational AI-assisted security training

---

*Code overview documented for Assignment 3A Research Outputs Portfolio*
