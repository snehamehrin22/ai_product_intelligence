"""
King Street West Neighborhood Intelligence

Analyzes King Street West (Toronto) through 4-lens framework:
- Anthropology: Culture, rituals, identity
- Economics: Spending power, affordability
- Geopolitics: Migration, policy, global forces
- History: Evolution, cycles, parallels

Outputs JSON report with business insights.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from city_intelligence.schemas import (
    City,
    Trend,
    DataSource,
    AnthropologyAnalysis,
    EconomicsAnalysis,
    GeopoliticsAnalysis,
    HistoryAnalysis,
    MultiLensAnalysis,
    BusinessInsight,
    BusinessOpportunity,
    BusinessThreat,
    CityIntelligenceReport
)

load_dotenv()
console = Console()


class KingStreetWestAnalyzer:
    """Analyzes King Street West neighborhood using 4-lens framework."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"

        # Neighborhood context
        self.neighborhood_context = """
King Street West is a major commercial corridor in downtown Toronto, running from University Ave to Dufferin St.

**Key Characteristics:**
- Entertainment District (John St to Spadina): Nightlife, theaters, restaurants
- Financial District (University to Yonge): Corporate, lunch spots, after-work bars
- Fashion District (Spadina to Bathurst): Mix of old garment industry, new condos, trendy cafes
- Liberty Village boundary (west of Bathurst): Transitional area

**Demographics:**
- Heavy weekday foot traffic from office workers (pre/post-pandemic)
- Weekend crowds for entertainment/dining
- Increasing condo dweller population (young professionals, 25-40)

**Historical Context:**
- Once dominated by entertainment venues (clubs, bars, restaurants)
- Significant condo development 2010-2020
- COVID impact: Many entertainment venues closed, office workers went remote
- Current state: Mixed signals - some revival, some persistent vacancies

**Observable Trends (pre-analysis):**
- Shift from late-night entertainment to daytime cafes/brunch spots
- More health/wellness-oriented businesses
- Fewer traditional bars, more "elevated casual" dining
- Persistent retail vacancies, especially on side streets
"""

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts/ directory."""
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            # Fallback to inline prompts if files don't exist yet
            return self._get_fallback_prompt(prompt_name)
        return prompt_path.read_text(encoding="utf-8")

    def _get_fallback_prompt(self, prompt_name: str) -> str:
        """Fallback prompts if files don't exist."""
        prompts = {
            "anthropology_lens": """You are an anthropologist analyzing cultural patterns in urban neighborhoods.

Analyze King Street West (Toronto) through an anthropological lens.

Focus on:
1. **Rituals & Behaviors**: What daily/weekly rituals are forming? How do people use this space?
2. **Identity Shifts**: How is the neighborhood's identity changing? Who claims it now vs 5 years ago?
3. **Status Symbols**: What signals belonging? What's "cool" vs "uncool" now?
4. **Community Patterns**: How are micro-communities forming? Who gathers where and why?

Ground your analysis in observable human behavior, not abstract theory.

Return JSON:
{
  "rituals_behaviors": "...",
  "identity_shifts": "...",
  "status_symbols": "...",
  "community_patterns": "...",
  "cultural_significance": "high" | "medium" | "low"
}
""",
            "economics_lens": """You are an economist analyzing consumption patterns in urban neighborhoods.

Analyze King Street West (Toronto) through an economic lens.

Focus on:
1. **Spending Power**: Who can afford to consume here? Income levels, discretionary spending
2. **Affordability vs Priority**: What's expensive but prioritized? What's affordable but ignored?
3. **Wealth Distribution**: How is wealth distributed across the neighborhood?
4. **Economic Anxiety**: Signs of financial stress or confidence in businesses/consumers

Be specific about price points, business models, and economic constraints.

Return JSON:
{
  "spending_power": "...",
  "affordability_vs_priority": "...",
  "wealth_distribution": "...",
  "economic_anxiety": "...",
  "market_size_estimate": "..."
}
""",
            "geopolitics_lens": """You are a geopolitical analyst examining how global forces shape local places.

Analyze King Street West (Toronto) through a geopolitical lens.

Focus on:
1. **Migration Patterns**: Who is moving to this neighborhood? International students, immigrants, domestic migration?
2. **Policy Impacts**: How do policies (zoning, liquor licenses, business regulations) shape this area?
3. **Global-Local Tension**: How do global trends (remote work, international dining trends) manifest here?
4. **International Influence**: What international forces matter? (e.g., investment, tourism, cultural imports)

Connect macro forces to observable local changes.

Return JSON:
{
  "migration_patterns": "...",
  "policy_impacts": "...",
  "global_local_tension": "...",
  "international_influence": "..."
}
""",
            "history_lens": """You are a historian analyzing how the past shapes the present.

Analyze King Street West (Toronto) through a historical lens.

Focus on:
1. **Historical Context**: How did we get here? What was this neighborhood historically?
2. **Cyclical vs New**: Is this trend recurring (e.g., urban renewal cycles) or genuinely unprecedented?
3. **Continuity vs Rupture**: What persists from the past? What represents a clean break?
4. **Historical Parallels**: Similar patterns in Toronto's history or other cities

Provide historical grounding, not just recent history.

Return JSON:
{
  "historical_context": "...",
  "cyclical_vs_new": "...",
  "continuity_vs_rupture": "...",
  "historical_parallels": "..."
}
"""
        }
        return prompts.get(prompt_name, "")

    def analyze_lens(self, lens_name: str, context: str) -> dict:
        """Run analysis through a single lens."""
        console.print(f"[cyan]Analyzing {lens_name} lens...[/cyan]")

        system_prompt = self._load_prompt(f"{lens_name}_lens")
        user_prompt = f"""Neighborhood Context:
{self.neighborhood_context}

Additional Context:
{context}

Analyze King Street West using the {lens_name} lens. Return valid JSON only."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"Generating {lens_name} analysis...", total=None)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

        result = json.loads(response.choices[0].message.content)
        console.print(f"[green]✓ {lens_name.title()} lens complete[/green]")
        return result

    def synthesize_lenses(self,
                         anthropology: dict,
                         economics: dict,
                         geopolitics: dict,
                         history: dict) -> str:
        """Synthesize all 4 lenses into coherent narrative."""
        console.print(f"[cyan]Synthesizing all lenses...[/cyan]")

        synthesis_prompt = """You are a strategic analyst synthesizing multi-disciplinary insights.

