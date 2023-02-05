import os
import openai
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
from tqdm.auto import tqdm
import time
import json

load_dotenv()

def get_segments_from_bq():
    # Load the service account key JSON file.
    credentials = Credentials.from_service_account_file(
        "./asklex-f6e79ca5e230.json")

    # Use the credentials to build a BigQuery client.
    bigquery_client = bigquery.Client(
        credentials=credentials, project=credentials.project_id)

    sql = """
        SELECT * FROM asklex.lexfridman_pod_transcriptions
    """

    # Make an API request.
    try:
        query_results_df = bigquery_client.query(sql).to_dataframe()
    except Exception as e:
        print(e)

    return query_results_df


def create_embeddings(segments):
    # Use openai module to create embeddings
    openai.organization = os.getenv("OPENAI_ORG_ID")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    MODEL = "text-embedding-ada-002"

    batch_size = 1000
    for i in tqdm(range(0, len(segments), batch_size)):
        # Create embeddings
        try:
            embeddings_batch = openai.Embedding.create(
                input=segments["text"].iloc[i:i+batch_size].tolist(),
                engine=MODEL
            )
            time.sleep(2)
        except Exception as e:
            print(e)

        # Put batch of embeddings into a list
        embeddings_batch = embeddings_batch["data"]

        # Save embeddings to JSON file
        with open('embeddings.json', 'w') as f:
            json.dump(embeddings_batch, f)

def main():
    segments_df = get_segments_from_bq()

    # Do half the segments, then the other half
    first_half = segments_df.iloc[:len(segments_df)//2]
    second_half = segments_df.iloc[len(segments_df)//2:]

    embeddings = create_embeddings(first_half)
    embeddings = create_embeddings(second_half)

if __name__ == "__main__":
    main()
