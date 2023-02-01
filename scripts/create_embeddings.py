import os
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import pandas as pd

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

# Print the results.
print(query_results_df.iloc[0])