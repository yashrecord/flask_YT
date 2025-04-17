#import yt_dlp
import subprocess
import os
#import whisper
import google.generativeai as palm
from generate_image import generate_image
from youtube_transcript_api import YouTubeTranscriptApi
import re
from new_summary import generate_newsummary
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")




class SummaryGenrationError():
    ...





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

def process_video_from_url(video_url,cookie_path="cookie.txt"):
    # video_path = download_video(video_url)
    # summary=generate_video_summary(video_path)
    # os.remove(video_path)
    
    subtitle=""
    video_id=extract_video_id(video_url)
    transcript=""
    video_path=""
    try:
        if cookie_path:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookie_path)
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

        for text in transcript:
            subtitle += " " + text["text"]

    except Exception as e:
        print(f"[Transcript Error] Falling back to Whisper: {str(e)}")
        return subtitle
        # video_path = download_video(video_url)
        # subtitle=generate_video_summary(video_path)
        # os.remove(video_path)
    else:
        for text in transcript:
            subtitle=subtitle+" "+text["text"]
    try:
        extracted_string = re.search(r'downloads/(.*?)\.mp4', video_path).group(1)+" "
    except Exception as e:
        extracted_string=""
    


    prompt=f"""
        Provide a very short summary, no more than three sentences, for the following video {extracted_string}subtitle:

        {subtitle}

        Summary:
        """
    summary=generate_newsummary(prompt)
    return summary


def download_video(video_url, download_dir="downloads", cookie_path="cookie.txt"):
    os.makedirs(download_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio[ext=mp4]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        return f"Error: {str(e)}"




# def extract_audio_from_video(video_path, audio_path):
#     """Extract audio from a video file using ffmpeg."""
#     cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_path]
#     subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     return audio_path

# def transcribe_audio_whisper(audio_path):
#     """Transcribe the audio using Whisper."""
#     model = whisper.load_model("tiny")  # You can use "tiny", "base", "small", "medium", "large"
#     result = model.transcribe(audio_path)
#     transcription = result["text"]
#     return transcription

def summarize_text(text,chunk_size=1024, overlap=100):
    # Remove this line as it is redundant
    palm.configure(api_key=api_key)  

    # Split the text into manageable chunks with some overlap for better context
    # text_chunks = []
    # for i in range(0, len(text), chunk_size - overlap):
    #     chunk = text[i:i + chunk_size]
    #     text_chunks.append(chunk)

    # summaries = []
    # for chunk in text_chunks:
    #     # Use a different model
    #     model = palm.GenerativeModel(model_name="models/gemini-pro")
    #     prompt = f"This is youtube subtitle, generate short word summary without losing any information: {chunk}"

    #     # Use the generate_content function
    #     response = model.generate_content(prompt)
    #     summaries.append(response.text)
    model = palm.GenerativeModel(model_name="models/gemini-pro")
    prompt = f"""
    Provide a very short summary, no more than three sentences, for the following video subtitle:

    {text}

    Summary:
    """
    response = model.generate_content(prompt)
    summaries=response.text

    normal_string = ''.join(summaries.split())

    #cleaned_text = final_string.replace("*", "").replace("\n", " ").strip()

    # Join the summaries of the chunks
    return ' '.join(normal_string.split())



def generate_video_summary(video_path, output_filename="summary.mp4"):
    """Generates a video summary with script."""
    audio_path = "temp_audio.wav"

    # 1. Extract Audio with ffmpeg
    extract_audio_from_video(video_path, audio_path)
    print("Audio extracted.")

    # 2. Transcribe Audio with Whisper
    transcription = transcribe_audio_whisper(audio_path)
    print("Audio transcribed.")
    os.remove(audio_path)
    # 3. Summarize Transcript
    return transcription
    
def Generate_promt(summary,human,text):
    prompt = f"""Please extract the following information from the video summary:\
    Video Topic: What is the main subject or theme of the video?\
    Target Audience: Who is the intended viewer of this video?\
    Thumbnail Style: Describe the desired visual style for the thumbnail image, including color scheme, composition, and overall aesthetic. {summary}"""

    if human:
        human="Include human or human face in thumbnial"
    else :
        human="Without any humanoid or anthropomorphic features"
    
    if not text:
        text="Do not include terms like signs, labels, or banners unless unavoidable and Focus on describing the aesthetics and clarity of the image"
    else:
        text="Include title or any Caching Phrases from summary"
    output_model=generate_newsummary(prompt)
    style=f"""Give only one best style for an image using the following points and use simple sentences and avoid spelling mistakes:
 
           {human} 
           {text}
           {output_model}

            Style:
        """
    text=generate_newsummary(style)

   
    return text

def genrate_thumbnail(text,human,text1):
    prompt=Generate_promt(text,human,text1)
    print(prompt)
    return generate_image(prompt)




if __name__ == '__main__':
   summary="This video explains the nuances of declaring pointers in C/C++.  Specifically, it covers how declaring multiple pointers on one line requires an asterisk before each pointer name, not just one at the beginning.  It also clarifies that when declaring a pointer to an array, the array brackets bind more tightly to the pointer type than the array size, meaning `char *str[20]` declares an array of pointers, not a pointer to an array."
   #text=genrate_thumbnail(summary,True,False)
   text=process_video_from_url("https://www.youtube.com/watch?v=LmpAntNjPj0")
   print(text)