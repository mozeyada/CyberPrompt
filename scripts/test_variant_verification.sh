#!/bin/bash
# Quick test script to verify variant testing instrumentation

echo "=========================================="
echo "Variant Testing Verification - Quick Test"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Backend is running"
else
    echo "   ✗ Backend is not running"
    echo "   Please start the backend first: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. This script will:"
echo "   - Find a prompt with variants (_s, _m, _l)"
echo "   - Run 3 tests (one per variant)"
echo "   - Show [VARIANT-CHECK] logs"
echo "   - Verify variants are different"
echo ""

# Find a prompt with variants
echo "3. Looking for prompts with variants in database..."
echo "   (This requires MongoDB connection)"
echo ""
echo "   Manual steps:"
echo "   a) Go to the UI: http://localhost:3000"
echo "   b) Navigate to 'Benchmark Runner' or 'RQ1 Flow'"
echo "   c) Select 1 prompt"
echo "   d) Enable 'Include length variants'"
echo "   e) Select 1 model (e.g., gpt-4o-mini)"
echo "   f) Enable 'Ensemble evaluation'"
echo "   g) Click 'Run Experiment'"
echo ""

echo "4. While the experiment runs, monitor logs:"
echo ""
echo "   # In another terminal, run:"
echo "   docker logs -f backend | grep '\[VARIANT-CHECK\]'"
echo ""
echo "   or if running locally:"
echo "   tail -f backend.log | grep '\[VARIANT-CHECK\]'"
echo ""

echo "5. What to look for in logs:"
echo ""
echo "   ✓ Prompt lengths should differ (S: ~200, M: ~500, L: ~900)"
echo "   ✓ Response lengths should differ"
echo "   ✓ Each run should have unique blob_id"
echo "   ✓ Scores should improve S→M→L (by 0.3-1.0 points)"
echo "   ✓ Standard deviation > 0 (judges disagree)"
echo ""

echo "6. After experiment completes, save logs:"
echo ""
echo "   docker logs backend 2>&1 | grep '\[VARIANT-CHECK\]' > variant_check_logs.txt"
echo ""
echo "   Then analyze with:"
echo "   cat variant_check_logs.txt"
echo ""

echo "=========================================="
echo "For detailed analysis, see:"
echo "  - IMPLEMENTATION_SUMMARY.md"
echo "  - VARIANT_TESTING_VERIFICATION_GUIDE.md"
echo "=========================================="


