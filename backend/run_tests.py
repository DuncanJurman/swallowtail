#!/usr/bin/env python3
"""
Test runner script for Swallowtail backend tests.

This script provides an easy way to run different categories of tests with various options.
It wraps pytest commands with sensible defaults and category-based test selection.

USAGE:
    python run_tests.py [category] [options]

CATEGORIES:
    all         - Run all tests
    unit        - Run unit tests only (fast, isolated component tests)
    integration - Run integration tests (component interaction with real services)
    crews       - Run crew tests (CrewAI crew implementations)
    flows       - Run flow tests (CrewAI flow orchestrations)
    infra       - Run infrastructure tests (database, storage, task queue)
    services    - Run service tests (external service integrations)
    agents      - Run agent tests (individual agent implementations)
    e2e         - Run end-to-end tests (complete user journeys)
    workflows   - Run workflow tests (legacy workflow patterns)

OPTIONS:
    -v, --verbose    - Verbose output showing individual test names
    -c, --coverage   - Generate coverage report (HTML and terminal)
    -k PATTERN       - Run only tests matching the given pattern
    -m MARKER        - Run only tests with specific pytest marker
    -s               - Show print statements during test execution
    --slow           - Include slow tests (excluded by default except for 'all')
    -l, --list       - List all available test categories
    --help           - Show this help message

EXAMPLES:
    python run_tests.py                     # Show available categories
    python run_tests.py all                 # Run all tests
    python run_tests.py unit -v             # Run unit tests with verbose output
    python run_tests.py integration -c      # Run integration tests with coverage
    python run_tests.py crews -k "evaluation"  # Run crew tests matching "evaluation"
    python run_tests.py e2e -s              # Run e2e tests showing print output
    python run_tests.py infra --slow        # Run infrastructure tests including slow ones

NOTES:
    - Tests are run using Poetry's virtual environment
    - Coverage reports are saved to htmlcov/ directory
    - Slow tests are excluded by default (except when running 'all')
    - Exit code matches pytest's exit code (0 for success)
"""

import sys
import subprocess
import argparse
from pathlib import Path


# Test category mappings
CATEGORIES = {
    'all': 'tests/',
    'unit': 'tests/unit/',
    'integration': 'tests/integration/',
    'crews': 'tests/crews/',
    'flows': 'tests/flows/',
    'infra': 'tests/infrastructure/',
    'infrastructure': 'tests/infrastructure/',
    'services': 'tests/services/',
    'agents': 'tests/agents/',
    'e2e': 'tests/e2e/',
    'workflows': 'tests/workflows/',
}

# Category descriptions
DESCRIPTIONS = {
    'all': 'All tests',
    'unit': 'Unit tests - Fast, isolated component tests',
    'integration': 'Integration tests - Component interaction tests',
    'crews': 'Crew tests - CrewAI crew implementation tests',
    'flows': 'Flow tests - CrewAI flow tests',
    'infra': 'Infrastructure tests - Database, storage, Celery tests',
    'services': 'Service tests - External service integration tests',
    'agents': 'Agent tests - Individual agent tests',
    'e2e': 'End-to-End tests - Complete user journey tests',
    'workflows': 'Workflow tests - Legacy workflow tests',
}


def build_pytest_command(category: str, args: argparse.Namespace) -> list:
    """Build the pytest command with appropriate arguments."""
    cmd = ['poetry', 'run', 'pytest']
    
    # Add test path
    test_path = CATEGORIES.get(category, 'tests/')
    cmd.append(test_path)
    
    # Add verbose flag
    if args.verbose:
        cmd.append('-v')
    
    # Add coverage
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # Add pattern matching
    if args.pattern:
        cmd.extend(['-k', args.pattern])
    
    # Add marker
    if args.marker:
        cmd.extend(['-m', args.marker])
    
    # Show print statements
    if args.show_output:
        cmd.append('-s')
    
    # Add slow tests
    if not args.slow and category != 'all':
        cmd.extend(['-m', 'not slow'])
    
    return cmd


def list_categories():
    """Print available test categories."""
    print("\nAvailable test categories:\n")
    print(f"{'Category':<15} {'Description'}")
    print("-" * 60)
    
    for cat in ['all'] + sorted([k for k in CATEGORIES.keys() if k != 'all']):
        if cat in DESCRIPTIONS:
            print(f"{cat:<15} {DESCRIPTIONS[cat]}")
    
    print("\nUse 'python run_tests.py <category>' to run tests")
    print("Use 'python run_tests.py --help' for more options\n")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description='Run Swallowtail backend tests by category',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'category',
        nargs='?',
        choices=list(CATEGORIES.keys()),
        help='Test category to run'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose test output'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Run with coverage report'
    )
    
    parser.add_argument(
        '-k', '--pattern',
        help='Run tests matching the given pattern'
    )
    
    parser.add_argument(
        '-m', '--marker',
        help='Run tests with specific marker'
    )
    
    parser.add_argument(
        '-s', '--show-output',
        action='store_true',
        help='Show print statements during tests'
    )
    
    parser.add_argument(
        '--slow',
        action='store_true',
        help='Include slow tests'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available test categories'
    )
    
    args = parser.parse_args()
    
    # Handle list option
    if args.list or not args.category:
        list_categories()
        return 0
    
    # Build pytest command
    cmd = build_pytest_command(args.category, args)
    
    # Print what we're running
    print(f"\n🧪 Running {DESCRIPTIONS.get(args.category, args.category)}...")
    print(f"📍 Command: {' '.join(cmd)}\n")
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())