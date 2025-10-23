# CyberPrompt Platform - Technical Specifications

**Research Project**: Benchmarking Generative AI Token Use in Cybersecurity Operations  
**Student**: Mohamed Zeyada (11693860)  
**Date**: October 2025

---

## Platform Overview

CyberPrompt is a research-grade web-based benchmarking platform designed to systematically evaluate the relationship between prompt length and output quality in cybersecurity operations. The platform implements a controlled experimental framework for RQ1 research on prompt optimization in SOC/GRC tasks.

## Technical Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB with AsyncIOMotor driver
- **API Design**: RESTful endpoints with async/await patterns
- **Authentication**: API key validation for external LLM providers
- **Background Tasks**: FastAPI async capabilities for concurrent task processing

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite for development and production builds
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React hooks and context
- **UI Components**: Custom components for experiment management

### Infrastructure
- **Containerization**: Docker with docker-compose for deployment
- **Database**: MongoDB 7.0 with persistent volume storage
- **Admin Interface**: Mongo Express for database management
- **Environment**: Development and production configurations

## Core Components

### Data Models
- **Prompts**: Academic dataset with S/M/L variants and metadata
- **Runs**: Experimental execution records with results
- **Users**: Researcher accounts and permissions
- **Analytics**: Cost-quality analysis and statistical results

### API Endpoints
- **Prompts**: CRUD operations for dataset management
- **Runs**: Experiment execution and result retrieval
- **Analytics**: Statistical analysis and visualization data
- **Research**: Filtered access to academic dataset variants

### Services
- **Analytics Service**: Cost-quality trade-off calculations
- **Background Jobs**: Automated experiment execution
- **Judge Interface**: Quality assessment framework
- **LLM Integration**: OpenAI/Claude API connectivity

## Dataset Integration

### Academic Dataset (v4)
- **Source**: `data/prompts.json` (300 prompts total)
- **Structure**: 100 base scenarios × 3 length variants (S/M/L)
- **Validation**: 95.3% token target compliance, 100% task consistency
- **Data Sources**: BOTSv3 integration with authentic cybersecurity data

### External Data Sources
- **BOTSv3 Dataset**: Real ransomware families, C2 infrastructure, Windows event codes
- **NIST Frameworks**: Cybersecurity controls and compliance requirements
- **Industry Standards**: SANS, ISO 27001, and regulatory frameworks

## Quality Assessment Framework

### 7-Dimension Evaluation Rubric
1. **Accuracy**: Factual correctness and technical precision
2. **Completeness**: Comprehensive coverage of task requirements
3. **Relevance**: Alignment with cybersecurity context and objectives
4. **Clarity**: Communication effectiveness and readability
5. **Actionability**: Practical applicability for security operations
6. **Compliance**: Regulatory and industry standard alignment
7. **Technical Correctness**: Domain-specific accuracy and terminology

## Experimental Design

### Controlled Experiment Framework
- **Independent Variable**: Prompt length (S: 150-250, M: 450-550, L: 800-1000 tokens)
- **Dependent Variables**: Quality scores, cost efficiency, processing time
- **Controlled Variables**: Task requirements, role assignments, scenario types
- **Sample Size**: 300 prompts (100 per condition) for statistical power (d=1.2, power=0.98)

### Statistical Analysis
- **Power Analysis**: Cohen's d calculations for effect size detection
- **Inferential Testing**: ANOVA for group comparisons with post-hoc analysis
- **Cost Analysis**: Token cost calculations and efficiency metrics
- **Quality Metrics**: 7-dimension scoring with inter-rater reliability

## Deployment Configuration

### Development Environment
```yaml
# docker-compose.yml
services:
  - cyberprompt-app (FastAPI backend)
  - cyberprompt-mongo (MongoDB database)
  - cyberprompt-ui (React frontend)
  - mongo-express (Database admin)
```

### Production Considerations
- **Scalability**: Horizontal scaling with load balancers
- **Security**: API key management and input validation
- **Monitoring**: Application logging and performance metrics
- **Backup**: Automated database backup and recovery procedures

## Research Applications

### Academic Use Cases
- **Prompt Engineering**: Systematic optimization of AI prompts in cybersecurity
- **Cost-Benefit Analysis**: Economic evaluation of LLM deployment strategies
- **Quality Assessment**: Standardized evaluation frameworks for security AI
- **Comparative Studies**: Cross-model performance benchmarking

### Industry Applications
- **SOC Operations**: Optimized prompt strategies for incident response
- **GRC Processes**: Efficient compliance assessment and documentation
- **CTI Analysis**: Effective threat intelligence synthesis and reporting
- **Training Programs**: Educational resources for AI-assisted security workflows

---

*Technical specifications documented for Assignment 3A Research Outputs Portfolio*
