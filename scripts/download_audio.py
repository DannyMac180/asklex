from datasets import load_dataset
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from tqdm.auto import tqdm

dataset = load_dataset("DannyMac180/lex_fridman_pod_youtube_metadata", split="train")
print(dataset)
save_path = "./dataset/audio_files"

def get_audio_files():
    # Use Pytube to download audio file
    # https://python-pytube.readthedocs.io/en/latest/user/quickstart.html
    for row in tqdm(dataset):
        # Instantiate download url from video_id
        url = f"https://www.youtube.com/watch?v={row['video_id']}"

        # try to create a YouTube video object
        try:
            yt = YouTube(url)
        except RegexMatchError:
            print(f"RegexMatchError: {url}")
            continue

        itag = None
        # Download only the audio files
        files = yt.streams.filter(only_audio=True)
        for file in files:
            if file.mime_type == "audio/mp4":
                itag = file.itag
                break
        if itag is None:
            print("NO MP3 AUDIO FOUND")
            continue
            
        # Get the correct mp3 'stream'
        stream = yt.streams.get_by_itag(itag)
        # Download the audio file
        stream.download(output_path=save_path, filename=f"{row['video_id']}.mp3")

get_audio_files()
