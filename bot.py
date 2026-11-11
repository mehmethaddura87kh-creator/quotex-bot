import threading
import time
import numpy as np
import pandas as pd
import telebot
from telebot import types
import yfinance as yf

# توكن البوت الخاص بك المحدث
TOKEN = "9060288987:AAFyt6lLCiB0weCBM7z-yS_CMA6isY9lGGk"

# الـ Chat ID الخاص بك
CHAT_ID = "5088345567"

bot = telebot.TeleBot(TOKEN)


# 1. استقبال أمر /start والأزرار التفاعلية
@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = types.InlineKeyboardMarkup(row_width=2)
  btn_status = types.InlineKeyboardButton(
      "📊 حالة السوق الرسمي", callback_data="status"
  )
  btn_help = types.InlineKeyboardButton("⚙️ تعليمات", callback_data="help")
  markup.add(btn_status, btn_help)

  bot.reply_to(
      message,
      "🚀 **أهلاً بك يا محمد في نظام تتبع السوق الرسمي الشامل لمنصة Quotex!**\n\n"
      "✅ تم تفعيل مراقبة **جميع أزواج العملات الرسمية** في الخلفية 24/7.",
      reply_markup=markup,
      parse_mode="Markdown",
  )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  if call.data == "status":
    bot.answer_callback_query(call.id, "النظام يعمل بكفاءة عالية على السحابة")
    bot.send_message(
        call.message.chat.id,
        "🟢 يتم الآن فحص جميع أزواج السوق الرسمي ومؤشراتها باستمرار.",
    )
  elif call.data == "help":
    bot.answer_callback_query(call.id, "قسم المساعدة")
    bot.send_message(
        call.message.chat.id,
        "💡 يراقب هذا البوت جميع أزواج العملات الرئيسية والمهجنة في السوق الرسمي"
        " ويرسل إشارات الفئة الأولى (Tier 1).",
    )


# 2. دالة فحص جميع أزواج السوق الرسمي والتحقق من المؤشرات
def market_scanner():
  # قائمة شاملة بجميع أزواج العملات الرئيسية والمهجنة في السوق الرسمي (Forex)
  symbols = [
      "EURUSD=X",
      "GBPUSD=X",
      "USDJPY=X",
      "AUDUSD=X",
      "USDCAD=X",
      "NZDUSD=X",
      "USDCHF=X",
      "GBPJPY=X",
      "EURJPY=X",
      "AUDJPY=X",
      "EURGBP=X",
      "EURAUD=X",
      "GBPAUD=X",
      "CADJPY=X",
      "CHFJPY=X",
      "NZDJPY=X",
      "EURNZD=X",
      "GBPNZD=X",
  ]

  while True:
    try:
      print("جاري فحص جميع أزواج السوق الرسمي...")

      for symbol in symbols:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)

        if len(data) > 15:
          close_prices = data["Close"].squeeze()

          # حساب مؤشر القوة النسبية RSI (14)
          delta = close_prices.diff()
          gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
          loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
          rs = gain / loss
          rsi = 100 - (100 / (1 + rs))

          current_rsi = rsi.iloc[-1]
          current_price = close_prices.iloc[-1]
          clean_symbol = symbol.replace("=X", "")

          print(
              f"الزوج: {clean_symbol} | السعر: {current_price:.4f} | RSI:"
              f" {current_rsi:.2f}"
          )

          # شرط إرسال الإشارة استناداً للتشبع البيعي أو الشرائي
          if current_rsi < 30 or current_rsi > 70:
            action = (
                "🟢 شراء / صعود (BUY / CALL)"
                if current_rsi < 30
                else "🔴 بيع / هبوط (SELL / PUT)"
            )

            signal_text = (
                f"🚀 **#{clean_symbol}** (السوق الرسمي - Quotex)\n\n"
                f"🔥 **التصنيف:** الفئة الأولى (Tier 1 - أعلى نسبة نجاح)\n"
                f"📊 **Action:** {action}\n"
                f"⏳ **المدة:** 5 Minute(s) (Expiry)\n"
                f"🎯 **Entry Price:** {current_price:.4f}\n"
                f"📈 **RSI Value:** {current_rsi:.2f}\n"
                f"📰 **حالة السوق:** مستقر ومراقب رسمياً.\n"
            )

            # زر تفاعلي لفتح المنصة مباشرة
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "📈 فتح منصة Quotex للتنفيذ",
                    url="https://quotex.com",
                )
            )

            # إرسال الإشارة إلى هاتفك حصرياً
            bot.send_message(
                CHAT_ID, signal_text, reply_markup=markup, parse_mode="Markdown"
            )

      # استراحة قصيرة بين دورات فحص الأزواج كاملة
      time.sleep(120)

    except Exception as e:
      print(f"حدث خطأ أثناء فحص السوق: {e}")
      time.sleep(60)


if __name__ == "__main__":
  # تشغيل المسح بالتوازي مع استقبال الأوامر لضمان عدم تجميد البوت
  scanner_thread = threading.Thread(target=market_scanner, daemon=True)
  scanner_thread.start()

  print("البوت يعمل الآن ويراقب جميع أزواج السوق الرسمي...")
  bot.infinity_polling(none_stop=True)
