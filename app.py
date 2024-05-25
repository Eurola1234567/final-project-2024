from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import csv

app = Flask(__name__)

# 設置 Line Bot 的 Channel access token 和 Channel secret
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    user_request = user_input.split(' ', 1)
    
    if len(user_request) < 2:
        reply_message = "請輸入有效的格式，例如：「1 實習」"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        return
    
    category = user_request[1]
    
    # 讀取 CSV 檔案
    with open('your_data.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # 篩選出符合使用者輸入的資料
        filtered_data = [row for row in reader if category in row['category']]
    
    if filtered_data:
        reply_message = "\n".join([f"{data['title']}: {data['description']}" for data in filtered_data])
    else:
        reply_message = f"抱歉，找不到符合「{category}」的資料。"
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

if __name__ == "__main__":
    app.run()
