from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Load from environment or set directly
RTMP_STATUS_URL = os.getenv("RTMP_STATUS_URL", "http://your-rtmp-server.com/stat")
STREAM_KEY = os.getenv("RTMP_STREAM_KEY", "mysecretkey123")

@app.route('/status', methods=['GET'])
def check_status():
    try:
        # Optional: override key via ?key= parameter
        key = request.args.get("key", STREAM_KEY)
        response = requests.get(RTMP_STATUS_URL, timeout=5)

        if response.status_code != 200:
            return jsonify({"live": False, "error": "Status endpoint unreachable"})

        data = response.text
        if key in data:
            return jsonify({
                "live": True,
                "title": "Free Fire Max Live!",
                "thumbnail": "https://example.com/thumbnail.jpg",
                "url": f"rtmp://your-server.com/live/{key}"
            })
        else:
            return jsonify({"live": False})
    except Exception as e:
        return jsonify({"live": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)