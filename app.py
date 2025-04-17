from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from summary import process_video_from_url, genrate_thumbnail,SummaryGenrationError
from pytube import YouTube
import requests
from PIL import Image
from io import BytesIO
import time

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = os.path.expanduser('~/YT_thumbnail/backend/Downloads')
for folder in [UPLOAD_FOLDER, THUMBNAIL_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    THUMBNAIL_FOLDER=THUMBNAIL_FOLDER,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
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
        summary = process_video_from_url(video_url)
        if(not summary):
            raise SummaryGenrationError
        # summary="Be not afraid of greatness.\
        #             Some are born great,\
        #             some achieve greatness,\
        #             and others have greatness thrust upon them.\
        #             -William Shakespeare"
        #time.sleep(30)
        
        return jsonify({'summary': summary})

    except Exception as e:
        print(f"Error in /summarize: {str(e)}")  # Debugging
        return jsonify({"error": f"Failed to process video: {str(e)}"}), 500

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
def generate_thumbnails():
    """Generate new thumbnails based on video summary."""
    try:
        data = request.get_json()
        summary = data.get('summary')
        video_url = data.get('video_url')
        human = data.get("includeHuman")
        text= data.get("includeText")

        if not summary or not video_url :
            return jsonify({"error": "Missing required parameters"}), 400
        
        if not human or not text:
            text=human=True

        image_name=genrate_thumbnail(summary,human,text)
        path=f"https://flaskyt-production.up.railway.app/thumbnails/{image_name}"
        mock_thumbnails = []
        mock_thumbnails.append(path)
    
        # print(summary)

        # # Here you would implement your thumbnail generation logic
        # # For now, returning a mock response
        # mock_thumbnails = [
        #     "http://127.0.0.1:5000/thumbnails/generated_image_20241116_094748.png",
        # ]
        print(mock_thumbnails.count)
        return jsonify({'thumbnails': mock_thumbnails })

    except Exception as e:
        print(f"Error in /generate_thumbnails: {str(e)}")  # Debugging
        return jsonify({"error": f"Failed to generate thumbnails: {str(e)}"}), 500

@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """Serve generated thumbnail images."""
    try:
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)
        if os.path.exists(thumbnail_path):
            return send_file(thumbnail_path)
        return jsonify({"error": "Thumbnail not found"}), 404

    except Exception as e:
        print(f"Error serving thumbnail: {str(e)}")  # Debugging
        return jsonify({"error": f"Failed to serve thumbnail: {str(e)}"}), 500

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
    app.run(host="0.0.0.0", port=7860)