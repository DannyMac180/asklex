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
            # Save batch of embeddings to JSON file
            with open('dataset/embeds_batches/embeds_batch_{idx}.json'.format(i), 'w') as f:
                json.dump(embeddings_batch["data"], f)
            time.sleep(2)
        except Exception as e:
            print(e)

def main():
    segments_df = get_segments_from_bq()
    create_embeddings(segments_df)

if __name__ == "__main__":
    main()
