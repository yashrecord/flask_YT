from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from summary import process_video_from_url, Generate_promt
from generate_image import generate_image
import requests


app = Flask(__name__)
CORS(app)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]  # No global limit, only per-route
)



def get_youtube_thumbnail(video_id):
    """Get the highest resolution thumbnail available for a YouTube video."""
    resolutions = [
        'maxresdefault',  # 1080p
        'sddefault',      # 640p
        'hqdefault',      # 480p
        'mqdefault',      # 320p
        'default'         # 120p
    ]
    
    for resolution in resolutions:
        url = f'https://img.youtube.com/vi/{video_id}/{resolution}.jpg'
        response = requests.get(url)
        if response.status_code == 200:
            return url
    return None

@app.route('/summarize', methods=['POST'])
@limiter.limit("2 per minute")
def summarize():
    """Generate summary for a video from URL or uploaded file."""
    try:
        data = request.get_json()
        print("Received request data:", data)  # Debugging

        video_url = data.get('video_url')
        video_id = data.get('video_id')

        if not video_url:
            return jsonify({"error": "Missing video URL"}), 400

        # Generate summary
        result = process_video_from_url(video_url)
        if not result or not result.get('summary'):
            raise ValueError
        
        return jsonify(result)

    except ValueError:
        print(f"Error in /summarize check issue return ")  # Debugging
        return jsonify({"error": f"Failed to process video"}), 500

@app.route('/get_current_thumbnail', methods=['POST'])
def get_current_thumbnail():
    """Get the current thumbnail of a YouTube video."""
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({"error": "Missing video ID"}), 400

        thumbnail_url = get_youtube_thumbnail(video_id)
        
        if not thumbnail_url:
            return jsonify({"error": "Could not fetch thumbnail"}), 404

        return jsonify({'thumbnail_url': thumbnail_url})

    except Exception as e:
        print(f"Error in /get_current_thumbnail: {str(e)}")  # Debugging
        return jsonify({"error": f"Failed to get thumbnail: {str(e)}"}), 500

@app.route('/generate_thumbnails', methods=['POST'])
@limiter.limit("2 per 30 seconds")
def generate_thumbnails():
    """Generate new thumbnails based on style string and optional custom text."""
    try:
        data = request.get_json()
        video_id = data.get('videoId')
        style = data.get('style')  # Now expecting a string directly
        custom_text = data.get('customText', '')  # Optional parameter

        if not video_id or not style:
            return jsonify({"error": "Missing required parameters: videoId and style"}), 400

        # Get video URL from video ID
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Generate the thumbnail using the style string
        prompt = style
        if custom_text:
            prompt = f"{prompt}\n\nInclude the following text: {custom_text}"

        image_url = generate_image(prompt)
        if image_url == "error":
            raise ValueError("Failed to generate image")
        
        return jsonify({
            "url": image_url
        }), 200

    except Exception as e:
        print(f"Error in /generate_thumbnails: {str(e)}")
        return jsonify({"error": f"Failed to generate thumbnails: {str(e)}"}), 500

@app.route('/generate_style', methods=['POST'])
@limiter.limit("2 per 30 seconds")
def generate_style():
    """Generate style description for thumbnail generation."""
    try:
        data = request.get_json()
        summary = data.get('summary')
        include_human = data.get('includeHuman', True)
        include_text = data.get('includeText', True)

        if not summary:
            return jsonify({"error": "Missing summary parameter"}), 400

        # Generate the style using Generate_promt
        style = Generate_promt(summary, include_human, include_text)
        
        return jsonify({
            "style": style
        }), 200

    except Exception as e:
        print(f"Error in /generate_style: {str(e)}")
        return jsonify({"error": f"Failed to generate style: {str(e)}"}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error."""
    return jsonify({"error": "File size exceeded limit (16MB)"}), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error occurred"}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle not found errors."""
    return jsonify({"error": "Requested resource not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860,debug=True)