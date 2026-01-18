"""
Interactive Streamlit UI for Token Cost Comparison.
Provides visualizations and analysis tools for comparing LLM costs.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calculator import TokenCalculator
from comparison import ModelComparator
from models import MODELS, get_all_providers


# Page configuration
st.set_page_config(
    page_title="LLM Token Cost Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
if 'calculator' not in st.session_state:
    st.session_state.calculator = TokenCalculator()
if 'comparator' not in st.session_state:
    st.session_state.comparator = ModelComparator()


def format_currency(value: float) -> str:
    """Format currency with appropriate precision."""
    if value < 0.0001:
        return f"${value:.8f}"
    elif value < 0.01:
        return f"${value:.6f}"
    elif value < 1:
        return f"${value:.4f}"
    else:
        return f"${value:.2f}"


def main():
    """Main application function."""

    # Header
    st.title("💰 LLM Token Cost Analyzer")
    st.markdown("Compare token costs across different AI models and providers")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        analysis_mode = st.radio(
            "Analysis Mode",
            ["Quick Compare", "Detailed Analysis", "Scale Calculator"],
            help="Choose your analysis type"
        )

        st.divider()

        # Provider filter
        all_providers = ["All"] + get_all_providers()
        selected_provider = st.selectbox(
            "Filter by Provider",
            all_providers,
            help="Filter models by provider"
        )

        st.divider()
        st.markdown("### About")
        st.info(
            "This tool helps you compare token costs across different LLM providers. "
            "Enter your input and output text to see real-time cost comparisons."
        )

    # Main content area
    if analysis_mode == "Quick Compare":
        show_quick_compare(selected_provider)
    elif analysis_mode == "Detailed Analysis":
        show_detailed_analysis(selected_provider)
    else:
        show_scale_calculator(selected_provider)


def show_quick_compare(provider_filter: str):
    """Quick comparison view."""

    st.header("Quick Cost Comparison")

    col1, col2 = st.columns(2)

    with col1:
        input_text = st.text_area(
            "Input Text (Prompt)",
            height=150,
            placeholder="Enter your prompt or input text here...",
            help="This is the text you send to the model"
        )

    with col2:
        output_text = st.text_area(
            "Output Text (Response)",
            height=150,
            placeholder="Enter expected output text here (optional)...",
            help="This is the expected response from the model"
        )

    if input_text:
        # Get comparison results
        results = st.session_state.comparator.compare_all_models(input_text, output_text)

        # Filter by provider if needed
        if provider_filter != "All":
            results = [r for r in results if r.provider == provider_filter]

        # Summary metrics
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Cheapest Model", results[0].model_name)
        with col2:
            st.metric("Cheapest Cost", format_currency(results[0].total_cost))
        with col3:
            st.metric("Most Expensive", results[-1].model_name)
        with col4:
            st.metric("Most Expensive Cost", format_currency(results[-1].total_cost))

        # Comparison table
        st.subheader("💵 Cost Comparison")

        df = pd.DataFrame([
            {
                "Rank": r.rank,
                "Model": r.model_name,
                "Provider": r.provider,
                "Total Cost": format_currency(r.total_cost),
                "Input Cost": format_currency(r.input_cost),
                "Output Cost": format_currency(r.output_cost),
                "Total Tokens": r.total_tokens,
                "vs Cheapest": f"+{r.cost_vs_cheapest:.1f}%",
            }
            for r in results
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Visualization
        st.subheader("📈 Cost Visualization")

        # Create bar chart
        fig = px.bar(
            df,
            x="Model",
            y=["Input Cost", "Output Cost"],
            title="Cost Breakdown by Model",
            barmode="stack",
            color_discrete_map={"Input Cost": "#4CAF50", "Output Cost": "#FF9800"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def show_detailed_analysis(provider_filter: str):
    """Detailed analysis view with more insights."""

    st.header("Detailed Cost Analysis")

    # Input section
    col1, col2 = st.columns([2, 1])

    with col1:
        input_text = st.text_area(
            "Input Text",
            height=150,
            placeholder="Enter your prompt...",
        )
        output_text = st.text_area(
            "Output Text",
            height=150,
            placeholder="Enter expected output...",
        )

    with col2:
        st.markdown("### Quick Stats")
        if input_text:
            st.metric("Input Characters", len(input_text))
            st.metric("Output Characters", len(output_text) if output_text else 0)
            st.metric("Total Characters", len(input_text) + len(output_text))

    if input_text:
        # Get all analyses
        analyses = st.session_state.calculator.analyze_all_models(input_text, output_text)

        # Filter by provider
        if provider_filter != "All":
            analyses = {
                k: v for k, v in analyses.items()
                if v["provider"] == provider_filter
            }

        # Provider comparison
        st.subheader("🏢 Provider Comparison")
        provider_stats = st.session_state.comparator.get_provider_comparison(input_text, output_text)

        provider_df = pd.DataFrame([
            {
                "Provider": provider,
                "Average Cost": format_currency(stats["avg_cost"]),
                "Min Cost": format_currency(stats["min_cost"]),
                "Max Cost": format_currency(stats["max_cost"]),
                "Models": stats["model_count"],
            }
            for provider, stats in provider_stats.items()
        ])

        st.dataframe(provider_df, use_container_width=True, hide_index=True)

        # Detailed model breakdown
        st.subheader("🔍 Detailed Model Breakdown")

        for model_id, analysis in sorted(
            analyses.items(),
            key=lambda x: x[1]["total_cost_usd"]
        ):
            with st.expander(f"{analysis['model_name']} - {format_currency(analysis['total_cost_usd'])}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Input Tokens", f"{analysis['input_tokens']:,}")
                    st.metric("Input Cost", format_currency(analysis['input_cost_usd']))
                    st.metric("Cost/1M Input", f"${analysis['cost_per_1m_input']:,.2f}")

                with col2:
                    st.metric("Output Tokens", f"{analysis['output_tokens']:,}")
                    st.metric("Output Cost", format_currency(analysis['output_cost_usd']))
                    st.metric("Cost/1M Output", f"${analysis['cost_per_1m_output']:,.2f}")

                with col3:
                    st.metric("Total Tokens", f"{analysis['total_tokens']:,}")
                    st.metric("Total Cost", format_currency(analysis['total_cost_usd']))
                    st.metric("Context Window", f"{analysis['context_window']:,}")

        # Cost distribution chart
        st.subheader("📊 Cost Distribution")

        cost_data = pd.DataFrame([
            {
                "Model": analysis["model_name"],
                "Total Cost (USD)": analysis["total_cost_usd"],
                "Provider": analysis["provider"],
            }
            for analysis in analyses.values()
        ])

        fig = px.scatter(
            cost_data,
            x="Model",
            y="Total Cost (USD)",
            color="Provider",
            size="Total Cost (USD)",
            title="Cost Comparison Across Models",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)


def show_scale_calculator(provider_filter: str):
    """Calculator for costs at scale."""

    st.header("Scale Cost Calculator")
    st.markdown("Calculate costs for high-volume usage scenarios")

    # Input section
    col1, col2 = st.columns([2, 1])

    with col1:
        input_text = st.text_area(
            "Sample Input Text",
            height=100,
            placeholder="Enter a sample prompt...",
        )
        output_text = st.text_area(
            "Sample Output Text",
            height=100,
            placeholder="Enter a sample output...",
        )

    with col2:
        num_requests = st.number_input(
            "Number of Requests",
            min_value=1,
            max_value=10000000,
            value=1000,
            step=100,
            help="Total number of API requests"
        )

        time_period = st.selectbox(
            "Time Period",
            ["Per Day", "Per Week", "Per Month", "Per Year", "One-time"],
        )

    if input_text:
        # Calculate costs at scale for all models
        st.subheader("💰 Cost Projections")

        scale_results = []
        for model_id in MODELS.keys():
            if provider_filter != "All" and MODELS[model_id].provider != provider_filter:
                continue

            result = st.session_state.comparator.calculate_cost_at_scale(
                model_id, input_text, output_text, num_requests
            )
            scale_results.append(result)

        # Sort by total cost
        scale_results.sort(key=lambda x: x["total_cost_usd"])

        # Display results
        df = pd.DataFrame([
            {
                "Model": r["model_name"],
                "Total Cost": format_currency(r["total_cost_usd"]),
                "Cost per Request": format_currency(r["cost_per_request"]),
                "Total Tokens": f"{r['total_tokens']:,}",
                "Input Tokens": f"{r['total_input_tokens']:,}",
                "Output Tokens": f"{r['total_output_tokens']:,}",
            }
            for r in scale_results
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Cost comparison chart
        st.subheader("📈 Cost Comparison at Scale")

        chart_data = pd.DataFrame([
            {
                "Model": r["model_name"],
                "Total Cost (USD)": r["total_cost_usd"],
            }
            for r in scale_results
        ])

        fig = px.bar(
            chart_data,
            x="Model",
            y="Total Cost (USD)",
            title=f"Total Cost for {num_requests:,} Requests ({time_period})",
            color="Total Cost (USD)",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Savings calculator
        if len(scale_results) > 1:
            st.subheader("💡 Potential Savings")

            cheapest = scale_results[0]
            most_expensive = scale_results[-1]

            savings = most_expensive["total_cost_usd"] - cheapest["total_cost_usd"]
            savings_percent = (savings / most_expensive["total_cost_usd"]) * 100

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Cheapest Option", cheapest["model_name"])
                st.metric("Cost", format_currency(cheapest["total_cost_usd"]))

            with col2:
                st.metric("Most Expensive", most_expensive["model_name"])
                st.metric("Cost", format_currency(most_expensive["total_cost_usd"]))

            with col3:
                st.metric("Potential Savings", format_currency(savings))
                st.metric("Savings %", f"{savings_percent:.1f}%")


if __name__ == "__main__":
    main()
