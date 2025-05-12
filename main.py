import os
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,                # SDK configuration holder :contentReference[oaicite:3]{index=3}
    ApiClient,                    # HTTP client wrapper :contentReference[oaicite:4]{index=4}
    MessagingApi,                 # Messaging API interface :contentReference[oaicite:5]{index=5}
    ReplyMessageRequest,          # Encapsulates reply request :contentReference[oaicite:6]{index=6}
    TextMessage,                  # Plain-text reply :contentReference[oaicite:7]{index=7}
    StickerMessage,               # Sticker reply :contentReference[oaicite:8]{index=8}
    ImageMessage,                 # Image reply (v3 name) :contentReference[oaicite:9]{index=9}
    VideoMessage,                 # Video reply (v3 name) :contentReference[oaicite:10]{index=10}
    LocationMessage,              # Location reply (v3 name) :contentReference[oaicite:11]{index=11}
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import google.generativeai as genai
import json
from datetime import datetime
import uuid

# ─── Load config ────────────────────────────────────────────────────────────────
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET       = os.getenv("CHANNEL_SECRET")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize v3 SDK client configuration
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler       = WebhookHandler(CHANNEL_SECRET)

# Add this after other environment variables
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)

# Your custom image search handler (unchanged)
from utils import MyGoImage
mygo = MyGoImage("./mygo_db.json")

# Add after other initializations
CONVERSATION_FILE = "conversations.json"

def load_conversations():
    try:
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_conversations(conversations):
    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

# Add these new routes before the callback route
@app.route("/api/conversations", methods=["GET"])
def get_all_conversations():
    conversations = load_conversations()
    return jsonify(conversations)

@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conversations = load_conversations()
    if conversation_id in conversations:
        return jsonify(conversations[conversation_id])
    return jsonify({"error": "Conversation not found"}), 404

@app.route("/api/conversations", methods=["DELETE"])
def delete_all_conversations():
    save_conversations({})
    return jsonify({"message": "All conversations deleted"})

@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    conversations = load_conversations()
    if conversation_id in conversations:
        del conversations[conversation_id]
        save_conversations(conversations)
        return jsonify({"message": f"Conversation {conversation_id} deleted"})
    return jsonify({"error": "Conversation not found"}), 404

# ─── Webhook endpoint ──────────────────────────────────────────────────────────
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# ─── Message handler ───────────────────────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip().lower()
    user_id = event.source.user_id
    conversations = load_conversations()
    
    # Initialize user's conversation history if it doesn't exist
    if user_id not in conversations:
        conversations[user_id] = {
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    # Store the user's message
    conversations[user_id]["messages"].append({
        "role": "user",
        "content": text,
        "timestamp": datetime.now().isoformat()
    })

    # Choose reply based on the user's text
    if text == "文字":
        message = TextMessage(text="這是一則文字回覆！")

    elif text == "貼圖":
        message = StickerMessage(package_id="1", sticker_id="1")

    elif text == "圖片":
        # **Use ImageMessage in v3** (not ImageSendMessage)
        message = ImageMessage(
            original_content_url="https://ryankert01.github.io/yzu-oss-hw4/image.png",
            preview_image_url="https://ryankert01.github.io/yzu-oss-hw4/image.png"
        )

    elif text == "影片":
        # **Use VideoMessage in v3** (not VideoSendMessage)
        message = VideoMessage(
            original_content_url="https://ryankert01.github.io/yzu-oss-hw4/video.mp4",
            preview_image_url="https://ryankert01.github.io/yzu-oss-hw4/video_preview.png"
        )

    elif text == "位置資訊":
        # **Use LocationMessage in v3** (not LocationSendMessage)
        message = LocationMessage(
            title="台北 101",
            address="台北市信義路五段7號",
            latitude=25.033968,
            longitude=121.564468
        )

    elif text.startswith("mygo:"):
        img_url = mygo.searchMyGoImage(text[5:].strip())
        if img_url:
            message = ImageMessage(
                original_content_url=img_url,
                preview_image_url=img_url
            )
        else:
            message = TextMessage(text="找不到圖片wwwwwwwww")

    else:
        try:
            # Get the prompt after "ai:"
            prompt = text.strip()
            
            # Call Gemini API
            response = model.generate_content(prompt)
            
            # Get the response text
            ai_response = response.text
            
            message = TextMessage(text=ai_response)
        except Exception as e:
            message = TextMessage(text=f"抱歉，AI 回應時發生錯誤: {str(e)}")

    # Store the bot's response
    conversations[user_id]["messages"].append({
        "role": "assistant",
        "content": message.text if isinstance(message, TextMessage) else "Non-text response",
        "timestamp": datetime.now().isoformat()
    })
    
    save_conversations(conversations)

    # Send the reply via v3 MessagingApi
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        request_payload = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[message]
        )
        messaging_api.reply_message(request_payload)

if __name__ == "__main__":
    app.run(port=8000)