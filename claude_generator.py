"""Claude API integration for HTML generation."""

import logging
import re
from typing import Optional

import anthropic

from config import config
from prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class ClaudeGenerator:
    """Generate HTML/CSS/JS using Claude API."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model = config.claude_model

    def generate_html(self, prompt: str) -> Optional[str]:
        """
        Generate responsive HTML/CSS/JS for the given prompt.

        Args:
            prompt: Description of what to build (e.g., "a pac man game")

        Returns:
            Complete HTML document string, or None on error
        """
        try:
            logger.info(f"Generating HTML for prompt: {prompt}")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(prompt),
                    }
                ],
            )

            # Extract the text response
            response_text = message.content[0].text

            # Extract HTML from response
            html_content = self._extract_html(response_text)

            if html_content:
                logger.info(f"Generated {len(html_content)} bytes of HTML")
                return html_content
            else:
                logger.error("No HTML content found in response")
                return None

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            return None

    def _extract_html(self, response: str) -> Optional[str]:
        """Extract HTML content from Claude's response."""
        response = response.strip()

        # If response is wrapped in markdown code block, extract it
        if "```html" in response:
            match = re.search(r"```html\s*([\s\S]*?)\s*```", response)
            if match:
                return match.group(1).strip()

        # Try generic code block
        if "```" in response:
            match = re.search(r"```\s*([\s\S]*?)\s*```", response)
            if match:
                content = match.group(1).strip()
                if content.startswith("<!DOCTYPE") or content.startswith("<html"):
                    return content

        # If response starts with <!DOCTYPE or <html, use as-is
        if response.startswith("<!DOCTYPE") or response.startswith("<html"):
            return response

        # Try to find HTML content anywhere in response
        if "<html" in response:
            start = response.find("<!DOCTYPE")
            if start == -1:
                start = response.find("<html")
            end = response.rfind("</html>")
            if end > start:
                return response[start : end + 7]

        # Return full response if it looks like HTML
        if "<head" in response and "<body" in response:
            return response

        return None
