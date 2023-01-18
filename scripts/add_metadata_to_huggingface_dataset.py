from googleapiclient.discovery import build
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def get_youtube_metadata(channel_id=os.environ.get('LEX_FRIDMAN_POD_CHANNEL_ID')):
    api_key = os.environ.get('YOUTUBE_API_KEY')

    # Create service object
    youtube = build('youtube', 'v3', developerKey=api_key)

    next_page_token = None
    # Get all the pages of channel metadata from the YouTube v3 API at the specifid channel_id
    while next_page_token is not "":

        # Retrieve channel metadata
        response = youtube.search().list(
            channelId=os.environ.get('LEX_FRIDMAN_POD_CHANNEL_ID'),
            type='video',
            part='snippet',
            maxResults=50,
            order='date',
            pageToken=next_page_token
        ).execute()

        next_page_token = response.get('nextPageToken')

    # Create dataframe containing metadata with video_id as index and title, description, and publishedAt as columns
    df = pd.DataFrame(columns=["video_id", "title", "publishedAt"])
    for item in response['items']:
        df = df.concat({
            "video_id": item['id']['videoId'],
            "title": item['snippet']['title'],
            "publishedAt": item['snippet']['publishedAt']
        }, ignore_index=True)
    print(df.head(800))

    # Save dataframe as csv
    df.to_csv("./dataset/lex_fridman_pod_youtube_metadata.csv", index=False)


get_youtube_metadata()
