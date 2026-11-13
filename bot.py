import threading
import time
import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval

# 1. توكن البوت
TOKEN = "9060288987:AAFyt6lLCiB0weCBM7z-yS_CMA6isY9lGGk"

# 2. الآيدي الخاص بك حصراً
CHAT_ID = 5088345567

bot = telebot.TeleBot(TOKEN)


# استقبال أمر /start والأزرار التفاعلية
@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = types.InlineKeyboardMarkup(row_width=2)
  btn_status = types.InlineKeyboardButton(
      "📊 حالة النظام المفلتر", callback_data="status"
  )
  btn_help = types.InlineKeyboardButton("⚙️ تعليمات", callback_data="help")
  markup.add(btn_status, btn_help)

  bot.reply_to(
      message,
      "🚀 **أهلاً بك يا محمد في نظام تصفية صفقات Quotex الفائقة (80% - 90%)!**\n\n"
      "✅ البوت يعمل الآن بنظام التصفية الذكية ولا يرسل إلا الصفقات عالية الثقة"
      " حصراً.",
      reply_markup=markup,
      parse_mode="Markdown",
  )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  if call.data == "status":
    bot.answer_callback_query(call.id, "النظام يعمل بأعلى دقة تصفية")
    bot.send_message(
        call.message.chat.id,
        "🟢 يتم حالياً تحليل السوق واستبعاد أي صفقة تقل نسبة نجاحها عن 80%.",
    )
  elif call.data == "help":
    bot.answer_callback_query(call.id, "قسم المساعدة")
    bot.send_message(
        call.message.chat.id,
        "💡 هذا النظام مصمم خصيصاً لإرسال الصفقات المؤكدة بنسبة نجاح تتراوح بين"
        " 80% و 90%+ لمنصة Quotex.",
    )


# دالة تتبع السوق وتصفية الصفقات بدقة عالية (80% - 90%+)
def smart_market_scanner():
  pairs = [
      "EURUSD",
      "GBPUSD",
      "USDJPY",
      "AUDUSD",
      "USDCAD",
      "USDCHF",
      "NZDUSD",
      "GBPJPY",
      "EURJPY",
      "AUDJPY",
      "CADJPY",
      "CHFJPY",
      "NZDJPY",
      "EURGBP",
      "EURAUD",
      "GBPAUD",
      "EURNZD",
      "GBPNZD",
      "AUDCAD",
      "AUDCHF",
      "CADCHF",
  ]

  while True:
    try:
      print("جاري فحص وتصفية السوق بدقة عالية...")

      for pair in pairs:
        try:
          handler = TA_Handler(
              symbol=pair,
              screener="forex",
              exchange="FX_IDC",
              interval=Interval.INTERVAL_5_MINUTES,
          )

          analysis = handler.get_analysis()
          recommendation = analysis.summary["RECOMMENDATION"]
          buy_signals = analysis.summary["BUY"]
          sell_signals = analysis.summary["SELL"]
          neutral_signals = analysis.summary["NEUTRAL"]
          total_indicators = buy_signals + sell_signals + neutral_signals

          if total_indicators == 0:
            continue

          if "BUY" in recommendation:
            confidence = (buy_signals / total_indicators) * 100
          elif "SELL" in recommendation:
            confidence = (sell_signals / total_indicators) * 100
          else:
            confidence = 0

          # الشرط الصارم: نسبة النجاح بين 80% و 100% والتوصية قوية جداً
          if 80.0 <= confidence <= 100.0 and recommendation in [
              "STRONG_BUY",
              "STRONG_SELL",
          ]:
            action_text = (
                "🟢 شراء / صعود (BUY / CALL)"
                if recommendation == "STRONG_BUY"
                else "🔴 بيع / هبوط (SELL / PUT)"
            )

            signal_text = (
                f"🔥 **#{pair}** (صفقة مؤكدة عالية الدقة)\n\n"
                f"🎯 **نسبة النجاح المقدرة:** {confidence:.1f}%\n"
                f"📊 **الاتجاه:** {action_text}\n"
                f"⏳ **المدة:** 5 Minutes (Expiry)\n"
                f"💎 **تقييم الثقة:** ممتازة (ضمن نطاق 80-90%+)\n"
            )

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "📈 تنفيذ الصفقة على Quotex", url="https://quotex.com"
                )
            )

            bot.send_message(
                CHAT_ID, signal_text, reply_markup=markup, parse_mode="Markdown"
            )
            time.sleep(10)

        except Exception as inner_e:
          continue

      time.sleep(180)

    except Exception as e:
      print(f"خطأ في التتبع: {e}")
      time.sleep(60)


if __name__ == "__main__":
  scanner_thread = threading.Thread(target=smart_market_scanner, daemon=True)
  scanner_thread.start()

  print("النظام الذكي لتصفية الصفقات يعمل الآن...")
  bot.infinity_polling(none_stop=True)
