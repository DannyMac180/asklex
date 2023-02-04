import os
import openai
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv
import pinecone
from tqdm.auto import tqdm

load_dotenv()


def get_segments_from_bq():
    # Load the service account key JSON file.
    credentials = Credentials.from_service_account_file(
        "./asklex-f6e79ca5e230.json")

    # Use the credentials to build a BigQuery client.
    bigquery_client = bigquery.Client(
        credentials=credentials, project=credentials.project_id)

    sql = """
        SELECT * FROM asklex.lexfridman_pod_transcriptions LIMIT 10
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

    # Create embeddings
    embeddings = openai.Embedding.create(
        input=segments["text"].tolist(),
        engine=MODEL
    )

    # Put embeddings into a list
    embeddings = embeddings["data"]
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

    metadata = []
    for i, embedding in tqdm(enumerate(embeddings)):
        meta = {
            "id": str(i),
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
    index.upsert(vectors=list(to_upsert))

def main():
    segments_df = get_segments_from_bq()
    embeddings = create_embeddings(segments_df)
    save_embeddings_to_pinecone(embeddings, segments_df)

if __name__ == "__main__":
    main()
