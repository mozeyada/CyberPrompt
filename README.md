# CyberCQBench

**Cost-effective and research-compliant AI evaluation for cybersecurity operations.**

CyberCQBench is a research platform that enables Security Operations Center (SOC) analysts, compliance professionals, and cybersecurity researchers to evaluate AI models for security tasks with full reproducibility and cost tracking.

## Why CyberCQBench?

As organizations adopt Large Language Models (LLMs) like GPT-4, Claude, and Gemini for incident analysis, compliance mapping, and threat intelligence reporting, one question remains unanswered: **Which AI is the most reliable, and at what cost?**

## Key Features

- **Research Compliance**: Full experiment tracking with dataset versioning and reproducible pipelines
- **Cost-Quality Analytics**: Interactive dashboards showing model performance vs API costs
- **7-Dimension SOC/GRC Rubric**: Technical accuracy, actionability, completeness, compliance alignment, risk awareness, relevance, clarity
- **Bias Mitigation**: Focus Sentence Prompting (FSP) for fair evaluation
- **Length Variant Analysis**: Automatic S+M+L prompt groups for controlled length studies
- **Static Dataset**: 300 prompts auto-loaded on startup + research-grade variants with token classification (250-350, 350-500, 600-750)
- **Adaptive Prompting**: Generate benchmarks from CTI/policy documents using Groq API
- **KL Divergence Validation**: Statistical validation of adaptive vs static prompt distributions
- **Experiment Grouping**: Track and compare experiments with metadata
- **Export Functionality**: CSV export with full research metadata

## Architecture

### Backend (Python 3.11 + FastAPI)
- **API**: FastAPI with automatic OpenAPI docs
- **Database**: MongoDB with Motor (async) + compound indexes
- **Models**: Pydantic v2 schemas with full validation
- **Evaluation**: 7-dimension rubric scoring system
- **Bias Control**: Focus Sentence Prompting (FSP) + granularity matching
- **Analytics**: Cost-quality frontiers, length bias analysis, risk curves

### Frontend (React + TypeScript + Vite)
- **UI Framework**: React 18 + TypeScript + TailwindCSS + shadcn/ui
- **Charts**: Recharts for interactive analytics
- **Data**: TanStack Query + Axios for API communication  
- **State**: Zustand for filters and local state
- **Animations**: Framer Motion for micro-interactions

### Infrastructure
- **Containerization**: Docker + docker-compose
- **Database**: MongoDB 7.0 with automated indexing
- **Environment**: 12-factor .env configuration
- **Development**: Hot-reload for both frontend and backend

## Quick Start

### Prerequisites
- Docker & docker-compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- OpenAI and/or Anthropic API keys
- Groq API key (for cost-effective adaptive prompting)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd CyberCQBench
cp .env.example .env
# Edit .env with your API keys and pricing config
```

### 2. Start Development Environment
```bash
# Start all services
make dev

