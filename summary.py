import os
import google.generativeai as palm
from generate_image import generate_image
from new_summary import generate_newsummary
from dotenv import load_dotenv
from pytude_d import get_youtube_transcript
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")


def process_video_from_url(video_url):
    
    
    subtitle=get_youtube_transcript(video_url)
    if not subtitle:
        return None, f"Error in transcript"
    prompt=f"""
        Provide a very short summary, no more than three sentences, for the following video {video_url} subtitle:

        {subtitle}

        Summary:
        """
    summary=generate_newsummary(prompt)
    return summary



def summarize_text(text,chunk_size=1024, overlap=100):
    # Remove this line as it is redundant
    palm.configure(api_key=api_key)  
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