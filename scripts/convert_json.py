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

    # Convert the Python object to a JSON string
    json_string = json.dumps(data)
    
    # Open a new file in write mode
    with open(new_file_path, 'w') as f:
        # Write the JSON string to the file
        f.write(json_string)
    
    return 'File saved successfully'


print(convert_to_json('dataset/lex_fridman_pod_transcriptions_2 copy.txt'))

# Iterate through first 10 elements in 'lex_fridman_pod_transcriptions_2.json'
for i in range(10):
    # Open 'lex_fridman_pod_transcriptions.json' in read mode
    with open('dataset/lex_fridman_pod_transcriptions.json', 'r') as file:
        # Load the json file
        data = json.load(file)
        # Print the json file
        print(data[i])
