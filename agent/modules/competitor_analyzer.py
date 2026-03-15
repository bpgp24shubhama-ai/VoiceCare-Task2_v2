"""
Competitor Analysis Module.

Uses GPT-5 web search to perform real-time competitive intelligence
on voice AI / contact center competitors, analyzing their LinkedIn
strategies, content patterns, and AI engine visibility.
"""

import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """Analyze competitors using GPT-5 with live web search."""

    def __init__(self, ai_engine, config: dict):
        self.ai = ai_engine
        self.config = config
        self.competitors = config.get("competitors", [])

    def full_competitive_analysis(self) -> dict:
        """Run a comprehensive competitive analysis across all competitors."""
        competitor_list = "\n".join(
            f"- {c['name']} ({c['website']}, LinkedIn: {c['linkedin']})"
            for c in self.competitors
        )

        prompt = f"""Perform a comprehensive competitive analysis for VoiceCare.ai against these competitors in the voice AI / contact center AI space:

{competitor_list}

Search the web for the LATEST information on each competitor. For each competitor, analyze:

1. **LinkedIn Presence**: Estimated follower count, posting frequency, engagement rates, content themes
2. **Content Strategy**: What types of content they post (thought leadership, product updates, case studies, videos, carousels), what gets the most engagement
3. **AI Engine Visibility**: Search for each competitor on queries like "best voice analytics software", "AI contact center solutions" - who ranks where?
4. **Recent News & Moves**: Latest funding, product launches, partnerships, awards
5. **Weaknesses & Gaps**: Where are they underperforming? What topics are they NOT covering?

Then provide:
- **Competitive Gap Analysis**: Where VoiceCare.ai can differentiate
- **Content Opportunities**: Specific topics/formats competitors are missing
- **Quick Win Strategies**: 5 immediate actions VoiceCare.ai can take to gain ground
- **Ranking**: Rank all competitors + VoiceCare.ai by estimated LinkedIn strength"""

        schema = {
            "competitors": [
                {
                    "name": "string",
                    "linkedin_followers_estimate": "number",
                    "posting_frequency": "string",
                    "top_content_themes": ["string"],
                    "engagement_level": "string",
                    "ai_visibility_score": "1-10",
                    "recent_moves": ["string"],
                    "weaknesses": ["string"],
                }
            ],
            "gap_analysis": ["string"],
            "content_opportunities": ["string"],
            "quick_wins": ["string"],
            "ranking": [{"rank": "number", "company": "string", "score": "number"}],
        }

        logger.info("Running full competitive analysis with web search...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def analyze_competitor_content(self, competitor_name: str) -> dict:
        """Deep-dive into a specific competitor's content strategy."""
        competitor = next(
            (c for c in self.competitors if c["name"].lower() == competitor_name.lower()),
            None,
        )
        if not competitor:
            return {"error": f"Competitor '{competitor_name}' not found in config"}

        prompt = f"""Do a deep analysis of {competitor['name']}'s LinkedIn content strategy.

Search their LinkedIn page ({competitor['linkedin']}) and website ({competitor['website']}) for recent activity.

Analyze:
1. **Last 20 posts**: What topics, formats (text, image, video, carousel, poll), and hooks do they use?
2. **Engagement patterns**: Which posts got the most likes/comments/shares? Why?
3. **Posting schedule**: When do they post? How often?
4. **Hashtag strategy**: What hashtags do they use consistently?
5. **Call-to-action patterns**: How do they drive engagement?
6. **Employee advocacy**: Are employees resharing company content?
7. **Thought leadership**: Do executives post separately? What about?

Provide specific, actionable insights VoiceCare.ai can use to outperform them."""

        schema = {
            "competitor": competitor_name,
            "content_formats": {"text": "percentage", "image": "percentage", "video": "percentage", "carousel": "percentage", "poll": "percentage"},
            "top_performing_themes": ["string"],
            "posting_schedule": "string",
            "hashtags": ["string"],
            "engagement_tactics": ["string"],
            "executive_presence": "string",
            "vulnerabilities": ["string"],
            "actionable_insights_for_voicecare": ["string"],
        }

        logger.info(f"Analyzing {competitor_name}'s content strategy...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def ai_engine_visibility_comparison(self) -> dict:
        """Compare how VoiceCare.ai vs competitors appear on AI engines."""
        queries = self.config.get("ai_visibility", {}).get("target_queries", [])
        query_list = "\n".join(f"- \"{q}\"" for q in queries)
        competitor_list = ", ".join(c["name"] for c in self.competitors)

        prompt = f"""Perform an AI engine visibility audit. Search the web for how VoiceCare.ai and its competitors ({competitor_list}) are referenced and ranked.

Test these search queries:
{query_list}

For each query, determine:
1. Which companies appear in search results?
2. What position/prominence does each company have?
3. Are they mentioned in review sites, comparison articles, analyst reports?

Also check:
- Wikipedia presence for each company
- Mentions on G2, Gartner, Forrester
- Presence in "best of" / "top X" listicles
- Citation frequency in industry publications

Provide a visibility scorecard and specific recommendations for VoiceCare.ai to improve its AI engine rankings."""

        schema = {
            "visibility_scorecard": [
                {
                    "company": "string",
                    "overall_score": "1-100",
                    "search_presence": "1-10",
                    "review_site_presence": "1-10",
                    "analyst_coverage": "1-10",
                    "listicle_presence": "1-10",
                }
            ],
            "query_results": [
                {
                    "query": "string",
                    "top_mentioned_companies": ["string"],
                    "voicecare_position": "string",
                }
            ],
            "recommendations": ["string"],
        }

        logger.info("Running AI engine visibility comparison...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def trending_topics_scan(self) -> dict:
        """Scan for trending topics in voice AI / CX space."""
        prompt = """Search the web for the LATEST trending topics and conversations in these spaces:

1. Voice AI and speech analytics
2. Contact center technology
3. Customer experience (CX) innovation
4. AI in customer service
5. Conversational AI

Find:
- What topics are generating the most buzz RIGHT NOW on LinkedIn?
- What recent industry reports or studies have been published?
- What conferences or events are coming up?
- What regulatory changes or industry shifts are happening?
- What viral posts or discussions are happening in these communities?

Return trending topics that VoiceCare.ai can create content around to ride the wave of current interest."""

        schema = {
            "trending_topics": [
                {
                    "topic": "string",
                    "trend_strength": "high/medium/low",
                    "relevance_to_voicecare": "high/medium/low",
                    "content_angle": "string",
                    "suggested_post_format": "string",
                }
            ],
            "upcoming_events": [{"event": "string", "date": "string", "opportunity": "string"}],
            "recent_reports": [{"title": "string", "source": "string", "key_finding": "string"}],
            "viral_discussions": [{"topic": "string", "platform": "string", "engagement": "string"}],
        }

        logger.info("Scanning for trending topics...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)