You have analyzed King Street West through 4 lenses. Now connect them:

**Anthropology Lens:**
{anthropology}

**Economics Lens:**
{economics}

**Geopolitics Lens:**
{geopolitics}

**History Lens:**
{history}

Synthesize these 4 perspectives into a coherent narrative (300-500 words) that:
1. Identifies CONNECTIONS between lenses (not just concatenation)
2. Resolves CONTRADICTIONS if any exist
3. Highlights what's UNIQUE vs UNIVERSAL about this neighborhood
4. Points to ACTIONABLE patterns for businesses

Return JSON:
{{
  "synthesis": "..."
}}
"""

        user_prompt = synthesis_prompt.format(
            anthropology=json.dumps(anthropology, indent=2),
            economics=json.dumps(economics, indent=2),
            geopolitics=json.dumps(geopolitics, indent=2),
            history=json.dumps(history, indent=2)
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )

        result = json.loads(response.choices[0].message.content)
        console.print(f"[green]✓ Synthesis complete[/green]")
        return result["synthesis"]

    def generate_business_insights(self,
                                   anthropology: dict,
                                   economics: dict,
                                   geopolitics: dict,
                                   history: dict,
                                   synthesis: str) -> dict:
        """Generate actionable business insights from analysis."""
        console.print(f"[cyan]Generating business insights...[/cyan]")

        business_prompt = """You are a business strategist translating cultural analysis into actionable opportunities.

Based on this 4-lens analysis of King Street West, identify:

1. **Business Opportunities** (2-3 specific ideas):
   - What type of business?
   - Target demographic (specific)
   - Location within King St W
   - Positioning/messaging
   - Timing (immediate/6mo/12mo)

2. **Business Threats** (2-3 risks):
   - What's at risk?
   - Which businesses are vulnerable?
   - Severity and timeline

**Analysis:**
Anthropology: {anthropology}
Economics: {economics}
Geopolitics: {geopolitics}
History: {history}
Synthesis: {synthesis}

