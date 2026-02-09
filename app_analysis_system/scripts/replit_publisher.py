#!/usr/bin/env python3
"""
Replit Publisher
Transforms multi-section analysis into YAML case study format matching template
Supports: business_origin, growth_loops, voice_of_customer (reddit_intelligence)
"""

import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime


def transform_to_yaml(json_data: dict, app_name: str, markdown_content: str = None) -> dict:
    """
    Transform multi-section analysis into Replit YAML case study format

    Args:
        json_data: Combined JSON from all sections (business_origin, growth_loops, voice_of_customer)
        app_name: Name of the app
        markdown_content: Optional full markdown analysis

    Returns:
        Dictionary in YAML case study format
    """

    # Detect which sections are present
    has_business_origin = "business_origin" in json_data
    has_growth_loops = "growth_loops" in json_data
    has_voice_of_customer = "voice_of_customer" in json_data

    # If old format (direct keys), treat as business_origin
    if not any([has_business_origin, has_growth_loops, has_voice_of_customer]):
        # Old format - direct keys
        business_origin_data = json_data
    else:
        # New format - nested by section
        business_origin_data = json_data.get("business_origin", {})

    # Extract business_origin data (for backwards compatibility)
    product_snapshot = business_origin_data.get("product_snapshot", {})
    founders = business_origin_data.get("founders", [])
    core_pain = business_origin_data.get("core_pain_problem", {})
    world_state = business_origin_data.get("world_state", {})
    competitive = business_origin_data.get("competitive_landscape", {})
    differentiation = business_origin_data.get("differentiation", {})
    human_need = business_origin_data.get("fundamental_human_need", {})
    early_growth = business_origin_data.get("early_growth", {})
    monetization = business_origin_data.get("monetization", {})
    synthesis = business_origin_data.get("success_synthesis", {})

    # Build YAML structure
    case_study = {
        "title": f"{app_name}: Complete Analysis",
        "description": f"Multi-lens analysis of {app_name} including business origin, growth dynamics, and user intelligence",
        "client": app_name,
        "industry": business_origin_data.get("category", "Technology"),
        "duration": "Research Phase",
        "tags": [
            "Business Origin",
            "Growth Analysis",
            "User Intelligence",
            business_origin_data.get("category", "App Analysis")
        ],
        "sections": []
    }

    # SECTION 1: Title
    case_study["sections"].append({
        "type": "title",
        "badge": "BUSINESS ORIGIN ANALYSIS",
        "main_title": f"{app_name}: {synthesis.get('historical_inevitability_thesis', 'The Story of How It Came to Be')}",
        "subtitle": product_snapshot.get("description", f"Understanding the origin and success of {app_name}"),
        "highlight_text": app_name
    })

    # SECTION 2: Why This App
    why_brand_cards = []

    # Card 1: Product snapshot
    why_brand_cards.append({
        "icon": "🎯",
        "title": "What It Actually Does",
        "description": product_snapshot.get("actual_job_to_be_done", product_snapshot.get("description", ""))
    })

    # Card 2: Core problem
    why_brand_cards.append({
        "icon": "💡",
        "title": "The Real Problem It Solved",
        "description": core_pain.get("problem_statement", "")
    })

    # Card 3: Why now
    why_brand_cards.append({
        "icon": "⏰",
        "title": "Why It Worked Then",
        "description": human_need.get("why_it_mattered_then", "")
    })

    # Card 4: Strategic insight
    why_brand_cards.append({
        "icon": "🧠",
        "title": "What They Understood",
        "description": differentiation.get("core_insight", "")
    })

    case_study["sections"].append({
        "type": "why_brand",
        "title": f"Why {app_name}",
        "subtitle": "What made this app worth studying",
        "highlight_text": app_name,
        "cards": why_brand_cards,
        "conclusion": [
            synthesis.get("why_it_worked", ""),
            synthesis.get("key_alignment_factors", "")
        ]
    })

    # SECTION 3: Business Understanding
    business_cards = []

    # Card 1: Founders & Origin
    if founders:
        founder_points = []
        for founder in founders:
            founder_points.append(f"**{founder.get('name', 'Founder')}**: {founder.get('background', '')}")
            if founder.get('relevant_lived_experience'):
                founder_points.append(f"Experience: {founder['relevant_lived_experience']}")
            if founder.get('founder_motivation'):
                founder_points.append(f"Motivation: {founder['founder_motivation']}")

        business_cards.append({
            "icon": "👥",
            "title": "Founders & Origin Story",
            "description": "Who built this and why they were uniquely positioned",
            "points": founder_points
        })

    # Card 2: Product Snapshot
    business_cards.append({
        "icon": "📱",
        "title": "Product Snapshot",
        "description": product_snapshot.get("description", ""),
        "points": [
            f"**Target User**: {product_snapshot.get('target_user', '')}",
            f"**Perceived Category**: {product_snapshot.get('perceived_category', '')}",
            f"**Actual Job**: {product_snapshot.get('actual_job_to_be_done', '')}"
        ]
    })

    # Card 3: Core Pain Problem
    business_cards.append({
        "icon": "❌",
        "title": "Core Pain Problem",
        "description": core_pain.get("problem_statement", ""),
        "points": [
            f"**Who Suffered**: {core_pain.get('who_experienced_it', '')}",
            f"**Why Existing Solutions Failed**: {core_pain.get('why_existing_solutions_failed', '')}",
            f"**Emotional Cost**: {core_pain.get('emotional_or_practical_cost', '')}"
        ]
    })

    # Card 4: World-State Analysis
    world_state_points = []
    if world_state.get("social_cultural"):
        world_state_points.append(f"**Social/Cultural**: {world_state['social_cultural']}")
    if world_state.get("economic"):
        world_state_points.append(f"**Economic**: {world_state['economic']}")
    if world_state.get("technological"):
        world_state_points.append(f"**Technological**: {world_state['technological']}")
    if world_state.get("user_behavior"):
        world_state_points.append(f"**User Behavior**: {world_state['user_behavior']}")
    if world_state.get("demographic"):
        world_state_points.append(f"**Demographic**: {world_state['demographic']}")

    business_cards.append({
        "icon": "🌍",
        "title": "World-State: Why Now?",
        "description": "What conditions made this possible",
        "points": world_state_points
    })

    # Card 5: Competitive Landscape
    competitive_points = [
        f"**Direct Competitors**: {', '.join(competitive.get('direct_competitors', []))}",
        f"**Indirect Substitutes**: {', '.join(competitive.get('indirect_substitutes', []))}",
        f"**Incumbent Failures**: {competitive.get('incumbent_failures', '')}",
        f"**User Tradeoffs Before**: {competitive.get('user_tradeoffs_before', '')}"
    ]

    business_cards.append({
        "icon": "⚔️",
        "title": "Competitive Landscape",
        "description": "Who they competed against and why incumbents failed",
        "points": competitive_points
    })

    # Card 6: Differentiation
    business_cards.append({
        "icon": "✨",
        "title": "Strategic Differentiation",
        "description": differentiation.get("core_insight", ""),
        "points": [
            f"**Assumptions Rejected**: {differentiation.get('assumptions_rejected', '')}",
            f"**Meaningful Differences**: {differentiation.get('meaningful_differences', '')}"
        ]
    })

    case_study["sections"].append({
        "type": "business_understanding",
        "title": "1. Understand The Business Engine",
        "subtitle": "Deep dive into the origin, problem, and market conditions",
        "cards": business_cards
    })

    # SECTION 4: Growth & Monetization
    growth_cards = []

    # Card 1: Early Growth
    initial_channels = early_growth.get("initial_channels", [])
    growth_cards.append({
        "icon": "📈",
        "title": "Early Growth & Distribution",
        "description": early_growth.get("why_users_adopted", ""),
        "points": [
            f"**Initial Channels**: {', '.join(initial_channels)}",
            f"**Early Distribution**: {early_growth.get('early_distribution_mechanics', '')}"
        ]
    })

    # Card 2: Monetization
    growth_cards.append({
        "icon": "💰",
        "title": "Monetization Logic",
        "description": monetization.get("initial_model", ""),
        "points": [
            f"**Why Users Paid**: {monetization.get('why_users_paid', '')}",
            f"**Models That Would Fail**: {monetization.get('models_that_would_fail', '')}"
        ]
    })

    # Card 3: Fundamental Human Need
    growth_cards.append({
        "icon": "💖",
        "title": "Fundamental Human Need",
        "description": f"Primary need: **{human_need.get('primary_need', '')}**",
        "points": [
            human_need.get("why_it_mattered_then", "")
        ]
    })

    case_study["sections"].append({
        "type": "business_understanding",
        "title": "2. Growth Engine & Human Psychology",
        "subtitle": "How they acquired users and tapped into deep needs",
        "cards": growth_cards
    })

    # SECTION 5: Why It Worked (Synthesis)
    synthesis_cards = [
        {
            "icon": "🎯",
            "title": "Why It Survived",
            "description": synthesis.get("why_it_worked", "")
        },
        {
            "icon": "🔗",
            "title": "Key Alignment Factors",
            "description": synthesis.get("key_alignment_factors", "")
        },
        {
            "icon": "⚡",
            "title": "Historical Inevitability",
            "description": synthesis.get("historical_inevitability_thesis", "")
        }
    ]

    case_study["sections"].append({
        "type": "why_brand",
        "title": "Why It Worked",
        "subtitle": "The synthesis: what aligned perfectly",
        "highlight_text": "aligned perfectly",
        "cards": synthesis_cards
    })

    # Add voice_of_customer section if present (reddit_intelligence type)
    if has_voice_of_customer:
        voc_data = json_data.get("voice_of_customer", {})
        voc_section = transform_voice_of_customer_to_reddit_intelligence(voc_data, app_name)
        if voc_section:
            case_study["sections"].append(voc_section)

    return case_study


