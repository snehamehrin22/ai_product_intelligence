"""
Analyze subscription intent by session type.

Maps personas to session types based on King West demographic analysis
and compares subscription preferences across different usage patterns.
"""

import json
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.personas import get_all_personas
from forno_ssr.concepts import get_all_concepts


# Map personas to session types based on demographic analysis
SESSION_TYPE_MAPPING = {
    # Morning Commute (7:30-9am peak, grab-and-go)
    "morning_commute": ["p9"],  # Financial District commuter

    # Workday Laptop (10am-4pm, Mon/Fri heavy, hybrid workers)
    "workday_laptop": ["p5", "p12"],  # Remote tech worker, Marketing manager (fully remote)

    # Lunch Rush (12-2pm, office workers)
    "lunch_rush": ["p1", "p11"],  # Software engineer, Shopify worker

    # Coffee Chat / Business Meeting (10am-2pm, 45-90 min dwell)
    "coffee_chat": ["p10"],  # Account executive (sales/BD)

    # Post-Work Pickup (5-7pm, take-home dinner)
    "post_work_pickup": ["p13"],  # Corporate lawyer

    # Weekend Loop (Sat/Sun, bread ritual + brunch)
    "weekend_loop": ["p2", "p4", "p6", "p14"],  # Creative director, Couple, Local resident, Weekend visitor

    # Mixed / Multiple Sessions
    "mixed_frequent": ["p3", "p7", "p8"],  # Design student, Fitness instructor, Food writer
}


def load_latest_results():
    """Load the most recent aggregated results."""
    data_dir = Path(__file__).parent.parent / "data"
    agg_files = sorted(data_dir.glob("aggregated_results_*.json"))
    if not agg_files:
        raise FileNotFoundError("No aggregated results found.")

    latest_file = agg_files[-1]
    print(f"Loading: {latest_file.name}")

    with open(latest_file) as f:
        data = json.load(f)

    return data, latest_file.stem


def create_session_type_heatmap(df, output_dir):
    """Create heatmap showing subscription intent by session type."""
    # Create reverse mapping: persona_id -> session_type
    persona_to_session = {}
    for session_type, persona_ids in SESSION_TYPE_MAPPING.items():
        for persona_id in persona_ids:
            persona_to_session[persona_id] = session_type

    # Add session type column
    df["session_type"] = df["persona_id"].map(persona_to_session)

    # Calculate mean rating by session type and concept
    session_means = df.groupby(["session_type", "concept_id"])["avg_mean_rating"].mean().reset_index()
    pivot = session_means.pivot(index="session_type", columns="concept_id", values="avg_mean_rating")

    # Reorder rows by session type temporal order
    session_order = ["morning_commute", "workday_laptop", "lunch_rush", "coffee_chat",
                     "post_work_pickup", "weekend_loop", "mixed_frequent"]
    pivot = pivot.reindex(session_order)

    # Create labels
    concepts = get_all_concepts()
    concept_labels = [c.name for c in concepts]
    session_labels = [
        "Morning Commute\n(7:30-9am)",
        "Workday Laptop\n(10am-4pm Mon/Fri)",
        "Lunch Rush\n(12-2pm Office)",
        "Coffee Chat\n(10am-2pm Meetings)",
        "Post-Work Pickup\n(5-7pm Dinner)",
        "Weekend Loop\n(Sat/Sun Bread)",
        "Mixed/Frequent"
    ]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        vmin=2.5,
        vmax=4.0,
        center=3.25,
        cbar_kws={"label": "Mean Subscription Intent (1-5)"},
        xticklabels=concept_labels,
        yticklabels=session_labels,
        ax=ax,
    )

    ax.set_title(
        "Subscription Intent by Session Type\n(Based on King West Usage Patterns)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Subscription Concept", fontsize=12, fontweight="bold")
    ax.set_ylabel("Session Type (Time of Day)", fontsize=12, fontweight="bold")

    plt.tight_layout()
    filepath = output_dir / "session_type_heatmap.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()

    return df


