import whisper
import torch
import json
from pathlib import Path
from datasets import load_dataset

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device {device}")

model = whisper.load_model("base").to(device)

# Get paths to audio files
paths = [str(x) for x in Path("./dataset/audio_files").glob("*.mp3")]

# Instantiate video_metadata from HuggingFace dataset
video_metadata = load_dataset("DannyMac180/lex_fridman_pod_youtube_metadata", split="train")

def transcribe_audio_and_save(paths):
    data = []
    for path in paths:
        # Get _id by splitting path and removing .mp3 extension
        _id = path.split('/')[-1][:-4]
        # Transcribe audio file
        transcription = model.transcribe(path)
        segments = transcription["segments"]
        # Get the metadata for the video with _id
        video_meta = video_metadata.filter(lambda x: x["video_id"] == _id)

        for segment in segments:
            meta = {
                "video_id": _id,
                "title": video_meta["title"],
                "publishedAt": video_meta["publishedAt"],
                **{
                    "segment_id": f"{_id}_{segment['start']}",
                    "text": segment["text"].strip(),
                    "start": segment["start"],
                    "end": segment["end"]
                }
            },
            data.append(meta)
        
        with open("dataset/lex_fridman_pod_transcriptions.json", "w", encoding="utf-8") as fp:
            for line in data:
                json.dump(line, fp)
                fp.write("\n")


transcribe_audio_and_save(paths)