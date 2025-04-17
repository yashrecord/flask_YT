import os
import shutil
from datetime import datetime
from gradio_client import Client
from gradio_client.exceptions import AppError


def generate_image(prompt):
    try:
        client = Client("black-forest-labs/FLUX.1-schnell")
        result = client.predict(
            prompt,
            randomize_seed=True,
            width=1280,  # Updated to YouTube thumbnail width
            height=720,  # Updated to YouTube thumbnail height
            num_inference_steps=4,
            api_name="/infer"
        )
        
        # Extract the file path from the result
        temp_file_path = result[0]
        
        # Define the downloads directory path
        downloads_dir = os.path.join(os.path.expanduser("~"), "YT_thumbnail/backend/Downloads")
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        
        # Generate a unique file name using a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"generated_image_{timestamp}.png"
        destination = os.path.join(downloads_dir, file_name)
        
        # Move the file to the downloads directory
        shutil.move(temp_file_path, destination)
        
        print(f"File saved in Downloads directory: {destination}")
        return file_name
    
    except AppError as e:
        print(f"Error: {e}")
        # Handle the error by retrying after some time or alerting the user
        print("You have exceeded the GPU quota. Please try again later.")
        return "error"

if __name__ == "__main__":
    # Provide a prompt for the image generation
    prompt = """Please generate image using following points:

    Target Audience: Programmers, particularly those learning C programming language

    Thumbnail Style:



    Visual: A simple, clean design with a focus on a code snippet or diagram illustrating pointer concepts.

    Color Scheme: A combination of dark and light colors, such as a dark background with bright text and graphics.

    Composition: A centered, minimalist layout with clear and concise elements.

    Overall Aesthetic: Technical, informative, and visually appealing"""
    generate_image(prompt)
