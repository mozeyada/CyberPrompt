# CyberCQBench

**The most cost-effective and trustworthy AI models for high-stakes security and compliance tasks.**

CyberCQBench is a groundbreaking platform that enables Security Operations Center (SOC) analysts, compliance professionals, and cybersecurity researchers to identify which AI models provide the best value for money while staying compliant.

## 🎯 Why CyberCQBench?

As organizations adopt Large Language Models (LLMs) like GPT-4, Claude, and Gemini for incident analysis, compliance mapping, and threat intelligence reporting, one question remains unanswered: **Which AI is the most reliable, and at what cost?**

CyberCQBench solves this by:
1. **Cost-Quality Trade-offs**: Interactive analytics showing which models provide the best value per dollar
2. **7-Dimension SOC/GRC Rubric**: Evaluating accuracy, compliance alignment, risk awareness, and clarity
3. **Bias Mitigation with FSP**: Fair evaluation regardless of verbosity or token inflation
4. **Reproducible Pipelines**: Fixed seeds, dataset versioning, and transparent scoring
5. **Real-time Cost Tracking**: Token-level cost analysis for budget-conscious decisions

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites
- Docker & docker-compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- OpenAI and/or Anthropic API keys

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

### 3. Seed Sample Data
```bash
make seed
```

### 4. Access the Application
- **CyberCQBench UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8081

### 5. Run Your First Experiment
1. Navigate to **Experiments** tab
2. Configure your SOC/GRC evaluation
3. Select models to compare (GPT-4, Claude, etc.)
4. Execute and view cost-quality results

## 📊 Key Innovations

### 🎯 Bias Mitigation with FSP (Focus Sentence Prompting)
Ensures fair evaluation regardless of verbosity or token inflation. No more penalizing concise, high-quality responses.

### 📈 Cost-Quality Dashboards
Interactive analytics show which models provide the best value for money. Make data-driven decisions for your SOC budget.

### ⚡ Scalable Background Processing
Large experiments (>10 runs) execute in background to prevent timeouts. Small experiments get immediate feedback.

### 🔄 Adaptive Benchmarking
Prompts evolve with new threats, compliance updates, and live CTI feeds – keeping evaluations relevant to current cybersecurity landscape.

### 🛡️ 7-Dimension SOC/GRC Rubric
Every LLM output is evaluated across:
1. **Technical Accuracy**: Factual correctness in SOC/GRC context
2. **Actionability**: Can analysts act on it without extra steps?
3. **Completeness**: Covers all key aspects implied by task
4. **Compliance Alignment**: Aligns with policy/regulatory tone
5. **Risk Awareness**: Acknowledges risks, limitations, uncertainty
6. **Relevance**: Stays on-task with no digressions  
7. **Clarity**: Clear, structured, unambiguous writing

### 🔍 Reproducible Pipelines
Fixed seeds, dataset versioning, and transparent scoring allow repeatable research and audits.

### 🔗 Strong Data Relationships
Direct linking between experiment runs and LLM outputs for easy debugging and analysis.

## 🛠️ API Endpoints

### Prompts
- `POST /prompts/import` - Import prompt collections
- `GET /prompts` - List/search prompts with filters
- `GET /prompts/{id}` - Get specific prompt

### Runs  
- `POST /runs/plan` - Plan experiment matrix
- `POST /runs/execute/{id}` - Execute single run
- `POST /runs/execute/batch` - Execute multiple runs
- `GET /runs/{id}` - Get run results with output
- `GET /runs` - List runs with filters

### Analytics
- `GET /analytics/cost_quality` - Cost vs quality data
- `GET /analytics/length_bias` - Length bias analysis  
- `GET /analytics/risk_curves` - Risk metrics vs length
- `GET /analytics/adaptive_relevance` - Derived relevance slopes

## 🧪 Development

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

## 📁 Project Structure

```
/app/
  /api/               # FastAPI routers
  /core/              # Config, logging, security  
  /models/            # Pydantic schemas
  /db/                # MongoDB connection & repositories
  /services/          # Business logic (consolidated)
    analytics_service.py  # Cost-quality analytics
    background_jobs.py    # Background task processing
    base.py              # Judge implementations
    composite.py         # Rubric score calculations
    experiment.py        # Experiment orchestration
    fsp.py              # Focus Sentence Prompting
    llm_client.py       # LLM API integrations
    prompt_generator.py # Dynamic prompt creation
    prompts.py          # Evaluation prompt templates
    risk.py             # Risk assessment metrics
  /utils/             # Token counting, cost calculation, ULID

/ui/                  # React/Vite frontend
  /src/
    /components/      # Reusable UI components
    /pages/           # Route components  
    /api/             # API client
    /state/           # Zustand stores
    /types/           # TypeScript definitions

/tests/               # Backend tests
/ui-tests/            # Frontend tests  
/docker/              # Docker configuration
/scripts/             # Utility scripts (seeding, etc.)
```

