import pandas as pd
import requests

def download_audio(metadata_csv):
    """Download audio from metadata CSV"""
    # Load metadata CSV
    metadata = pd.read_csv(metadata_csv)
    # Download audio
    for index, row in metadata.iterrows():
        # Download audio using requests
        response = requests.get(row["audio_url"])
        print(f"Downloading {row['guid']}.mp3, {row['title']}")
        # Format the 'guid' without https://lexfridman.com/podcast/
        guid = row["guid"].replace("https://lexfridman.com/?p=", "")
        # Save mp3 file to audio directory
        with open(f"/home/dmac/test_dev/asklex.ai/dataset/audio/{guid}.mp3", "wb") as f:
            f.write(response.content)

if __name__ == "__main__":
    download_audio("~/test_dev/asklex.ai/dataset/lexfridman_rss_metadata.csv")
