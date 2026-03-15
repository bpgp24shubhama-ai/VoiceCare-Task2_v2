"""
Core AI Engine - GPT-5 with Web Search integration.

This is the central brain of the Growth Engine Agent. It uses OpenAI GPT-5
with web search enabled to provide real-time, reasoning-backed responses
for all growth hacking operations.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIEngine:
    """Core AI engine powered by GPT-5 with web search and reasoning."""

    def __init__(self, config: dict):
        self.config = config
        ai_cfg = config.get("ai", {})
        self.model = ai_cfg.get("model", "gpt-5")
        self.temperature = ai_cfg.get("temperature", 0.7)
        self.max_tokens = ai_cfg.get("max_tokens", 16000)
        self.reasoning_effort = ai_cfg.get("reasoning_effort", "high")
        self.web_search_cfg = ai_cfg.get("web_search", {})

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        company = self.config.get("company", {})
        return f"""You are an elite AI Growth Engine Agent for {company.get('name', 'VoiceCare.ai')}.

Company: {company.get('name')}
Website: {company.get('website')}
Description: {company.get('description')}
LinkedIn: {company.get('linkedin_url')}
Current LinkedIn Followers: {company.get('current_followers', 2900)}
Target LinkedIn Followers: {company.get('target_followers', 10000)}
Timeline: {company.get('target_months', 3)} months

Your mission is to devise and execute growth strategies to:
1. Grow LinkedIn followers from {company.get('current_followers', 2900)} to {company.get('target_followers', 10000)} in {company.get('target_months', 3)} months WITHOUT buying leads
2. Increase VoiceCare.ai visibility and ranking on AI engines (ChatGPT, Perplexity, Gemini, etc.)
3. Outrank competitors in the voice AI / contact center AI space

You have access to real-time web search. Use it to:
- Research competitors' latest moves, content strategies, and engagement patterns
- Find trending topics in voice AI, contact centers, and customer experience
- Discover viral content patterns on LinkedIn
- Audit how VoiceCare.ai appears on AI search engines vs competitors

Always provide actionable, specific, data-backed recommendations. No generic advice.
Today's date: {datetime.now().strftime('%Y-%m-%d')}"""

    def query(
        self,
        prompt: str,
        use_web_search: bool = True,
        search_context_size: Optional[str] = None,
    ) -> dict:
        """Send a query to GPT-5 with optional web search.

        Args:
            prompt: The user/agent prompt.
            use_web_search: Whether to enable web search tool.
            search_context_size: Override context size (low/medium/high).

        Returns:
            dict with 'response', 'citations', and 'usage' keys.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        kwargs = {
            "model": self.model,
            "input": messages,
            "max_output_tokens": self.max_tokens,
        }

        # Enable web search via the responses API
        if use_web_search and self.web_search_cfg.get("enabled", True):
            ctx_size = search_context_size or self.web_search_cfg.get(
                "context_size", "medium"
            )
            kwargs["tools"] = [
                {"type": "web_search_preview", "search_context_size": ctx_size}
            ]

        try:
            response = self.client.responses.create(**kwargs)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            raise

    def _parse_response(self, response) -> dict:
        """Parse the GPT-5 response, extracting text and citations."""
        text_parts = []
        citations = []

        for item in response.output:
            if item.type == "message":
                for block in item.content:
                    if block.type == "output_text":
                        text_parts.append(block.text)
                        # Extract inline citations if present
                        if hasattr(block, "annotations") and block.annotations:
                            for ann in block.annotations:
                                if hasattr(ann, "url"):
                                    citations.append(
                                        {
                                            "title": getattr(ann, "title", ""),
                                            "url": ann.url,
                                        }
                                    )

        return {
            "response": "\n".join(text_parts),
            "citations": citations,
            "model": self.model,
            "timestamp": datetime.now().isoformat(),
        }

    def structured_query(
        self, prompt: str, output_schema: dict, use_web_search: bool = True
    ) -> dict:
        """Query GPT-5 and get structured JSON output.

        Args:
            prompt: The prompt with instructions to return JSON.
            output_schema: Expected schema description for the prompt.
            use_web_search: Whether to enable web search.

        Returns:
            Parsed JSON dict from the model response.
        """
        schema_desc = json.dumps(output_schema, indent=2)
        enhanced_prompt = f"""{prompt}

IMPORTANT: Return your response as valid JSON matching this schema:
{schema_desc}

Return ONLY the JSON object, no markdown fences or extra text."""

        result = self.query(enhanced_prompt, use_web_search=use_web_search)
        raw = result["response"].strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse structured response, returning raw text")
            parsed = {"raw_response": raw}

        parsed["_citations"] = result.get("citations", [])
        parsed["_timestamp"] = result.get("timestamp")
        return parsed
