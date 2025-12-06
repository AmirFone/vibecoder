"""HTTP server for serving generated HTML files."""

import logging
import threading

from flask import Flask, abort, send_from_directory
from flask_cors import CORS

from config import config

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create Flask app for serving generated HTML files."""
    app = Flask(__name__)
    CORS(app)

    # Suppress Flask's default logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)

    @app.route("/")
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vibecoder</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    padding: 20px;
                    box-sizing: border-box;
                }
                .container {
                    max-width: 500px;
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 0.5em;
                }
                p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                code {
                    background: rgba(255,255,255,0.2);
                    padding: 0.2em 0.5em;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Vibecoder</h1>
                <p>Send an iMessage with <code>vibecode: [your idea]</code> to create something!</p>
                <p>Example: <code>vibecode: a pac man game</code></p>
            </div>
        </body>
        </html>
        """

    @app.route("/v/<filename>")
    def serve_creation(filename):
        """Serve a generated HTML file."""
        try:
            return send_from_directory(
                config.generated_html_dir, filename, mimetype="text/html"
            )
        except FileNotFoundError:
            abort(404)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


class HTTPServer:
    """HTTP server wrapper for running Flask in background."""

    def __init__(self):
        self.app = create_app()
        self.thread = None

    def start(self):
        """Start the HTTP server in a background thread."""

        def run():
            self.app.run(
                host=config.http_host,
                port=config.http_port,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        logger.info(
            f"HTTP server started on http://{config.http_host}:{config.http_port}"
        )

    def get_url(self, filename: str) -> str:
        """Get the public URL for a generated file."""
        return f"{config.public_url_base}/v/{filename}"