def transform_voice_of_customer_to_reddit_intelligence(voc_data: dict, app_name: str) -> dict:
    """
    Transform voice_of_customer behavioral analysis into reddit_intelligence section format

    Args:
        voc_data: Voice of customer JSON data from behavioral analysis
        app_name: Name of the app

    Returns:
        reddit_intelligence section dict matching template structure
    """

    # Build reddit_intelligence section (even if voc_data is empty, use defaults)
    section = {
        "type": "reddit_intelligence"
    }

    # Verdict (required)
    verdict = voc_data.get("verdict", {})
    section["verdict"] = {
        "headline": verdict.get("headline", "Analysis in progress"),
        "subhead": verdict.get("subhead", f"Community sentiment analysis for {app_name}"),
        "trajectory": verdict.get("trajectory", "stable"),
        "trajectoryLabel": verdict.get("trajectoryLabel", "Stable")
    }

    # Metadata (required)
    metadata = voc_data.get("metadata", {})
    section["metadata"] = {
        "posts": metadata.get("posts", metadata.get("total_posts", 0)),
        "subreddits": metadata.get("subreddits", metadata.get("total_subreddits", 0)),
        "timespan": metadata.get("timespan", metadata.get("date_range", "Unknown")),
        "confidence": metadata.get("confidence", "medium"),
        "lastUpdated": metadata.get("lastUpdated", datetime.now().strftime("%B %Y"))
    }

    # Sentiment distribution (required)
    sentiment = voc_data.get("sentiment", {})
    section["sentiment"] = {
        "positive": sentiment.get("positive", 0),
        "negative": sentiment.get("negative", 0),
        "neutral": sentiment.get("neutral", 0),
        "mixed": sentiment.get("mixed", 0)
    }

    # Sentiment shift over time (optional)
    shift = voc_data.get("shift", voc_data.get("sentiment_shift", {}))
    if shift:
        section["shift"] = {
            "title": shift.get("title", "The Sentiment Shift"),
            "events": shift.get("events", [])
        }

    # Wins (where app is winning)
    wins = voc_data.get("wins", voc_data.get("where_winning", []))
    if wins:
        section["wins"] = wins

    # Losses (where app is losing)
    losses = voc_data.get("losses", voc_data.get("where_losing", []))
    if losses:
        section["losses"] = losses

    # Multi-lens interpretation
    lenses = voc_data.get("lenses", voc_data.get("multi_lens_interpretation", []))
    if lenses:
        section["lenses"] = lenses

    # Emergent lens (discovered patterns)
    emergent_lens = voc_data.get("emergentLens", voc_data.get("emergent_lens", {}))
    if emergent_lens:
        section["emergentLens"] = emergent_lens

    # Growth and retention loops
    loops = voc_data.get("loops", voc_data.get("growth_loops", []))
    if loops:
        section["loops"] = loops

    # Competitors mentioned
    competitors = voc_data.get("competitors", voc_data.get("competitive_landscape", []))
    if competitors:
        section["competitors"] = competitors

    # Strategic recommendations
    recommendations = voc_data.get("recommendations", voc_data.get("strategic_implications", {}))
    if recommendations:
        section["recommendations"] = {
            "leanInto": recommendations.get("leanInto", recommendations.get("lean_into", [])),
            "pullBack": recommendations.get("pullBack", recommendations.get("pull_back", [])),
            "structuralChange": recommendations.get("structuralChange", recommendations.get("structural_change", {}))
        }

    return section


