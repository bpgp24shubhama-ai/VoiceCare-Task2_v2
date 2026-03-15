"""
SEMrush API Client Module.

Provides real quantitative SEO data — keyword volumes, domain traffic,
backlink profiles, competitor rankings — that gets injected into GPT-5
prompts to ground every analysis in hard numbers rather than inference.

SEMrush API docs: https://developer.semrush.com/api/
"""

import logging
import os
import time
from typing import Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

SEMRUSH_API_BASE = "https://api.semrush.com/"
SEMRUSH_APP_BASE = "https://api.semrush.com/analytics/v1/"


class SEMrushClient:
    """Lightweight SEMrush API client for growth intelligence."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SEMRUSH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SEMrush API key not set. Add SEMRUSH_API_KEY to your .env file."
            )
        self.session = requests.Session()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get(self, params: dict, base: str = SEMRUSH_API_BASE) -> list[dict]:
        """Make a GET request and return parsed rows."""
        params["key"] = self.api_key
        url = base + "?" + urlencode(params)
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            return self._parse_csv(resp.text)
        except requests.HTTPError as e:
            logger.error(f"SEMrush API error {e.response.status_code}: {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"SEMrush request failed: {e}")
            raise

    @staticmethod
    def _parse_csv(text: str) -> list[dict]:
        """Parse SEMrush's semicolon-delimited response into dicts."""
        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        if not lines or lines[0].startswith("ERROR"):
            if lines:
                logger.warning(f"SEMrush returned: {lines[0]}")
            return []
        headers = [h.strip() for h in lines[0].split(";")]
        rows = []
        for line in lines[1:]:
            values = [v.strip() for v in line.split(";")]
            rows.append(dict(zip(headers, values)))
        return rows

    # ------------------------------------------------------------------ #
    # Domain-level endpoints                                               #
    # ------------------------------------------------------------------ #

    def domain_overview(self, domain: str, database: str = "us") -> dict:
        """Get high-level domain metrics: traffic, authority, keyword count.

        Returns a single dict with keys like:
          Organic Keywords, Organic Traffic, Organic Cost, Adwords Keywords,
          Adwords Traffic, Adwords Cost, Authority Score, etc.
        """
        rows = self._get({
            "type": "domain_ranks",
            "domain": domain,
            "database": database,
            "export_columns": (
                "Dn,Rk,Or,Ot,Oc,Ad,At,Ac,Sh,Sv,Fk,Fv"
            ),
        })
        return rows[0] if rows else {}

    def get_organic_keywords(
        self,
        domain: str,
        limit: int = 20,
        database: str = "us",
        sort_by: str = "tr",  # tr = traffic, po = position
    ) -> list[dict]:
        """Get the top organic keywords a domain ranks for.

        Each row includes: Keyword, Position, Search Volume, CPC, URL, Traffic %.
        """
        return self._get({
            "type": "domain_organic",
            "domain": domain,
            "database": database,
            "display_limit": limit,
            "display_sort": f"{sort_by}_desc",
            "export_columns": "Ph,Po,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td",
        })

    def get_top_pages(self, domain: str, limit: int = 10, database: str = "us") -> list[dict]:
        """Get the top traffic-driving pages on a domain."""
        return self._get({
            "type": "domain_organic_organic",
            "domain": domain,
            "database": database,
            "display_limit": limit,
            "export_columns": "Ur,Pc,Tg,Tr",
        })

    def get_backlinks_overview(self, domain: str) -> dict:
        """Get backlink profile summary for a domain."""
        rows = self._get(
            {
                "type": "backlinks_overview",
                "target": domain,
                "target_type": "root_domain",
                "export_columns": (
                    "total,domains_num,urls_num,ips_num,"
                    "ipclassc_num,follows_num,nofollows_num,"
                    "texts_num,images_num,forms_num,frames_num"
                ),
            },
            base="https://api.semrush.com/analytics/v1/",
        )
        return rows[0] if rows else {}

    def get_referring_domains(self, domain: str, limit: int = 20) -> list[dict]:
        """Get top referring domains (for authority signal analysis)."""
        return self._get(
            {
                "type": "backlinks_refdomains",
                "target": domain,
                "target_type": "root_domain",
                "export_columns": "domain,score,backlinks_num,ip,country,first_seen,last_seen",
                "display_limit": limit,
                "display_sort": "backlinks_num_desc",
            },
            base="https://api.semrush.com/analytics/v1/",
        )

    # ------------------------------------------------------------------ #
    # Keyword-level endpoints                                              #
    # ------------------------------------------------------------------ #

    def keyword_overview(self, keyword: str, database: str = "us") -> dict:
        """Get volume, difficulty, and CPC for a single keyword."""
        rows = self._get({
            "type": "phrase_this",
            "phrase": keyword,
            "database": database,
            "export_columns": "Ph,Nq,Cp,Co,Nr,Td",
        })
        return rows[0] if rows else {}

    def keyword_suggestions(
        self, seed_keyword: str, limit: int = 20, database: str = "us"
    ) -> list[dict]:
        """Get keyword suggestions based on a seed keyword."""
        return self._get({
            "type": "phrase_related",
            "phrase": seed_keyword,
            "database": database,
            "display_limit": limit,
            "display_sort": "nq_desc",
            "export_columns": "Ph,Nq,Cp,Co,Nr,Td",
        })

    def keyword_difficulty(self, keyword: str, database: str = "us") -> dict:
        """Get keyword difficulty score (0-100)."""
        rows = self._get({
            "type": "phrase_kdi",
            "phrase": keyword,
            "database": database,
            "export_columns": "Ph,Kd",
        })
        return rows[0] if rows else {}

    def serp_competitors(self, keyword: str, limit: int = 10, database: str = "us") -> list[dict]:
        """Get domains currently ranking for a keyword (SERP competitors)."""
        return self._get({
            "type": "phrase_organic",
            "phrase": keyword,
            "database": database,
            "display_limit": limit,
            "export_columns": "Dn,Ur,Po,Nq,Cp,Tr,Co,Nr,Tc",
        })

    # ------------------------------------------------------------------ #
    # Competitor intelligence                                              #
    # ------------------------------------------------------------------ #

    def keyword_gap(
        self,
        our_domain: str,
        competitor_domain: str,
        limit: int = 20,
        database: str = "us",
    ) -> list[dict]:
        """Find keywords the competitor ranks for but we don't.

        These are gap opportunities to prioritise.
        """
        return self._get({
            "type": "domain_organic",
            "domain": competitor_domain,
            "database": database,
            "display_limit": limit,
            "display_sort": "tr_desc",
            "export_columns": "Ph,Po,Nq,Cp,Ur,Tr,Co",
        })

    def compare_domains(
        self, domains: list[str], database: str = "us"
    ) -> list[dict]:
        """Get overview metrics for multiple domains side-by-side."""
        results = []
        for domain in domains:
            try:
                overview = self.domain_overview(domain, database)
                overview["_domain"] = domain
                results.append(overview)
                time.sleep(0.3)  # respect rate limits
            except Exception as e:
                logger.warning(f"Could not fetch overview for {domain}: {e}")
                results.append({"_domain": domain, "_error": str(e)})
        return results

    # ------------------------------------------------------------------ #
    # Convenience: bulk data pull for the growth agent                    #
    # ------------------------------------------------------------------ #

    def full_domain_report(self, domain: str, database: str = "us") -> dict:
        """Fetch a comprehensive snapshot for one domain.

        Returns:
            {
                "overview":       dict,
                "top_keywords":   list[dict],
                "backlinks":      dict,
            }
        """
        logger.info(f"Fetching full SEMrush report for {domain}...")
        report: dict = {"domain": domain}

        try:
            report["overview"] = self.domain_overview(domain, database)
        except Exception as e:
            report["overview"] = {"_error": str(e)}

        try:
            report["top_keywords"] = self.get_organic_keywords(domain, limit=15, database=database)
        except Exception as e:
            report["top_keywords"] = []

        try:
            report["backlinks"] = self.get_backlinks_overview(domain)
        except Exception as e:
            report["backlinks"] = {"_error": str(e)}

        return report

    def competitive_landscape(
        self, our_domain: str, competitor_domains: list[str], database: str = "us"
    ) -> dict:
        """Pull full reports for our domain + all competitors.

        Returns a dict keyed by domain with full_domain_report values.
        """
        all_domains = [our_domain] + competitor_domains
        landscape = {}
        for domain in all_domains:
            landscape[domain] = self.full_domain_report(domain, database)
            time.sleep(0.4)
        return landscape
