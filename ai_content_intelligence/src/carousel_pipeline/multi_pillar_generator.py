"""
Multi-pillar carousel generation module.

Generates 3 carousels from a single research file using the direct XML prompt approach.
Two-stage generation: Claude (draft) → ChatGPT (tighten).
"""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

from .schemas import DirectCarouselOutput, XMLCarouselSlide
from .prompt_builder import build_carousel_prompt, get_pillar_metadata

load_dotenv()


def parse_xml_carousel(xml_text: str) -> Dict:
    """
    Parse XML carousel response into dict.

    Args:
        xml_text: XML string from LLM response

    Returns:
        Dict with carousel data
    """
    # Remove any text before/after the XML
    start = xml_text.find("<carousel>")
    end = xml_text.find("</carousel>") + len("</carousel>")

    if start == -1 or end == -1:
        raise ValueError("No <carousel> tags found in response")

    xml_text = xml_text[start:end]

    # Parse XML
    root = ET.fromstring(xml_text)

    carousel_data = {
        "title": root.find("title").text if root.find("title") is not None else "Untitled",
        "pillar": root.find("pillar").text if root.find("pillar") is not None else "unknown",
        "slides": []
    }

    # Parse slides
    slides_elem = root.find("slides")
    if slides_elem is not None:
        for slide in slides_elem.findall("slide"):
            index = int(slide.get("index", 0))
            title = slide.find("title")
            text_lines = [t.text for t in slide.findall("text") if t.text]

            carousel_data["slides"].append({
                "index": index,
                "title": title.text if title is not None and title.text else None,
                "text_lines": text_lines
            })

    return carousel_data


