# MyGo LINE Bot

一個基於 Flask 與 LINE Messaging API v3 的聊天機器人範例，支援多種回覆類型：文字、貼圖、圖片、影片、位置資訊，以及自訂的「MyGo 動漫圖」搜尋功能。


## 功能介紹

- **文字回覆**：輸入 `文字`，機器人回覆一段文字訊息。
- **貼圖回覆**：輸入 `貼圖`，機器人回覆範例貼圖（package_id=1, sticker_id=1）。
- **圖片回覆**：輸入 `圖片`，機器人發送預先設定的靜態圖片。
- **影片回覆**：輸入 `影片`，機器人發送影片（mp4）以及縮圖。
- **位置資訊**：輸入 `位置資訊`，機器人回傳台北 101 的地理位置（經緯度+地址）。
- **MyGo 圖片搜尋**：輸入 `mygo:<關鍵字>`，透過自訂工具 `MyGoImage` 查詢資料庫並回傳對應圖片網址；若搜尋不到，回覆「找不到圖片wwwwwwwww」。
- **預設回覆**：其他輸入皆引導用戶輸入上述關鍵字以測試不同回覆類型。

## deployed on render
it will redeploy on every push to main branch

## run locally
1. clone the repo
2. create a virtual environment
```bash
python3 -m venv venv
```
3. activate the virtual environment
```bash
source venv/bin/activate
```
4. install the requirements
```bash
pip install -r requirements.txt
```
5. run the app
```bash
gunicorn main:app
```

or 
```bash
python main.py
```

## ran tests

## Reference

- [MyGo Line bot project](https://hackmd.io/@StevenShih-0402/mygorobot)
- [line login](https://developers.line.biz/console/)
- [Render](https://dashboard.render.com/)