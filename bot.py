#from keys import TOKEN , PAYMENT_TOKEN
from telegram import Update, LabeledPrice
import requests
from datetime import datetime
import base64
import hashlib
import re
from telegram.ext import ApplicationBuilder, filters,ContextTypes,CommandHandler,MessageHandler,PreCheckoutQueryHandler
TOKEN = "7230204547:AAEcDzkQbN6ckLED2idFEsuKS181O6tDXeY"


base_url = "http://127.0.0.1:5000/"
PAYMENT_TOKEN = "284685063:TEST:NWMyMTA3ZTI1YmJk"

def generate_signature():
    timestamp = str(datetime.utcnow().timestamp())
    code = hashlib.sha256((timestamp + SECRET_CODE).encode()).digest()
    encoded_code = base64.urlsafe_b64encode(code).decode().rstrip("=")
    return timestamp, encoded_code

async def help_comand(update: Update, context: ContextTypes.DEFAULT_TYPE ):

    username = update.message.from_user.username
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hi, i am link shortening bot. To start click on /start"                         
        )

async def start_comand(update: Update, context: ContextTypes.DEFAULT_TYPE ):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="To short the link, please send me the link "                          
        )

async def short_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    #r = requests.get(base_url, prams ={"text": mes_text} )
    #await context.bot.send_message(chat_id=update.effective_chat.id, text=r)
    mes_text = update.message.text
    username = update.message.from_user.first_name
    first_name = update.message.from_user.first_name
    chat_id = update.message.from_user.id

    try:
        pattern = re.compile(
            r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
        )
        matches = re.findall(pattern, mes_text)
        if matches:
            for link in matches:
                payload = {
                    "link":link,
                    "username":username,
                    "first_name":first_name,
                    "chat_id":chat_id
                }
                r = requests.get(base_url + "short", params = payload)
                # http is success when = 200
                if r.status_code == 200:
                    result = r.json()
                    if result.get('status') == "success":
                        #send msg to user with link 
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"Here is short link: {result.get('shorted_link')}"
                        )
                    else:
                        #send msg falaid    
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="sorry you exhausted all of your free trials. please /subscribe to continue using our service "
                        ) 
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="sorry, something  wrong "
                    ) 
        else:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, The message does not contain a link ")
            #await context.bot.send_message(chat_id=chat_id, text= update)
    except:
        await context.bot.send_message(chat_id=chat_id, text="Sorry, no parse the link")

async def sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    r = requests.get(base_url+"cheek_user",params={"chat_id":chat_id} )
    if r.text == "trial":
        title = "unlimited subscription"
        description = "subscribe to short unlimited number of links"
        payload = "Super secret"
        currency = "EGP"
        price = 3
        prices = [LabeledPrice("Unlimited", price * 400 ), LabeledPrice("for month", price*100)]
        await context.bot.send_invoice(
            chat_id,
            title,
            description,
            payload,
            PAYMENT_TOKEN,
            currency,
            prices,
            need_name=True
        )
    else:
        await update.message.reply_text("You are already subscribed", quote=True)

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "SuperSecret":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = {
        "user_id": update.message.from_user.id,
        "first_name": update.message.from_user.first_name,
    }
    timestamp, token = generate_signature()
    headers = {"timestamp": timestamp, "token": token}
    r = requests.get(base_url + "sub", params=payload, headers=headers)
    if r.ok:
        await update.message.reply_text("Thank you for your payment")


if __name__=="__main__" :
    app = ApplicationBuilder().token(TOKEN).build()


    #create commande handler 
    help_handler = CommandHandler('help', help_comand)
    sub_handler = CommandHandler('subscribe', sub_callback)
    start_handler = CommandHandler('start', start_comand)
    Mes_handler = MessageHandler(filters.TEXT, short_link)
    



    #create registeres commande 
    app.add_handler(help_handler)
    app.add_handler(sub_handler)
    app.add_handler(start_handler)
    app.add_handler(Mes_handler)
    


    app.run_polling()
