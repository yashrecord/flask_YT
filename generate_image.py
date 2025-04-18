import os
import shutil
from datetime import datetime
from gradio_client import Client
from gradio_client.exceptions import AppError
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("IMAGE_KEY")
if not api_key:
    raise ValueError(" IMAGE_KEY environment variable not set. Please add it to your .env file.")


# Configuration       
cloudinary.config( 
    cloud_name = "dsfiew0iy", 
    api_key = "371416444248654", 
    api_secret = api_key,
    secure=True
)


def generate_image(prompt):
    try:
        # Call the model
        client = Client("black-forest-labs/FLUX.1-schnell")
        result = client.predict(
            prompt,
            randomize_seed=True,
            width=1280,
            height=720,
            num_inference_steps=4,
            api_name="/infer"
        )

        temp_file_path = result[0]

        # Create a unique name (no folder, just filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"generated_image_{timestamp}.png"

        # Upload directly to Cloudinary
        public_id = file_name.rsplit('.', 1)[0]
        upload_result = cloudinary.uploader.upload(
            temp_file_path,
            public_id=public_id,
            overwrite=True
        )

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # Check upload result
        if upload_result and "secure_url" in upload_result:
            print(f"✅ Uploaded successfully! URL: {upload_result['secure_url']}")
            return upload_result['secure_url']  # Return public_id or URL if needed

        else:
            print("❌ Upload failed, no URL returned")
            return "error"

        

    except AppError as e:
        print(f"❌ Model Error: {e}")
        print("You have exceeded the GPU quota. Please try again later.")
        return "error"
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
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
    print(generate_image(prompt))
