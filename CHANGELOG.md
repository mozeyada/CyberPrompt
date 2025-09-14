# CyberCQBench Changelog

## [1.2.0] - 2025-01-XX - Research Enhancement & Bug Fixes

### 🔧 **Critical Bug Fixes**

#### **1. Fixed FSP Implementation Bug** ⚠️
- **Issue**: Focus Sentence Prompting (FSP) code existed but wasn't properly integrated into judge evaluation
- **Fixed**: FSP now correctly implements sentence-based evaluation with full context for true length-invariant scoring
- **Impact**: Enables fair cost-quality comparison across models and prompt lengths
- **Files**: `app/services/base.py`

#### **2. Fixed KL Divergence Validation**
- **Issue**: KL divergence used incorrect source field ("static" vs "CySecBench")
- **Fixed**: Proper validation of adaptive prompts against CySecBench baseline for RQ2 research
- **Impact**: Accurate statistical validation for adaptive vs static benchmarking
- **Files**: `app/api/validation.py`

#### **3. Fixed Progress Bar Calculation**
- **Issue**: Benchmark runner progress didn't account for length variants multiplier
- **Fixed**: Progress calculation now correctly includes ×3 multiplier when variants enabled
- **Impact**: Accurate progress tracking during experiments
- **Files**: `ui/src/pages/BenchmarkRunner.tsx`

#### **4. Fixed Prompt Count Display**
- **Issue**: Prompt selector showed incorrect counts when length filters applied
- **Fixed**: Displays actual M and L variant prompts under selected originals
- **Impact**: Clear visibility of what will be tested when variants enabled
- **Files**: `ui/src/components/Selectors/PromptSelector.tsx`

### 🚀 **New Features**

#### **Groq API Integration**
- **Added**: Groq API support for cost-effective adaptive prompt generation
- **Models**: llama-3.1-70b-versatile, llama-3.1-8b-instant
- **Purpose**: Preserve OpenAI/Gemini quota while enabling RQ2 research
- **Files**: `app/services/groq_client.py`, `app/core/config.py`

#### **Adaptive Prompting System**
- **Added**: Complete adaptive prompt generation from policy documents
- **Features**: Text input processing, consistent data structure with static prompts
- **Integration**: Seamless integration with existing benchmark pipeline
- **Files**: `ui/src/pages/AdaptivePrompting.tsx`, `app/utils/adaptive_prompt_generator.py`

#### **Enhanced Analytics Dashboard**
- **Added**: FSP indicators (circles vs diamonds) on Overview page
- **Added**: 15-row recent runs table with length classification
- **Improved**: Streamlined verbose research explanations while maintaining statistical rigor
- **Files**: `ui/src/components/Charts/Overview.tsx`, `ui/src/pages/Insights.tsx`

### 📊 **Research Enhancements**

#### **Length Variant Analysis**
- **Enhanced**: Perfect traceability for S+M+L prompt groups (≤300, 301-800, >800 tokens)
- **Dataset**: 952 research-grade prompts (318 originals + 317 medium + 317 long variants)
- **Purpose**: Enables systematic RQ1 prompt length studies

#### **KL Divergence Validation**
- **Purpose**: Statistical validation for RQ2 comparing adaptive vs static prompt distributions
- **Implementation**: Proper scenario and length distribution analysis
- **Endpoint**: `GET /validation/kl-divergence`

### 🏗️ **Architecture Improvements**

#### **Database Layer Enhancement**
- **Structure**: Clean separation between API, services, and database layers
- **Pattern**: Repository pattern with 5 main repositories (Prompt, Run, OutputBlob, Baseline, SourceDocument)
- **Driver**: MongoDB with Motor async driver for optimal performance
- **Files**: `app/db/connection.py`, `app/db/repositories.py`

### 🔄 **API Enhancements**

#### **New Endpoints**
- `POST /prompts/adaptive/generate` - Generate adaptive prompts from policy documents
- `GET /validation/kl-divergence` - KL divergence between adaptive and static prompts

#### **Enhanced Endpoints**
- `GET /prompts` - Improved filtering with include_variants support
- `POST /runs/execute/batch` - Better progress tracking with variants

### 📚 **Documentation Updates**
- Updated README.md with Groq integration and adaptive prompting
- Added new API endpoints documentation
- Enhanced configuration examples
- Updated supported models list
- Added usage examples for adaptive prompting

### 🔬 **Research Validation**
- **RQ1**: Systematic prompt length effects on LLM cost-quality trade-offs
- **RQ2**: Adaptive vs static benchmarking effectiveness with statistical validation
- **Bias Studies**: True length-invariant scoring with fixed FSP implementation
- **Reproducibility**: Fixed seeds, dataset versioning, transparent scoring

---

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