"""
AI Engine Visibility Optimizer (GEO - Generative Engine Optimization).

Optimizes VoiceCare.ai's presence and ranking on AI-powered search engines
like ChatGPT, Perplexity, Google Gemini, Claude, and Microsoft Copilot.

SEMrush integration provides real keyword volumes, SERP competitor lists,
and backlink authority data so every GEO recommendation is grounded in
actual search data, not estimates.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AIVisibilityOptimizer:
    """Optimize VoiceCare.ai visibility on AI search engines."""

    def __init__(self, ai_engine, config: dict, semrush=None):
        self.ai = ai_engine
        self.config = config
        self.semrush = semrush  # optional SEMrushClient
        self.target_engines = config.get("ai_visibility", {}).get("target_engines", [])
        self.target_queries = config.get("ai_visibility", {}).get("target_queries", [])

    # ------------------------------------------------------------------ #
    # Internal helper                                                      #
    # ------------------------------------------------------------------ #

    def _build_keyword_intelligence(self) -> str:
        """Fetch SEMrush data for target queries and return a prompt block."""
        if not self.semrush:
            return ""

        lines = ["\n## SEMrush Keyword Intelligence (real data — use exact figures)\n"]
        for query in self.target_queries[:8]:  # cap API calls
            try:
                kw = self.semrush.keyword_overview(query)
                serp = self.semrush.serp_competitors(query, limit=5)
                vol = kw.get("Nq", "N/A")
                diff = kw.get("Co", "N/A")
                cpc = kw.get("Cp", "N/A")
                serp_domains = [r.get("Dn", "") for r in serp]
                lines.append(f'**"{query}"**: volume={vol}, difficulty={diff}/100, CPC=${cpc}')
                lines.append(f"  SERP top-5: {', '.join(serp_domains)}")
            except Exception as e:
                logger.debug(f"SEMrush keyword lookup failed for '{query}': {e}")
        return "\n".join(lines)

    def full_geo_audit(self) -> dict:
        """Perform a full Generative Engine Optimization audit."""
        query_list = "\n".join(f'- "{q}"' for q in self.target_queries)
        engine_list = ", ".join(self.target_engines)
        kw_intelligence = self._build_keyword_intelligence()
        competitor_names = ", ".join(
            c["name"] for c in self.config.get("competitors", []) if c.get("name")
        )

        prompt = f"""Perform a comprehensive Generative Engine Optimization (GEO) audit for VoiceCare.ai.

GEO is the practice of optimizing a brand's visibility in AI-powered search engines ({engine_list}).
{kw_intelligence}
STEP 1 - Current State Audit:
Search the web to understand VoiceCare.ai's current digital footprint:
- Website content and SEO
- Presence on review sites (G2, Gartner, Capterra, TrustRadius)
- Wikipedia or knowledge base mentions
- Industry publication citations
- Social media presence
- Backlink profile quality

STEP 2 - Query Simulation:
Using the real SEMrush SERP data above (where provided), AND web search, determine who ranks for each query and who AI engines would cite:
{query_list}

STEP 3 - Competitor Benchmark:
Compare VoiceCare.ai's digital footprint to competitors ({competitor_names}).
Use the SEMrush keyword data to quantify exactly how far ahead or behind each competitor is.
Who has stronger signals for AI engine citation?

STEP 4 - GEO Strategy:
Create a detailed, prioritized action plan to improve VoiceCare.ai's AI engine visibility:

1. **Quick SEO wins**: Keywords with high volume + low difficulty from SEMrush data above where VoiceCare.ai is absent
2. **Content Authority Signals**: How to create content that AI engines cite
3. **Structured Data**: Schema markup, knowledge graph optimization
4. **Third-Party Validation**: Review sites, analyst reports, listicles to target
5. **Citation Building**: How to get mentioned in sources AI engines trust
6. **Technical SEO for AI**: Site structure, FAQ pages, entity optimization"""

        schema = {
            "current_visibility_score": "number (1-100)",
            "digital_footprint": {
                "website_authority": "string",
                "review_site_presence": ["string"],
                "publication_mentions": ["string"],
                "knowledge_base_status": "string",
            },
            "query_analysis": [
                {
                    "query": "string",
                    "likely_ai_response_includes": ["string"],
                    "voicecare_mentioned": "boolean",
                    "gap_to_close": "string",
                }
            ],
            "competitor_comparison": [
                {
                    "company": "string",
                    "geo_score": "number",
                    "strongest_signal": "string",
                }
            ],
            "geo_action_plan": [
                {
                    "priority": "number",
                    "action": "string",
                    "category": "string",
                    "expected_impact": "high/medium/low",
                    "effort": "high/medium/low",
                    "timeline": "string",
                    "details": "string",
                }
            ],
        }

        logger.info("Running full GEO audit...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_geo_content_plan(self) -> dict:
        """Generate content specifically designed to be cited by AI engines."""
        prompt = """Create a Generative Engine Optimization (GEO) content plan tailored for VoiceCare.ai, a company specializing in healthcare voice AI, AI medical scribes, ambient clinical voice solutions, and patient engagement automation.

