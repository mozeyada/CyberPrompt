# Dataset Generation Guide

## Overview

CyberCQBench uses a **reproducible, academic-grade dataset** of 300 cybersecurity prompts (100 base prompts × 3 length variants: Short, Medium, Long) for RQ1 and RQ2 research.

The dataset is **already included** in this repository at `data/prompts.json`. You only need to regenerate it if you want to modify the scenarios or validate reproducibility.

---

## Quick Start (Use Existing Dataset)

The dataset is pre-generated and ready to use:

```bash
# Dataset is already at:
data/prompts.json

# Load it into MongoDB:
python scripts/import_cysecbench.py
```

**Note**: The research dataset import script `scripts/import_cysecbench.py` loads the complete 300-prompt dataset into MongoDB for research experiments.

---

## Regenerate Dataset (Optional)

### Prerequisites

1. **Python 3.11+** with dependencies:
```bash
pip install tiktoken
```

2. **Optional**: BOTS v3 dataset (only if you want to use real data sources)
   - Download from: https://github.com/splunk/botsv3
   - Extract to: `datasets/botsv3_data_set/`
   - **Note**: Script works without this (uses fallback data)

### Generate Dataset

```bash
# Run the generation script
python scripts/generate_research_dataset.py

# Output: data/prompts.json (300 prompts)
```

### What Gets Generated

**100 Base Prompts** across 3 scenarios:
- **50 SOC Incidents**: Ransomware, BEC, Insider Threat, APT, Cloud Breach
- **30 GRC Assessments**: GDPR, SOX, NIST CSF compliance
- **20 CTI Analysis**: Threat actor profiling, IOC analysis, strategic intelligence

**3 Length Variants** per base prompt:
- **Short (S)**: 250-350 tokens - Tactical responses (SOC L1/L2)
- **Medium (M)**: 350-500 tokens - Analytical plans (SOC L3/IR)
- **Long (L)**: 600-750 tokens - Executive briefings (CISO/Board)

**Total**: 300 prompts with controlled token distribution for RQ1 research

---

## Dataset Structure

```json
{
  "exported_at": "2025-01-15T10:30:00",
  "dataset_version": "20250115_academic_v2_realistic",
  "total_prompts": 300,
  "research_metadata": {
    "base_prompts": 100,
    "length_variants": ["S", "M", "L"],
    "scenarios": ["SOC_INCIDENT", "GRC_MAPPING", "CTI_SUMMARY"],
    "academic_validation": true,
    "industry_realistic": true
  },
  "prompts": [
    {
      "prompt_id": "academic_soc_001_s",
      "text": "Based on the incident below...",
      "scenario": "SOC_INCIDENT",
      "category": "Ransomware Incident",
      "length_bin": "S",
      "token_count": 287,
      "dataset_version": "20250115_academic_v2_realistic",
      "metadata": {
        "data_sources": ["symantec:ep:security:file", "firewall:logs"],
        "academic_grade": true
      }
    }
  ]
}
```

---

## Reproducibility

The script uses **fixed seed (42)** for academic reproducibility:

```python
random.seed(42)  # Ensures identical results across runs
```

Running the script multiple times produces **identical output** for research validation.

---

## Validation

After generation, validate the dataset:

```bash
# Check token distribution
python -c "
import json
with open('data/prompts.json') as f:
    data = json.load(f)
    for length in ['S', 'M', 'L']:
        prompts = [p for p in data['prompts'] if p['length_bin'] == length]
        avg_tokens = sum(p['token_count'] for p in prompts) / len(prompts)
        print(f'{length}: {len(prompts)} prompts, avg {avg_tokens:.0f} tokens')
"
```

**Expected Output**:
```
S: 100 prompts, avg 308 tokens
M: 100 prompts, avg 418 tokens
L: 100 prompts, avg 653 tokens
```

---

## Research Notes

### Why These Token Ranges?

Based on **real SOC/GRC operational workflows**:

- **Short (250-350)**: Tactical incident response during active attacks
  - Example: "Isolate host, block C2 IP, preserve memory"
  - User: SOC L1/L2 analysts under time pressure

- **Medium (350-500)**: Analytical investigation plans
  - Example: "Analyze malware, correlate logs, map to MITRE ATT&CK"
  - User: SOC L3/IR teams conducting forensics

- **Long (600-750)**: Strategic executive briefings
  - Example: "Board report with business impact, legal implications, remediation roadmap"
  - User: CISO/Board/Regulators requiring comprehensive analysis

### Why 100 Base Prompts?

- **Statistical significance**: n=100 per length bin for RQ1 analysis
- **Balanced distribution**: 50 SOC / 30 GRC / 20 CTI reflects real-world workload
- **Controlled experiments**: Each base prompt has S/M/L variants for direct comparison

---

## Customization

To modify scenarios or token ranges, edit `scripts/generate_research_dataset.py`:

```python
RESEARCH_CONFIG = {
    "total_base_prompts": 100,
    "length_variants": ["S", "M", "L"],
    "token_targets": {
        "S": (250, 350),  # Modify ranges here
        "M": (350, 500),
        "L": (600, 750)
    }
}
```

Then regenerate:
```bash
python scripts/generate_research_dataset.py
```

---

## Citation

If you use this dataset generation methodology in your research:

```bibtex
@software{cybercqbench2025,
  title={CyberCQBench: Cost-Quality Benchmarking for Cybersecurity AI},
  author={Zeyada, [Your Name]},
  year={2025},
  url={https://github.com/[your-repo]/CyberCQBench}
}
```

---

## Troubleshooting

**Issue**: Script fails with "BOTS dataset not found"
- **Solution**: Script uses fallback data. Ignore warning or download BOTS v3.

**Issue**: Token counts don't match expected ranges
- **Solution**: Ensure `tiktoken` is installed: `pip install tiktoken`

**Issue**: Different output on each run
- **Solution**: Check that `random.seed(42)` is set in the script

---

## Support

For questions about dataset generation:
- Open an issue on GitHub
- See `CALCULATION_AUDIT.md` for methodology details
- Check `README.md` for full project documentation