# Or individually:
make docker-up    # Start backend + database
make dev-frontend # Start frontend dev server
```

### 3. Access the Application (300 static prompts auto-loaded)
- **CyberCQBench UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8081

### 5. Run Your First Experiment

**Option A: Research Wizard Landing (Recommended)**
1. Navigate to **Research** for guided research workflow
2. Choose between RQ1 (prompt length) or RQ2 (adaptive benchmarking) flows
3. Follow structured wizards with integrated results

**Option B: RQ1 Research Wizard**
1. Navigate to **RQ1 Flow** for guided prompt length analysis
2. Follow the 4-step wizard: Introduction → Demo → Experiment → Results
3. Automatically includes S+M+L prompt variants for controlled studies
4. View integrated results with cost-quality analysis

**Option C: RQ2 Research Wizard**
1. Navigate to **RQ2 Flow** for adaptive benchmarking analysis
2. Follow the 3-step wizard: Introduction → Demo → Results
3. Compare static vs adaptive prompt effectiveness
4. View KL divergence validation and coverage analysis

**Option D: Standard Benchmarking**
1. Navigate to **Benchmark Runner** tab
2. Choose security scenarios and configure evaluation settings
3. **Optional**: Enable "Include length variants" for S+M+L prompt groups
4. Select models to compare (GPT-4, Claude, etc.)
5. Configure bias controls (FSP recommended for fair scoring)
6. Execute and view cost-quality results in real-time

## Key Innovations

### Fixed FSP Implementation Bug ⚠️
**CRITICAL FIX**: Focus Sentence Prompting (FSP) code existed but wasn't properly integrated into judge evaluation. Now correctly implements sentence-based evaluation with full context for true length-invariant scoring.

### Research-Grade Analytics
**Overview Page**: Real-time cost efficiency analysis with FSP indicators (circles vs diamonds) and 15-row recent runs table with length classification.
**Research Wizard Landing**: Central hub for guided research workflows with real-time statistics.
**RQ1 Flow Wizard**: 4-step guided research workflow for systematic prompt length analysis with integrated results display.
**RQ2 Flow Wizard**: 3-step guided workflow for adaptive vs static benchmarking comparison with KL divergence validation.
**Advanced Analytics Page**: Statistical significance testing with confidence intervals, p-values, and research validation for RQ1 & RQ2.

### Length Variant Analysis
Controlled S+M+L prompt groups (250-350, 350-500, 600-750 tokens) with perfect traceability. 300 research-grade prompts: 100 originals + 100 medium + 100 long variants.

### KL Divergence Validation
Proper implementation validates adaptive prompts from CTI/policy documents against CySecBench baseline for RQ2 research validation.

### Adaptive Prompting System
Generate contextually relevant benchmarks from policy documents and CTI feeds using cost-effective Groq API. Maintains consistent data structure with static prompts for seamless integration.

### Streamlined UX
Removed verbose research explanations while maintaining statistical rigor. Clean, actionable insights with essential interpretation guides.

### 7-Dimension SOC/GRC Rubric
Every LLM output is evaluated across:
1. **Technical Accuracy**: Factual correctness in SOC/GRC context
2. **Actionability**: Can analysts act on it without extra steps?
3. **Completeness**: Covers all key aspects implied by task
4. **Compliance Alignment**: Aligns with policy/regulatory tone
5. **Risk Awareness**: Acknowledges risks, limitations, uncertainty
6. **Relevance**: Stays on-task with no digressions  
7. **Clarity**: Clear, structured, unambiguous writing

### Reproducible Pipelines
Fixed seeds, dataset versioning, and transparent scoring allow repeatable research and audits.

### Strong Data Relationships
Direct linking between experiment runs and LLM outputs for easy debugging and analysis.

### Research-Grade Dataset
**300 Total Prompts** (100 base × 3 length variants) structured for academic analysis:
- **100 Base Prompts**: 50 SOC incidents, 30 GRC assessments, 20 CTI analysis
- **3 Length Variants**: Short (250-350), Medium (350-500), Long (600-750 tokens)
- **Perfect Traceability**: Each variant linked to base prompt via metadata
- **Controlled Length Distribution**: Enables systematic RQ1 prompt length studies
- **FSP Integration**: Proper sentence-based evaluation for bias-free scoring
- **Reproducible**: Fixed seed (42) ensures identical generation across runs

**Token Classification**:
- **Short (S)**: 250-350 tokens - Tactical responses (SOC L1/L2)
- **Medium (M)**: 350-500 tokens - Analytical plans (SOC L3/IR)
- **Long (L)**: 600-750 tokens - Executive briefings (CISO/Board)

**Dataset Generation**: See [DATASET_GENERATION.md](DATASET_GENERATION.md) for details

## API Endpoints

### Prompts
- `POST /prompts/import` - Import prompt collections
- `GET /prompts` - List prompts with scenario, length_bin, prompt_type, include_variants filters
- `GET /prompts/{id}` - Get specific prompt
- `POST /prompts/adaptive/generate` - Generate adaptive prompts from policy documents

### Runs  
- `POST /runs/plan` - Plan experiment matrix
- `POST /runs/execute/batch` - Execute multiple runs
- `GET /runs` - List runs with experiment_id, dataset_version filters
- `GET /runs/experiments` - List experiments with summary stats
- `GET /runs/{id}` - Get run details with output

### Analytics
- `GET /analytics/cost_quality` - Cost vs quality scatter data
- `GET /analytics/length_bias` - Length bias analysis
- `GET /analytics/coverage` - Prompt coverage statistics

### Validation
- `GET /validation/kl-divergence` - KL divergence between adaptive and static prompts

### Export
- `GET /export/runs.csv` - Export runs with full metadata
- `GET /export/experiments.csv` - Export experiment summaries

## Development

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot-reload
make dev-backend

# Run tests
make test

# Lint and format
make lint
make format
```

