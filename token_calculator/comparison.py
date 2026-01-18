"""
Comparative analysis utilities for model costs.
Provides ranking, cost differences, and insights across models.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from calculator import TokenCalculator
from models import MODELS, get_all_providers


@dataclass
class ComparisonResult:
    """Results from comparing multiple models."""

    model_id: str
    model_name: str
    provider: str
    total_cost: float
    input_cost: float
    output_cost: float
    total_tokens: int
    rank: int
    cost_vs_cheapest: float  # Percentage difference
    cost_vs_most_expensive: float  # Percentage difference


class ModelComparator:
    """Provides comparative analysis across models."""

    def __init__(self):
        self.calculator = TokenCalculator()

    def compare_all_models(
        self,
        input_text: str,
        output_text: str = "",
    ) -> List[ComparisonResult]:
        """
        Compare all models and rank by total cost.

        Args:
            input_text: Input/prompt text
            output_text: Output/completion text (optional)

        Returns:
            List of ComparisonResult objects sorted by cost (cheapest first)
        """
        # Get analysis for all models
        analyses = self.calculator.analyze_all_models(input_text, output_text)

        # Sort by total cost
        sorted_models = sorted(
            analyses.items(),
            key=lambda x: x[1]["total_cost_usd"]
        )

        # Calculate min and max costs
        min_cost = sorted_models[0][1]["total_cost_usd"]
        max_cost = sorted_models[-1][1]["total_cost_usd"]

        # Create comparison results
        results = []
        for rank, (model_id, analysis) in enumerate(sorted_models, start=1):
            total_cost = analysis["total_cost_usd"]

            # Calculate percentage differences
            if min_cost == 0:
                cost_vs_cheapest = 0
            else:
                cost_vs_cheapest = ((total_cost - min_cost) / min_cost) * 100

            if max_cost == 0:
                cost_vs_most_expensive = 0
            else:
                cost_vs_most_expensive = ((total_cost - max_cost) / max_cost) * 100

            results.append(ComparisonResult(
                model_id=model_id,
                model_name=analysis["model_name"],
                provider=analysis["provider"],
                total_cost=total_cost,
                input_cost=analysis["input_cost_usd"],
                output_cost=analysis["output_cost_usd"],
                total_tokens=analysis["total_tokens"],
                rank=rank,
                cost_vs_cheapest=cost_vs_cheapest,
                cost_vs_most_expensive=cost_vs_most_expensive,
            ))

        return results

    def get_provider_comparison(
        self,
        input_text: str,
        output_text: str = "",
    ) -> Dict[str, dict]:
        """
        Compare average costs by provider.

        Args:
            input_text: Input/prompt text
            output_text: Output/completion text (optional)

        Returns:
            Dictionary with provider-level statistics
        """
        analyses = self.calculator.analyze_all_models(input_text, output_text)

        # Group by provider
        provider_costs: Dict[str, List[float]] = {}
        for analysis in analyses.values():
            provider = analysis["provider"]
            if provider not in provider_costs:
                provider_costs[provider] = []
            provider_costs[provider].append(analysis["total_cost_usd"])

        # Calculate statistics per provider
        provider_stats = {}
        for provider, costs in provider_costs.items():
            provider_stats[provider] = {
                "avg_cost": sum(costs) / len(costs),
                "min_cost": min(costs),
                "max_cost": max(costs),
                "model_count": len(costs),
            }

        return provider_stats

    def get_best_value_models(
        self,
        input_text: str,
        output_text: str = "",
        top_n: int = 3,
    ) -> List[ComparisonResult]:
        """
        Get the top N most cost-effective models.

        Args:
            input_text: Input/prompt text
            output_text: Output/completion text (optional)
            top_n: Number of top models to return

        Returns:
            List of top N cheapest models
        """
        all_results = self.compare_all_models(input_text, output_text)
        return all_results[:top_n]

    def calculate_cost_at_scale(
        self,
        model_id: str,
        input_text: str,
        output_text: str,
        num_requests: int,
    ) -> dict:
        """
        Calculate costs for running multiple requests.

        Args:
            model_id: ID of the model
            input_text: Sample input text
            output_text: Sample output text
            num_requests: Number of requests to simulate

        Returns:
            Dictionary with scaled cost projections
        """
        single_analysis = self.calculator.analyze_single_model(
            model_id, input_text, output_text
        )

        total_input_tokens = single_analysis["input_tokens"] * num_requests
        total_output_tokens = single_analysis["output_tokens"] * num_requests
        total_cost = single_analysis["total_cost_usd"] * num_requests

        return {
            "model_id": model_id,
            "model_name": single_analysis["model_name"],
            "num_requests": num_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost_usd": total_cost,
            "cost_per_request": single_analysis["total_cost_usd"],
        }

    def find_cheapest_for_use_case(
        self,
        input_text: str,
        output_text: str,
        monthly_requests: int,
    ) -> Tuple[str, float]:
        """
        Find the most cost-effective model for a given use case.

        Args:
            input_text: Sample input text
            output_text: Sample output text
            monthly_requests: Expected monthly request volume

        Returns:
            Tuple of (model_id, monthly_cost)
        """
        analyses = self.calculator.analyze_all_models(input_text, output_text)

        cheapest_model = None
        lowest_monthly_cost = float('inf')

        for model_id, analysis in analyses.items():
            monthly_cost = analysis["total_cost_usd"] * monthly_requests
            if monthly_cost < lowest_monthly_cost:
                lowest_monthly_cost = monthly_cost
                cheapest_model = model_id

        return cheapest_model, lowest_monthly_cost

    def get_cost_breakdown_summary(
        self,
        input_text: str,
        output_text: str = "",
    ) -> dict:
        """
        Get a comprehensive summary of costs across all models.

        Args:
            input_text: Input/prompt text
            output_text: Output/completion text (optional)

        Returns:
            Dictionary with overall statistics
        """
        analyses = self.calculator.analyze_all_models(input_text, output_text)
        costs = [a["total_cost_usd"] for a in analyses.values()]

        return {
            "total_models": len(analyses),
            "cheapest_cost": min(costs),
            "most_expensive_cost": max(costs),
            "average_cost": sum(costs) / len(costs),
            "cost_range": max(costs) - min(costs),
            "price_variance_ratio": max(costs) / min(costs) if min(costs) > 0 else 0,
        }
