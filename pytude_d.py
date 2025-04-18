import os
import uuid
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import re

HF_API_URL = "https://rockingyash-speechtotext.hf.space/transcribe/"

def extract_video_id(youtube_url):
    # Regular expression for extracting the video ID
    pattern = (
        r'(?:https?:\/\/)?(?:www\.)?'
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|'
        r'youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)  # The video ID is in the first capture group
    return None


def get_youtube_transcript(video_url):
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return None, "Invalid YouTube URL"
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([line['text'] for line in transcript])
        return text, None
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None, f"No transcript: {str(e)}"
    except Exception as e:
        return None, f"Transcript API error: {str(e)}"

def download_audio_file(video_url, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)
    filename = os.path.join(download_dir, f"{uuid.uuid4().hex}.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_path = ydl.prepare_filename(info)
            return downloaded_path, None
    except Exception as e:
        return None, f"Download error: {e}"

def transcribe_with_api(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(HF_API_URL, files={"file": f})
        if response.status_code == 200:
            return response.json().get("transcription"), None
        else:
            return None, f"API Error {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Request error: {str(e)}"
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as cleanup_err:
            print(f"Cleanup error: {cleanup_err}")

def full_transcription_pipeline(video_url):
    print("🔍 Trying YouTube transcript...")
    transcript, err = get_youtube_transcript(video_url)
    if transcript:
        print("✅ Got YouTube transcript!")
        return transcript

    print(f"❌ {err} — Falling back to Whisper transcription...")

    file_path, download_err = download_audio_file(video_url)
    if not file_path:
        return f"Download failed: {download_err}"

    print("🎙️ Sending audio to Whisper API...")
    transcription, api_err = transcribe_with_api(file_path)
    if transcription:
        print("✅ Transcription complete!")
        return transcription
    else:
        return f"Whisper API failed: {api_err}"

# 🎬 Example usage
if __name__ == "__main__":
    yt_url = input("Enter YouTube URL: ")
    result = full_transcription_pipeline(yt_url)
    print("\n--- Final Transcript ---\n")
    print(result)
