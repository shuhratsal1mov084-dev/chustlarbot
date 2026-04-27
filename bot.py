import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import BOT_TOKEN, ADMIN_ID, WEBAPP_URL
from db import db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class AddPlayerStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_text = State()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    players = db.get_players()
    
    if not players:
        await message.answer(
            "🎮 No players available yet.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🎮 Open Admin Panel",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )]
                ]
            )
        )
        return
    
    keyboard_buttons = [
        [InlineKeyboardButton(text=player["name"], callback_data=f"player_{player['id']}")]
        for player in players
    ]
    
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🎮 Open Admin Panel",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ])
    
    await message.answer(
        "🎮 Select a player:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    )


@dp.callback_query(F.data.startswith("player_"))
async def player_callback(query: types.CallbackQuery):
    player_id = int(query.data.split("_")[1])
    player = db.get_player_by_id(player_id)
    
    if not player:
        await query.answer("Player not found", show_alert=True)
        return
    
    await query.answer()
    await query.message.answer(
        f"🎮 <b>{player['name']}</b>\n\n{player['text']}",
        parse_mode="HTML"
    )


@dp.message(Command("add"))
async def add_player_handler(message: types.Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Unauthorized")
        return
    
    if not command.args:
        await message.answer("Usage: /add Name|Text")
        return
    
    try:
        parts = command.args.split("|")
        if len(parts) != 2:
            await message.answer("Usage: /add Name|Text")
            return
        
        name = parts[0].strip()
        text = parts[1].strip()
        
        if not name or not text:
            await message.answer("Name and text cannot be empty")
            return
        
        success = db.add_player(name, text)
        if success:
            await message.answer(f"✅ Player '{name}' added successfully")
        else:
            await message.answer(f"❌ Player '{name}' already exists")
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


@dp.message(Command("del"))
async def delete_player_handler(message: types.Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Unauthorized")
        return
    
    if not command.args:
        await message.answer("Usage: /del ID")
        return
    
    try:
        player_id = int(command.args.strip())
        success = db.delete_player(player_id)
        if success:
            await message.answer(f"✅ Player {player_id} deleted successfully")
        else:
            await message.answer(f"❌ Player {player_id} not found")
    except ValueError:
        await message.answer("❌ Invalid player ID")
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


@dp.message()
async def unknown_handler(message: types.Message):
    await message.answer(
        "❌ Unknown command. Use /start to see available commands."
    )


async def main():
    print("🤖 Bot is starting...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