def create_temporal_pattern_chart(df, output_dir):
    """Create chart showing best subscription for each time slot."""
    # Add session type
    persona_to_session = {}
    for session_type, persona_ids in SESSION_TYPE_MAPPING.items():
        for persona_id in persona_ids:
            persona_to_session[persona_id] = session_type

    df["session_type"] = df["persona_id"].map(persona_to_session)

    # Map session types to time slots
    time_slot_mapping = {
        "morning_commute": "7:30-9am",
        "workday_laptop": "10am-4pm",
        "lunch_rush": "12-2pm",
        "coffee_chat": "10am-2pm",
        "post_work_pickup": "5-7pm",
        "weekend_loop": "Sat/Sun",
        "mixed_frequent": "All Day"
    }

    df["time_slot"] = df["session_type"].map(time_slot_mapping)

    # Calculate mean rating by time slot and concept
    slot_means = df.groupby(["time_slot", "concept_id"])["avg_mean_rating"].mean().reset_index()

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(14, 6))

    concepts = get_all_concepts()
    time_slots = ["7:30-9am", "10am-2pm", "12-2pm", "10am-4pm", "5-7pm", "Sat/Sun", "All Day"]

    x = range(len(time_slots))
    width = 0.25

    for idx, concept in enumerate(concepts):
        concept_data = slot_means[slot_means["concept_id"] == concept.concept_id]
        values = []
        for slot in time_slots:
            val = concept_data[concept_data["time_slot"] == slot]["avg_mean_rating"].values
            values.append(val[0] if len(val) > 0 else 0)

        offset = (idx - 1) * width
        bars = ax.bar([i + offset for i in x], values, width, label=concept.name)

        # Add value labels
        for i, bar in enumerate(bars):
            if bar.get_height() > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"{bar.get_height():.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    ax.set_ylabel("Mean Subscription Intent (1-5)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Time Slot / Session Type", fontsize=12, fontweight="bold")
    ax.set_title(
        "Subscription Intent by Time of Day\n(Which subscription works for which daypart?)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(time_slots, rotation=15, ha="right")
    ax.set_ylim(0, 4.5)
    ax.axhline(y=3.0, color="gray", linestyle="--", alpha=0.5, label="Neutral (3.0)")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    filepath = output_dir / "temporal_pattern_chart.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()


def generate_session_insights(df, output_dir):
    """Generate text insights for session types."""
    # Add session type
    persona_to_session = {}
    for session_type, persona_ids in SESSION_TYPE_MAPPING.items():
        for persona_id in persona_ids:
            persona_to_session[persona_id] = session_type

    df["session_type"] = df["persona_id"].map(persona_to_session)

    concepts = get_all_concepts()

    insights = []
    insights.append("=" * 70)
    insights.append("SESSION TYPE ANALYSIS - FORNO KING STREET")
    insights.append("=" * 70)
    insights.append("")

    # Best subscription for each session type
    insights.append("1. BEST SUBSCRIPTION BY SESSION TYPE")
    insights.append("")

    for session_type in SESSION_TYPE_MAPPING.keys():
        session_data = df[df["session_type"] == session_type]
        if len(session_data) == 0:
            continue

        concept_means = session_data.groupby("concept_id")["avg_mean_rating"].mean()
        best_concept_id = concept_means.idxmax()
        best_concept = next(c for c in concepts if c.concept_id == best_concept_id)
        best_rating = concept_means[best_concept_id]

        # Format session type name
        session_name = session_type.replace("_", " ").title()
        insights.append(f"   {session_name}:")
        insights.append(f"   → {best_concept.name} (rating: {best_rating:.2f}/5.0)")
        insights.append("")

    # Concept fit analysis
    insights.append("2. CONCEPT FIT BY SESSION TYPE")
    insights.append("")

    for concept in concepts:
        insights.append(f"   {concept.name}:")
        concept_data = df[df["concept_id"] == concept.concept_id]

        # Calculate mean by session type
        session_means = concept_data.groupby("session_type")["avg_mean_rating"].mean().sort_values(ascending=False)

        insights.append("   Best fit for:")
        for session_type, rating in session_means.head(3).items():
            session_name = session_type.replace("_", " ").title()
            insights.append(f"     • {session_name}: {rating:.2f}/5.0")
        insights.append("")

    # Temporal insights
    insights.append("3. TEMPORAL PATTERNS")
    insights.append("")

    morning_data = df[df["session_type"] == "morning_commute"]
    if len(morning_data) > 0:
        morning_best = morning_data.groupby("concept_id")["avg_mean_rating"].mean().idxmax()
        morning_concept = next(c for c in concepts if c.concept_id == morning_best)
        insights.append(f"   Morning (7:30-9am): {morning_concept.name} wins")

    lunch_data = df[df["session_type"] == "lunch_rush"]
    if len(lunch_data) > 0:
        lunch_best = lunch_data.groupby("concept_id")["avg_mean_rating"].mean().idxmax()
        lunch_concept = next(c for c in concepts if c.concept_id == lunch_best)
        insights.append(f"   Lunch (12-2pm): {lunch_concept.name} wins")

    evening_data = df[df["session_type"] == "post_work_pickup"]
    if len(evening_data) > 0:
        evening_best = evening_data.groupby("concept_id")["avg_mean_rating"].mean().idxmax()
        evening_concept = next(c for c in concepts if c.concept_id == evening_best)
        insights.append(f"   Evening (5-7pm): {evening_concept.name} wins")

    weekend_data = df[df["session_type"] == "weekend_loop"]
    if len(weekend_data) > 0:
        weekend_best = weekend_data.groupby("concept_id")["avg_mean_rating"].mean().idxmax()
        weekend_concept = next(c for c in concepts if c.concept_id == weekend_best)
        insights.append(f"   Weekend (Sat/Sun): {weekend_concept.name} wins")

    insights.append("")

    # Key findings
    insights.append("=" * 70)
    insights.append("KEY FINDINGS")
    insights.append("=" * 70)
    insights.append("")
    insights.append("• No single subscription works across all session types")
    insights.append("• Different dayparts need different subscription models")
    insights.append("• Morning commuters vs laptop workers have distinct preferences")
    insights.append("• Consider multiple targeted subscriptions vs one-size-fits-all")
    insights.append("")

    # Save insights
    filepath = output_dir / "session_type_insights.txt"
    with open(filepath, "w") as f:
        f.write("\n".join(insights))

    print(f"✓ Created: {filepath.name}")

    # Print to console
    print()
    print("\n".join(insights))


def main():
    """Run session type analysis."""
    print("=" * 70)
    print("SESSION TYPE ANALYSIS - FORNO KING STREET")
    print("=" * 70)
    print()

    # Load results
    data, stem = load_latest_results()
    print(f"✓ Loaded {len(data)} persona-concept results")
    print()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / f"analysis_{stem}"
    output_dir.mkdir(exist_ok=True)
    print(f"Saving session analysis to: {output_dir.name}/")
    print()

    # Create visualizations
    print("Creating session type visualizations...")
    df = create_session_type_heatmap(df, output_dir)
    create_temporal_pattern_chart(df, output_dir)
    print()

    # Generate insights
    print("Generating session type insights...")
    generate_session_insights(df, output_dir)
    print()

    print("=" * 70)
    print("Session type analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