The goal is to engineer content that generative AI engines (ChatGPT, Perplexity, Gemini, Google AI Overviews, etc.) will discover, extract, and cite when healthcare providers, hospital administrators, and practice managers ask questions about clinical voice AI and related topics.

Please design a content plan broken down into these five strategic categories, incorporating the latest GEO best practices (e.g., "answer nuggets," factual density, prompt-based research, and schema markup):

1. **Definitive Guides (Entity & Topical Authority):**
   - AI systems favor comprehensive, structurally clear content that answers follow-up questions.
   - *Examples:* "The Complete Guide to Ambient Clinical Voice Solutions in 2026," "AI Medical Scribes vs. Traditional Dictation: A Data-Driven Comparison."

2. **Original Research & Data (Citation-Worthy Fact-Density):**
   - AI engines specifically look for unique data, benchmarks, and verifiable statistics to cite in their answers.
   - *Examples:* Ideas for physician burnout surveys, time-savings impact reports on AI patient intake, or clinical documentation error-rate benchmarks.

3. **Comparison Pages (AI Shortlist & Consideration Phase):**
   - Buyers ask AI tools for unbiased comparisons. We need structured pages with tables and feature matrices so AI pulls our data rather than third-party interpretations.
   - *Examples:* "Top 10 AI Medical Scribe Platforms Compared," "Healthcare Voice AI Solutions: Feature & EHR Integration Matrix."

4. **Conversational FAQs & Prompt Responses:**
   - Content mapped directly to the long-tail, conversational prompts users type into AI systems (e.g., "How do I choose an AI scribe for Epic?").
   - *Examples:* A knowledge base of "Answer Nuggets" (short, 40-60 word definitive answers) covering HIPAA compliance, security, and implementation.

5. **Technical & E-E-A-T Content (Trust Signals):**
   - Technical depth establishes authority.
   - *Examples:* EHR integration guides (Epic, Cerner), whitepapers on ambient AI data privacy protocols, and clinical case studies with hard ROI metrics.