def publish_to_replit(json_file: str, app_name: str, output_dir: str = None):
    """
    Publish Perplexity analysis to Replit YAML format

    Args:
        json_file: Path to Perplexity JSON output
        app_name: Name of the app
        output_dir: Directory to save YAML file
    """

    # Load JSON data
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    # Transform to YAML format
    case_study = transform_to_yaml(json_data, app_name)

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(__file__).parent.parent / 'outputs' / 'replit'

    output_path.mkdir(parents=True, exist_ok=True)

    # Save YAML file
    yaml_filename = f"{app_name.lower().replace(' ', '-')}.yaml"
    yaml_file = output_path / yaml_filename

    with open(yaml_file, 'w') as f:
        yaml.dump(case_study, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"✅ Published to Replit format:")
    print(f"   📄 {yaml_file}")
    print(f"\n📝 To add to your Replit app:")
    print(f"   1. Copy {yaml_filename} to your Replit project's case-studies/ folder")
    print(f"   2. Access at: /case-studies/{app_name.lower().replace(' ', '-')}")

    return yaml_file


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish_to_replit.py 'App Name' 'path/to/json_data.json' [output_dir]")
        print("Example: python publish_to_replit.py 'Flo Health' '../outputs/flo_test/flo_health_data.json' '../outputs/replit'")
        sys.exit(1)

    app_name = sys.argv[1]
    json_file = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        yaml_file = publish_to_replit(json_file, app_name, output_dir)
        print(f"\n✅ Replit case study created successfully!")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