def generate_with_claude(
    prompt: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514"
) -> str:
    """
    Generate carousel XML with Claude.

    Args:
        prompt: Complete prompt (from prompt_builder)
        api_key: Anthropic API key
        model: Claude model

    Returns:
        XML response string
    """
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        temperature=0.3,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def tighten_with_chatgpt(
    carousel_xml: str,
    api_key: str,
    model: str = "gpt-4o"
) -> str:
    """
    Optional: Tighten prose with ChatGPT while keeping structure.

    Args:
        carousel_xml: XML carousel from Claude
        api_key: OpenAI API key
        model: GPT model

    Returns:
        Tightened XML string
    """
    client = OpenAI(api_key=api_key)

    system_prompt = """You are a prose editor.

Your job: tighten the text in this carousel XML WITHOUT changing the structure.

Rules:
- Keep ALL XML tags exactly as they are
- Keep the same number of slides
- Keep slide titles unchanged
- Tighten the text lines: shorter sentences (avg 3-6 words), remove filler, sharpen language
- Match the style: calm, surgical, non-hype
- No emojis, no buzzwords

Return the complete XML with tightened text."""

    user_prompt = f"""Tighten the prose in this carousel:

{carousel_xml}

Return the complete XML with tightened text. Keep structure identical."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=4000
    )

    return response.choices[0].message.content


def generate_carousel_for_pillar(
    research_path: str,
    pillar_id: str,
    use_chatgpt_tightening: bool = True,
    optional_constraints: str = "",
    custom_template_path: str = None
) -> DirectCarouselOutput:
    """
    Generate carousel for a single pillar.

    Args:
        research_path: Path to research markdown file
        pillar_id: Pillar identifier (e.g., "pillar_01")
        use_chatgpt_tightening: Whether to use ChatGPT for prose tightening
        optional_constraints: Optional constraints string
        custom_template_path: Optional path to custom prompt template (for iterations)

    Returns:
        Validated DirectCarouselOutput
    """
    # Load API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not anthropic_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    if use_chatgpt_tightening and not openai_key:
        raise ValueError("OPENAI_API_KEY not found (required for prose tightening)")

    # Load research
    research_path_obj = Path(research_path)
    if not research_path_obj.exists():
        raise FileNotFoundError(f"Research file not found: {research_path}")

    research = research_path_obj.read_text(encoding="utf-8")

    # Build prompt
    print(f"\n📚 Building prompt for {pillar_id}...")
    prompt = build_carousel_prompt(
        research=research,
        pillar_id=pillar_id,
        optional_constraints=optional_constraints,
        custom_template_path=custom_template_path
    )

    # Stage 1: Claude generation
    print(f"🤖 Stage 1: Generating with Claude...")
    claude_xml = generate_with_claude(prompt, anthropic_key)

    # Stage 2: Optional ChatGPT tightening
    final_xml = claude_xml
    if use_chatgpt_tightening:
        print(f"✍️  Stage 2: Tightening prose with ChatGPT...")
        final_xml = tighten_with_chatgpt(claude_xml, openai_key)

    # Parse XML
    print(f"✓ Parsing XML response...")
    carousel_dict = parse_xml_carousel(final_xml)

    # Get metadata
    pillar_meta = get_pillar_metadata(pillar_id)

    # Build validated model
    slides = [
        XMLCarouselSlide(
            index=s["index"],
            title=s["title"],
            text_lines=s["text_lines"]
        )
        for s in carousel_dict["slides"]
    ]

    carousel = DirectCarouselOutput(
        title=carousel_dict["title"],
        pillar=pillar_id,
        slides=slides,
        source_research=str(research_path),
        framework_used=pillar_meta["framework_file"],
        total_slides=len(slides)
    )

    print(f"✓ Carousel generated ({carousel.total_slides} slides)")

    return carousel


def generate_all_three_carousels(
    research_path: str,
    output_dir: str = "data/carousel_outputs",
    use_chatgpt_tightening: bool = True,
    save_xml: bool = True,
    save_json: bool = True
) -> Dict[str, DirectCarouselOutput]:
    """
    Generate all 3 carousels from a single research file.

    Args:
        research_path: Path to research markdown file
        output_dir: Directory to save outputs
        use_chatgpt_tightening: Whether to use ChatGPT for prose tightening
        save_xml: Save XML output
        save_json: Save JSON output

    Returns:
        Dict mapping pillar_id to DirectCarouselOutput
    """
    research_name = Path(research_path).stem
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("🚀 MULTI-PILLAR CAROUSEL GENERATION")
    print("="*70)
    print(f"\nResearch: {research_name}")
    print(f"Output: {output_dir}")
    print(f"\nGenerating 3 carousels (one per pillar)...")

    results = {}

    for pillar_id in ["pillar_01", "pillar_02", "pillar_03"]:
        print("\n" + "-"*70)
        print(f"PILLAR: {pillar_id}")
        print("-"*70)

        try:
            # Generate carousel
            carousel = generate_carousel_for_pillar(
                research_path=research_path,
                pillar_id=pillar_id,
                use_chatgpt_tightening=use_chatgpt_tightening
            )

            results[pillar_id] = carousel

            # Get pillar name for filename
            pillar_meta = get_pillar_metadata(pillar_id)
            pillar_slug = pillar_meta["id"]

            # Save XML
            if save_xml:
                xml_path = output_path / f"{research_name}_{pillar_id}_{pillar_slug}.xml"
                xml_content = build_xml_from_carousel(carousel)
                xml_path.write_text(xml_content, encoding="utf-8")
                print(f"💾 XML saved: {xml_path}")

            # Save JSON
            if save_json:
                json_path = output_path / f"{research_name}_{pillar_id}_{pillar_slug}.json"
                json_path.write_text(
                    json.dumps(carousel.model_dump(), indent=2, default=str),
                    encoding="utf-8"
                )
                print(f"💾 JSON saved: {json_path}")

        except Exception as e:
            print(f"❌ Error generating {pillar_id}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print(f"✅ Complete! Generated {len(results)}/3 carousels")
    print("="*70)

    return results


def build_xml_from_carousel(carousel: DirectCarouselOutput) -> str:
    """
    Build XML string from DirectCarouselOutput.

    Args:
        carousel: Validated carousel model

    Returns:
        XML string
    """
    root = ET.Element("carousel")

    title_elem = ET.SubElement(root, "title")
    title_elem.text = carousel.title

    pillar_elem = ET.SubElement(root, "pillar")
    pillar_elem.text = carousel.pillar

    slides_elem = ET.SubElement(root, "slides")

    for slide in carousel.slides:
        slide_elem = ET.SubElement(slides_elem, "slide")
        slide_elem.set("index", str(slide.index))

        if slide.title:
            title_elem = ET.SubElement(slide_elem, "title")
            title_elem.text = slide.title

        for line in slide.text_lines:
            text_elem = ET.SubElement(slide_elem, "text")
            text_elem.text = line

    # Pretty print
    from xml.dom import minidom
    xml_str = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ")
