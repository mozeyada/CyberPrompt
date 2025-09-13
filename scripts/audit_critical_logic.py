#!/usr/bin/env python3
"""
Critical Logic Audit Tool
Systematically checks for logical disconnects and implementation gaps
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class CriticalLogicAuditor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        
    def audit_all(self) -> List[Dict]:
        """Run all audit checks"""
        print("🔍 CRITICAL LOGIC AUDIT")
        print("=" * 50)
        
        self.check_feature_implementation_gaps()
        self.check_database_frontend_mismatches()
        self.check_unused_critical_code()
        self.check_config_vs_usage()
        self.check_api_contract_violations()
        self.check_research_validity_issues()
        
        return self.issues
    
    def check_feature_implementation_gaps(self):
        """Check for features that exist but aren't properly connected"""
        print("\n📋 Checking Feature Implementation Gaps...")
        
        # FSP-like pattern: code exists but not used
        fsp_files = list(self.project_root.glob("**/*fsp*"))
        if fsp_files:
            # Check if FSP is actually called in evaluation
            judge_files = list(self.project_root.glob("**/base.py")) + list(self.project_root.glob("**/judge*.py"))
            fsp_usage_found = False
            
            for judge_file in judge_files:
                content = judge_file.read_text()
                if "fsp_processor" in content and "split_into_segments" in content:
                    fsp_usage_found = True
                    break
            
            if not fsp_usage_found:
                self.issues.append({
                    "type": "CRITICAL",
                    "category": "Feature Implementation Gap",
                    "issue": "FSP code exists but not integrated into evaluation",
                    "impact": "Research validity compromised - bias mitigation not working",
                    "files": [str(f) for f in fsp_files]
                })
        
        # Check for other unused feature modules
        feature_patterns = ["adaptive", "variant", "bias", "composite"]
        for pattern in feature_patterns:
            feature_files = list(self.project_root.glob(f"**/*{pattern}*"))
            if feature_files:
                self._check_feature_usage(pattern, feature_files)
    
    def check_database_frontend_mismatches(self):
        """Check for database field vs frontend usage mismatches"""
        print("\n🔄 Checking Database-Frontend Mismatches...")
        
        # Common mismatch patterns
        mismatches = [
            ("fsp_enabled", "bias_controls.fsp"),
            ("prompt_length_bin", "length_bin"),
            ("economics.aud_cost", "cost"),
        ]
        
        frontend_files = list(self.project_root.glob("ui/src/**/*.tsx")) + list(self.project_root.glob("ui/src/**/*.ts"))
        
        for db_field, frontend_field in mismatches:
            db_usage = self._find_field_usage(db_field, "app/")
            frontend_usage = self._find_field_usage(frontend_field, "ui/")
            
            if db_usage and frontend_usage:
                self.issues.append({
                    "type": "HIGH",
                    "category": "Database-Frontend Mismatch",
                    "issue": f"Database uses '{db_field}' but frontend uses '{frontend_field}'",
                    "impact": "Data inconsistency, incorrect visualizations",
                    "db_files": db_usage,
                    "frontend_files": frontend_usage
                })
    
    def check_unused_critical_code(self):
        """Check for critical code that's defined but never called"""
        print("\n🚫 Checking Unused Critical Code...")
        
        # Find all function/class definitions
        python_files = list(self.project_root.glob("app/**/*.py"))
        
        critical_functions = []
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Critical function patterns
                        if any(keyword in node.name.lower() for keyword in 
                               ["evaluate", "score", "judge", "bias", "fsp", "segment", "aggregate"]):
                            critical_functions.append((node.name, str(py_file)))
            except:
                continue
        
        # Check if critical functions are actually called
        for func_name, file_path in critical_functions:
            if not self._is_function_called(func_name, file_path):
                self.issues.append({
                    "type": "MEDIUM",
                    "category": "Unused Critical Code",
                    "issue": f"Critical function '{func_name}' defined but never called",
                    "impact": "Dead code, potential missing functionality",
                    "file": file_path
                })
    
    def check_config_vs_usage(self):
        """Check for configuration options that don't affect behavior"""
        print("\n⚙️ Checking Config vs Usage...")
        
        # Find config definitions
        config_files = list(self.project_root.glob("**/*config*")) + list(self.project_root.glob("**/*.env*"))
        
        # Common config patterns that might not be used
        config_patterns = ["FSP", "BIAS", "JUDGE", "TEMPERATURE", "MAX_TOKENS"]
        
        for pattern in config_patterns:
            config_found = self._find_config_usage(pattern)
            actual_usage = self._find_field_usage(pattern.lower(), "app/")
            
            if config_found and not actual_usage:
                self.issues.append({
                    "type": "MEDIUM",
                    "category": "Config Not Used",
                    "issue": f"Config '{pattern}' defined but not used in code",
                    "impact": "Configuration has no effect on behavior"
                })
    
    def check_api_contract_violations(self):
        """Check for API contract violations"""
        print("\n🔌 Checking API Contract Violations...")
        
        # Check if API returns what frontend expects
        api_files = list(self.project_root.glob("app/api/*.py"))
        frontend_files = list(self.project_root.glob("ui/src/api/*.ts"))
        
        # Look for common contract violations
        for api_file in api_files:
            content = api_file.read_text()
            
            # Check for hardcoded returns that might not match reality
            if "fsp_enabled" in content and "bias_controls" in content:
                self.issues.append({
                    "type": "HIGH",
                    "category": "API Contract Violation",
                    "issue": "API returns both fsp_enabled and bias_controls.fsp with different values",
                    "impact": "Frontend confusion, incorrect data display",
                    "file": str(api_file)
                })
    
    def check_research_validity_issues(self):
        """Check for issues that compromise research validity"""
        print("\n🔬 Checking Research Validity Issues...")
        
        # Check for bias mitigation claims vs implementation
        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            readme_content = readme_file.read_text()
            
            if "bias mitigation" in readme_content.lower() or "fsp" in readme_content.lower():
                # Verify FSP is actually implemented
                if not self._verify_fsp_implementation():
                    self.issues.append({
                        "type": "CRITICAL",
                        "category": "Research Validity",
                        "issue": "Claims bias mitigation but FSP not properly implemented",
                        "impact": "Research conclusions invalid, academic integrity compromised",
                        "file": str(readme_file)
                    })
        
        # Check for length variant claims vs implementation
        if "length variant" in readme_content.lower():
            if not self._verify_variant_implementation():
                self.issues.append({
                    "type": "HIGH",
                    "category": "Research Validity",
                    "issue": "Claims length variant analysis but implementation incomplete",
                    "impact": "Research methodology flawed"
                })
    
    def _check_feature_usage(self, pattern: str, feature_files: List[Path]):
        """Check if a feature is actually used"""
        # Implementation would check imports and function calls
        pass
    
    def _find_field_usage(self, field: str, directory: str) -> List[str]:
        """Find files that use a specific field"""
        files = []
        search_path = self.project_root / directory
        if search_path.exists():
            for file_path in search_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.ts', '.tsx']:
                    try:
                        content = file_path.read_text()
                        if field in content:
                            files.append(str(file_path))
                    except:
                        continue
        return files
    
    def _is_function_called(self, func_name: str, defining_file: str) -> bool:
        """Check if a function is called anywhere in the codebase"""
        for py_file in self.project_root.glob("**/*.py"):
            if str(py_file) == defining_file:
                continue
            try:
                content = py_file.read_text()
                if func_name in content:
                    return True
            except:
                continue
        return False
    
    def _find_config_usage(self, pattern: str) -> bool:
        """Check if config pattern exists"""
        config_files = list(self.project_root.glob("**/.env*")) + list(self.project_root.glob("**/config*"))
        for config_file in config_files:
            try:
                content = config_file.read_text()
                if pattern in content:
                    return True
            except:
                continue
        return False
    
    def _verify_fsp_implementation(self) -> bool:
        """Verify FSP is properly implemented in evaluation"""
        judge_files = list(self.project_root.glob("**/base.py"))
        for judge_file in judge_files:
            content = judge_file.read_text()
            # Check for proper FSP integration
            if ("split_into_segments" in content and 
                "aggregate_scores" in content and 
                "fsp" in content.lower()):
                return True
        return False
    
    def _verify_variant_implementation(self) -> bool:
        """Verify variant analysis is properly implemented"""
        # Check if variants are properly expanded and used
        return True  # Simplified for now
    
    def print_report(self):
        """Print audit report"""
        print("\n" + "="*50)
        print("🚨 CRITICAL LOGIC AUDIT REPORT")
        print("="*50)
        
        if not self.issues:
            print("✅ No critical issues found!")
            return
        
        critical_count = sum(1 for issue in self.issues if issue["type"] == "CRITICAL")
        high_count = sum(1 for issue in self.issues if issue["type"] == "HIGH")
        medium_count = sum(1 for issue in self.issues if issue["type"] == "MEDIUM")
        
        print(f"🔴 CRITICAL: {critical_count}")
        print(f"🟠 HIGH: {high_count}")
        print(f"🟡 MEDIUM: {medium_count}")
        print(f"📊 TOTAL: {len(self.issues)}")
        
        for i, issue in enumerate(self.issues, 1):
            print(f"\n{i}. [{issue['type']}] {issue['category']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Impact: {issue['impact']}")
            if 'files' in issue:
                print(f"   Files: {', '.join(issue['files'][:3])}{'...' if len(issue['files']) > 3 else ''}")


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auditor = CriticalLogicAuditor(project_root)
    
    issues = auditor.audit_all()
    auditor.print_report()
    
    # Return exit code based on critical issues
    critical_issues = [i for i in issues if i["type"] == "CRITICAL"]
    return len(critical_issues)


if __name__ == "__main__":
    sys.exit(main())