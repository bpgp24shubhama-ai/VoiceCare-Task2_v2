"""
Competitor Analysis Module.

Uses GPT-5 web search + SEMrush real data to perform competitive
intelligence on voice AI / contact center competitors, analyzing their
LinkedIn strategies, content patterns, and AI engine visibility.

SEMrush enriches every analysis with hard numbers: organic traffic,
keyword rankings, backlink authority, and keyword gaps.
"""

import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """Analyze competitors using GPT-5 + SEMrush live data."""

    def __init__(self, ai_engine, config: dict, semrush=None):
        self.ai = ai_engine
        self.config = config
        self.competitors = config.get("competitors", [])
        self.semrush = semrush  # optional SEMrushClient

    # ------------------------------------------------------------------ #
    # Internal helper                                                      #
    # ------------------------------------------------------------------ #

    def _semrush_section(self, our_domain: str) -> str:
        """Fetch SEMrush data for all domains and format as a prompt block.

        Returns an empty string if SEMrush is not configured.
        """
        if not self.semrush:
            return ""

        competitor_domains = [
            c["website"].replace("https://", "").replace("http://", "").rstrip("/")
            for c in self.competitors
        ]
        our_domain_clean = our_domain.replace("https://", "").replace("http://", "").rstrip("/")

        try:
            logger.info("Fetching SEMrush competitive landscape data...")
            landscape = self.semrush.competitive_landscape(our_domain_clean, competitor_domains)
        except Exception as e:
            logger.warning(f"SEMrush data fetch failed: {e}")
            return ""

        lines = ["\n## REAL SEMrush Data (use these exact figures in your analysis)\n"]
        for domain, report in landscape.items():
            ov = report.get("overview", {})
            kws = report.get("top_keywords", [])
            bl = report.get("backlinks", {})
            lines.append(f"### {domain}")
            lines.append(f"- Organic Keywords: {ov.get('Or', 'N/A')}")
            lines.append(f"- Monthly Organic Traffic: {ov.get('Ot', 'N/A')}")
            lines.append(f"- Authority Score: {ov.get('Rk', 'N/A')}")
            lines.append(f"- Backlinks Total: {bl.get('total', 'N/A')}")
            lines.append(f"- Referring Domains: {bl.get('domains_num', 'N/A')}")
            if kws:
                top3 = [(k.get("Ph", ""), k.get("Po", ""), k.get("Nq", "")) for k in kws[:3]]
                kw_str = ", ".join(f'"{ph}" (pos {po}, vol {nq})' for ph, po, nq in top3)
                lines.append(f"- Top keywords: {kw_str}")
            lines.append("")
        return "\n".join(lines)

    def full_competitive_analysis(self) -> dict:
        """Run a comprehensive competitive analysis across all competitors."""
        competitor_list = "\n".join(
            f"- {c['name']} ({c['website']}, LinkedIn: {c['linkedin']})"
            for c in self.competitors
        )
        our_domain = self.config.get("company", {}).get("website", "voicecare.ai")
        semrush_block = self._semrush_section(our_domain)

        prompt = f"""Perform a comprehensive competitive analysis for VoiceCare.ai against these competitors in the voice AI / contact center AI space:

{competitor_list}
{semrush_block}
Search the web for the LATEST information on each competitor. For each competitor, analyze:

1. **SEO & Traffic** (use the SEMrush figures above as ground truth — do NOT estimate traffic if real data is provided):
   - Organic traffic, keyword count, authority score, backlinks
   - Top-ranking keywords and content pages
2. **LinkedIn Presence**: Estimated follower count, posting frequency, engagement rates, content themes
3. **Content Strategy**: What types of content they post (thought leadership, product updates, case studies, videos, carousels), what gets the most engagement
4. **AI Engine Visibility**: Search for each competitor on queries like "best voice analytics software", "AI contact center solutions" - who ranks where?
5. **Recent News & Moves**: Latest funding, product launches, partnerships, awards
6. **Weaknesses & Gaps**: Where are they underperforming? What topics are they NOT covering?

Then provide:
- **Competitive Gap Analysis**: Where VoiceCare.ai can differentiate
- **Keyword Gap**: Which high-value keywords competitors rank for that VoiceCare.ai should target
- **Content Opportunities**: Specific topics/formats competitors are missing
- **Quick Win Strategies**: 5 immediate actions VoiceCare.ai can take to gain ground
- **Ranking**: Rank all competitors + VoiceCare.ai by combined digital strength (SEO + LinkedIn + AI visibility)"""

        schema = {
            "competitors": [
                {
                    "name": "string",
                    "organic_traffic": "number or string from SEMrush",
                    "organic_keywords": "number or string from SEMrush",
                    "authority_score": "number or string from SEMrush",
                    "backlinks": "number or string from SEMrush",
                    "top_seo_keywords": ["string"],
                    "linkedin_followers_estimate": "number",
                    "posting_frequency": "string",
                    "top_content_themes": ["string"],
                    "engagement_level": "string",
                    "ai_visibility_score": "1-10",
                    "recent_moves": ["string"],
                    "weaknesses": ["string"],
                }
            ],
            "keyword_gaps": [
                {"keyword": "string", "competitor_ranking": "string", "search_volume": "string", "difficulty": "string"}
            ],
            "gap_analysis": ["string"],
            "content_opportunities": ["string"],
            "quick_wins": ["string"],
            "ranking": [{"rank": "number", "company": "string", "score": "number", "rationale": "string"}],
        }

        logger.info("Running full competitive analysis with web search...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def semrush_keyword_gap_analysis(self, competitor_name: str) -> dict:
        """Use SEMrush to find exact keyword gaps vs a competitor."""
        competitor = next(
            (c for c in self.competitors if c["name"].lower() == competitor_name.lower()),
            None,
        )
        if not competitor:
            return {"error": f"Competitor '{competitor_name}' not found in config"}

        our_domain = (
            self.config.get("company", {})
            .get("website", "voicecare.ai")
            .replace("https://", "").replace("http://", "").rstrip("/")
        )
        comp_domain = (
            competitor["website"]
            .replace("https://", "").replace("http://", "").rstrip("/")
        )

        if not self.semrush:
            return {"error": "SEMrush not configured. Add SEMRUSH_API_KEY to .env"}

        try:
            gap_keywords = self.semrush.keyword_gap(our_domain, comp_domain, limit=30)
            our_overview = self.semrush.domain_overview(our_domain)
            comp_overview = self.semrush.domain_overview(comp_domain)
        except Exception as e:
            return {"error": str(e)}

        gap_list = "\n".join(
            f"- \"{row.get('Ph', '')}\" | pos {row.get('Po', '?')} | vol {row.get('Nq', '?')} | url: {row.get('Ur', '')}"
            for row in gap_keywords[:20]
        )

        prompt = f"""Analyse this SEMrush keyword gap data and recommend a content strategy.

VoiceCare.ai vs {competitor_name}:
- Our organic traffic: {our_overview.get('Ot', 'N/A')} | keywords: {our_overview.get('Or', 'N/A')}
- {competitor_name} organic traffic: {comp_overview.get('Ot', 'N/A')} | keywords: {comp_overview.get('Or', 'N/A')}

Top keywords {competitor_name} ranks for that VoiceCare.ai does NOT rank for:
{gap_list}

For each keyword group, recommend:
1. Content type to create (blog post, landing page, comparison page, FAQ, etc.)
2. Suggested title
3. Key angle/thesis
4. LinkedIn content tie-in (how to promote via LinkedIn)
5. Expected traffic if we rank top-5

Prioritise by: (high volume × low difficulty × high relevance to VoiceCare.ai)."""

        schema = {
            "competitor": competitor_name,
            "traffic_gap": "string - how much more traffic competitor gets",
            "keyword_opportunities": [
                {
                    "keyword": "string",
                    "search_volume": "string",
                    "competitor_position": "string",
                    "content_type": "string",
                    "suggested_title": "string",
                    "angle": "string",
                    "linkedin_tie_in": "string",
                    "priority": "high/medium/low",
                }
            ],
            "quick_content_wins": ["string"],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=False)

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
