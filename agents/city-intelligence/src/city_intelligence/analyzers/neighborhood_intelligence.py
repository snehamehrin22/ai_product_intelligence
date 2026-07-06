"""
Neighborhood Intelligence Analyzer

Conducts comprehensive 15-section analysis of a neighborhood:
1. Identity
2. Historical Evolution
3. Demographics
4. Economic Landscape
5. Business Ecosystem
6. Human Movement
7. Third Place Analysis
8. Behavioral Patterns
9. Cultural Signals
10. Macro Trends
11. Neighborhood Needs
12. Future Outlook
13. Café Implications
14. Strategic Insights
15. Executive Summary (Synthesis)

Uses GPT-4o with structured JSON output to ensure valid responses.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..schemas import (
    City,
    NeighborhoodIdentity,
    HistoricalEvolution,
    DemographicAnalysis,
    EconomicLandscape,
    BusinessEcosystem,
    HumanMovement,
    ThirdPlaceAnalysis,
    BehavioralPatterns,
    CulturalSignals,
    MacroTrends,
    NeighborhoodNeeds,
    FutureOutlook,
    CafeImplications,
    StrategicInsights,
    NeighborhoodIntelligenceReport
)

load_dotenv()
console = Console()


class NeighborhoodIntelligenceAnalyzer:
    """Analyzes neighborhoods using 15-section framework."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.prompts_dir = Path(__file__).parent.parent.parent.parent / "prompts"

        # Token usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts/ directory."""
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    def _call_llm(self, prompt: str, max_tokens: int = 3000, temperature: float = 0.3) -> Dict:
        """Call OpenAI API with structured JSON response."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Generating analysis...", total=None)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

        # Track usage
        self.total_tokens += response.usage.total_tokens
        # Rough cost estimate: $5/1M input tokens, $15/1M output tokens for GPT-4o
        input_cost = (response.usage.prompt_tokens / 1_000_000) * 5
        output_cost = (response.usage.completion_tokens / 1_000_000) * 15
        self.total_cost += (input_cost + output_cost)

        return json.loads(response.choices[0].message.content)

    def _fill_prompt_template(self, template: str, neighborhood: str, city: str) -> str:
        """Fill prompt template with neighborhood and city info."""
        return template.replace("{{neighborhood_name}}", neighborhood) \
                      .replace("{{city_name}}", city) \
                      .replace("{{city_name_lower}}", city.lower())

    def analyze_identity(self, neighborhood: str, city: str) -> NeighborhoodIdentity:
        """Section 1: Neighborhood Identity."""
        console.print("[cyan]Analyzing neighborhood identity...[/cyan]")

        prompt_template = self._load_prompt("neighborhood_identity")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = NeighborhoodIdentity(**result)

        console.print("[green]✓ Identity analysis complete[/green]")
        return validated

    def analyze_historical_evolution(self, neighborhood: str, city: str) -> HistoricalEvolution:
        """Section 2: Historical Evolution."""
        console.print("[cyan]Analyzing historical evolution...[/cyan]")

        prompt_template = self._load_prompt("historical_evolution")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2500)
        validated = HistoricalEvolution(**result)

        console.print("[green]✓ Historical evolution analysis complete[/green]")
        return validated

    def analyze_demographics(self, neighborhood: str, city: str) -> DemographicAnalysis:
        """Section 3: Demographics."""
        console.print("[cyan]Analyzing demographics...[/cyan]")

        prompt_template = self._load_prompt("demographic_analysis")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2500)
        validated = DemographicAnalysis(**result)

        console.print("[green]✓ Demographic analysis complete[/green]")
        return validated

    def analyze_economic_landscape(self, neighborhood: str, city: str) -> EconomicLandscape:
        """Section 4: Economic Landscape."""
        console.print("[cyan]Analyzing economic landscape...[/cyan]")

        prompt_template = self._load_prompt("economic_landscape")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2500)
        validated = EconomicLandscape(**result)

        console.print("[green]✓ Economic landscape analysis complete[/green]")
        return validated

    def analyze_business_ecosystem(self, neighborhood: str, city: str) -> BusinessEcosystem:
        """Section 5: Business Ecosystem."""
        console.print("[cyan]Analyzing business ecosystem...[/cyan]")

        prompt_template = self._load_prompt("business_ecosystem")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = BusinessEcosystem(**result)

        console.print("[green]✓ Business ecosystem analysis complete[/green]")
        return validated

    def analyze_human_movement(self, neighborhood: str, city: str) -> HumanMovement:
        """Section 6: Human Movement."""
        console.print("[cyan]Analyzing human movement patterns...[/cyan]")

        prompt_template = self._load_prompt("human_movement")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=3000)
        validated = HumanMovement(**result)

        console.print("[green]✓ Human movement analysis complete[/green]")
        return validated

    def analyze_third_places(self, neighborhood: str, city: str) -> ThirdPlaceAnalysis:
        """Section 7: Third Place Analysis."""
        console.print("[cyan]Analyzing third places (Ray Oldenburg framework)...[/cyan]")

        prompt_template = self._load_prompt("third_place_analysis")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = ThirdPlaceAnalysis(**result)

        console.print("[green]✓ Third place analysis complete[/green]")
        return validated

    def analyze_behavioral_patterns(self, neighborhood: str, city: str) -> BehavioralPatterns:
        """Section 8: Behavioral Patterns."""
        console.print("[cyan]Analyzing behavioral patterns...[/cyan]")

        prompt_template = self._load_prompt("behavioral_patterns")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = BehavioralPatterns(**result)

        console.print("[green]✓ Behavioral patterns analysis complete[/green]")
        return validated

    def analyze_cultural_signals(self, neighborhood: str, city: str) -> CulturalSignals:
        """Section 9: Cultural Signals."""
        console.print("[cyan]Analyzing cultural signals and values...[/cyan]")

        prompt_template = self._load_prompt("cultural_signals")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = CulturalSignals(**result)

        console.print("[green]✓ Cultural signals analysis complete[/green]")
        return validated

    def analyze_macro_trends(self, neighborhood: str, city: str) -> MacroTrends:
        """Section 10: Macro Trends."""
        console.print("[cyan]Analyzing macro trends...[/cyan]")

        prompt_template = self._load_prompt("macro_trends")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = MacroTrends(**result)

        console.print("[green]✓ Macro trends analysis complete[/green]")
        return validated

    def analyze_neighborhood_needs(self, neighborhood: str, city: str) -> NeighborhoodNeeds:
        """Section 11: Neighborhood Needs."""
        console.print("[cyan]Analyzing unmet neighborhood needs...[/cyan]")

        prompt_template = self._load_prompt("neighborhood_needs")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=2000)
        validated = NeighborhoodNeeds(**result)

        console.print("[green]✓ Neighborhood needs analysis complete[/green]")
        return validated

    def analyze_future_outlook(self, neighborhood: str, city: str) -> FutureOutlook:
        """Section 12: Future Outlook."""
        console.print("[cyan]Analyzing future outlook (3/5/10 years)...[/cyan]")

        prompt_template = self._load_prompt("future_outlook")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        result = self._call_llm(prompt, max_tokens=3000)
        validated = FutureOutlook(**result)

        console.print("[green]✓ Future outlook analysis complete[/green]")
        return validated

    def analyze_cafe_implications(
        self,
        neighborhood: str,
        city: str,
        previous_analyses: Dict
    ) -> CafeImplications:
        """Section 13: Café Implications."""
        console.print("[cyan]Synthesizing café implications...[/cyan]")

        prompt_template = self._load_prompt("cafe_implications")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        # Add context from previous analyses
        context = f"\n\n# PREVIOUS ANALYSES SUMMARY:\n{json.dumps(previous_analyses, indent=2)}"
        prompt += context

        result = self._call_llm(prompt, max_tokens=2500)
        validated = CafeImplications(**result)

        console.print("[green]✓ Café implications complete[/green]")
        return validated

    def analyze_strategic_insights(
        self,
        neighborhood: str,
        city: str,
        previous_analyses: Dict
    ) -> StrategicInsights:
        """Section 14: Strategic Insights."""
        console.print("[cyan]Generating strategic insights...[/cyan]")

        prompt_template = self._load_prompt("strategic_insights")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        # Add context from previous analyses
        context = f"\n\n# PREVIOUS ANALYSES SUMMARY:\n{json.dumps(previous_analyses, indent=2)}"
        prompt += context

        result = self._call_llm(prompt, max_tokens=2000)
        validated = StrategicInsights(**result)

        console.print("[green]✓ Strategic insights complete[/green]")
        return validated

    def synthesize_all(
        self,
        neighborhood: str,
        city: str,
        all_analyses: Dict
    ) -> Dict:
        """Section 15: Executive Summary (Synthesis)."""
        console.print("[cyan]Synthesizing executive summary...[/cyan]")

        prompt_template = self._load_prompt("neighborhood_synthesis")
        prompt = self._fill_prompt_template(prompt_template, neighborhood, city)

        # Add all analyses as context
        context = f"\n\n# ALL ANALYSES:\n{json.dumps(all_analyses, indent=2)}"
        prompt += context

        result = self._call_llm(prompt, max_tokens=2500)

        console.print("[green]✓ Executive summary complete[/green]")
        return result

    def run_full_analysis(
        self,
        neighborhood: str,
        city: str,
        city_metadata: Optional[Dict] = None
    ) -> NeighborhoodIntelligenceReport:
        """Run complete 15-section neighborhood intelligence analysis."""
        console.print(f"\n[bold cyan]🏙️  Neighborhood Intelligence: {neighborhood}, {city}[/bold cyan]\n")

        # Section 1-12: Independent analyses
        identity = self.analyze_identity(neighborhood, city)
        historical = self.analyze_historical_evolution(neighborhood, city)
        demographics = self.analyze_demographics(neighborhood, city)
        economics = self.analyze_economic_landscape(neighborhood, city)
        business = self.analyze_business_ecosystem(neighborhood, city)
        movement = self.analyze_human_movement(neighborhood, city)
        third_places = self.analyze_third_places(neighborhood, city)
        behavioral = self.analyze_behavioral_patterns(neighborhood, city)
        cultural = self.analyze_cultural_signals(neighborhood, city)
        macro = self.analyze_macro_trends(neighborhood, city)
        needs = self.analyze_neighborhood_needs(neighborhood, city)
        future = self.analyze_future_outlook(neighborhood, city)

        # Prepare summary for sections 13-15
        previous_analyses = {
            "identity": identity.model_dump(),
            "historical_evolution": historical.model_dump(),
            "demographics": demographics.model_dump(),
            "economics": economics.model_dump(),
            "business_ecosystem": business.model_dump(),
            "human_movement": movement.model_dump(),
            "third_places": third_places.model_dump(),
            "behavioral_patterns": behavioral.model_dump(),
            "cultural_signals": cultural.model_dump(),
            "macro_trends": macro.model_dump(),
            "neighborhood_needs": needs.model_dump(),
            "future_outlook": future.model_dump()
        }

        # Section 13-14: Synthesis-dependent analyses
        cafe = self.analyze_cafe_implications(neighborhood, city, previous_analyses)
        strategic = self.analyze_strategic_insights(neighborhood, city, previous_analyses)

        # Section 15: Executive Summary
        all_analyses = {
            **previous_analyses,
            "cafe_implications": cafe.model_dump(),
            "strategic_insights": strategic.model_dump()
        }
        synthesis = self.synthesize_all(neighborhood, city, all_analyses)

        # Build city metadata
        city_obj = City(
            name=city,
            country=city_metadata.get("country", "Unknown") if city_metadata else "Unknown",
            region=city_metadata.get("region") if city_metadata else None,
            population=city_metadata.get("population") if city_metadata else None,
            timezone=city_metadata.get("timezone") if city_metadata else None
        )

        # Create final report
        report = NeighborhoodIntelligenceReport(
            neighborhood_name=neighborhood,
            city=city_obj,
            time_period=f"{city} - June 2026",
            identity=identity,
            historical_evolution=historical,
            demographics=demographics,
            economics=economics,
            business_ecosystem=business,
            human_movement=movement,
            third_places=third_places,
            behavioral_patterns=behavioral,
            cultural_signals=cultural,
            macro_trends=macro,
            neighborhood_needs=needs,
            future_outlook=future,
            cafe_implications=cafe,
            strategic_insights=strategic,
            neighborhood_story=synthesis.get("neighborhood_story", ""),
            defining_human_needs=synthesis.get("defining_human_needs", ""),
            defining_economic_forces=synthesis.get("defining_economic_forces", ""),
            defining_cultural_forces=synthesis.get("defining_cultural_forces", ""),
            cafe_success_factors=synthesis.get("cafe_success_factors", ""),
            one_sentence_summary=synthesis.get("one_sentence_summary", ""),
            data_sources_used=[],
            limitations=["Based on AI analysis", "No primary field research", "Data currency varies"]
        )

        console.print(f"\n[green bold]✓ Complete analysis finished![/green bold]")
        console.print(f"[yellow]Total tokens used: {self.total_tokens:,}[/yellow]")
        console.print(f"[yellow]Estimated cost: ${self.total_cost:.2f}[/yellow]\n")

        return report
