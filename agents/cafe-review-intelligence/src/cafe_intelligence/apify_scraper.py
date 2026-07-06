"""
Apify Google Maps scraper integration.

Uses Apify's Google Maps Scraper to fetch reviews for cafes.
"""

import os
from datetime import datetime
from typing import List, Optional
from apify_client import ApifyClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .schemas import Review, ReviewBatch

console = Console()


class ApifyScraper:
    """Scraper for Google Maps reviews using Apify."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Apify client.

        Args:
            api_token: Apify API token (defaults to APIFY_API_TOKEN env var)
        """
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN not found in environment")

        self.client = ApifyClient(self.api_token)

        # Apify actor for Google Maps scraper
        # Using compass/crawler-google-places (free tier compatible)
        self.actor_id = "compass/crawler-google-places"

    def scrape_cafe_reviews(
        self,
        cafe_name: str,
        location: str = "Toronto",
        max_reviews: int = 50,
        language: str = "en"
    ) -> ReviewBatch:
        """
        Scrape Google Maps reviews for a cafe.

        Args:
            cafe_name: Name of the cafe
            location: City/location (default: Toronto)
            max_reviews: Maximum number of reviews to fetch
            language: Review language (default: en)

        Returns:
            ReviewBatch with all scraped reviews
        """
        console.print(f"\n[cyan]Scraping reviews for: {cafe_name} ({location})[/cyan]")

        # Construct search query
        search_query = f"{cafe_name} {location}"

        console.print(f"[dim]Searching for: {search_query}[/dim]")

        # Apify actor input for compass/crawler-google-places
        run_input = {
            "searchStringsArray": [search_query],
            "maxCrawledPlacesPerSearch": 1,  # Only first result
            "language": language,
            "maxReviews": max_reviews,
            "reviewsSort": "newest",
        }

        # Run the actor and wait for completion
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Fetching reviews from Apify...", total=None)

            run = self.client.actor(self.actor_id).call(run_input=run_input)

        # Fetch results - Run object has attributes, not dict access
        reviews_data = []

        try:
            # Access as attribute, not dictionary
            dataset_id = run.default_dataset_id
            for item in self.client.dataset(dataset_id).iterate_items():
                # This actor returns review items directly
                reviews_data.append(item)
        except (AttributeError, TypeError) as e:
            console.print(f"[yellow]Warning: Could not access dataset: {e}[/yellow]")

        if not reviews_data:
            console.print(f"[yellow]Warning: No reviews found for {cafe_name}[/yellow]")
            # Return empty batch
            return ReviewBatch(
                cafe_name=cafe_name,
                location=location,
                reviews=[],
                total_reviews=0,
                average_rating=0.0,
                date_range_start=datetime.now(),
                date_range_end=datetime.now()
            )

        # Parse reviews - compass actor returns place data with reviews
        if reviews_data and "reviews" in reviews_data[0]:
            place_data = reviews_data[0]
            reviews = self._parse_reviews(place_data, cafe_name)
        else:
            reviews = []

        if not reviews:
            console.print(f"[yellow]Warning: No valid reviews parsed for {cafe_name}[/yellow]")
            return ReviewBatch(
                cafe_name=cafe_name,
                location=location,
                reviews=[],
                total_reviews=0,
                average_rating=0.0,
                date_range_start=datetime.now(),
                date_range_end=datetime.now()
            )

        # Calculate stats
        total_reviews = len(reviews)
        average_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0.0
        dates = [r.date for r in reviews]
        date_range_start = min(dates)
        date_range_end = max(dates)

        console.print(f"[green]✓ Scraped {total_reviews} reviews (avg rating: {average_rating:.1f})[/green]")

        return ReviewBatch(
            cafe_name=cafe_name,
            location=location,
            reviews=reviews,
            total_reviews=total_reviews,
            average_rating=average_rating,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )

    def _parse_reviews_direct(self, reviews_data: list, cafe_name: str) -> List[Review]:
        """
        Parse reviews from web_wanderer actor (returns reviews directly).

        Args:
            reviews_data: List of review items from Apify
            cafe_name: Name of the cafe

        Returns:
            List of validated Review objects
        """
        reviews = []

        for review_item in reviews_data:
            try:
                # Parse review date
                published_at = review_item.get("publishedAtDate") or review_item.get("date")
                if published_at:
                    # Handle ISO format or timestamp
                    if isinstance(published_at, str):
                        review_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    else:
                        review_date = datetime.fromtimestamp(published_at)
                else:
                    review_date = datetime.now()

                # Extract review text
                review_text = review_item.get("text", "").strip()
                if not review_text:
                    # Skip reviews without text
                    continue

                # Get rating (may be named differently)
                rating = review_item.get("stars") or review_item.get("rating", 0)

                # Create Review object (Pydantic will validate)
                review = Review(
                    cafe_name=cafe_name,
                    rating=int(rating),
                    text=review_text,
                    date=review_date,
                    reviewer_name=review_item.get("name") or review_item.get("reviewerName"),
                    source="Google Maps"
                )

                reviews.append(review)

            except Exception as e:
                # Log parsing error but continue
                console.print(f"[yellow]Warning: Failed to parse review: {e}[/yellow]")
                continue

        return reviews

    def _parse_reviews(self, place_data: dict, cafe_name: str) -> List[Review]:
        """
        Parse raw Apify data into Review objects.

        Args:
            place_data: Raw place data from Apify
            cafe_name: Name of the cafe

        Returns:
            List of validated Review objects
        """
        reviews = []

        for review_data in place_data.get("reviews", []):
            try:
                # Parse review date
                published_at = review_data.get("publishedAtDate")
                if published_at:
                    # Apify returns ISO format string
                    review_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                else:
                    # Fallback to now if no date
                    review_date = datetime.now()

                # Extract review text
                review_text = review_data.get("text", "").strip()
                if not review_text:
                    # Skip reviews without text
                    continue

                # Create Review object (Pydantic will validate)
                review = Review(
                    cafe_name=cafe_name,
                    rating=int(review_data.get("stars", 0)),
                    text=review_text,
                    date=review_date,
                    reviewer_name=review_data.get("name"),
                    source="Google Maps"
                )

                reviews.append(review)

            except Exception as e:
                # Log parsing error but continue
                console.print(f"[yellow]Warning: Failed to parse review: {e}[/yellow]")
                continue

        return reviews

    def scrape_multiple_cafes(
        self,
        cafe_names: List[str],
        location: str = "Toronto",
        max_reviews_per_cafe: int = 50
    ) -> List[ReviewBatch]:
        """
        Scrape reviews for multiple cafes.

        Args:
            cafe_names: List of cafe names
            location: City/location
            max_reviews_per_cafe: Max reviews per cafe

        Returns:
            List of ReviewBatch objects
        """
        batches = []

        console.print(f"\n[bold cyan]Scraping {len(cafe_names)} cafes...[/bold cyan]")

        for i, cafe_name in enumerate(cafe_names, 1):
            console.print(f"\n[bold]Cafe {i}/{len(cafe_names)}[/bold]")

            try:
                batch = self.scrape_cafe_reviews(
                    cafe_name=cafe_name,
                    location=location,
                    max_reviews=max_reviews_per_cafe
                )
                batches.append(batch)

            except Exception as e:
                console.print(f"[red]Error scraping {cafe_name}: {e}[/red]")
                continue

        console.print(f"\n[green bold]✓ Completed scraping {len(batches)}/{len(cafe_names)} cafes[/green bold]")

        return batches


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    scraper = ApifyScraper()

    # Test single cafe
    batch = scraper.scrape_cafe_reviews(
        cafe_name="Quantum Coffee",
        location="Toronto",
        max_reviews=20
    )

    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"Cafe: {batch.cafe_name}")
    console.print(f"Total reviews: {batch.total_reviews}")
    console.print(f"Average rating: {batch.average_rating:.1f}")
    console.print(f"Date range: {batch.date_range_start.date()} to {batch.date_range_end.date()}")

    # Show sample review
    if batch.reviews:
        console.print(f"\n[bold]Sample review:[/bold]")
        sample = batch.reviews[0]
        console.print(f"Rating: {sample.rating} stars")
        console.print(f"Date: {sample.date.date()}")
        console.print(f"Text: {sample.text[:200]}...")
