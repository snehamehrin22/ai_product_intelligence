"""
Interactive carousel creation pipeline.

Sequential workflow:
1. Load research → Apply framework → Review
2. Select carousel angle → Generate draft → Review
3. Tighten prose → Review
4. Capture feedback at each step
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.framework_analyzer import (
    analyze_research,
    display_analysis_summary
)
from src.carousel_pipeline.carousel_generator import (
    generate_carousel,
    display_carousel
)
from src.carousel_pipeline.schemas import (
    FrameworkAnalysis,
    CarouselContent,
    StepFeedback,
    CarouselFeedback
)

load_dotenv()


def get_user_feedback(step_name: str) -> StepFeedback:
    """Capture user feedback for a pipeline step."""
    print("\n" + "="*70)
    print(f"📝 FEEDBACK: {step_name.upper().replace('_', ' ')}")
    print("="*70)

    # Quality rating
    while True:
        try:
            rating = int(input("\n⭐ Quality rating (1-5): "))
            if 1 <= rating <= 5:
                break
            print("   Please enter a number between 1 and 5")
        except ValueError:
            print("   Please enter a valid number")

    # Approval
    while True:
        approved_input = input("✅ Approve this step? (y/n): ").lower()
        if approved_input in ['y', 'n']:
            approved = approved_input == 'y'
            break
        print("   Please enter 'y' or 'n'")

    # Issues
    issues = []
    print("\n🔍 Issues identified (press Enter on empty line when done):")
    while True:
        issue = input("   • ")
        if not issue.strip():
            break
        issues.append(issue.strip())

    # Optional details
    what_was_wrong = None
    what_was_missing = None
    notes = None

    if not approved or issues:
        print("\n📋 Optional details:")
        wrong = input("   What was wrong? (Enter to skip): ")
        if wrong.strip():
            what_was_wrong = wrong.strip()

        missing = input("   What was missing? (Enter to skip): ")
        if missing.strip():
            what_was_missing = missing.strip()

        note = input("   Additional notes? (Enter to skip): ")
        if note.strip():
            notes = note.strip()

    return StepFeedback(
        step_name=step_name,
        quality_rating=rating,
        approved=approved,
        issues=issues,
        what_was_wrong=what_was_wrong,
        what_was_missing=what_was_missing,
        notes=notes
    )


def save_feedback(feedback: CarouselFeedback, output_path: str):
    """Save feedback to JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(feedback.model_dump(), indent=2, default=str),
        encoding="utf-8"
    )
    print(f"\n💾 Feedback saved to: {output_path}")


