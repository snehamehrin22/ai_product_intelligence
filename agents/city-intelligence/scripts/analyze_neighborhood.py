#!/usr/bin/env python3
"""
Neighborhood Intelligence CLI

Analyzes a neighborhood through 15-section deep intelligence framework.

Usage:
    python scripts/analyze_neighborhood.py --neighborhood "King Street West" --city "Toronto"
    python scripts/analyze_neighborhood.py --neighborhood "King Street West" --city "Toronto" --output json,markdown
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from city_intelligence.analyzers.neighborhood_intelligence import NeighborhoodIntelligenceAnalyzer
from rich.console import Console
from rich.table import Table

console = Console()


def save_json_report(report, output_dir: Path, neighborhood: str):
    """Save report as JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{neighborhood.lower().replace(' ', '_')}_intelligence_{timestamp}.json"
    filepath = output_dir / filename

    # Convert to dict for JSON serialization
    report_dict = report.model_dump(mode='json')

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ JSON report saved to: {filepath}[/green]")
    return filepath


def save_markdown_report(report, output_dir: Path, neighborhood: str):
    """Save report as Markdown."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{neighborhood.lower().replace(' ', '_')}_intelligence_{timestamp}.md"
    filepath = output_dir / filename

    # Generate markdown
    md = f"""# Neighborhood Intelligence Report: {report.neighborhood_name}

**City:** {report.city.name}, {report.city.country}
**Report Date:** {report.report_date.strftime('%Y-%m-%d')}
**Time Period:** {report.time_period}

---

## Executive Summary

### One-Sentence Summary
{report.one_sentence_summary}

### Neighborhood Story
{report.neighborhood_story}

### Defining Forces

**Human Needs:**
{report.defining_human_needs}

**Economic Forces:**
{report.defining_economic_forces}

**Cultural Forces:**
{report.defining_cultural_forces}

**Why Cafés Succeed/Fail Here:**
{report.cafe_success_factors}

---

## 1. Neighborhood Identity

**Known For:** {report.identity.known_for}

**Resident Description:** {report.identity.resident_description}

**Outsider Description:** {report.identity.outsider_description}

**Emotions Evoked:** {report.identity.emotions_evoked}

**Cultural Uniqueness:** {report.identity.cultural_uniqueness}

**Defining Values:** {report.identity.defining_values}

**Stereotypes:** {report.identity.stereotypes}

**Café Implications:** {report.identity.cafe_implications}

---

## 2. Historical Evolution

**Development History:** {report.historical_evolution.development_history}

**Major Events:** {report.historical_evolution.major_events}

**Immigration History:** {report.historical_evolution.immigration_history}

**Shaping Industries:** {report.historical_evolution.shaping_industries}

**Turning Points:** {report.historical_evolution.turning_points}

**Gentrification Patterns:** {report.historical_evolution.gentrification_patterns}

**Business Evolution:** {report.historical_evolution.business_evolution}

**Identity Changes:** {report.historical_evolution.identity_changes}

**Café Implications:** {report.historical_evolution.cafe_implications}

---

## 3. Demographics

**Population Growth:** {report.demographics.population_growth}

**Age Distribution:** {report.demographics.age_distribution}

**Income Levels:** {report.demographics.income_levels}

**Education Levels:** {report.demographics.education_levels}

**Household Composition:** {report.demographics.household_composition}

**Renters vs Owners:** {report.demographics.renters_vs_owners}

**Housing Types:** {report.demographics.housing_types}

**Household Size:** {report.demographics.household_size}

**Immigration Patterns:** {report.demographics.immigration_patterns}

**Languages Spoken:** {report.demographics.languages_spoken}

**Family Structure:** {report.demographics.family_structure}

**Business Influence:** {report.demographics.business_influence}

**Café Implications:** {report.demographics.cafe_implications}

---

## 4. Economic Landscape

**Commercial Rents:** {report.economics.commercial_rents}

**Residential Rents:** {report.economics.residential_rents}

**Office Occupancy:** {report.economics.office_occupancy}

**Remote Work Impact:** {report.economics.remote_work_impact}

