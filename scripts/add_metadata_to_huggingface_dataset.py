import os
import pandas as pd
import feedparser
import datasets
from dotenv import load_dotenv
load_dotenv()


def get_metadata_from_rss(rss_url):
    """Get metadata from RSS feed"""
    feed = feedparser.parse(rss_url)
    metadata = []
    for entry in feed.entries:
        metadata.append({
            # Populate fields with guid, title, description, enclosure_url, pub_date
            "guid": entry.guid,
            "title": entry.title,
            "description": entry.description,
            "audio_url": entry.enclosures[0].url,
            "pub_date": entry.published
        })
    return metadata

def save_metadata_as_csv_to_hf(metadata, dataset_name="lexfridman_rss_metadata"):
    """Save metadata as CSV"""
    csv = pd.DataFrame(metadata).to_csv()
    # Save CSV to HuggingFace Datasets
    datasets.save_dataset(data=csv, dataset_name=dataset_name, split="train", overwrite=True)


def main():
    # Get metadata from RSS feed
    metadata = get_metadata_from_rss("https://lexfridman.com/feed/podcast/")
    # Save metadata as CSV
    save_metadata_as_csv_to_hf(metadata)

if __name__ == "__main__":
    main()