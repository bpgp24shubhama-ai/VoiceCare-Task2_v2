"""
Growth Engine Orchestrator.

Central coordinator that ties all modules together and provides
a unified interface for running growth operations.
"""

import json
import logging
import os
from datetime import datetime

import yaml

from agent.core import AIEngine
from agent.modules.competitor_analyzer import CompetitorAnalyzer
from agent.modules.linkedin_growth import LinkedInGrowthEngine
from agent.modules.ai_visibility import AIVisibilityOptimizer
from agent.modules.content_generator import ContentGenerator
from agent.modules.growth_hacks import GrowthHackEngine
from agent.modules.analytics import GrowthAnalytics
from agent.modules.semrush import SEMrushClient
from agent.modules.dashboard import generate_dashboard

logger = logging.getLogger(__name__)


class GrowthEngineOrchestrator:
    """Orchestrate all growth engine modules."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.ai = AIEngine(self.config)

        # SEMrush is optional — modules degrade gracefully when not configured
        semrush = None
        semrush_key = os.getenv("SEMRUSH_API_KEY")
        if semrush_key:
            try:
                semrush = SEMrushClient(api_key=semrush_key)
                logger.info("SEMrush client initialised — real keyword data enabled.")
            except Exception as e:
                logger.warning(f"SEMrush init failed: {e}. Continuing without SEMrush.")
        else:
            logger.info("SEMRUSH_API_KEY not set — SEMrush enrichment disabled.")

        self.semrush = semrush

        # Initialize all modules, passing SEMrush where relevant
        self.competitor = CompetitorAnalyzer(self.ai, self.config, semrush=semrush)
        self.linkedin = LinkedInGrowthEngine(self.ai, self.config)
        self.visibility = AIVisibilityOptimizer(self.ai, self.config, semrush=semrush)
        self.content = ContentGenerator(self.ai, self.config, semrush=semrush)
        self.growth = GrowthHackEngine(self.ai, self.config)
        self.analytics = GrowthAnalytics(self.ai, self.config)

    def run_initial_strategy(self) -> dict:
        """Run the complete initial strategy generation.

        This is the first thing to run - it generates the full growth
        playbook, competitive analysis, and GEO audit.
        """
        logger.info("=" * 60)
        logger.info("VOICECARE.AI GROWTH ENGINE - INITIAL STRATEGY")
        logger.info("=" * 60)

        results = {}

        # 1. Competitive Analysis
        logger.info("\n[1/5] Running Competitive Analysis...")
        results["competitive_analysis"] = self.competitor.full_competitive_analysis()
        self.analytics.save_output(results["competitive_analysis"], "competitive_analysis")

        # 2. AI Engine Visibility Audit
        logger.info("\n[2/5] Running GEO Audit...")
        results["geo_audit"] = self.visibility.full_geo_audit()
        self.analytics.save_output(results["geo_audit"], "geo_audit")

        # 3. Growth Playbook
        logger.info("\n[3/5] Generating 12-Week Growth Playbook...")
        results["growth_playbook"] = self.growth.generate_full_growth_playbook()
        self.analytics.save_output(results["growth_playbook"], "growth_playbook")

        # 4. LinkedIn Algorithm Optimization
        logger.info("\n[4/5] Researching LinkedIn Algorithm...")
        results["algorithm_guide"] = self.growth.linkedin_algorithm_optimization()
        self.analytics.save_output(results["algorithm_guide"], "algorithm_guide")

        # 5. Week 1 Content Calendar
        logger.info("\n[5/5] Generating Week 1 Content Calendar...")
        results["week1_calendar"] = self.linkedin.generate_weekly_content_calendar(week_number=1)
        self.analytics.save_output(results["week1_calendar"], "week1_calendar")

        logger.info("\n" + "=" * 60)
        logger.info("INITIAL STRATEGY COMPLETE - All outputs saved to data/output/")
        logger.info("=" * 60)

        dashboard_path = generate_dashboard()
        logger.info(f"Dashboard → {dashboard_path}")

        return results

    def run_weekly_cycle(self, week_number: int, current_followers: int, **metrics) -> dict:
        """Run the weekly growth cycle.

        Args:
            week_number: Current week (1-12).
            current_followers: Current LinkedIn follower count.
            **metrics: Additional metrics (posts_published, impressions, etc.)
        """
        logger.info(f"\n{'=' * 60}")
        logger.info(f"WEEKLY CYCLE - Week {week_number}")
        logger.info(f"{'=' * 60}")

        results = {}

        # 1. Weekly Report
        logger.info("\n[1/4] Generating Weekly Report...")
        results["report"] = self.analytics.generate_weekly_report(
            week_number=week_number,
            current_followers=current_followers,
            **metrics,
        )

        # 2. Trending Topics
        logger.info("\n[2/4] Scanning Trending Topics...")
        results["trends"] = self.competitor.trending_topics_scan()
        self.analytics.save_output(results["trends"], f"week{week_number}_trends")

        # 3. Next Week Content Calendar
        logger.info("\n[3/4] Generating Content Calendar...")
        context = f"Last week's top performing content themes: {json.dumps(results['report'].get('what_worked', []))}"
        results["content_calendar"] = self.linkedin.generate_weekly_content_calendar(
            week_number=week_number + 1,
            context=context,
        )
        self.analytics.save_output(results["content_calendar"], f"week{week_number + 1}_calendar")

        # 4. Competitor Check
        logger.info("\n[4/4] Checking Competitor Activity...")
        results["competitor_update"] = self.competitor.ai_engine_visibility_comparison()
        self.analytics.save_output(results["competitor_update"], f"week{week_number}_competitors")

        logger.info(f"\nWeek {week_number} cycle complete.")
        generate_dashboard()
        return results

    def generate_content(self, content_type: str, topic: str, **kwargs) -> dict:
        """Generate a specific piece of content on demand.

        Args:
            content_type: One of 'post', 'carousel', 'poll', 'thought_leadership', 'data_post'.
            topic: The topic to write about.
            **kwargs: Additional args (executive_name, executive_role, etc.)
        """
        generators = {
            "post": lambda: self.linkedin.generate_viral_post(topic, kwargs.get("format", "text")),
            "carousel": lambda: self.content.generate_carousel(topic, kwargs.get("slides", 10)),
            "poll": lambda: self.content.generate_poll(topic),
            "thought_leadership": lambda: self.content.generate_thought_leadership_post(
                kwargs.get("executive_name", "CEO"),
                kwargs.get("executive_role", "CEO"),
                topic,
            ),
            "data_post": lambda: self.content.generate_data_driven_post(topic),
        }

        generator = generators.get(content_type)
        if not generator:
            return {"error": f"Unknown content type: {content_type}. Available: {list(generators.keys())}"}

        result = generator()
        self.analytics.save_output(result, f"content_{content_type}")
        return result

    def run_geo_optimization(self) -> dict:
        """Run full GEO optimization suite."""
        logger.info("Running GEO Optimization Suite...")

        results = {}
        results["audit"] = self.visibility.full_geo_audit()
        self.analytics.save_output(results["audit"], "geo_audit")

        results["content_plan"] = self.visibility.generate_geo_content_plan()
        self.analytics.save_output(results["content_plan"], "geo_content_plan")

        results["mentions"] = self.visibility.monitor_ai_mentions()
        self.analytics.save_output(results["mentions"], "ai_mentions")

        results["schema"] = self.visibility.generate_schema_markup_recommendations()
        self.analytics.save_output(results["schema"], "schema_recommendations")

        generate_dashboard()
        return results

    def run_growth_hacks(self) -> dict:
        """Run all growth hack strategy generators."""
        logger.info("Generating Growth Hack Strategies...")

        results = {}
        results["playbook"] = self.growth.generate_full_growth_playbook()
        self.analytics.save_output(results["playbook"], "growth_playbook")

        results["viral_loops"] = self.growth.viral_content_loop_strategy()
        self.analytics.save_output(results["viral_loops"], "viral_loops")

        results["employee_advocacy"] = self.growth.employee_advocacy_program()
        self.analytics.save_output(results["employee_advocacy"], "employee_advocacy")

        results["partnerships"] = self.growth.partnership_growth_strategy()
        self.analytics.save_output(results["partnerships"], "partnerships")

        generate_dashboard()
        return results

    def interactive_query(self, question: str) -> str:
        """Ask the agent any growth-related question with web search."""
        result = self.ai.query(question, use_web_search=True)
        return result["response"]
