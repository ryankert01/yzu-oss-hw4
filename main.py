import os
from dotenv import load_dotenv
from flask import Flask, request, abort

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

# ─── Load config ────────────────────────────────────────────────────────────────
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET       = os.getenv("CHANNEL_SECRET")

# Initialize v3 SDK client configuration
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler       = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# Your custom image search handler (unchanged)
from utils import MyGoImage
mygo = MyGoImage("./mygo_db.json")

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

    # Choose reply based on the user’s text
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
            preview_image_url="https://static01.nyt.com/images/2025/05/03/multimedia/03biz-berkshire-file-ckmj/03biz-berkshire-file-ckmj-articleLarge.jpg"
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
        message = TextMessage(
            text="請輸入：文字、貼圖、圖片、影片 或 位置資訊 來測試不同回覆。"
        )

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