For each recommended content piece, please specify:
- **Title, format, and estimated length**
- **Target conversational prompts/queries it should capture**
- **Key entities, terms, and specific data points to include**
- **Formatting requirements for AI extractability** (e.g., H2s, bullet lists, comparison tables, schema types)
- **Omnichannel distribution strategy** (e.g., publishing on the main blog, Reddit, healthcare forums, YouTube, or PR distribution to secure external citations)"""

        schema = {
            "content_pieces": [
                {
                    "title": "string",
                    "category": "string",
                    "format": "string",
                    "target_queries": ["string"],
                    "key_topics": ["string"],
                    "publish_on": "string",
                    "estimated_length": "string",
                    "distribution": ["string"],
                    "priority": "number",
                }
            ],
            "quick_wins": ["string"],
            "monthly_content_cadence": {
                "guides": "number",
                "data_pieces": "number",
                "comparisons": "number",
                "faqs": "number",
                "technical": "number",
            },
        }

        logger.info("Generating GEO content plan...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def audit_specific_query(self, query: str) -> dict:
        """Audit VoiceCare.ai's visibility for a specific AI search query."""
        prompt = f"""Search the web for: "{query}"

Analyze the results and determine:
1. Which companies/products appear prominently in search results?
2. What sources are most authoritative for this query?
3. Would an AI engine like ChatGPT or Perplexity mention VoiceCare.ai in response to this query?
4. If not, what would it take for VoiceCare.ai to be included?
5. What content exists that currently answers this query best?
6. What content gap could VoiceCare.ai fill?

Provide a specific action plan to get VoiceCare.ai mentioned for this query."""

        schema = {
            "query": query,
            "current_top_results": [
                {"source": "string", "company_mentioned": "string", "ranking_signal": "string"}
            ],
            "voicecare_visibility": "string",
            "action_plan": [
                {"action": "string", "priority": "number", "expected_impact": "string"}
            ],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_schema_markup_recommendations(self) -> dict:
        """Generate structured data / schema markup recommendations."""
        prompt = """Search for the latest best practices in structured data and schema markup for SaaS/AI companies.

Create specific schema markup recommendations for VoiceCare.ai to improve AI engine visibility:

1. **Organization Schema**: Complete company information
2. **Product Schema**: For voice analytics products
3. **FAQ Schema**: For common questions
4. **Review Schema**: For customer testimonials
5. **Article Schema**: For blog posts and guides
6. **Software Application Schema**: For the platform

For each, provide:
- The specific schema type
- Required properties to include
- Sample JSON-LD code
- Where to implement it
- Expected impact on AI engine visibility"""

        schema = {
            "recommendations": [
                {
                    "schema_type": "string",
                    "purpose": "string",
                    "implementation_location": "string",
                    "sample_jsonld": "string",
                    "impact": "string",
                }
            ],
            "implementation_priority": ["string"],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def keyword_opportunity_report(self, seed_keywords: list[str] | None = None) -> dict:
        """Use SEMrush to find keyword opportunities, then GPT-5 to prioritise them.

        Args:
            seed_keywords: Override list; defaults to config target_queries.
        """
        if not self.semrush:
            return {"error": "SEMrush not configured. Add SEMRUSH_API_KEY to .env"}

        seeds = seed_keywords or self.target_queries[:5]
        all_suggestions: list[dict] = []

        for kw in seeds:
            try:
                suggestions = self.semrush.keyword_suggestions(kw, limit=15)
                all_suggestions.extend(suggestions)
            except Exception as e:
                logger.warning(f"Keyword suggestions failed for '{kw}': {e}")

        if not all_suggestions:
            return {"error": "No keyword data returned from SEMrush"}

        kw_table = "\n".join(
            f"- \"{row.get('Ph', '')}\" | vol={row.get('Nq', '?')} | diff={row.get('Co', '?')} | CPC=${row.get('Cp', '?')}"
            for row in all_suggestions[:40]
        )

        prompt = f"""Analyse these SEMrush keyword suggestions for VoiceCare.ai and build a prioritised keyword strategy.

{kw_table}

For each keyword, recommend:
1. Whether VoiceCare.ai should target it (YES/NO/MAYBE)
2. The best content format (blog post, landing page, comparison, FAQ, case study)
3. A LinkedIn content angle to support SEO (LinkedIn post → traffic → ranking signal)
4. Expected ROI: how this keyword could drive leads or brand awareness

Group the keywords into themes and recommend a phased rollout:
- Month 1: quick wins (high vol, low diff)
- Month 2: authority builders
- Month 3: competitive battles"""

        schema = {
            "keyword_themes": [
                {
                    "theme": "string",
                    "keywords": [
                        {
                            "keyword": "string",
                            "volume": "string",
                            "difficulty": "string",
                            "target": "YES/NO/MAYBE",
                            "content_format": "string",
                            "linkedin_angle": "string",
                            "priority": "number",
                        }
                    ],
                }
            ],
            "month_1_quick_wins": ["string"],
            "month_2_authority_builders": ["string"],
            "month_3_competitive_battles": ["string"],
        }

        logger.info("Generating keyword opportunity report...")
        return self.ai.structured_query(prompt, schema, use_web_search=False)

    def monitor_ai_mentions(self) -> dict:
        """Monitor how VoiceCare.ai is being mentioned across the web."""
        prompt = """Search the web for ANY mentions of VoiceCare.ai, voicecare.ai, or "Voice Care AI".

Find:
1. All web pages, articles, or posts that mention VoiceCare.ai
2. Review site listings (G2, Capterra, Gartner, etc.)
3. Social media mentions
4. News articles
5. Comparison pages or listicles
6. Forum discussions

Also search for common misspellings or variations.

For each mention found:
- URL and source
- Context (positive, neutral, negative)
- Whether it helps or hurts AI engine visibility
- Action to take (claim listing, respond, amplify, correct, etc.)"""

        schema = {
            "mentions_found": [
                {
                    "source": "string",
                    "url": "string",
                    "context": "string",
                    "sentiment": "positive/neutral/negative",
                    "action_needed": "string",
                }
            ],
            "missing_from": ["string - platforms/sites where VoiceCare.ai should be listed"],
            "priority_actions": ["string"],
        }

        logger.info("Monitoring AI mentions...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)