Return JSON:
{{
  "opportunities": [
    {{
      "opportunity_type": "new_business" | "expansion" | "pivot" | "product" | "service",
      "description": "...",
      "target_demographic": "...",
      "target_locations": ["specific streets/blocks"],
      "positioning": "...",
      "timing": "immediate" | "6_months" | "12_months" | "uncertain",
      "investment_range": "..."
    }}
  ],
  "threats": [
    {{
      "threat_type": "disruption" | "decline" | "saturation" | "regulation" | "demographic_shift",
      "description": "...",
      "affected_businesses": ["..."],
      "severity": "high" | "medium" | "low",
      "timeline": "immediate" | "6_months" | "12_months" | "long_term"
    }}
  ],
  "evidence_strength": "high" | "medium" | "low",
  "confidence_reasoning": "..."
}}
"""

        user_prompt = business_prompt.format(
            anthropology=json.dumps(anthropology, indent=2),
            economics=json.dumps(economics, indent=2),
            geopolitics=json.dumps(geopolitics, indent=2),
            history=json.dumps(history, indent=2),
            synthesis=synthesis
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )

        result = json.loads(response.choices[0].message.content)
        console.print(f"[green]✓ Business insights generated[/green]")
        return result

    def run_full_analysis(self, additional_context: str = "") -> CityIntelligenceReport:
        """Run complete 4-lens analysis."""
        console.print("\n[bold cyan]🌆 King Street West Intelligence Analysis[/bold cyan]\n")

        # Step 1: Run all 4 lenses
        anthropology_data = self.analyze_lens("anthropology", additional_context)
        economics_data = self.analyze_lens("economics", additional_context)
        geopolitics_data = self.analyze_lens("geopolitics", additional_context)
        history_data = self.analyze_lens("history", additional_context)

        # Step 2: Synthesize
        synthesis = self.synthesize_lenses(
            anthropology_data,
            economics_data,
            geopolitics_data,
            history_data
        )

        # Step 3: Generate business insights
        business_data = self.generate_business_insights(
            anthropology_data,
            economics_data,
            geopolitics_data,
            history_data,
            synthesis
        )

        # Build Pydantic models
        city = City(
            name="Toronto",
            country="Canada",
            region="Ontario",
            timezone="America/Toronto"
        )

        trend = Trend(
            id="king-street-west-transformation",
            name="King Street West Post-Pandemic Transformation",
            description="Shift from entertainment-heavy to presence-economy neighborhood",
            category="Hospitality & Urban Development",
            neighborhoods=["Entertainment District", "Fashion District", "Financial District"],
            demographics=["Young professionals 25-40", "Condo dwellers", "Office workers"],
            data_sources=[]
        )

        anthropology = AnthropologyAnalysis(**anthropology_data)
        economics = EconomicsAnalysis(**economics_data)
        geopolitics = GeopoliticsAnalysis(**geopolitics_data)
        history = HistoryAnalysis(**history_data)

        multi_lens = MultiLensAnalysis(
            trend=trend,
            anthropology=anthropology,
            economics=economics,
            geopolitics=geopolitics,
            history=history,
            synthesis=synthesis
        )

        # Parse business insights
        opportunities = [BusinessOpportunity(**opp) for opp in business_data.get("opportunities", [])]
        threats = [BusinessThreat(**threat) for threat in business_data.get("threats", [])]

        business_insight = BusinessInsight(
            trend_id=trend.id,
            opportunities=opportunities,
            threats=threats,
            evidence_strength=business_data.get("evidence_strength", "medium"),
            confidence_reasoning=business_data.get("confidence_reasoning", ""),
            next_steps=[]
        )

        # Create executive summary
        executive_summary = f"""King Street West is undergoing a structural transformation from an entertainment-heavy corridor to a presence-economy neighborhood.

{synthesis[:200]}...

This analysis identifies {len(opportunities)} business opportunities and {len(threats)} threats based on multi-lens analysis."""

        report = CityIntelligenceReport(
            city=city,
            time_period="June 2026",
            trends=[multi_lens],
            business_insights=[business_insight],
            data_sources_used=[],
            limitations=["Based on qualitative LLM analysis", "No primary data collection yet"],
            executive_summary=executive_summary,
            top_opportunities=[opp.description for opp in opportunities[:5]],
            top_threats=[threat.description for threat in threats[:5]]
        )

        console.print("\n[green bold]✓ Analysis complete![/green bold]\n")
        return report

    def save_report(self, report: CityIntelligenceReport, output_dir: Path = None):
        """Save report to JSON file."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data"

        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"king_street_west_intelligence_{timestamp}.json"
        filepath = output_dir / filename

        # Convert to dict for JSON serialization
        report_dict = report.model_dump(mode='json')

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Report saved to: {filepath}[/green]")
        return filepath


def main():
    """Run King Street West analysis."""

    # Optional: Add field observations or additional context
    additional_context = """
**Recent Observations (June 2026):**
- Several new health-focused cafes opened in Fashion District
- Multiple restaurant vacancies between Spadina and Bathurst
- Increased condo construction along King West
- Fewer late-night venues operating
- More daytime/brunch-focused establishments
"""

    try:
        analyzer = KingStreetWestAnalyzer()
        report = analyzer.run_full_analysis(additional_context)
        filepath = analyzer.save_report(report)

        # Print summary
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Trends analyzed: {len(report.trends)}")
        console.print(f"Business opportunities: {len(report.business_insights[0].opportunities)}")
        console.print(f"Business threats: {len(report.business_insights[0].threats)}")
        console.print(f"\nReport saved: {filepath}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
