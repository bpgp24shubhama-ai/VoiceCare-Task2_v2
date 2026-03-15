"""
Content Generation Engine.

Generates various types of LinkedIn content optimized for engagement
and growth, including posts, carousels, polls, articles, and newsletters.

When a SEMrush client is provided, content is enriched with real keyword
data so every piece is also optimised for organic search (dual-purpose:
LinkedIn reach AND SEO ranking signal for AI engine visibility).
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate high-engagement LinkedIn content for VoiceCare.ai."""

    def __init__(self, ai_engine, config: dict, semrush=None):
        self.ai = ai_engine
        self.config = config
        self.semrush = semrush  # optional SEMrushClient

    def _keyword_context(self, topic: str) -> str:
        """Fetch SEMrush keyword suggestions for a topic and return a prompt block."""
        if not self.semrush:
            return ""
        try:
            suggestions = self.semrush.keyword_suggestions(topic, limit=10)
            if not suggestions:
                return ""
            lines = ["\n## SEMrush Keyword Data for this topic (weave naturally into content)\n"]
            for row in suggestions[:8]:
                ph = row.get("Ph", "")
                nq = row.get("Nq", "?")
                co = row.get("Co", "?")
                lines.append(f'- "{ph}" — monthly searches: {nq}, difficulty: {co}/100')
            lines.append(
                "\nNaturally include 2-3 of these phrases in the content to boost SEO as well as LinkedIn reach.\n"
            )
            return "\n".join(lines)
        except Exception as e:
            logger.debug(f"SEMrush keyword fetch failed for '{topic}': {e}")
            return ""

    def generate_carousel(self, topic: str, slide_count: int = 10) -> dict:
        """Generate a LinkedIn carousel post with slide-by-slide content."""
        kw_block = self._keyword_context(topic)
        prompt = f"""Create a viral LinkedIn carousel for VoiceCare.ai about: {topic}
{kw_block}
Search the web for the latest data, stats, and insights on this topic.

Design a {slide_count}-slide carousel that follows the proven LinkedIn carousel formula:

Slide 1 (Cover): Bold, curiosity-driven title. Should make people STOP scrolling.
Slides 2-{slide_count - 1}: One key insight per slide. Use:
  - Big numbers / statistics
  - Short sentences (max 2 per slide)
  - Visual hierarchy (headline + supporting text)
  - Progressive revelation (each slide builds on the last)
Slide {slide_count} (CTA): Follow VoiceCare.ai for more insights + key takeaway

Also provide:
- The LinkedIn post caption (hook + brief description + hashtags)
- Design direction for each slide (colors, layout, icons)
- Target audience and why this will resonate"""

        schema = {
            "topic": topic,
            "post_caption": "string - the LinkedIn text post accompanying the carousel",
            "slides": [
                {
                    "slide_number": "number",
                    "headline": "string",
                    "body_text": "string",
                    "design_notes": "string",
                    "data_source": "string (if applicable)",
                }
            ],
            "target_audience": "string",
            "virality_factors": ["string"],
            "hashtags": ["string"],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_poll(self, topic: str) -> dict:
        """Generate an engaging LinkedIn poll."""
        prompt = f"""Create a high-engagement LinkedIn poll for VoiceCare.ai about: {topic}

Search for trending discussions and debates in voice AI / contact center / CX space.

Requirements:
- Poll question must be PROVOCATIVE or SURPRISING to drive participation
- Options should be balanced (no obviously "right" answer)
- Include a "See results" option to maximize votes
- Write a compelling post caption that frames the poll
- Plan a follow-up post to share results and insights

The best LinkedIn polls:
1. Tap into genuine debates in the industry
2. Make people curious about what others think
3. Drive comments beyond just voting
4. Position the poster (VoiceCare.ai) as a thought leader"""

        schema = {
            "poll_question": "string",
            "options": ["string - 4 options including See results"],
            "post_caption": "string",
            "why_engaging": "string",
            "follow_up_post_plan": "string",
            "hashtags": ["string"],
            "expected_engagement": "string",
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_thought_leadership_post(self, executive_name: str, executive_role: str, topic: str) -> dict:
        """Generate a thought leadership post for an executive."""
        prompt = f"""Write a thought leadership LinkedIn post for {executive_name}, {executive_role} at VoiceCare.ai, about: {topic}

Search the web for the latest developments, data, and conversations about this topic.

The post should:
1. Be written in first person from {executive_name}'s perspective
2. Share a unique, contrarian, or insightful take
3. Draw from real industry data and trends (found via web search)
4. Feel authentic and personal, not corporate
5. Position VoiceCare.ai as an industry leader WITHOUT being salesy
6. Drive meaningful comments and discussion

Structure:
- Hook (pattern interrupt first line)
- Personal observation or experience
- Industry insight backed by data
- The contrarian take or unique perspective
- What this means for the industry
- Question to drive comments

This should NOT read like AI-generated content. Make it human."""

        schema = {
            "author": executive_name,
            "role": executive_role,
            "topic": topic,
            "full_post": "string",
            "hook": "string",
            "key_data_points_used": ["string"],
            "hashtags": ["string"],
            "engagement_prediction": "string",
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_data_driven_post(self, data_topic: str) -> dict:
        """Generate a post built around data and statistics."""
        kw_block = self._keyword_context(data_topic)
        prompt = f"""Create a data-driven LinkedIn post for VoiceCare.ai about: {data_topic}
{kw_block}
CRITICAL: Search the web for REAL, RECENT statistics and data about this topic. Include:
- Industry reports (Gartner, Forrester, McKinsey, etc.)
- Survey results
- Market data
- Research findings

Build the post around 3-5 compelling data points that tell a story. Format:

Hook: A surprising statistic that grabs attention
Body: Walk through the data points, connecting them to tell a narrative
Insight: What VoiceCare.ai has observed from its own experience
CTA: Ask readers to share their experience

Make the data points visually scannable (use numbers, percentages, bullet formatting).
Cite the sources within the post for credibility."""

        schema = {
            "topic": data_topic,
            "full_post": "string",
            "data_points": [
                {"stat": "string", "source": "string", "year": "string"}
            ],
            "hashtags": ["string"],
            "credibility_score": "string - why this post will be seen as authoritative",
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def repurpose_content(self, original_content: str, source_format: str) -> dict:
        """Repurpose existing content into multiple LinkedIn formats."""
        prompt = f"""Take this {source_format} content and repurpose it into multiple LinkedIn content pieces:

ORIGINAL CONTENT:
{original_content}

Create ALL of the following from this single piece of content:

1. **Text Post**: Standard LinkedIn text post (hook + value + CTA)
2. **Carousel Outline**: 8-10 slide carousel with headlines and body text
3. **Poll**: Engaging poll question derived from the content
4. **Newsletter Snippet**: Section for a LinkedIn newsletter
5. **Comment Bait**: 3 provocative one-liner posts derived from key points
6. **Thread**: Multi-post thread (3 connected posts over 3 days)
7. **Quote Graphics**: 3-5 quotable one-liners for image posts

Each format should be ready to publish with hashtags and engagement hooks."""

        schema = {
            "source_format": source_format,
            "text_post": "string",
            "carousel": {
                "caption": "string",
                "slides": [{"slide": "number", "headline": "string", "body": "string"}],
            },
            "poll": {"question": "string", "options": ["string"]},
            "newsletter_snippet": "string",
            "comment_bait_posts": ["string"],
            "thread": [{"day": "number", "post": "string"}],
            "quote_graphics": ["string"],
            "hashtags": ["string"],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=False)