**Major Employers:** {report.economics.major_employers}

**Employment Mix:** {report.economics.employment_mix}

**Consumer Spending:** {report.economics.consumer_spending}

**Vacancy Rates:** {report.economics.vacancy_rates}

**Independent vs Chains:** {report.economics.independent_vs_chains}

**Luxury vs Budget:** {report.economics.luxury_vs_budget}

**Economic Forces:** {report.economics.economic_forces}

**Café Implications:** {report.economics.cafe_implications}

---

## 5. Business Ecosystem

**Business Mix:** {report.business_ecosystem.business_mix}

**Clustering Patterns:** {report.business_ecosystem.clustering_patterns}

**Reinforcement:** {report.business_ecosystem.reinforcement}

**Competition:** {report.business_ecosystem.competition}

**Foot Traffic Drivers:** {report.business_ecosystem.foot_traffic_drivers}

**Café Implications:** {report.business_ecosystem.cafe_implications}

---

## 6. Human Movement

**Morning Patterns:** {report.human_movement.morning_patterns}

**Lunch Patterns:** {report.human_movement.lunch_patterns}

**Afternoon Patterns:** {report.human_movement.afternoon_patterns}

**Evening Patterns:** {report.human_movement.evening_patterns}

**Weekend Patterns:** {report.human_movement.weekend_patterns}

**Tourist Patterns:** {report.human_movement.tourist_patterns}

**Commuter Patterns:** {report.human_movement.commuter_patterns}

**Resident Patterns:** {report.human_movement.resident_patterns}

**Student Patterns:** {report.human_movement.student_patterns}

**Worker Patterns:** {report.human_movement.worker_patterns}

**Foot Traffic Origin:** {report.human_movement.foot_traffic_origin}

**Foot Traffic Destination:** {report.human_movement.foot_traffic_destination}

**Highest Activity Streets:** {report.human_movement.highest_activity_streets}

**Café Implications:** {report.human_movement.cafe_implications}

---

## 7. Third Place Analysis

**Third Place Adequacy:** {report.third_places.third_place_adequacy}

**Gathering Spots:** {report.third_places.gathering_spots}

**Lingering Spots:** {report.third_places.lingering_spots}

**Stranger Interaction:** {report.third_places.stranger_interaction}

**Community Formation:** {report.third_places.community_formation}

**Existing Social Infrastructure:** {report.third_places.existing_social_infrastructure}

**Missing Infrastructure:** {report.third_places.missing_infrastructure}

**Café Implications:** {report.third_places.cafe_implications}

---

## 8. Behavioral Patterns

**Recurring Behaviors:** {report.behavioral_patterns.recurring_behaviors}

**Neighborhood Rhythms:** {report.behavioral_patterns.neighborhood_rhythms}

**Café Implications:** {report.behavioral_patterns.cafe_implications}

---

## 9. Cultural Signals

**Expressed Values:** {report.cultural_signals.expressed_values}

**Value Manifestations:** {report.cultural_signals.value_manifestations}

**Café Implications:** {report.cultural_signals.cafe_implications}

---

## 10. Macro Trends

**Shaping Trends:** {report.macro_trends.shaping_trends}

**Accelerating Trends:** {report.macro_trends.accelerating_trends}

**Declining Trends:** {report.macro_trends.declining_trends}

**Café Implications:** {report.macro_trends.cafe_implications}

---

## 11. Neighborhood Needs

**Unmet Needs:**
"""

    for need in report.neighborhood_needs.unmet_needs:
        md += f"\n- **{need.need}** (Confidence: {need.confidence})\n  - Evidence: {need.evidence}\n"

    md += f"\n**Café Implications:** {report.neighborhood_needs.cafe_implications}\n\n---\n\n"

    md += f"""## 12. Future Outlook

**3-Year Outlook:** {report.future_outlook.three_year_outlook}

**5-Year Outlook:** {report.future_outlook.five_year_outlook}

**10-Year Outlook:** {report.future_outlook.ten_year_outlook}

**Population Changes:** {report.future_outlook.population_changes}

**Housing Changes:** {report.future_outlook.housing_changes}

