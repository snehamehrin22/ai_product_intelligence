"""Video processing: download, OCR, transcription."""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional
import cv2
import pytesseract
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class VideoProcessor:
    """Processes Instagram Reels to extract hooks."""

    def __init__(self, download_dir: str = "downloads"):
        """Initialize video processor."""
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)

        # Initialize OpenAI client for Whisper API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.openai_client = OpenAI(api_key=api_key)

    def download_video(self, video_url: str, shortcode: str) -> Optional[str]:
        """
        Download Instagram video using yt-dlp.

        Args:
            video_url: Instagram video URL
            shortcode: Reel shortcode for filename

        Returns:
            Path to downloaded video file, or None if failed
        """
        output_path = self.download_dir / f"{shortcode}.mp4"

        if output_path.exists():
            print(f"Video {shortcode} already downloaded")
            return str(output_path)

        try:
            # yt-dlp command to download video
            cmd = [
                "yt-dlp",
                "-f", "best",
                "-o", str(output_path),
                video_url
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Downloaded: {shortcode}")
            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"Failed to download {shortcode}: {e}")
            return None

    def extract_ocr_from_hook(self, video_path: str, hook_duration: int = 5) -> str:
        """
        Extract on-screen text from first N seconds (hook).

        Args:
            video_path: Path to video file
            hook_duration: Duration of hook in seconds (default 5)

        Returns:
            Extracted text from hook section
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Sample frames every 0.5 seconds in hook window
        frame_interval = int(fps * 0.5)
        max_frame = int(fps * hook_duration)

        extracted_texts = []
        frame_num = 0

        while frame_num < max_frame:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if not ret:
                break

            # Convert to PIL Image for OCR
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Extract text
            text = pytesseract.image_to_string(image)
            if text.strip():
                extracted_texts.append(text.strip())

            frame_num += frame_interval

        cap.release()

        # Deduplicate and combine
        unique_texts = list(dict.fromkeys(extracted_texts))  # Preserve order
        combined_text = " ".join(unique_texts)

        return combined_text

    def transcribe_audio(self, video_path: str) -> str:
        """
        Transcribe audio from video using OpenAI Whisper API.

        Args:
            video_path: Path to video file

        Returns:
            Transcribed text
        """
        try:
            # Open the audio file
            with open(video_path, "rb") as audio_file:
                # Use OpenAI Whisper API
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def extract_hook_data(self, video_url: str, shortcode: str) -> Dict[str, str]:
        """
        Extract hook and full transcript from video (OCR + Whisper).

        Args:
            video_url: Instagram video URL
            shortcode: Reel shortcode

        Returns:
            Dictionary with hook_ocr, hook_transcript, full_transcript, combined_hook
        """
        # Download video
        video_path = self.download_video(video_url, shortcode)

        if not video_path:
            return {
                "hook_ocr": "",
                "hook_transcript": "",
                "full_transcript": "",
                "combined_hook": ""
            }

        # Extract OCR from first 5 seconds
        print(f"Extracting OCR from {shortcode}...")
        ocr_text = self.extract_ocr_from_hook(video_path, hook_duration=5)

        # Transcribe full audio
        print(f"Transcribing audio from {shortcode}...")
        full_transcript = self.transcribe_audio(video_path)

        # Get first ~30 words of transcript (hook approximation)
        transcript_words = full_transcript.split()[:30]
        hook_transcript = " ".join(transcript_words)

        # Combine OCR and hook transcript
        combined_hook = f"{ocr_text} {hook_transcript}".strip()

        return {
            "hook_ocr": ocr_text,
            "hook_transcript": hook_transcript,
            "full_transcript": full_transcript,
            "combined_hook": combined_hook
        }
