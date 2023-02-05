import os
import openai
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
import pinecone
from tqdm.auto import tqdm
import time

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
    embeddings = []
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
        embeddings.extend(embeddings_batch)

    return embeddings

def save_embeddings_to_pinecone(embeddings, segments_df):
    # Use pinecone module to save embeddings
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )

    # Create a Pinecone index
    # check if 'openai' index already exists (only create index if not)
    if 'asklex-embeddings' not in pinecone.list_indexes():
        pinecone.create_index('asklex-embeddings', dimension=len(embeddings[0]['embedding']))
    # connect to index
    index = pinecone.Index('asklex-embeddings')

    # Wrap the below code in a function that performs the process in batches of 100
    batch_size = 100
    metadata = []
    for i, embedding in tqdm(enumerate(embeddings)):
        meta = {
            "id": str(segments_df.row_number().iloc[i]),
            "title": segments_df["title"].iloc[i],
            "episode_id": segments_df["episode_id"].iloc[i],
            "segment_start": segments_df["segment_start"].iloc[i],
            "segment_end": segments_df["segment_end"].iloc[i],
            "text": segments_df["text"].iloc[i],
        }
        metadata.append(meta)
    
    ids = [meta['id'] for meta in metadata]
    
    embeds = [embedding['embedding'] for embedding in embeddings]

    to_upsert = zip(ids, embeds, metadata)
    
    for i in range(0, len(embeds), batch_size):
        index.upsert(vectors=list(to_upsert[i:i+batch_size]))

def main():
    segments_df = get_segments_from_bq()

    # Do half the segments, then the other half
    first_half = segments_df.iloc[:len(segments_df)//2]
    second_half = segments_df.iloc[len(segments_df)//2:]

    embeddings = create_embeddings(first_half)
    save_embeddings_to_pinecone(embeddings, first_half)

    embeddings = create_embeddings(second_half)
    save_embeddings_to_pinecone(embeddings, second_half)

if __name__ == "__main__":
    main()
