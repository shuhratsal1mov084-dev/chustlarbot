import json
import asyncio
from flask import Flask, render_template, request, redirect
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import cloudinary
import cloudinary.uploader

# ================= CONFIG =================
TOKEN = "8649118325:AAHAhci1MpQKLDfSfQxq6lvrDUM06h4H8jo"

# Cloudinary config (ro'yxatdan olasan)
cloudinary.config(
    cloud_name="CLOUD_NAME",
    api_key="API_KEY",
    api_secret="API_SECRET"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = Flask(__name__)

# ================= JSON =================
def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# ================= BOT =================
@dp.message(Command("start"))
async def start(msg: types.Message):
    data = load_data()

    if not data:
        await msg.answer("Hozircha chust yo'q 😢")
        return

    text = "🎮 Playerlar:\n"
    for p in data:
        text += f"- {p['name']}\n"

    await msg.answer(text)

@dp.message()
async def send_player(msg: types.Message):
    data = load_data()

    for p in data:
        if msg.text == p["name"]:
            await msg.answer_photo(p["image"], caption=p["text"])

# ================= WEB =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    data = load_data()

    if request.method == "POST":
        file = request.files["image"]

        # Cloudinaryga yuklash
        result = cloudinary.uploader.upload(file)
        image_url = result["secure_url"]

        new = {
            "name": request.form["name"],
            "image": image_url,
            "text": request.form["text"]
        }

        data.append(new)
        save_data(data)

        return redirect("/admin")

    return render_template("admin.html", data=data)

@app.route("/delete/<name>")
def delete(name):
    data = load_data()
    data = [p for p in data if p["name"] != name]
    save_data(data)
    return redirect("/admin")

# ================= RUN =================
async def start_bot():
    await dp.start_polling(bot)

def run_all():
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    run_all()
