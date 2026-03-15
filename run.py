#!/usr/bin/env python3
"""
VoiceCare.ai AI Growth Engine Agent - CLI Runner.

Usage:
    python run.py strategy              Run initial strategy generation
    python run.py weekly N FOLLOWERS    Run weekly cycle (week N, current followers)
    python run.py content TYPE TOPIC    Generate specific content
    python run.py geo                   Run GEO optimization suite
    python run.py growth-hacks          Run growth hack generators
    python run.py calendar N            Generate content calendar for week N
    python run.py competitor NAME       Deep-dive competitor analysis
    python run.py audit QUERY           Audit AI visibility for a search query
    python run.py ask "QUESTION"        Ask any growth question with web search
    python run.py interactive           Interactive chat mode

  SEMrush commands (requires SEMRUSH_API_KEY in .env):
    python run.py semrush domain DOMAIN             Full domain report
    python run.py semrush keyword KEYWORD           Keyword overview + SERP
    python run.py semrush gap COMPETITOR            Keyword gap vs competitor
    python run.py semrush keywords                  Keyword opportunity report
    python run.py semrush landscape                 Full competitive landscape
"""

import json
import logging
import sys
import os

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import GrowthEngineOrchestrator

console = Console()

logging.basicConfig(
    level=os.getenv("AGENT_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def print_result(data: dict, title: str = "Result"):
    """Pretty-print a result dict."""
    console.print(Panel(f"[bold green]{title}[/bold green]"))

    # Remove internal metadata for display
    display = {k: v for k, v in data.items() if not k.startswith("_")}
    formatted = json.dumps(display, indent=2, default=str)

    if len(formatted) > 5000:
        # For large outputs, show a summary and save to file
        console.print(f"[dim]Full output ({len(formatted)} chars) - showing key sections:[/dim]\n")
        for key, value in display.items():
            if isinstance(value, str) and len(value) > 200:
                console.print(f"[bold]{key}:[/bold] {value[:200]}...")
            elif isinstance(value, list) and len(value) > 3:
                console.print(f"[bold]{key}:[/bold] ({len(value)} items)")
                for item in value[:3]:
                    if isinstance(item, dict):
                        console.print(f"  - {json.dumps(item, default=str)[:150]}...")
                    else:
                        console.print(f"  - {str(item)[:150]}")
                console.print(f"  ... and {len(value) - 3} more")
            else:
                console.print(f"[bold]{key}:[/bold] {json.dumps(value, default=str)[:300]}")
            console.print()
    else:
        console.print(formatted)

    if "_citations" in data and data["_citations"]:
        console.print("\n[bold blue]Sources:[/bold blue]")
        for cite in data["_citations"]:
            console.print(f"  - {cite.get('title', 'Source')}: {cite.get('url', '')}")


@click.group()
def cli():
    """VoiceCare.ai AI Growth Engine Agent"""
    pass


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def strategy(config):
    """Run the full initial strategy generation."""
    console.print(Panel(
        "[bold magenta]VoiceCare.ai AI Growth Engine[/bold magenta]\n"
        "Running Initial Strategy Generation...\n\n"
        "This will generate:\n"
        "1. Competitive Analysis\n"
        "2. GEO (AI Visibility) Audit\n"
        "3. 12-Week Growth Playbook\n"
        "4. LinkedIn Algorithm Guide\n"
        "5. Week 1 Content Calendar",
        title="Growth Engine",
    ))

    engine = GrowthEngineOrchestrator(config)
    results = engine.run_initial_strategy()

    for name, data in results.items():
        print_result(data, name.replace("_", " ").title())

    console.print("\n[bold green]All outputs saved to data/output/[/bold green]")


@cli.command()
@click.argument("week", type=int)
@click.argument("followers", type=int)
@click.option("--posts", default=0, help="Posts published this week")
@click.option("--impressions", default=0, help="Total impressions")
@click.option("--engagement", default=0, help="Top post engagement")
@click.option("--views", default=0, help="Profile views")
@click.option("--clicks", default=0, help="Website clicks")
@click.option("--config", default="config.yaml", help="Path to config file")
def weekly(week, followers, posts, impressions, engagement, views, clicks, config):
    """Run weekly growth cycle. Usage: weekly WEEK_NUMBER CURRENT_FOLLOWERS"""
    console.print(Panel(
        f"[bold magenta]Week {week} Growth Cycle[/bold magenta]\n"
        f"Current Followers: {followers}",
        title="Weekly Cycle",
    ))

    engine = GrowthEngineOrchestrator(config)
    results = engine.run_weekly_cycle(
        week_number=week,
        current_followers=followers,
        posts_published=posts,
        total_impressions=impressions,
        top_post_engagement=engagement,
        profile_views=views,
        website_clicks=clicks,
    )

    for name, data in results.items():
        print_result(data, name.replace("_", " ").title())


@cli.command()
@click.argument("content_type", type=click.Choice(["post", "carousel", "poll", "thought_leadership", "data_post"]))
@click.argument("topic")
@click.option("--format", "fmt", default="text", help="Post format (text/carousel/poll)")
@click.option("--exec-name", default="CEO", help="Executive name for thought leadership")
@click.option("--exec-role", default="CEO", help="Executive role")
@click.option("--slides", default=10, help="Number of carousel slides")
@click.option("--config", default="config.yaml", help="Path to config file")
def content(content_type, topic, fmt, exec_name, exec_role, slides, config):
    """Generate specific content. Usage: content TYPE TOPIC"""
    engine = GrowthEngineOrchestrator(config)
    result = engine.generate_content(
        content_type,
        topic,
        format=fmt,
        executive_name=exec_name,
        executive_role=exec_role,
        slides=slides,
    )
    print_result(result, f"{content_type.title()} Content")


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def geo(config):
    """Run full GEO (AI visibility) optimization suite."""
    console.print(Panel(
        "[bold magenta]GEO Optimization Suite[/bold magenta]\n"
        "Auditing AI engine visibility...",
        title="GEO",
    ))

    engine = GrowthEngineOrchestrator(config)
    results = engine.run_geo_optimization()

    for name, data in results.items():
        print_result(data, name.replace("_", " ").title())


@cli.command("growth-hacks")
@click.option("--config", default="config.yaml", help="Path to config file")
def growth_hacks(config):
    """Run all growth hack strategy generators."""
    engine = GrowthEngineOrchestrator(config)
    results = engine.run_growth_hacks()

    for name, data in results.items():
        print_result(data, name.replace("_", " ").title())


@cli.command()
@click.argument("week", type=int)
@click.option("--context", default="", help="Additional context for content generation")
@click.option("--config", default="config.yaml", help="Path to config file")
def calendar(week, context, config):
    """Generate content calendar for a specific week."""
    engine = GrowthEngineOrchestrator(config)
    result = engine.linkedin.generate_weekly_content_calendar(week, context)
    engine.analytics.save_output(result, f"week{week}_calendar")
    print_result(result, f"Week {week} Content Calendar")


@cli.command()
@click.argument("name")
@click.option("--config", default="config.yaml", help="Path to config file")
def competitor(name, config):
    """Deep-dive analysis of a specific competitor."""
    engine = GrowthEngineOrchestrator(config)
    result = engine.competitor.analyze_competitor_content(name)
    engine.analytics.save_output(result, f"competitor_{name}")
    print_result(result, f"Competitor Analysis: {name}")


@cli.command()
@click.argument("query")
@click.option("--config", default="config.yaml", help="Path to config file")
def audit(query, config):
    """Audit AI visibility for a specific search query."""
    engine = GrowthEngineOrchestrator(config)
    result = engine.visibility.audit_specific_query(query)
    engine.analytics.save_output(result, "query_audit")
    print_result(result, f"Query Audit: {query}")


@cli.command()
@click.argument("question")
@click.option("--config", default="config.yaml", help="Path to config file")
def ask(question, config):
    """Ask any growth-related question with web search."""
    engine = GrowthEngineOrchestrator(config)
    response = engine.interactive_query(question)
    console.print(Markdown(response))


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def interactive(config):
    """Start interactive chat mode with the Growth Engine."""
    console.print(Panel(
        "[bold magenta]VoiceCare.ai Growth Engine - Interactive Mode[/bold magenta]\n"
        "Ask any question about growth strategy, content, competitors, etc.\n"
        "The agent has web search enabled for real-time insights.\n"
        "Type 'quit' to exit.",
        title="Interactive Mode",
    ))

    engine = GrowthEngineOrchestrator(config)

    while True:
        try:
            question = console.input("\n[bold cyan]You>[/bold cyan] ")
            if question.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break

            console.print("[dim]Searching and thinking...[/dim]")
            response = engine.interactive_query(question)
            console.print(f"\n[bold green]Agent>[/bold green]")
            console.print(Markdown(response))
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


# ------------------------------------------------------------------ #
# SEMrush command group                                                #
# ------------------------------------------------------------------ #

@cli.group()
def semrush():
    """SEMrush data commands (requires SEMRUSH_API_KEY in .env)."""
    pass


@semrush.command("domain")
@click.argument("domain")
@click.option("--db", default="us", help="SEMrush database (us, uk, ca, au, ...)")
@click.option("--config", default="config.yaml", help="Path to config file")
def semrush_domain(domain, db, config):
    """Full domain report: traffic, authority, top keywords, backlinks."""
    engine = GrowthEngineOrchestrator(config)
    if not engine.semrush:
        console.print("[bold red]SEMRUSH_API_KEY not set.[/bold red] Add it to your .env file.")
        return
    report = engine.semrush.full_domain_report(domain, database=db)
    engine.analytics.save_output(report, f"semrush_domain_{domain.replace('.', '_')}")
    print_result(report, f"SEMrush Domain Report: {domain}")


@semrush.command("keyword")
@click.argument("keyword")
@click.option("--db", default="us", help="SEMrush database")
@click.option("--config", default="config.yaml", help="Path to config file")
def semrush_keyword(keyword, db, config):
    """Keyword overview (volume, difficulty, CPC) + current SERP top-10."""
    engine = GrowthEngineOrchestrator(config)
    if not engine.semrush:
        console.print("[bold red]SEMRUSH_API_KEY not set.[/bold red]")
        return

    overview = engine.semrush.keyword_overview(keyword, database=db)
    serp = engine.semrush.serp_competitors(keyword, limit=10, database=db)
    suggestions = engine.semrush.keyword_suggestions(keyword, limit=10, database=db)

    result = {
        "keyword": keyword,
        "overview": overview,
        "serp_top_10": serp,
        "related_keywords": suggestions,
    }
    engine.analytics.save_output(result, f"semrush_keyword_{keyword[:30].replace(' ', '_')}")
    print_result(result, f"SEMrush Keyword: {keyword}")


@semrush.command("gap")
@click.argument("competitor_name")
@click.option("--config", default="config.yaml", help="Path to config file")
def semrush_gap(competitor_name, config):
    """Keyword gap analysis vs a competitor — keywords they rank for, we don't."""
    engine = GrowthEngineOrchestrator(config)
    if not engine.semrush:
        console.print("[bold red]SEMRUSH_API_KEY not set.[/bold red]")
        return
    result = engine.competitor.semrush_keyword_gap_analysis(competitor_name)
    engine.analytics.save_output(result, f"keyword_gap_{competitor_name}")
    print_result(result, f"Keyword Gap vs {competitor_name}")


@semrush.command("keywords")
@click.option("--seeds", default="", help="Comma-separated seed keywords (overrides config)")
@click.option("--config", default="config.yaml", help="Path to config file")
def semrush_keywords(seeds, config):
    """Keyword opportunity report — find and prioritise keywords to target."""
    engine = GrowthEngineOrchestrator(config)
    if not engine.semrush:
        console.print("[bold red]SEMRUSH_API_KEY not set.[/bold red]")
        return
    seed_list = [s.strip() for s in seeds.split(",")] if seeds else None
    result = engine.visibility.keyword_opportunity_report(seed_list)
    engine.analytics.save_output(result, "keyword_opportunities")
    print_result(result, "Keyword Opportunity Report")


@semrush.command("landscape")
@click.option("--db", default="us", help="SEMrush database")
@click.option("--config", default="config.yaml", help="Path to config file")
def semrush_landscape(db, config):
    """Full competitive landscape — SEMrush metrics for VoiceCare.ai + all competitors."""
    engine = GrowthEngineOrchestrator(config)
    if not engine.semrush:
        console.print("[bold red]SEMRUSH_API_KEY not set.[/bold red]")
        return

    our_domain = (
        engine.config.get("company", {})
        .get("website", "voicecare.ai")
        .replace("https://", "").replace("http://", "").rstrip("/")
    )
    competitor_domains = [
        c["website"].replace("https://", "").replace("http://", "").rstrip("/")
        for c in engine.config.get("competitors", [])
    ]

    console.print("[dim]Fetching SEMrush data for all domains (this may take ~30s)...[/dim]")
    landscape = engine.semrush.competitive_landscape(our_domain, competitor_domains, database=db)
    engine.analytics.save_output(landscape, "semrush_landscape")

    # Pretty-print as a table
    table = Table(title="SEMrush Competitive Landscape", show_lines=True)
    table.add_column("Domain", style="bold cyan")
    table.add_column("Org. Traffic", justify="right")
    table.add_column("Org. Keywords", justify="right")
    table.add_column("Authority", justify="right")
    table.add_column("Backlinks", justify="right")
    table.add_column("Ref. Domains", justify="right")

    for domain, report in landscape.items():
        ov = report.get("overview", {})
        bl = report.get("backlinks", {})
        label = f"[green]{domain}[/green]" if domain == our_domain else domain
        table.add_row(
            label,
            ov.get("Ot", "N/A"),
            ov.get("Or", "N/A"),
            ov.get("Rk", "N/A"),
            bl.get("total", "N/A"),
            bl.get("domains_num", "N/A"),
        )

    console.print(table)
    console.print(f"\n[dim]Full data saved to data/output/[/dim]")


if __name__ == "__main__":
    cli()