### Frontend Development  
```bash
cd ui
npm install
npm run dev     # Development server
npm test        # Run tests
npm run build   # Production build
```

### Testing
```bash
# Backend tests
pytest tests/ -v --cov=app

# Frontend tests  
cd ui && npm test

# Integration tests
make test
```

## Project Structure

```
/app/
  /api/               # FastAPI routers (runs, prompts, analytics, export)
  /core/              # Configuration and security
  /models/            # Pydantic data models
  /db/                # MongoDB connection and repositories
  /services/          # Business logic
    experiment.py        # Experiment orchestration
    analytics_service.py # Cost-quality analytics
    llm_client.py       # LLM API integrations
    base.py             # Judge implementations
    composite.py        # Rubric calculations
  /utils/             # Utilities (tokens, costs, IDs)

/ui/                  # React frontend
  /src/
    /components/      # UI components (ScrollToTop, RQ1Results)
    /pages/           # Main pages (WizardLanding, RQ1Flow, RQ2Flow, Overview, BenchmarkRunner, Insights)
    /api/             # API client
    /types/           # TypeScript definitions

/scripts/             # Data migration and utility scripts
  create_academic_variants.py  # Generate S+M+L prompt variants
  fix_token_counts.py         # Recalculate token classifications
/cysecbench-data/     # Original research dataset (330 prompts)
/uploads/             # Policy documents for adaptive prompting
```

## FAQ

**Q: Who is CyberCQBench for?**  
A: SOC analysts, compliance auditors, cybersecurity researchers, and enterprise AI teams evaluating LLMs for security operations.

**Q: What problem does it solve?**  
A: Current tools focus only on model accuracy or coverage. None integrate cost vs quality, SOC/GRC rubric scoring, and bias mitigation into one reproducible system.

**Q: How is this different from CySecBench, DefenderBench, or Chroma?**  
A: 
- **CySecBench** → Provided the rubric baseline, but static & cost-blind
- **DefenderBench** → Added SOC-like diversity, but no GRC scoring or token analysis  
- **Chroma** → Inspired adaptive query generation, but not tuned for cybersecurity
- **CyberCQBench** → Unifies all three with FSP bias mitigation + cost analytics + length variant analysis for comprehensive SOC/GRC research

**Q: How does it track cost vs quality?**  
A: Each evaluation logs tokens, API pricing, and 7-dimension rubric scores. Dashboards visualize cost–quality trade-offs per model, scenario, and task length.

**Q: Why is this important now?**  
A: AI adoption in SOC and GRC is exploding, but without transparent benchmarking, organizations risk overspending and failing compliance checks. CyberCQBench ensures responsible, cost-effective use with academic-grade reproducibility.

**Q: What makes the dataset special?**  
A: 300 research-grade prompts with controlled length variants (Short 250-350, Medium 350-500, Long 600-750 tokens) enabling systematic studies of prompt length effects on LLM performance and cost efficiency.

## Configuration

### Environment Variables (.env)
```bash
APP_ENV=dev
API_KEYS=key1,key2,key3
MONGO_URI=mongodb://mongo:27017
MONGO_DB=genai_bench

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Pricing (AUD per 1K tokens)
PRICE_INPUT.gpt4=0.03
PRICE_OUTPUT.gpt4=0.06
PRICE_INPUT.claude35=0.025
PRICE_OUTPUT.claude35=0.075
```

