"""
Analyze Forno Cultura SSR survey results.

Creates visualizations and extracts insights from the survey data.
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.personas import get_all_personas, get_persona_by_id
from forno_ssr.concepts import get_all_concepts, get_concept_by_id


def load_latest_results():
    """Load the most recent aggregated results."""
    data_dir = Path(__file__).parent.parent / "data"

    # Find latest aggregated results file
    agg_files = sorted(data_dir.glob("aggregated_results_*.json"))
    if not agg_files:
        raise FileNotFoundError("No aggregated results found. Run run_survey.py first.")

    latest_file = agg_files[-1]
    print(f"Loading: {latest_file.name}")

    with open(latest_file) as f:
        data = json.load(f)

    return data, latest_file.stem


def create_heatmap(df, output_dir):
    """Create persona × concept heatmap of mean ratings."""
    personas = get_all_personas()
    concepts = get_all_concepts()

    # Create pivot table
    pivot = df.pivot(index="persona_id", columns="concept_id", values="avg_mean_rating")

    # Reorder rows and columns
    persona_order = [p.persona_id for p in personas]
    concept_order = [c.concept_id for c in concepts]
    pivot = pivot.reindex(index=persona_order, columns=concept_order)

    # Create better labels
    persona_labels = [f"{p.persona_id}\n{p.age}yo {p.role.split()[0]}" for p in personas]
    concept_labels = [f"{c.concept_id}\n{c.name.split()[0:2]}" for c in concepts]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Create heatmap
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        vmin=1.0,
        vmax=5.0,
        center=3.0,
        cbar_kws={"label": "Mean Subscription Intent (1-5)"},
        xticklabels=concept_labels,
        yticklabels=persona_labels,
        ax=ax,
    )

    ax.set_title(
        "Subscription Intent by Persona and Concept\n(Higher = More Likely to Subscribe)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Subscription Concept", fontsize=12, fontweight="bold")
    ax.set_ylabel("Customer Persona", fontsize=12, fontweight="bold")

    plt.tight_layout()
    filepath = output_dir / "heatmap_persona_concept.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()


def create_concept_comparison(df, output_dir):
    """Create bar chart comparing concepts across all personas."""
    concepts = get_all_concepts()

    # Calculate mean rating for each concept
    concept_means = df.groupby("concept_id")["avg_mean_rating"].mean().to_dict()
    concept_stds = df.groupby("concept_id")["avg_mean_rating"].std().to_dict()

    concept_names = [c.name for c in concepts]
    means = [concept_means[c.concept_id] for c in concepts]
    stds = [concept_stds[c.concept_id] for c in concepts]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(concepts))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=["#ff6b6b", "#4ecdc4", "#45b7d1"])

    # Add value labels on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{mean:.2f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_ylabel("Mean Subscription Intent (1-5)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Average Subscription Intent by Concept\n(Across All 8 Personas)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(concept_names, rotation=15, ha="right")
    ax.set_ylim(0, 5.5)
    ax.axhline(y=3.0, color="gray", linestyle="--", alpha=0.5, label="Neutral (3.0)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    filepath = output_dir / "concept_comparison.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()


def create_distribution_chart(data, output_dir):
    """Create probability distribution charts for each concept."""
    concepts = get_all_concepts()

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for idx, concept in enumerate(concepts):
        ax = axes[idx]

        # Get all results for this concept
        concept_data = [d for d in data if d["concept_id"] == concept.concept_id]

        # Average probability distribution across all personas
        avg_probs = {i: 0 for i in range(1, 6)}
        for d in concept_data:
            for rating in range(1, 6):
                avg_probs[rating] += d["avg_probability_distribution"][str(rating)]

        # Normalize
        total = len(concept_data)
        avg_probs = {k: v / total for k, v in avg_probs.items()}

        # Plot
        ratings = list(avg_probs.keys())
        probs = list(avg_probs.values())

        bars = ax.bar(ratings, probs, color=["#e74c3c", "#e67e22", "#f39c12", "#2ecc71", "#27ae60"])
        ax.set_xlabel("Subscription Intent Rating", fontweight="bold")
        ax.set_ylabel("Probability", fontweight="bold")
        ax.set_title(f"{concept.name}\n(Averaged across personas)", fontsize=10)
        ax.set_ylim(0, max(probs) * 1.2)
        ax.set_xticks(ratings)

        # Add value labels
        for bar, prob in zip(bars, probs):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{prob:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.suptitle(
        "Subscription Intent Probability Distributions by Concept",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    filepath = output_dir / "distribution_by_concept.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()


def create_persona_profiles(df, data, output_dir):
    """Create persona profile charts showing preferences."""
    personas = get_all_personas()

    # Calculate grid dimensions based on number of personas
    n_personas = len(personas)
    n_cols = 4
    n_rows = (n_personas + n_cols - 1) // n_cols  # Ceiling division

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 4))
    axes = axes.flatten()

    for idx, persona in enumerate(personas):
        ax = axes[idx]

        # Get ratings for this persona
        persona_data = df[df["persona_id"] == persona.persona_id]
        concepts = get_all_concepts()

        concept_names = [c.concept_id for c in concepts]
        ratings = [
            persona_data[persona_data["concept_id"] == c_id]["avg_mean_rating"].values[0]
            for c_id in concept_names
        ]

        # Plot
        bars = ax.barh(concept_names, ratings, color=["#3498db", "#9b59b6", "#e74c3c"])
        ax.set_xlabel("Mean Rating", fontsize=9)
        ax.set_title(
            f"{persona.persona_id}: {persona.age}yo {persona.role[:30]}", fontsize=9, fontweight="bold"
        )
        ax.set_xlim(0, 5)
        ax.axvline(x=3.0, color="gray", linestyle="--", alpha=0.5)

        # Add value labels
        for bar, rating in zip(bars, ratings):
            ax.text(
                rating + 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{rating:.2f}",
                va="center",
                fontsize=8,
            )

    # Hide unused subplots
    for idx in range(n_personas, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle(
        "Subscription Intent by Persona\n(Each persona's ratings across all 3 concepts)",
        fontsize=14,
        fontweight="bold",
        y=1.0,
    )
    plt.tight_layout()
    filepath = output_dir / "persona_profiles.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✓ Created: {filepath.name}")
    plt.close()


def generate_insights(df, data, output_dir):
    """Generate text insights and recommendations."""
    personas = get_all_personas()
    concepts = get_all_concepts()

    insights = []
    insights.append("=" * 70)
    insights.append("FORNO CULTURA SUBSCRIPTION SSR - KEY INSIGHTS")
    insights.append("=" * 70)
    insights.append("")

    # Overall winner
    concept_means = df.groupby("concept_id")["avg_mean_rating"].mean()
    best_concept_id = concept_means.idxmax()
    best_concept = get_concept_by_id(best_concept_id)
    insights.append("1. OVERALL BEST CONCEPT")
    insights.append(f"   Winner: {best_concept.name}")
    insights.append(f"   Average rating: {concept_means[best_concept_id]:.2f}/5.0")
    insights.append("")

    # Segment fit
    insights.append("2. SEGMENT FIT ANALYSIS")
    for concept in concepts:
        concept_df = df[df["concept_id"] == concept.concept_id]
        top_personas = concept_df.nlargest(3, "avg_mean_rating")

        insights.append(f"\n   {concept.name}:")
        insights.append(f"   Best fit for:")
        for _, row in top_personas.iterrows():
            persona = get_persona_by_id(row["persona_id"])
            insights.append(
                f"     • {persona.age}yo {persona.role} (rating: {row['avg_mean_rating']:.2f})"
            )

    insights.append("")

    # Qualitative themes (sample some responses)
    insights.append("3. SAMPLE QUALITATIVE RESPONSES")
    for concept in concepts[:1]:  # Just show first concept as example
        concept_data = [d for d in data if d["concept_id"] == concept.concept_id]
        insights.append(f"\n   {concept.name} - Sample feedback:")
        for i, d in enumerate(concept_data[:3]):
            insights.append(f"     {i+1}. \"{d['sample_responses'][0]}\"")

    insights.append("")
    insights.append("=" * 70)
    insights.append("RECOMMENDATION")
    insights.append("=" * 70)
    insights.append(f"Pilot {best_concept.name} at King Street for 3 months with:")
    insights.append("• Target demographic: Based on high-intent personas above")
    insights.append("• KPIs: Sign-ups, retention rate, add-on spend, NPS")
    insights.append("• Success threshold: 20+ subscribers in month 1")
    insights.append("")

    # Save insights
    filepath = output_dir / "insights_report.txt"
    with open(filepath, "w") as f:
        f.write("\n".join(insights))

    print(f"✓ Created: {filepath.name}")

    # Print to console
    print()
    print("\n".join(insights))


def main():
    """Run analysis."""
    print("=" * 70)
    print("ANALYZING FORNO SUBSCRIPTION SSR RESULTS")
    print("=" * 70)
    print()

    # Load results
    data, stem = load_latest_results()
    print(f"✓ Loaded {len(data)} persona-concept results")
    print()

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)

    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / f"analysis_{stem}"
    output_dir.mkdir(exist_ok=True)
    print(f"Saving outputs to: {output_dir.name}/")
    print()

    # Create visualizations
    print("Creating visualizations...")
    create_heatmap(df, output_dir)
    create_concept_comparison(df, output_dir)
    create_distribution_chart(data, output_dir)
    create_persona_profiles(df, data, output_dir)
    print()

    # Generate insights
    print("Generating insights...")
    generate_insights(df, data, output_dir)
    print()

    print("=" * 70)
    print(f"Analysis complete! Outputs saved to: {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
