import whisper
import torch
import json
import pandas as pd
from pathlib import Path
import tqdm

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device {device}")

model = whisper.load_model("base").to(device)

# Get paths to audio files
paths = [str(x) for x in Path("./dataset/audio").glob("*.mp3")]

# Instantiate video_metadata from HuggingFace dataset
episode_metadata = pd.read_csv("./dataset/lexfridman_rss_metadata.csv")
# Apply .replace("https://lexfridman.com/?p=", "") to guid column
episode_metadata["guid"] = episode_metadata["guid"].apply(lambda x: x.replace("https://lexfridman.com/?p=", ""))

def transcribe_audio_and_save(paths):
    data = []
    for path in paths:
        # Get _id by splitting path and removing .mp3 extension
        _id = path.replace(".mp3", "").split("/")[-1]
        # Transcribe audio file
        print(f"Transcribing {_id}")
        transcription = model.transcribe(path)
        segments = transcription["segments"]
        # Get the metadata for the episode with _id
        episode_meta = episode_metadata[episode_metadata["guid"] == _id]

        for segment in segments:
            meta = {
                "episode_id": _id,
                "title": episode_meta["title"],
                "pub_date": episode_meta["pub_date"],
                **{
                    "segment_id": f"{_id}_{segment['start']}",
                    "text": segment["text"].strip(),
                    "start": segment["start"],
                    "end": segment["end"]
                }
            }
            print(meta)
            data.append(meta)
        
        with open("dataset/lex_fridman_pod_transcriptions.json", "w", encoding="utf-8") as fp:
            for line in data:
                json.dump(line, fp)
                fp.write("\n")


transcribe_audio_and_save(paths)