import os
import openai
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
from tqdm.auto import tqdm
import time
import pinecone

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
            # Create pinecone index
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENV")
            )

            # check if 'openai' index already exists (only create index if not)
            if 'asklex' not in pinecone.list_indexes():
                pinecone.create_index('asklex', dimension=len(embeddings_batch["data"][0]))
            # connect to index
            index = pinecone.Index('asklex')

            # Comprehend the embeddings into an array
            embeds = [embedding["embedding"] for embedding in embeddings_batch["data"]]

            # Upsert the embeddings into the index in batches of 100
            pinecone_batch_size = 100
            for i in range(0, len(embeds), pinecone_batch_size):
                index.upsert(embeds[i:i+pinecone_batch_size], segments.iloc[i:i+pinecone_batch_size].to_dict("records"))

            time.sleep(2)
        except Exception as e:
            print(e)

def main():
    segments_df = get_segments_from_bq()
    create_embeddings(segments_df)

if __name__ == "__main__":
    main()
