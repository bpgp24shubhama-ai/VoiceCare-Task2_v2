"""
LinkedIn Growth Strategy Module.

Generates content calendars, individual posts, engagement strategies,
and growth hacks specifically designed to grow LinkedIn followers
from 2,900 to 10,000 in 3 months.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class LinkedInGrowthEngine:
    """LinkedIn growth strategy generator and executor."""

    def __init__(self, ai_engine, config: dict):
        self.ai = ai_engine
        self.config = config
        self.linkedin_cfg = config.get("linkedin", {})
        self.company = config.get("company", {})

    def generate_weekly_content_calendar(self, week_number: int = 1, context: str = "") -> dict:
        """Generate a full week's content calendar with posts ready to publish."""
        content_mix = self.linkedin_cfg.get("content_mix", {})
        hashtags = self.linkedin_cfg.get("hashtag_strategy", {})
        primary_tags = " ".join(hashtags.get("primary", []))
        secondary_tags = " ".join(hashtags.get("secondary", []))

        prompt = f"""Create a detailed 7-day LinkedIn content calendar for VoiceCare.ai (Week {week_number} of 12-week growth plan).

Current followers: {self.company.get('current_followers', 2900)}
Target: {self.company.get('target_followers', 10000)} in 3 months
Week {week_number} milestone: ~{2900 + int((10000 - 2900) * week_number / 12)} followers

Content mix targets:
- Thought Leadership: {content_mix.get('thought_leadership', 0.3)*100}%
- Product Insights: {content_mix.get('product_insights', 0.15)*100}%
- Industry Trends: {content_mix.get('industry_trends', 0.2)*100}%
- Customer Stories: {content_mix.get('customer_stories', 0.1)*100}%
- Engagement Hooks: {content_mix.get('engagement_hooks', 0.15)*100}%
- Data-Driven Posts: {content_mix.get('data_driven_posts', 0.1)*100}%

Primary hashtags: {primary_tags}
Secondary hashtags (rotate): {secondary_tags}

{"Additional context: " + context if context else "Search the web for current trending topics in voice AI, contact centers, and CX to make content timely."}

For EACH day, create a COMPLETE, READY-TO-POST LinkedIn post that includes:
1. A hook (first line that stops the scroll - this is CRITICAL)
2. The body with value-driven content
3. A call-to-action
4. Relevant hashtags (mix of primary + secondary)
5. Suggested visual/media (describe what image, carousel, or video to pair)
6. Best posting time
7. Engagement strategy (how to boost this post's reach)

Make posts authentic, insightful, and NOT salesy. Use patterns from viral LinkedIn posts:
- Start with a bold statement, question, or contrarian take
- Use short paragraphs and line breaks
- Include data points and specific numbers
- End with a question to drive comments
- Avoid corporate jargon"""

        schema = {
            "week_number": week_number,
            "theme": "string - weekly overarching theme",
            "follower_milestone": "number",
            "posts": [
                {
                    "day": "string (Monday-Sunday)",
                    "post_type": "string",
                    "post_time": "string",
                    "hook": "string - the critical first line",
                    "full_post_text": "string - complete ready-to-post content",
                    "hashtags": ["string"],
                    "media_suggestion": "string",
                    "engagement_strategy": "string",
                    "expected_reach_multiplier": "string",
                }
            ],
            "weekly_engagement_tasks": ["string"],
        }

        logger.info(f"Generating Week {week_number} content calendar...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_viral_post(self, topic: str, format_type: str = "text") -> dict:
        """Generate a single viral-optimized LinkedIn post."""
        prompt = f"""Create a viral LinkedIn post for VoiceCare.ai about: {topic}

Format: {format_type}

Search the web for the latest data, statistics, and news about this topic to make the post timely and authoritative.

The post MUST follow these viral LinkedIn patterns:
1. **Hook**: First line must stop the scroll. Use one of these patterns:
   - Bold contrarian statement ("Everyone's wrong about X")
   - Shocking statistic ("X% of contact centers are making this mistake")
   - Personal story opener ("I just talked to a CX leader who...")
   - Question that provokes ("What if your contact center could...")

2. **Structure**: Short paragraphs (1-2 lines max), use line breaks liberally

3. **Value**: Give away genuinely useful insight - the kind people save and share

4. **Social proof**: Include real data, research findings, or industry benchmarks

5. **CTA**: End with a question or invitation that drives comments, NOT a link

6. **Hashtags**: 3-5 relevant hashtags at the end

{"For carousel format: Provide 8-10 slide titles and content for each slide." if format_type == "carousel" else ""}
{"For poll format: Provide the poll question and 4 options." if format_type == "poll" else ""}

Make it sound human and authentic, NOT like AI-generated corporate content."""

        schema = {
            "topic": topic,
            "format": format_type,
            "hook": "string",
            "full_post": "string - complete ready-to-publish text",
            "hashtags": ["string"],
            "media_direction": "string",
            "best_post_time": "string",
            "engagement_prediction": "string",
            "boost_tactics": ["string"],
        }

        if format_type == "carousel":
            schema["slides"] = [{"slide_number": "number", "title": "string", "content": "string"}]
        elif format_type == "poll":
            schema["poll_question"] = "string"
            schema["poll_options"] = ["string"]

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_comment_strategy(self) -> dict:
        """Generate a strategic commenting plan to boost visibility."""
        competitor_list = ", ".join(
            c["name"] for c in self.config.get("competitors", [])
        )

        prompt = f"""Create a strategic LinkedIn commenting plan for VoiceCare.ai to 10x visibility.

Search LinkedIn and the web for influential voices, trending posts, and key conversations in:
- Voice AI / Speech Analytics
- Contact Center Technology
- Customer Experience
- Conversational AI
- Enterprise AI

Create a commenting strategy that covers:

1. **Target Accounts to Comment On** (20+ specific people/companies):
   - Industry influencers and thought leaders
   - Competitor executives ({competitor_list})
   - Industry analysts (Gartner, Forrester, etc.)
   - LinkedIn Top Voices in CX/AI
   - Relevant media/journalists

2. **Comment Templates** (10 templates):
   - For agreeing and adding value
   - For respectfully challenging a point
   - For sharing a relevant VoiceCare.ai insight
   - For asking smart follow-up questions
   - For sharing relevant data points

3. **Engagement Rules**:
   - Comment within first 30 min of target's post
   - Always add value, never just "Great post!"
   - Comments should be 3-5 lines minimum
   - Include a subtle positioning statement when relevant
   - Aim for 15-20 strategic comments per day

4. **Employee Advocacy Plan**:
   - How to get team members to amplify content
   - Template messages for team coordination"""

        schema = {
            "target_accounts": [
                {
                    "name": "string",
                    "role": "string",
                    "linkedin_profile": "string",
                    "relevance": "string",
                    "comment_approach": "string",
                }
            ],
            "comment_templates": [
                {
                    "scenario": "string",
                    "template": "string",
                    "when_to_use": "string",
                }
            ],
            "daily_engagement_routine": ["string"],
            "employee_advocacy_plan": {
                "strategy": "string",
                "template_messages": ["string"],
                "kpis": ["string"],
            },
        }

        logger.info("Generating comment strategy...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_linkedin_newsletter_plan(self) -> dict:
        """Plan a LinkedIn newsletter to drive subscriber growth."""
        prompt = """Design a LinkedIn Newsletter strategy for VoiceCare.ai to drive follower growth.

Search for successful LinkedIn newsletters in B2B SaaS, AI, and CX spaces. Analyze what works.

Create:
1. **Newsletter Concept**: Name, tagline, value proposition, target audience
2. **First 12 Issues** (one per week for 3 months):
   - Title (must be click-worthy)
   - Key angle/thesis
   - 3-4 sections per issue
   - Data/research to include
3. **Growth Tactics**:
   - How to promote each issue
   - Cross-promotion strategies
   - Guest contributor strategy
4. **Subscriber-to-Follower Conversion**:
   - How newsletter drives page follows
   - CTAs to include in each issue"""

        schema = {
            "newsletter_name": "string",
            "tagline": "string",
            "value_proposition": "string",
            "target_audience": "string",
            "issues": [
                {
                    "week": "number",
                    "title": "string",
                    "thesis": "string",
                    "sections": ["string"],
                    "data_sources": ["string"],
                }
            ],
            "growth_tactics": ["string"],
            "conversion_strategy": ["string"],
        }

        logger.info("Generating newsletter plan...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def generate_event_strategy(self) -> dict:
        """Plan LinkedIn Events and Live sessions for growth."""
        prompt = """Design a LinkedIn Events & Live strategy for VoiceCare.ai.

Search for upcoming conferences, webinars, and events in voice AI, contact center, and CX spaces.

Create:
1. **LinkedIn Live Series**: Monthly live sessions
   - Topics, formats, guest speakers to invite
   - Promotion timeline (2 weeks before, 1 week, day-of)
   - Post-event content repurposing plan

2. **LinkedIn Audio Events**: Weekly casual discussions
   - Topic ideas for 12 weeks
   - How to attract attendees

3. **Industry Event Leverage**: How to capitalize on industry events
   - Pre-event, during, and post-event content
   - Live commentary strategy

4. **Collaborative Events**: Joint events with partners/complementary companies
   - Who to partner with
   - Event formats"""

        schema = {
            "live_series": [
                {
                    "month": "number",
                    "topic": "string",
                    "format": "string",
                    "guest_speakers": ["string"],
                    "promotion_plan": ["string"],
                    "repurposing_plan": ["string"],
                }
            ],
            "audio_events": [{"week": "number", "topic": "string", "format": "string"}],
            "industry_events_to_leverage": [
                {"event": "string", "date": "string", "strategy": "string"}
            ],
            "collaboration_ideas": [
                {"partner": "string", "event_type": "string", "mutual_benefit": "string"}
            ],
        }

        logger.info("Generating event strategy...")
        return self.ai.structured_query(prompt, schema, use_web_search=True)
