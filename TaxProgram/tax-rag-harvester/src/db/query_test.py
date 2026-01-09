"""
Query Test Module

Tests and validates RAG retrieval quality with tax-specific queries.
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional

import yaml

from .schema import TaxVectorDB

logger = logging.getLogger(__name__)


@dataclass
class TestQuery:
    """A test query with expected results."""
    query: str
    expected_content: list[str]  # Keywords that should appear
    expected_form: Optional[str] = None
    category: str = "general"
    difficulty: str = "medium"


# Test queries organized by category
TEST_QUERIES = {
    "factual": [
        TestQuery(
            query="What is the standard deduction for single filers?",
            expected_content=["standard deduction", "single", "$14,600"],
            expected_form="1040",
            category="factual",
            difficulty="easy"
        ),
        TestQuery(
            query="What is the HSA contribution limit for family coverage?",
            expected_content=["HSA", "family", "contribution", "limit"],
            expected_form="8889",
            category="factual",
            difficulty="easy"
        ),
        TestQuery(
            query="What is the maximum IRA contribution for someone under 50?",
            expected_content=["IRA", "contribution", "limit"],
            category="factual",
            difficulty="medium"
        ),
    ],
    "procedural": [
        TestQuery(
            query="How do I report HSA distributions on my tax return?",
            expected_content=["Form 8889", "distribution", "line"],
            expected_form="8889",
            category="procedural",
            difficulty="medium"
        ),
        TestQuery(
            query="What forms do I need if I sold stock this year?",
            expected_content=["Schedule D", "Form 8949", "capital"],
            category="procedural",
            difficulty="medium"
        ),
        TestQuery(
            query="How do I claim the child tax credit?",
            expected_content=["child tax credit", "Schedule 8812"],
            category="procedural",
            difficulty="medium"
        ),
    ],
    "scenario": [
        TestQuery(
            query="I'm self-employed and work from home. What can I deduct?",
            expected_content=["home office", "Schedule C", "business"],
            category="scenario",
            difficulty="hard"
        ),
        TestQuery(
            query="My child is in college. What education credits am I eligible for?",
            expected_content=["education", "credit", "Form 8863"],
            category="scenario",
            difficulty="hard"
        ),
        TestQuery(
            query="I received a 1099-NEC as a freelancer. How do I report this income?",
            expected_content=["Schedule C", "self-employment", "1099"],
            category="scenario",
            difficulty="medium"
        ),
    ],
    "edge_cases": [
        TestQuery(
            query="What if I can't pay my taxes by April 15?",
            expected_content=["extension", "penalty", "payment"],
            category="edge_cases",
            difficulty="medium"
        ),
        TestQuery(
            query="I got married mid-year. How do I file?",
            expected_content=["married", "filing", "joint"],
            category="edge_cases",
            difficulty="medium"
        ),
    ]
}


class QueryTester:
    """Tests retrieval quality against known queries."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.db = TaxVectorDB(config_path)
    
    def run_query(self, test: TestQuery, n_results: int = 5) -> dict:
        """Run a single test query and evaluate results."""
        results = self.db.query(
            query_text=test.query,
            form_number=test.expected_form,
            n_results=n_results
        )
        
        # Evaluate results
        evaluation = {
            "query": test.query,
            "category": test.category,
            "difficulty": test.difficulty,
            "num_results": len(results['documents']),
            "expected_content": test.expected_content,
            "found_content": [],
            "relevance_scores": [],
            "passed": False
        }
        
        # Check if expected content appears in results
        all_text = ' '.join(results['documents']).lower()
        
        for expected in test.expected_content:
            if expected.lower() in all_text:
                evaluation['found_content'].append(expected)
        
        # Calculate relevance score
        if test.expected_content:
            relevance = len(evaluation['found_content']) / len(test.expected_content)
            evaluation['relevance_scores'].append(relevance)
            evaluation['passed'] = relevance >= 0.5  # At least 50% of expected content found
        
        # Add result details
        evaluation['results'] = []
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        )):
            evaluation['results'].append({
                "rank": i + 1,
                "distance": dist,
                "source": meta.get('source_doc', ''),
                "form": meta.get('form_number', ''),
                "preview": doc[:200] + "..." if len(doc) > 200 else doc
            })
        
        return evaluation
    
    def run_suite(self, categories: Optional[list[str]] = None) -> dict:
        """Run a suite of test queries."""
        if categories is None:
            categories = list(TEST_QUERIES.keys())
        
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "by_category": {},
            "by_difficulty": {"easy": [], "medium": [], "hard": []},
            "evaluations": []
        }
        
        for category in categories:
            if category not in TEST_QUERIES:
                continue
            
            category_results = {"passed": 0, "failed": 0}
            
            for test in TEST_QUERIES[category]:
                evaluation = self.run_query(test)
                results['evaluations'].append(evaluation)
                results['total'] += 1
                
                if evaluation['passed']:
                    results['passed'] += 1
                    category_results['passed'] += 1
                else:
                    results['failed'] += 1
                    category_results['failed'] += 1
                
                results['by_difficulty'][test.difficulty].append(evaluation['passed'])
            
            results['by_category'][category] = category_results
        
        return results
    
    def print_report(self, results: dict):
        """Print a formatted test report."""
        print("\n" + "=" * 60)
        print("TAX RAG RETRIEVAL TEST REPORT")
        print("=" * 60)
        
        # Overall stats
        total = results['total']
        passed = results['passed']
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nOverall: {passed}/{total} passed ({pass_rate:.1f}%)")
        
        # By category
        print("\nBy Category:")
        for category, stats in results['by_category'].items():
            cat_total = stats['passed'] + stats['failed']
            cat_rate = (stats['passed'] / cat_total * 100) if cat_total > 0 else 0
            status = "✓" if cat_rate >= 80 else "⚠" if cat_rate >= 50 else "✗"
            print(f"  {status} {category}: {stats['passed']}/{cat_total} ({cat_rate:.0f}%)")
        
        # By difficulty
        print("\nBy Difficulty:")
        for diff, outcomes in results['by_difficulty'].items():
            if outcomes:
                diff_passed = sum(outcomes)
                diff_total = len(outcomes)
                diff_rate = (diff_passed / diff_total * 100)
                print(f"  {diff}: {diff_passed}/{diff_total} ({diff_rate:.0f}%)")
        
        # Failed queries
        failed_evals = [e for e in results['evaluations'] if not e['passed']]
        if failed_evals:
            print("\nFailed Queries:")
            for eval in failed_evals[:5]:  # Show first 5
                print(f"\n  Query: {eval['query']}")
                print(f"  Expected: {eval['expected_content']}")
                print(f"  Found: {eval['found_content']}")
                if eval['results']:
                    print(f"  Top result: {eval['results'][0]['source']}")
        
        print("\n" + "=" * 60)
    
    def interactive_query(self):
        """Interactive query mode for manual testing."""
        print("\n=== Interactive Tax Query Mode ===")
        print("Type 'quit' to exit\n")
        
        while True:
            query = input("Query: ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            results = self.db.query(query_text=query, n_results=5)
            
            print(f"\nFound {len(results['documents'])} results:\n")
            
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'],
                results['metadatas'],
                results['distances']
            ), 1):
                print(f"--- Result {i} (distance: {dist:.4f}) ---")
                print(f"Source: {meta.get('source_doc', 'unknown')}")
                print(f"Form: {meta.get('form_number', 'N/A')}")
                print(f"Section: {meta.get('section', 'N/A')}")
                print(f"Topics: {meta.get('topics', 'N/A')}")
                print(f"\n{doc[:500]}...")
                print()


def main():
    """Main entry point."""
    import sys
    
    tester = QueryTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            tester.interactive_query()
        elif sys.argv[1] == '--suite':
            categories = sys.argv[2:] if len(sys.argv) > 2 else None
            results = tester.run_suite(categories)
            tester.print_report(results)
        elif sys.argv[1] == '--query':
            query = ' '.join(sys.argv[2:])
            test = TestQuery(query=query, expected_content=[])
            evaluation = tester.run_query(test)
            print(json.dumps(evaluation, indent=2))
    else:
        # Run full suite by default
        results = tester.run_suite()
        tester.print_report(results)


if __name__ == "__main__":
    main()