def main():
    """Run interactive carousel pipeline."""

    if len(sys.argv) < 2:
        print("Usage: python scripts/interactive_carousel_pipeline.py <research_file.md>")
        print("\nExample:")
        print("  python scripts/interactive_carousel_pipeline.py '/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Content/Research/App Research/eight_sleep.md'")
        sys.exit(1)

    research_path = sys.argv[1]
    research_name = Path(research_path).stem

    # Configuration
    pillar_id = "growth_loops_are_changing"
    framework_path = "prompts/frameworks/growth_loops_teardown_framework.md"

    print("\n" + "="*70)
    print("🚀 INTERACTIVE CAROUSEL PIPELINE")
    print("="*70)
    print(f"\nProduct: {research_name}")
    print(f"Research: {Path(research_path).name}")
    print(f"Pillar: {pillar_id}")
    print(f"\nThis workflow has 3 steps:")
    print("  1. Framework Analysis")
    print("  2. Carousel Generation (Claude draft)")
    print("  3. Prose Tightening (ChatGPT)")
    print(f"\nYou'll review and provide feedback after each step.")

    input("\n⏎  Press Enter to start...")

    # Initialize feedback
    session_feedback = CarouselFeedback(
        product_name=research_name,
        research_file=research_path,
        pillar_used=pillar_id,
        started_at=datetime.now()
    )

    # Output paths
    analysis_output = f"data/analysis_outputs/{research_name}_framework_analysis.json"
    carousel_output = f"data/carousel_outputs/{research_name}_carousel.json"
    feedback_output = f"data/feedback/{research_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        # ====================================================================
        # STEP 1: Framework Analysis
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 1: FRAMEWORK ANALYSIS")
        print("="*70)

        analysis = analyze_research(
            research_path=research_path,
            pillar_id=pillar_id,
            framework_path=framework_path,
            output_path=analysis_output
        )

        display_analysis_summary(analysis)

        # Get feedback
        framework_feedback = get_user_feedback("framework_analysis")
        session_feedback.framework_analysis_feedback = framework_feedback

        if not framework_feedback.approved:
            print("\n⚠️  Framework analysis not approved. Stopping pipeline.")
            print("   You can manually edit the analysis JSON and re-run carousel generation.")
            save_feedback(session_feedback, feedback_output)
            sys.exit(0)

        # ====================================================================
        # STEP 2: Select Carousel Angle
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 2: SELECT CAROUSEL ANGLE")
        print("="*70)

        print(f"\nThe framework identified {len(analysis.carousel_angles)} potential angles:")
        for i, angle in enumerate(analysis.carousel_angles, 1):
            print(f"\n  {i}. {angle}")

        while True:
            try:
                angle_choice = int(input(f"\nSelect angle (1-{len(analysis.carousel_angles)}): "))
                if 1 <= angle_choice <= len(analysis.carousel_angles):
                    break
                print(f"   Please enter a number between 1 and {len(analysis.carousel_angles)}")
            except ValueError:
                print("   Please enter a valid number")

        carousel_angle = analysis.carousel_angles[angle_choice - 1]
        print(f"\n✓ Selected: {carousel_angle}")

        # ====================================================================
        # STEP 3: Generate Carousel
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 3: CAROUSEL GENERATION")
        print("="*70)

        carousel = generate_carousel(
            analysis=analysis,
            carousel_angle=carousel_angle,
            product_name=research_name,
            output_path=carousel_output
        )

        display_carousel(carousel)

        # Get feedback
        carousel_feedback = get_user_feedback("carousel_draft")
        session_feedback.carousel_draft_feedback = carousel_feedback

        if not carousel_feedback.approved:
            print("\n⚠️  Carousel draft not approved. You can:")
            print("   1. Manually edit the carousel JSON")
            print("   2. Re-run with different angle")
            print("   3. Adjust prompts based on feedback")
            save_feedback(session_feedback, feedback_output)
            sys.exit(0)

        # ====================================================================
        # STEP 4: Final Review
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 4: FINAL REVIEW")
        print("="*70)

        print("\n📋 Carousel ready for publication!")
        print(f"📁 Saved to: {carousel_output}")

        # Overall success rating
        while True:
            try:
                success_rating = int(input("\n⭐ Overall success rating (1-5): "))
                if 1 <= success_rating <= 5:
                    break
                print("   Please enter a number between 1 and 5")
            except ValueError:
                print("   Please enter a valid number")

        # Published?
        while True:
            published_input = input("📤 Will you publish this? (y/n): ").lower()
            if published_input in ['y', 'n']:
                published = published_input == 'y'
                break
            print("   Please enter 'y' or 'n'")

        # Update feedback
        session_feedback.success_rating = success_rating
        session_feedback.published = published
        session_feedback.completed_at = datetime.now()

        # Calculate time
        duration = (session_feedback.completed_at - session_feedback.started_at).total_seconds() / 60
        session_feedback.time_to_complete = duration

        # Save final feedback
        save_feedback(session_feedback, feedback_output)

        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE")
        print("="*70)
        print(f"\n⏱️  Time: {duration:.1f} minutes")
        print(f"⭐ Success: {success_rating}/5")
        print(f"📤 Publishing: {'Yes' if published else 'No'}")
        print(f"\n📁 Files:")
        print(f"   • Analysis: {analysis_output}")
        print(f"   • Carousel: {carousel_output}")
        print(f"   • Feedback: {feedback_output}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        session_feedback.completed_at = datetime.now()
        save_feedback(session_feedback, feedback_output)
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session_feedback.completed_at = datetime.now()
        save_feedback(session_feedback, feedback_output)
        sys.exit(1)


if __name__ == "__main__":
    main()
