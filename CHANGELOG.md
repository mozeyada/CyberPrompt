# CyberCQBench Changelog

## [1.1.0] - 2024-01-XX - Architecture Improvements

### 🔧 **Fixed Critical Issues**

#### **1. Strengthened Data Model Relationships**
- **Changed**: Renamed `Run.output_ref` → `Run.output_blob_id` for clearer relationship to `OutputBlob.blob_id`
- **Impact**: Improved data integrity and easier debugging of LLM responses
- **Files**: `app/models/__init__.py`, `app/api/runs.py`

#### **2. Implemented Background Task Processing**
- **Added**: Background execution for large experiment batches (>10 runs)
- **Added**: `app/services/background_jobs.py` for async task processing
- **Changed**: `/runs/execute/batch` endpoint now uses FastAPI BackgroundTasks
- **Impact**: Prevents timeout issues with large experiments, improves user experience
- **Files**: `app/api/runs.py`, `app/services/background_jobs.py`

#### **3. Removed Dangling Features**
- **Removed**: `Audit` and `AuditRequest` models (unused feature)
- **Removed**: `AuditRepository` class
- **Impact**: Cleaner codebase, no confusion about unimplemented features
- **Files**: `app/models/__init__.py`, `app/db/repositories.py`

#### **4. Reorganized Directory Structure**
- **Moved**: `app/analytics/` → `app/services/analytics_service.py`
- **Moved**: `app/evaluation/*` → `app/services/`
- **Moved**: `app/judges/*` → `app/services/`
- **Moved**: `app/research/*` → `app/services/`
- **Impact**: Consistent architecture with all business logic in `services/`
- **Files**: Multiple files reorganized and imports updated

### 🚀 **New Features**

#### **Scalable Experiment Processing**
- Small batches (≤10 runs): Execute synchronously for immediate feedback
- Large batches (>10 runs): Execute in background with status tracking
- Configurable concurrency (1-10 concurrent runs)
- HTTP 202 Accepted response for background jobs

### 📚 **Documentation Updates**
- Updated `PROJECT_ARCHITECTURE.md` with new directory structure
- Added background processing to data flow diagrams
- Updated API endpoint documentation
- Added scalable processing to core features
- Created `CHANGELOG.md` for tracking changes

### 🔄 **API Changes**

#### **Modified Endpoints**
- `POST /runs/execute/batch`: Now supports background processing
  - Returns immediate response for large batches
  - Includes `status: "accepted"` for background jobs
  - Maintains backward compatibility for small batches

#### **Enhanced Responses**
- `GET /runs/{id}`: Now properly links to OutputBlob content via `output_blob_id`

### 🏗️ **Internal Improvements**
- Consolidated business logic in `services/` directory
- Improved import organization
- Removed unused code and models
- Better separation of concerns

### ⚡ **Performance**
- Background processing prevents API timeouts
- Configurable concurrency for optimal resource usage
- Immediate feedback for small experiments

### 🔒 **Stability**
- Stronger data model relationships
- Removed potential confusion from unused features
- Cleaner, more maintainable codebase

---

## [1.0.0] - 2024-01-XX - Initial Release

### 🎉 **Initial Features**
- 7-dimension SOC/GRC rubric evaluation
- Cost-quality analysis with AUD pricing
- Focus Sentence Prompting (FSP) bias mitigation
- Support for OpenAI and Anthropic models
- Interactive React frontend
- MongoDB data persistence
- Docker containerization
- Research dataset integration (CySecBench)

### 🏗️ **Architecture**
- FastAPI backend with async MongoDB
- React + TypeScript frontend
- Pydantic data validation
- ULID-based unique identifiers
- RESTful API design

### 📊 **Analytics**
- Cost vs quality scatter plots
- Length bias analysis
- Risk assessment curves
- Model comparison dashboards

### 🔬 **Research Capabilities**
- Adaptive benchmarking
- Scenario-based evaluation
- Reproducible experiments
- Statistical analysis tools