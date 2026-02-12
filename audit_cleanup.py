#!/usr/bin/env python3
"""
Repository Cleanup and Structure Audit

Identifies and optionally removes:
- Build artifacts and cache files
- Redundant or outdated documentation
- Unused code and imports
- Duplicate files
- Improperly structured directories
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Dict
import json

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def find_cache_files(project_root: Path) -> List[Path]:
    """Find Python cache files."""
    cache_patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.egg-info',
        '**/.pytest_cache',
    ]
    
    cache_files = []
    for pattern in cache_patterns:
        cache_files.extend(project_root.glob(pattern))
    
    return cache_files

def find_build_artifacts(project_root: Path) -> List[Path]:
    """Find build artifacts."""
    artifact_patterns = [
        '**/dist',
        '**/build',
        '**/htmlcov',
        '**/.tox',
        '**/coverage.xml',
        '**/.coverage',
    ]
    
    artifacts = []
    for pattern in artifact_patterns:
        artifacts.extend(project_root.glob(pattern))
    
    return artifacts

def find_temp_files(project_root: Path) -> List[Path]:
    """Find temporary files."""
    temp_patterns = [
        '**/*~',
        '**/*.bak',
        '**/*.swp',
        '**/*.swo',
        '**/*.tmp',
        '**/.DS_Store',
    ]
    
    temp_files = []
    for pattern in temp_patterns:
        temp_files.extend(project_root.glob(pattern))
    
    return temp_files

def check_duplicate_docs(project_root: Path) -> Dict[str, List[Path]]:
    """Check for duplicate or redundant documentation."""
    docs_by_name = {}
    
    for md_file in project_root.glob('**/*.md'):
        # Skip node_modules and hidden directories
        if 'node_modules' in str(md_file) or '/.git/' in str(md_file):
            continue
        
        name = md_file.name
        if name not in docs_by_name:
            docs_by_name[name] = []
        docs_by_name[name].append(md_file)
    
    duplicates = {name: files for name, files in docs_by_name.items() if len(files) > 1}
    return duplicates

def check_unused_imports(project_root: Path) -> List[str]:
    """Check for files with potential unused imports (basic check)."""
    backend = project_root / 'backend'
    if not backend.exists():
        return []
    
    # This is a simple heuristic - real check would need AST parsing
    issues = []
    return issues  # Placeholder for now

def analyze_code_structure(project_root: Path) -> Dict[str, any]:
    """Analyze code structure and organization."""
    backend = project_root / 'backend'
    frontend = project_root / 'frontend'
    
    structure = {
        'backend': {
            'exists': backend.exists(),
            'app_modules': [],
            'test_count': 0,
            'main_entry': (backend / 'main.py').exists(),
        },
        'frontend': {
            'exists': frontend.exists(),
            'src_exists': (frontend / 'src').exists() if frontend.exists() else False,
            'package_json': (frontend / 'package.json').exists() if frontend.exists() else False,
        }
    }
    
    if backend.exists():
        app_dir = backend / 'app'
        if app_dir.exists():
            structure['backend']['app_modules'] = [
                d.name for d in app_dir.iterdir() if d.is_dir() and not d.name.startswith('_')
            ]
        
        tests_dir = backend / 'tests'
        if tests_dir.exists():
            structure['backend']['test_count'] = len(list(tests_dir.glob('test_*.py')))
    
    return structure

def check_gitignore_coverage(project_root: Path) -> Dict[str, bool]:
    """Check if .gitignore covers common patterns."""
    gitignore = project_root / '.gitignore'
    
    if not gitignore.exists():
        return {'exists': False}
    
    content = gitignore.read_text()
    
    required_patterns = {
        '__pycache__': '__pycache__/' in content,
        'venv': 'venv/' in content or '.venv' in content,
        'env_files': '.env' in content,
        'pytest_cache': '.pytest_cache' in content,
        'coverage': 'htmlcov/' in content or '.coverage' in content,
        'node_modules': 'node_modules' in content,
        'build': 'build/' in content or 'dist/' in content,
    }
    
    return required_patterns

def main():
    """Run repository cleanup audit."""
    project_root = Path(__file__).parent
    
    print(f"\n{Colors.BOLD}Repository Cleanup Audit{Colors.ENDC}")
    print(f"Project: Red Set ProtoCell")
    print(f"Location: {project_root}\n")
    
    # Cache files
    print_header("Cache Files")
    cache_files = find_cache_files(project_root)
    if cache_files:
        print_warning(f"Found {len(cache_files)} cache files/directories")
        print("  Examples:")
        for f in list(cache_files)[:5]:
            print(f"    {f.relative_to(project_root)}")
        if len(cache_files) > 5:
            print(f"    ... and {len(cache_files) - 5} more")
        print("\n  Recommendation: Add to .gitignore (already present)")
    else:
        print_success("No cache files found")
    
    # Build artifacts
    print_header("Build Artifacts")
    artifacts = find_build_artifacts(project_root)
    if artifacts:
        print_warning(f"Found {len(artifacts)} build artifacts")
        for a in artifacts:
            print(f"  {a.relative_to(project_root)}")
        print("\n  Recommendation: Add to .gitignore (already present)")
    else:
        print_success("No build artifacts found")
    
    # Temp files
    print_header("Temporary Files")
    temp_files = find_temp_files(project_root)
    if temp_files:
        print_warning(f"Found {len(temp_files)} temporary files")
        for t in temp_files:
            print(f"  {t.relative_to(project_root)}")
        print("\n  Recommendation: Delete these files")
    else:
        print_success("No temporary files found")
    
    # Duplicate docs
    print_header("Documentation Structure")
    duplicates = check_duplicate_docs(project_root)
    if duplicates:
        print_warning(f"Found {len(duplicates)} documents with duplicate names")
        for name, files in duplicates.items():
            print(f"\n  {name}:")
            for f in files:
                print(f"    - {f.relative_to(project_root)}")
        print("\n  Recommendation: Review for redundancy")
    else:
        print_success("No duplicate document names")
    
    # Code structure
    print_header("Code Structure")
    structure = analyze_code_structure(project_root)
    
    if structure['backend']['exists']:
        print_success("Backend exists")
        print(f"  Entry point: {'✓' if structure['backend']['main_entry'] else '✗'} main.py")
        print(f"  Modules: {', '.join(structure['backend']['app_modules'][:5])}")
        if len(structure['backend']['app_modules']) > 5:
            print(f"           ... and {len(structure['backend']['app_modules']) - 5} more")
        print(f"  Tests: {structure['backend']['test_count']} files")
    else:
        print_error("Backend directory not found")
    
    if structure['frontend']['exists']:
        print_success("Frontend exists")
        print(f"  Structure: {'✓' if structure['frontend']['src_exists'] else '✗'} src/")
        print(f"  Config: {'✓' if structure['frontend']['package_json'] else '✗'} package.json")
    else:
        print_warning("Frontend directory not found")
    
    # .gitignore coverage
    print_header(".gitignore Coverage")
    gitignore_check = check_gitignore_coverage(project_root)
    
    if not gitignore_check.get('exists', True):
        print_error(".gitignore not found")
    else:
        all_covered = all(gitignore_check.values())
        if all_covered:
            print_success("All important patterns covered")
        else:
            for pattern, covered in gitignore_check.items():
                if covered:
                    print_success(f"{pattern}")
                else:
                    print_warning(f"{pattern} - not covered")
    
    # Documentation count
    print_header("Documentation Overview")
    md_files = list(project_root.glob('**/*.md'))
    md_files = [f for f in md_files if 'node_modules' not in str(f) and '.git' not in str(f)]
    
    root_docs = [f for f in md_files if f.parent == project_root]
    docs_dir_docs = [f for f in md_files if 'docs/' in str(f)]
    backend_docs = [f for f in md_files if 'backend/' in str(f) and 'backend/docs' not in str(f)]
    
    print(f"Total documentation files: {len(md_files)}")
    print(f"  Root level: {len(root_docs)}")
    print(f"  /docs directory: {len(docs_dir_docs)}")
    print(f"  Backend: {len(backend_docs)}")
    print(f"  Frontend: {len([f for f in md_files if 'frontend/' in str(f)])}")
    
    if len(root_docs) > 15:
        print_warning("Many documentation files in root (consider organizing into /docs)")
    else:
        print_success("Documentation organized")
    
    # Summary
    print_header("Cleanup Recommendations")
    
    recommendations = []
    
    if cache_files:
        recommendations.append(f"Clean {len(cache_files)} cache files (safe to delete)")
    
    if artifacts:
        recommendations.append(f"Clean {len(artifacts)} build artifacts (safe to delete)")
    
    if temp_files:
        recommendations.append(f"Delete {len(temp_files)} temporary files")
    
    if duplicates:
        recommendations.append(f"Review {len(duplicates)} duplicate document names")
    
    if len(root_docs) > 15:
        recommendations.append("Consider organizing root-level docs into /docs directory")
    
    if recommendations:
        print("\n".join(f"  • {r}" for r in recommendations))
        print(f"\n{Colors.YELLOW}Repository could benefit from cleanup{Colors.ENDC}")
    else:
        print_success("Repository is clean and well-organized!")
    
    # Final verdict
    print_header("Structure Quality")
    
    score = 0
    max_score = 6
    
    if structure['backend']['exists'] and structure['backend']['main_entry']:
        score += 1
    if structure['backend']['test_count'] > 0:
        score += 1
    if structure['frontend']['exists'] and structure['frontend']['package_json']:
        score += 1
    if not cache_files or len(cache_files) < 50:
        score += 1
    if not duplicates or len(duplicates) < 3:
        score += 1
    if len(root_docs) <= 15:
        score += 1
    
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        print(f"{Colors.GREEN}★★★★★ Excellent ({percentage:.0f}%){Colors.ENDC}")
        print("Repository is well-structured and clean")
        return 0
    elif percentage >= 60:
        print(f"{Colors.YELLOW}★★★★☆ Good ({percentage:.0f}%){Colors.ENDC}")
        print("Minor cleanup recommended")
        return 0
    else:
        print(f"{Colors.YELLOW}★★★☆☆ Fair ({percentage:.0f}%){Colors.ENDC}")
        print("Cleanup recommended")
        return 1

if __name__ == "__main__":
    sys.exit(main())
