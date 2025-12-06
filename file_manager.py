"""File manager for saving generated HTML files."""

import logging
import os
import uuid
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)


class FileManager:
    """Manage generated HTML file storage."""

    def __init__(self):
        self.base_dir = config.generated_html_dir
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the generated directory exists."""
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Using directory: {os.path.abspath(self.base_dir)}")

    def save_html(self, html_content: str, prompt: str = "") -> str:
        """
        Save HTML content to a file and return the filename.

        Args:
            html_content: The HTML string to save
            prompt: Original prompt (for generating meaningful filename)

        Returns:
            Filename (without path) of the saved file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]

        # Create a safe filename from prompt (first few words)
        safe_prompt = self._sanitize_filename(prompt)[:30] if prompt else "creation"

        filename = f"{timestamp}_{safe_prompt}_{unique_id}.html"
        filepath = os.path.join(self.base_dir, filename)

        # Save the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Saved HTML to: {filepath}")
        return filename

    def _sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename."""
        # Keep only alphanumeric characters and spaces
        safe = "".join(c if c.isalnum() else "_" for c in text.lower())
        # Remove consecutive underscores
        while "__" in safe:
            safe = safe.replace("__", "_")
        return safe.strip("_")

    def get_file_path(self, filename: str) -> str:
        """Get full path for a filename."""
        return os.path.join(self.base_dir, filename)

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(self.get_file_path(filename))
