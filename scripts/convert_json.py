import json


def convert_to_json(file_path, new_file_path='dataset/lex_fridman_pod_transcriptions.json'):
    # Open the file
    with open(file_path, 'r') as f:
        # Read the contents of the file
        file_contents = f.read()

    # Replace the new line character with a comma
    file_contents = file_contents.replace('[', '')
    file_contents = file_contents.replace(']', '')
    file_contents = file_contents.replace('\n', ',')

    # Append the square bracket to make it a valid json array
    file_contents = "[" + file_contents[:-1] + "]"

    # Load the file contents into a Python object
    data = json.loads(file_contents)

    # Write the data as newline delimited JSON
    with open(new_file_path, "w") as ndjson_file:
        for item in data:
            ndjson_file.write(json.dumps(item) + "\n")

    return 'File saved successfully'

# Convert the file to a valid JSON file
convert_to_json('dataset/lex_fridman_pod_transcriptions_2 copy.txt')

# Iterate through first 10 elements in 'lex_fridman_pod_transcriptions_2.json'
for i in range(10):
    # Open 'lex_fridman_pod_transcriptions.json' in read mode
    with open('dataset/lex_fridman_pod_transcriptions.json', 'r') as file:
        # Load the json file
        data = json.load(file)
        # Print the json file
        print(data[i])
