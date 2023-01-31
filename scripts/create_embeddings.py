import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load the service account key JSON file.
credentials = Credentials.from_service_account_file("./asklex-f6e79ca5e230.json")

# Use the credentials to build a BigQuery client.
bigquery_client = build("bigquery", "v2", credentials=credentials)

# # Get the dataset with id 'asklex' from the BigQuery client.
# dataset = bigquery_client.datasets().get(
#     projectId="asklex",
#     datasetId="asklex"
# ).execute()

# print(dataset)

# Make an API request.
query_results = bigquery_client.jobs().query(
    projectId="asklex",
    body={
        'query': 'SELECT * FROM asklex.lexfridman_pod_transcriptions LIMIT 100'
    }
).execute()

# Print the results.
for row in query_results['rows']:
    print(row['f'])