import os
import openai
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_segments_from_bq():
    # Load the service account key JSON file.
    credentials = Credentials.from_service_account_file("./asklex-f6e79ca5e230.json")

    # Use the credentials to build a BigQuery client.
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)

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

    print(embeddings)
    
create_embeddings(get_segments_from_bq())