## ❓ FAQ

**Q: Who is CyberCQBench for?**  
A: SOC analysts, compliance auditors, cybersecurity researchers, and enterprise AI teams evaluating LLMs for security operations.

**Q: What problem does it solve?**  
A: Current tools focus only on model accuracy or coverage. None integrate cost vs quality, SOC/GRC rubric scoring, and bias mitigation into one reproducible system.

**Q: How is this different from CySecBench, DefenderBench, or Chroma?**  
A: 
- **CySecBench** → Provided the rubric baseline, but static & cost-blind
- **DefenderBench** → Added SOC-like diversity, but no GRC scoring or token analysis  
- **Chroma** → Inspired adaptive query generation, but not tuned for cybersecurity
- **CyberCQBench** → Unifies all three with FSP bias mitigation + cost analytics for real-world SOC/GRC

**Q: How does it track cost vs quality?**  
A: Each evaluation logs tokens, API pricing, and 7-dimension rubric scores. Dashboards visualize cost–quality trade-offs per model, scenario, and task length.

**Q: Why is this important now?**  
A: AI adoption in SOC and GRC is exploding, but without transparent benchmarking, organizations risk overspending and failing compliance checks. CyberCQBench ensures responsible, cost-effective use.

## 🔧 Configuration

### Environment Variables (.env)
```bash
APP_ENV=dev
API_KEYS=key1,key2,key3
MONGO_URI=mongodb://mongo:27017
MONGO_DB=genai_bench

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Pricing (AUD per 1K tokens)
PRICE_INPUT.gpt4=0.03
PRICE_OUTPUT.gpt4=0.06
PRICE_INPUT.claude35=0.025
PRICE_OUTPUT.claude35=0.075
```

### Supported Models
- **OpenAI**: gpt-4, gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Anthropic**: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
- **Google**: gemini-2.5-flash (coming soon)
- **Extensible**: Add new providers via LLM client adapters

## 📈 Usage Examples

### 1. Plan and Execute Experiments
```python
# Plan runs
plan = {
    "prompts": ["prompt_id_1", "prompt_id_2"], 
    "models": ["gpt-4o", "claude-3-5-sonnet"],
    "repeats": 3,
    "bias_controls": {"fsp": True, "granularity_demo": True}
}

# Execute
run_ids = await experiment_service.plan_runs(plan)
results = await experiment_service.execute_batch(run_ids)
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

### 3. Export Data
```bash
curl -H "x-api-key: your_key" \
     "http://localhost:8000/exports/runs.csv" > results.csv
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)  
5. Open Pull Request

### Code Style
- **Python**: ruff + black + mypy
- **TypeScript**: eslint + prettier
- **Commits**: Conventional commits preferred

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎆 Impact Statement

*"CyberCQBench makes cost–performance benchmarking as critical as penetration testing in modern SOC and compliance workflows. It's not just about which AI is smarter – it's about which AI is smarter per dollar while staying compliant."*

## 📅 Availability

CyberCQBench is available as:
- **Open Research Tool**: This repository (MIT License)
- **Enterprise Service**: Contact for scalable, AWS-hosted version with Amazon Bedrock integration

## 🙏 Acknowledgments

- Inspired by CySecBench for cybersecurity rubric structure
- Built on FastAPI, React, and MongoDB for production reliability
- Uses OpenAI and Anthropic APIs for LLM inference
- Statistical analysis powered by SciPy
- Interactive charts powered by Recharts
- Research collaboration with QUT School of Information Systems

## 📞 Support

- **Issues**: GitHub Issues
- **Research Collaboration**: Dr. Gowri Ramachandran (g.ramachandran@qut.edu.au)
- **Documentation**: `/docs` endpoint when running
- **Industry Partnerships**: Contact for enterprise deployment

---

**CyberCQBench** - Cost-effective AI for SOC & Compliance 🛡️💰