**Transit Changes:** {report.future_outlook.transit_changes}

**Retail Changes:** {report.future_outlook.retail_changes}

**Commercial Changes:** {report.future_outlook.commercial_changes}

**Cultural Changes:** {report.future_outlook.cultural_changes}

**Technology Changes:** {report.future_outlook.technology_changes}

**Consumer Behavior Changes:** {report.future_outlook.consumer_behavior_changes}

**Business Types to Succeed:** {report.future_outlook.business_types_to_succeed}

**Café Implications:** {report.future_outlook.cafe_implications}

---

## 13. Café Implications

**Ideal Café Type:** {report.cafe_implications.ideal_cafe_type}

**Ideal Customer:** {report.cafe_implications.ideal_customer}

**Ideal Experience:** {report.cafe_implications.ideal_experience}

**Product Priorities:** {report.cafe_implications.product_priorities}

**What to Avoid:** {report.cafe_implications.what_to_avoid}

**Differentiation:** {report.cafe_implications.differentiation}

---

## 14. Strategic Insights

**Pre-Lease Insights:** {report.strategic_insights.pre_lease_insights}

**Outsider Mistakes:** {report.strategic_insights.outsider_mistakes}

**Critical Dynamics:** {report.strategic_insights.critical_dynamics}

**Invisible Opportunities:** {report.strategic_insights.invisible_opportunities}

---

## Limitations

"""

    for limitation in report.limitations:
        md += f"- {limitation}\n"

    md += f"\n---\n\n*Report generated {report.report_date.strftime('%Y-%m-%d %H:%M:%S')}*\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md)

    console.print(f"[green]✓ Markdown report saved to: {filepath}[/green]")
    return filepath


def main():
    """Run neighborhood intelligence analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze a neighborhood using 15-section intelligence framework"
    )
    parser.add_argument(
        "--neighborhood",
        required=True,
        help="Neighborhood name (e.g., 'King Street West')"
    )
    parser.add_argument(
        "--city",
        required=True,
        help="City name (e.g., 'Toronto')"
    )
    parser.add_argument(
        "--country",
        default="Canada",
        help="Country name (default: Canada)"
    )
    parser.add_argument(
        "--output",
        default="json,markdown",
        help="Output formats (comma-separated: json,markdown)"
    )

    args = parser.parse_args()

    # Parse output formats
    output_formats = [fmt.strip() for fmt in args.output.split(",")]

    # Initialize analyzer
    try:
        analyzer = NeighborhoodIntelligenceAnalyzer()
    except Exception as e:
        console.print(f"[red]Error initializing analyzer: {e}[/red]")
        console.print("[yellow]Make sure OPENAI_API_KEY is set in .env file[/yellow]")
        sys.exit(1)

    # Run analysis
    city_metadata = {
        "country": args.country,
        "region": None,
        "population": None,
        "timezone": None
    }

    try:
        report = analyzer.run_full_analysis(
            neighborhood=args.neighborhood,
            city=args.city,
            city_metadata=city_metadata
        )
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Save outputs
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    if "json" in output_formats:
        filepath = save_json_report(report, output_dir, args.neighborhood)
        saved_files.append(filepath)

    if "markdown" in output_formats or "md" in output_formats:
        filepath = save_markdown_report(report, output_dir, args.neighborhood)
        saved_files.append(filepath)

    # Print summary table
    console.print("\n[bold]Analysis Summary:[/bold]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim")
    table.add_column("Value")

    table.add_row("Neighborhood", args.neighborhood)
    table.add_row("City", args.city)
    table.add_row("Sections Analyzed", "15")
    table.add_row("Tokens Used", f"{analyzer.total_tokens:,}")
    table.add_row("Estimated Cost", f"${analyzer.total_cost:.2f}")
    table.add_row("Files Generated", str(len(saved_files)))

    console.print(table)

    console.print(f"\n[green bold]✓ Analysis complete![/green bold]")
    console.print(f"\n[cyan]One-sentence summary:[/cyan]")
    console.print(f"[italic]{report.one_sentence_summary}[/italic]\n")


if __name__ == "__main__":
    main()
