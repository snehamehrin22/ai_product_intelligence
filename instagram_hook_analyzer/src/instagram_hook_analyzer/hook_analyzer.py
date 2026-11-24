"""GPT-4o hook analysis."""

import os
import json
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class HookAnalyzerAI:
    """Analyzes hooks using GPT-4o."""

    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)

    def analyze_hook(
        self,
        hook_text: str,
        full_transcript: str,
        engagement: Dict[str, int],
        caption: str = ""
    ) -> Dict:
        """
        Analyze Instagram Reel: hook, body framework, CTA.

        Args:
            hook_text: Hook text (OCR + first 30 words)
            full_transcript: Complete video transcript
            engagement: Dict with views, likes, comments
            caption: Full reel caption

        Returns:
            Analysis dictionary with hook, framework, CTA
        """
        system_prompt = """You are a viral content strategist specializing in Instagram Reels.

Analyze the FULL REEL structure:
1. HOOK (first 3-5 seconds) - Attention capture mechanism
2. BODY FRAMEWORK - How content is structured (story arc, teaching framework, list format, etc.)
3. CTA (Call to Action) - What the creator asks viewers to do

Hook patterns:
- curiosity_gap, bold_claim, question, number, problem_callout, result_reveal,
  how_to_promise, story_open, direct_address, pattern_interrupt

Body frameworks:
- problem_agitate_solution, before_after_bridge, listicle, story_arc,
  teaching_steps, compare_contrast, myth_busting, personal_story

CTA types:
- follow, save, share, comment, link_in_bio, dm, watch_more, try_this, none

Return JSON only."""

        user_prompt = f"""Analyze this Instagram Reel:

HOOK (first 5 seconds - OCR + audio):
{hook_text}

FULL TRANSCRIPT:
{full_transcript}

CAPTION:
{caption}

ENGAGEMENT:
- Views: {engagement.get('views') or 0:,}
- Likes: {engagement.get('likes') or 0:,}
- Comments: {engagement.get('comments') or 0:,}

Return JSON:
{{
  "hook_pattern": "pattern_name",
  "hook_text_extracted": "exact hook text spoken/shown",
  "hook_score": 0-100,
  "body_framework": "framework_name",
  "body_summary": "2-3 sentence summary of how the body delivers value",
  "cta_type": "cta_type",
  "cta_text_extracted": "exact CTA spoken/shown",
  "what_works": "Why this reel is effective (2-3 sentences)",
  "what_fails": "Missed opportunities (2-3 sentences)",
  "key_takeaway": "One sentence - what makes this viral"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"GPT-4o analysis error: {e}")
            return {
                "hook_pattern": "unknown",
                "hook_score": 0,
                "what_works": "Analysis failed",
                "what_fails": str(e),
                "suggested_rewrite": ""
            }
