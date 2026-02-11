"""
Feedback analysis and learning module.

Analyzes captured feedback to identify patterns and suggest prompt improvements.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter, defaultdict

from .schemas import CarouselFeedback, StepFeedback


def load_all_feedback(feedback_dir: str = "data/feedback") -> List[CarouselFeedback]:
    """Load all feedback files from directory."""
    feedback_path = Path(feedback_dir)
    if not feedback_path.exists():
        return []

    feedback_files = list(feedback_path.glob("*.json"))
    feedbacks = []

    for file in feedback_files:
        data = json.loads(file.read_text(encoding="utf-8"))
        feedbacks.append(CarouselFeedback(**data))

    return feedbacks


def analyze_step_performance(feedbacks: List[CarouselFeedback]) -> Dict[str, Any]:
    """Analyze performance by pipeline step."""
    step_stats = defaultdict(lambda: {
        "count": 0,
        "approved_count": 0,
        "avg_rating": 0.0,
        "ratings": [],
        "common_issues": []
    })

    for feedback in feedbacks:
        for step_name in ["framework_analysis", "carousel_draft", "final_tightening"]:
            step_feedback: StepFeedback = getattr(feedback, f"{step_name}_feedback", None)

            if step_feedback:
                stats = step_stats[step_name]
                stats["count"] += 1
                stats["ratings"].append(step_feedback.quality_rating)

                if step_feedback.approved:
                    stats["approved_count"] += 1

                stats["common_issues"].extend(step_feedback.issues)

    # Calculate averages
    for step_name, stats in step_stats.items():
        if stats["count"] > 0:
            stats["avg_rating"] = sum(stats["ratings"]) / len(stats["ratings"])
            stats["approval_rate"] = stats["approved_count"] / stats["count"]

            # Count issue frequency
            issue_counter = Counter(stats["common_issues"])
            stats["top_issues"] = issue_counter.most_common(5)

    return dict(step_stats)


def analyze_pillar_performance(feedbacks: List[CarouselFeedback]) -> Dict[str, Any]:
    """Analyze performance by content pillar."""
    pillar_stats = defaultdict(lambda: {
        "count": 0,
        "published_count": 0,
        "avg_success": 0.0,
        "success_ratings": [],
        "avg_time": 0.0,
        "times": []
    })

    for feedback in feedbacks:
        pillar = feedback.pillar_used
        stats = pillar_stats[pillar]

        stats["count"] += 1
        stats["success_ratings"].append(feedback.success_rating)

        if feedback.published:
            stats["published_count"] += 1

        if feedback.time_to_complete:
            stats["times"].append(feedback.time_to_complete)

    # Calculate averages
    for pillar, stats in pillar_stats.items():
        if stats["count"] > 0:
            stats["avg_success"] = sum(stats["success_ratings"]) / len(stats["success_ratings"])
            stats["publish_rate"] = stats["published_count"] / stats["count"]

        if stats["times"]:
            stats["avg_time"] = sum(stats["times"]) / len(stats["times"])

    return dict(pillar_stats)


def identify_improvement_areas(feedbacks: List[CarouselFeedback]) -> List[Dict[str, Any]]:
    """Identify top areas for improvement based on feedback."""
    improvements = []

    # Analyze each step
    step_stats = analyze_step_performance(feedbacks)

    for step_name, stats in step_stats.items():
        if stats["count"] == 0:
            continue

        # Low approval rate
        if stats["approval_rate"] < 0.7:
            improvements.append({
                "priority": "high",
                "area": step_name,
                "issue": f"Low approval rate: {stats['approval_rate']:.1%}",
                "evidence": f"{stats['approved_count']}/{stats['count']} approved",
                "top_issues": stats["top_issues"][:3]
            })

        # Low rating
        if stats["avg_rating"] < 3.5:
            improvements.append({
                "priority": "high",
                "area": step_name,
                "issue": f"Low quality rating: {stats['avg_rating']:.1f}/5",
                "evidence": f"Average from {len(stats['ratings'])} sessions",
                "top_issues": stats["top_issues"][:3]
            })

        # Common issues
        if stats["top_issues"] and stats["top_issues"][0][1] > 2:
            improvements.append({
                "priority": "medium",
                "area": step_name,
                "issue": f"Recurring issue: {stats['top_issues'][0][0]}",
                "evidence": f"Occurred {stats['top_issues'][0][1]} times",
                "suggestion": "Update prompt to explicitly address this"
            })

    return improvements


def generate_feedback_report(feedback_dir: str = "data/feedback") -> Dict[str, Any]:
    """Generate comprehensive feedback report."""
    feedbacks = load_all_feedback(feedback_dir)

    if not feedbacks:
        return {
            "total_sessions": 0,
            "message": "No feedback data found"
        }

    return {
        "total_sessions": len(feedbacks),
        "published_count": sum(1 for f in feedbacks if f.published),
        "publish_rate": sum(1 for f in feedbacks if f.published) / len(feedbacks),
        "avg_success_rating": sum(f.success_rating for f in feedbacks) / len(feedbacks),
        "avg_time_minutes": sum(f.time_to_complete for f in feedbacks if f.time_to_complete) / len([f for f in feedbacks if f.time_to_complete]) if any(f.time_to_complete for f in feedbacks) else 0,
        "step_performance": analyze_step_performance(feedbacks),
        "pillar_performance": analyze_pillar_performance(feedbacks),
        "improvement_areas": identify_improvement_areas(feedbacks)
    }


def display_feedback_report(report: Dict[str, Any]):
    """Display feedback report."""
    print("\n" + "="*70)
    print("📊 FEEDBACK ANALYSIS REPORT")
    print("="*70)

    if report.get("total_sessions", 0) == 0:
        print("\n❌ No feedback data found")
        return

    # Overall metrics
    print(f"\n📈 Overall Metrics:")
    print(f"   • Total Sessions: {report['total_sessions']}")
    print(f"   • Published: {report['published_count']} ({report['publish_rate']:.1%})")
    print(f"   • Avg Success Rating: {report['avg_success_rating']:.1f}/5")
    if report['avg_time_minutes'] > 0:
        print(f"   • Avg Time: {report['avg_time_minutes']:.1f} minutes")

    # Step performance
    print(f"\n🔍 Step Performance:")
    for step_name, stats in report['step_performance'].items():
        if stats['count'] > 0:
            print(f"\n   {step_name.replace('_', ' ').title()}:")
            print(f"      • Sessions: {stats['count']}")
            print(f"      • Approval Rate: {stats['approval_rate']:.1%}")
            print(f"      • Avg Rating: {stats['avg_rating']:.1f}/5")
            if stats['top_issues']:
                print(f"      • Top Issue: {stats['top_issues'][0][0]} ({stats['top_issues'][0][1]}x)")

    # Pillar performance
    print(f"\n🎯 Pillar Performance:")
    for pillar, stats in report['pillar_performance'].items():
        print(f"\n   {pillar.replace('_', ' ').title()}:")
        print(f"      • Sessions: {stats['count']}")
        print(f"      • Publish Rate: {stats['publish_rate']:.1%}")
        print(f"      • Avg Success: {stats['avg_success']:.1f}/5")
        if stats['avg_time'] > 0:
            print(f"      • Avg Time: {stats['avg_time']:.1f} min")

    # Improvement areas
    if report['improvement_areas']:
        print(f"\n⚠️  Improvement Areas ({len(report['improvement_areas'])}):")
        for i, improvement in enumerate(report['improvement_areas'][:5], 1):
            print(f"\n   {i}. [{improvement['priority'].upper()}] {improvement['area'].replace('_', ' ').title()}")
            print(f"      Issue: {improvement['issue']}")
            print(f"      Evidence: {improvement['evidence']}")
            if improvement.get('suggestion'):
                print(f"      Suggestion: {improvement['suggestion']}")

    print("\n" + "="*70)
