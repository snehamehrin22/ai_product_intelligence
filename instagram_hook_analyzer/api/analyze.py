"""Vercel serverless function for Instagram hook analysis."""

from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from instagram_hook_analyzer import HookAnalyzer


class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler."""

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        username = data.get('username')
        num_reels = data.get('numReels', 10)

        if not username:
            self.send_error(400, "Username is required")
            return

        try:
            # Run analysis
            analyzer = HookAnalyzer()
            results_df = analyzer.analyze_creators(
                usernames=[username],
                max_reels_per_creator=num_reels,
                output_path=f"/tmp/{username}_analysis.csv"
            )

            # Convert to JSON response
            reels = []
            for _, row in results_df.iterrows():
                reels.append({
                    'url': row['reel_url'],
                    'hookScore': int(row['hook_score']) if row['hook_score'] else 0,
                    'hookPattern': row['hook_pattern'],
                    'hookExtracted': row['hook_text_extracted'],
                    'bodyFramework': row['body_framework'],
                    'bodySummary': row['body_summary'],
                    'ctaType': row['cta_type'],
                    'ctaExtracted': row['cta_text_extracted'],
                    'transcript': row['full_transcript'],
                    'keyTakeaway': row['key_takeaway'],
                    'views': int(row['views']) if row['views'] else None,
                    'likes': int(row['likes']) if row['likes'] else None
                })

            # Calculate summary stats
            summary = {
                'totalReels': len(reels),
                'avgHookScore': int(results_df['hook_score'].mean()) if not results_df.empty else 0,
                'topPattern': results_df['hook_pattern'].mode()[0] if not results_df.empty else 'N/A'
            }

            response = {
                'success': True,
                'reels': reels,
                'summary': summary
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
