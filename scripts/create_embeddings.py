import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd

# Load the service account key JSON file.
credentials = Credentials.from_service_account_file("./asklex-f6e79ca5e230.json")

# Use the credentials to build a BigQuery client.
bigquery_client = build("bigquery", "v2", credentials=credentials)

# Make an API request.
try:
    query_results = bigquery_client.jobs().query(
        projectId="asklex",
        body={
            'query': 'SELECT * FROM asklex.lexfridman_pod_transcriptions LIMIT 10'
        }
    ).execute()
except Exception as e:
    print(e)

query_results = bigquery_client.jobs().query(
    projectId="asklex",
    body={
        'query': 'SELECT * FROM asklex.lexfridman_pod_transcriptions LIMIT 10'
    }
).execute()

table_fields = query_results["schema"]["fields"]

# Get the rows of data in dictionary form from query_results.
rows = query_results["rows"]

# Convert the query_results to a pandas dataframe, and set the column names from the table_fields 'name element.
df = pd.DataFrame(rows['f'], columns=[field["name"] for field in table_fields])

# Print the first row of the df.
print(df.iloc[0])