import streamlit as st
import pandas as pd
import asyncio
import json
import math
from typing import List, Dict, Optional
import random
import time
from httpx import AsyncClient, Response
from parsel import Selector


# List of User-Agents to mimic different devices/browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/604.1",
]

# Initialize the HTTP client
async def get_client():
    headers = {
        "User-Agent": random.choice(USER_AGENTS),  # Rotate User-Agents
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
    }
    return AsyncClient(headers=headers, follow_redirects=True)

# Function to parse hotel page
def parse_hotel_page(result: Response) -> Dict:
    """Parse hotel data from hotel pages."""
    selector = Selector(result.text)
    basic_data = json.loads(selector.xpath("//script[contains(text(),'aggregateRating')]/text()").get())
    description = selector.css("div.fIrGe._T::text").get()
    amenities = []
    for feature in selector.xpath("//div[contains(@data-test-target, 'amenity')]/text()"):
        amenities.append(feature.get())
    reviews = []
    for review in selector.xpath("//div[@data-reviewid]"):
        title = review.xpath(".//div[@data-test-target='review-title']/a/span/span/text()").get()
        text = review.xpath(".//span[@data-test-target='review-text']/span/text()").get()
        rate = review.xpath(".//div[@data-test-target='review-rating']/span/@class").get()
        rate = (int(rate.split("ui_bubble_rating")[-1].split("_")[-1].replace("0", ""))) if rate else None
        trip_data = review.xpath(".//span[span[contains(text(),'Date of stay')]]/text()").get()
        reviews.append({
            "title": title,
            "text": text,
            "rate": rate,
            "tripDate": trip_data
        })

    return {
        "basic_data": basic_data,
        "description": description,
        "featues": amenities,
        "reviews": reviews
    }

async def scrape_hotel(url: str, max_review_pages: Optional[int] = None) -> Dict:
    """Scrape hotel data and reviews"""
    client = await get_client()
    first_page = await client.get(url)
    
    # Check for blocking
    assert first_page.status_code != 403, "request is blocked"
    
    hotel_data = parse_hotel_page(first_page)

    # Get total reviews and pages
    _review_page_size = 1
    total_reviews = int(hotel_data["basic_data"]["aggregateRating"]["reviewCount"])
    total_review_pages = math.ceil(total_reviews / _review_page_size)

    if max_review_pages and max_review_pages < total_review_pages:
        total_review_pages = max_review_pages
    
    # Scrape review pages with delay
    review_urls = [
        url.replace("-Reviews-", f"-Reviews-or{_review_page_size * i}-")
        for i in range(1, total_review_pages)
    ]
    
    for response in asyncio.as_completed(review_urls):
        time.sleep(random.uniform(1, 3))  # Introduce random delay
        data = parse_hotel_page(await response)
        hotel_data["reviews"].extend(data["reviews"])

    return hotel_data

# The rest of your scraping and Streamlit app code remains the same...
# Synchronous wrapper for scraping
def scrape_hotel_sync(url: str, max_review_pages: int) -> Dict:
    return asyncio.run(scrape_hotel(url, max_review_pages))

# Streamlit App
st.title("TripAdvisor Hotel Review Scraper")

# Input section for URL
hotel_url = st.text_input("Enter the TripAdvisor hotel review page URL:")

# Input section for the number of pages to scrape
max_pages = st.number_input("Enter the number of review pages to scrape (1 page = 10 reviews):", min_value=1, step=1)

# Button to trigger scraping
if st.button("Scrape Reviews"):
    with st.spinner("Scraping reviews..."):
        if hotel_url:
            hotel_data = scrape_hotel_sync(hotel_url, max_pages)
            reviews = hotel_data['reviews']
            
            if reviews:
                df = pd.DataFrame(reviews)
                st.write(df)

                # Download button for CSV
                csv = df.to_csv(index=False)
                st.download_button(label="Download reviews as CSV", data=csv, mime="text/csv", file_name="tripadvisor_reviews.csv")
                
                st.success("Scraping complete!")
            else:
                st.error("No reviews found.")
        else:
            st.error("Please provide a valid URL.")