### Supported Models
- **OpenAI**: gpt-4, gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Anthropic**: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
- **Groq**: llama-3.1-70b-versatile, llama-3.1-8b-instant (for adaptive prompting)
- **Google**: gemini-2.5-flash (coming soon)
- **Extensible**: Add new providers via LLM client adapters

## Usage Examples

### 1. Plan and Execute Experiments
```python
# Plan runs with length variants
plan = {
    "prompt_ids": ["prompt_001"],  # Original prompt
    "model_names": ["gpt-4o", "claude-3-5-sonnet"],
    "repeats": 3,
    "bias_controls": {"fsp": True}  # Enable fair scoring
}

# Execute (automatically includes S+M+L variants if enabled)
results = await runsApi.executeBatch(plan)
```

### 2. Analyze Results
```python
# Cost-quality analysis
cost_quality = await analytics_service.cost_quality_analysis(
    scenario="SOC_INCIDENT",
    models=["gpt-4o", "claude-3-5-sonnet"]
)

# Length bias detection  
length_bias = await analytics_service.length_bias_analysis(
    dimension="technical_accuracy"
)
```

### 3. Generate Adaptive Prompts
```python
# Generate prompts from policy documents
adaptive_prompts = await promptsApi.generateAdaptive({
    "policy_text": "Your SOC/GRC policy document...",
    "model_name": "llama-3.1-70b-versatile",
    "num_prompts": 10,
    "scenarios": ["SOC_INCIDENT", "GRC_MAPPING"]
})

# Validate with KL divergence
validation = await validationApi.klDivergence()
```

### 4. Export Data
```bash
# Export all runs with full metadata
curl -H "x-api-key: your_key" \
     "http://localhost:8000/export/runs.csv" > results.csv

# Export experiment summaries
curl -H "x-api-key: your_key" \
     "http://localhost:8000/export/experiments.csv" > experiments.csv
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)  
5. Open Pull Request

### Code Style
- **Python**: ruff + black + mypy
- **TypeScript**: eslint + prettier
- **Commits**: Conventional commits preferred

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Research Impact

*"CyberCQBench enables the first systematic study of prompt length effects on LLM cost-quality trade-offs in cybersecurity operations. With 300 research-grade prompts across controlled length variants, it makes cost–performance benchmarking as rigorous as penetration testing in modern SOC and compliance workflows."*

### Academic Applications
- **RQ1**: Analyze how prompt length influences LLM output quality and cost efficiency
- **RQ2**: Compare static vs adaptive benchmarking effectiveness
- **Bias Studies**: Quantify and mitigate verbosity bias in LLM evaluation
- **Reproducible Research**: Fixed seeds, dataset versioning, transparent scoring

## Availability

CyberCQBench is available as:
- **Open Research Tool**: This repository (MIT License)
- **Enterprise Service**: Contact for scalable, AWS-hosted version with Amazon Bedrock integration

## Acknowledgments

- **Research Foundation**: CySecBench (Wahréus, Hussain, & Papadimitratos, 2025) for cybersecurity rubric structure
- **Methodological Inspiration**: DefenderBench (Zhang et al., 2025) for SOC-like task diversity
- **Bias Mitigation**: "Same Evaluation, More Tokens" (Domhan & Zhu, 2025) for FSP implementation
- **Adaptive Benchmarking**: Chroma Generative Benchmarking (Hong et al., 2025) for query generation
- **Technical Stack**: FastAPI, React, MongoDB, OpenAI/Anthropic APIs, SciPy, Recharts
- **Academic Collaboration**: QUT School of Information Systems, Dr. Gowri Ramachandran

## Support

- **Issues**: GitHub Issues
- **Research Collaboration**: Dr. Gowri Ramachandran (g.ramachandran@qut.edu.au)
- **Documentation**: `/docs` endpoint when running
- **Industry Partnerships**: Contact for enterprise deployment

---

**CyberCQBench** - Cost-effective AI for SOC & Compliance
