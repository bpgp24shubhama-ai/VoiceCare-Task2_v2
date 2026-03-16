"""
Analytics & Reporting Module.

Tracks growth metrics, generates reports, and provides
data-driven recommendations for strategy adjustments.
"""

import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _output_base() -> str:
    """Return the base directory for all data outputs.

    Honours the VOICECARE_DATA_DIR environment variable so that the
    Vercel deployment (read-only filesystem) can redirect writes to /tmp/.
    Falls back to the project root derived from this file's location.
    """
    custom = os.environ.get("VOICECARE_DATA_DIR")
    if custom:
        return custom
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


REPORTS_DIR = os.path.join(_output_base(), "data", "reports")


class GrowthAnalytics:
    """Track and report on growth metrics."""

    def __init__(self, ai_engine, config: dict):
        self.ai = ai_engine
        self.config = config
        self.company = config.get("company", {})
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate_weekly_report(
        self,
        week_number: int,
        current_followers: int,
        posts_published: int = 0,
        top_post_engagement: int = 0,
        total_impressions: int = 0,
        profile_views: int = 0,
        website_clicks: int = 0,
    ) -> dict:
        """Generate a comprehensive weekly growth report."""
        start_followers = self.company.get("current_followers", 2900)
        target = self.company.get("target_followers", 10000)
        expected_weekly = (target - start_followers) / 12
        expected_at_week = int(start_followers + expected_weekly * week_number)
        actual_vs_expected = current_followers - expected_at_week

        prompt = f"""Generate a weekly growth report for VoiceCare.ai - Week {week_number} of 12.

METRICS:
- Starting followers: {start_followers}
- Current followers: {current_followers}
- Target followers: {target}
- Expected at Week {week_number}: {expected_at_week}
- Variance: {'+' if actual_vs_expected >= 0 else ''}{actual_vs_expected} followers
- Posts published this week: {posts_published}
- Top post engagement: {top_post_engagement}
- Total impressions: {total_impressions}
- Profile views: {profile_views}
- Website clicks: {website_clicks}

{'ON TRACK' if actual_vs_expected >= 0 else 'BEHIND TARGET - NEED ACCELERATION'}

Search the web for any new LinkedIn growth tactics or algorithm changes that could help.

Provide:
1. **Performance Summary**: How are we doing vs. targets?
2. **What Worked**: Which content/tactics drove the most growth?
3. **What Didn't Work**: What underperformed and why?
4. **Course Corrections**: Specific changes for next week
5. **Next Week Focus**: Top 3 priorities
6. **Competitor Movement**: Any notable competitor activity this week?
7. **Growth Forecast**: Updated projection - will we hit 10K?"""

        schema = {
            "week": week_number,
            "metrics": {
                "current_followers": current_followers,
                "target_at_week": expected_at_week,
                "variance": actual_vs_expected,
                "on_track": actual_vs_expected >= 0,
                "growth_rate": f"{((current_followers - start_followers) / start_followers * 100):.1f}%",
            },
            "performance_summary": "string",
            "what_worked": ["string"],
            "what_didnt_work": ["string"],
            "course_corrections": ["string"],
            "next_week_priorities": ["string"],
            "competitor_activity": ["string"],
            "forecast": {
                "projected_final_followers": "number",
                "will_hit_target": "boolean",
                "confidence": "string",
                "acceleration_needed": "string",
            },
        }

        report = self.ai.structured_query(prompt, schema, use_web_search=True)

        # Save report to file
        reports_dir = os.path.join(_output_base(), "data", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_file = os.path.join(reports_dir, f"week_{week_number}_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Weekly report saved to {report_file}")

        return report

    def generate_strategy_assessment(self, metrics_history: list) -> dict:
        """Assess overall strategy effectiveness and recommend pivots."""
        metrics_json = json.dumps(metrics_history, indent=2)

        prompt = f"""Analyze VoiceCare.ai's growth trajectory and assess strategy effectiveness.

METRICS HISTORY:
{metrics_json}

Target: Grow from {self.company.get('current_followers', 2900)} to {self.company.get('target_followers', 10000)} in 12 weeks.

Search the web for benchmark data on LinkedIn company page growth rates in B2B SaaS.

Provide:
1. **Trajectory Analysis**: Are we on pace? What's the growth curve look like?
2. **Strategy Effectiveness Score**: Rate each strategy category (content, engagement, GEO, partnerships) on a 1-10 scale
3. **Pivot Recommendations**: What should we double down on? What should we stop?
4. **Benchmark Comparison**: How does our growth rate compare to industry benchmarks?
5. **Risk Assessment**: What could prevent us from hitting 10K?
6. **Acceleration Tactics**: If behind, what emergency tactics could catch us up?"""

        schema = {
            "trajectory": {
                "current_pace": "string",
                "projected_end_followers": "number",
                "on_track": "boolean",
            },
            "strategy_scores": [
                {"strategy": "string", "score": "number", "assessment": "string"}
            ],
            "pivot_recommendations": {
                "double_down": ["string"],
                "stop_doing": ["string"],
                "start_doing": ["string"],
            },
            "benchmark_comparison": "string",
            "risks": ["string"],
            "acceleration_tactics": ["string"],
        }

        return self.ai.structured_query(prompt, schema, use_web_search=True)

    def save_output(self, data: dict, filename: str) -> str:
        """Save any output data to the reports directory."""
        output_dir = os.path.join(_output_base(), "data", "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(
            output_dir,
            f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Output saved to {filepath}")
        return filepath
