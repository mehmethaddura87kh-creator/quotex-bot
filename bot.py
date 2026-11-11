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
      "📊 حالة تتبع السوق الشامل", callback_data="status"
  )
  btn_help = types.InlineKeyboardButton("⚙️ تعليمات", callback_data="help")
  markup.add(btn_status, btn_help)

  bot.reply_to(
      message,
      "🚀 **أهلاً بك يا محمد في نظام تتبع السوق العالمي المباشر عبر TradingView!**\n\n"
      "✅ يتم الآن فحص **جميع الأزواج العالمية** ومؤشرات TradingView المباشرة 24/7.",
      reply_markup=markup,
      parse_mode="Markdown",
  )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  if call.data == "status":
    bot.answer_callback_query(call.id, "النظام يعمل ومتصل بـ TradingView")
    bot.send_message(
        call.message.chat.id,
        "🟢 يتم فحص كافة الأزواج العالمية الرسمية استناداً إلى التحليل الفني"
        " المباشر.",
    )
  elif call.data == "help":
    bot.answer_callback_query(call.id, "قسم المساعدة")
    bot.send_message(
        call.message.chat.id,
        "💡 يتتبع هذا البوت جميع الأزواج العالمية ويصفي الإشارات بحيث لا يرسل"
        " إلا صفقات التوافق القوي بنسبة 80% فما فوق.",
    )


# دالة تتبع حركة السوق الشاملة عبر TradingView
def tradingview_scanner():
  # قائمة شاملة بجميع الأزواج العالمية (الرئيسية، المهجنة، والتقاطعات)
  pairs = [
      # الأزواج الرئيسية (Majors)
      "EURUSD",
      "GBPUSD",
      "USDJPY",
      "AUDUSD",
      "USDCAD",
      "USDCHF",
      "NZDUSD",
      # أزواج الين الياباني (Yen Crosses)
      "GBPJPY",
      "EURJPY",
      "AUDJPY",
      "CADJPY",
      "CHFJPY",
      "NZDJPY",
      # الأزواج التقاطعية والمهجنة الأخرى (Crosses)
      "EURGBP",
      "EURAUD",
      "GBPAUD",
      "EURNZD",
      "GBPNZD",
      "EURNZD",
      "AUDCAD",
      "AUDCHF",
      "AUDNZD",
      "CADCHF",
      "EURNZD",
      "GBPCAD",
      "GBPCHF",
      "NZDCAD",
      "NZDCHF",
  ]

  while True:
    try:
      print("جاري فحص جميع الأزواج العالمية من TradingView...")

      for pair in pairs:
        try:
          # فحص الزوج على فريم الـ 5 دقائق
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

          # حساب نسبة الثقة أو التوافق
          if "BUY" in recommendation and total_indicators > 0:
            confidence = (buy_signals / total_indicators) * 100
          elif "SELL" in recommendation and total_indicators > 0:
            confidence = (sell_signals / total_indicators) * 100
          else:
            confidence = 0

          # الشرط: توصية قوية (Strong) + نسبة نجاح/ثقة 80% فما فوق
          if confidence >= 80.0 and recommendation in [
              "STRONG_BUY",
              "STRONG_SELL",
          ]:
            action_text = (
                "🟢 شراء / صعود (BUY / CALL)"
                if recommendation == "STRONG_BUY"
                else "🔴 بيع / هبوط (SELL / PUT)"
            )

            signal_text = (
                f"🚀 **#{pair}** (تتبع TradingView الشامل)\n\n"
                f"🔥 **قوة الإشارة:** {confidence:.1f}% (نسبة عالية 80%+)\n"
                f"📊 **الاتجاه:** {action_text}\n"
                f"⏳ **المدة:** 5 Minutes (Expiry)\n"
                f"📰 **تقييم TradingView:** {recommendation}\n"
            )

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "📈 فتح منصة Quotex للتنفيذ", url="https://quotex.com"
                )
            )

            # إرسال الإشارة لك حصرياً على الخاص
            bot.send_message(
                CHAT_ID, signal_text, reply_markup=markup, parse_mode="Markdown"
            )

        except Exception as inner_e:
          # تخطي الزوج الحالي في حال حدث خطأ مؤقت في جلب بياناته والانتقال لغيره
          continue

      # استراحة قصيرة بين الدورات الشاملة
      time.sleep(120)

    except Exception as e:
      print(f"خطأ عام أثناء فحص السوق: {e}")
      time.sleep(60)


if __name__ == "__main__":
  # تشغيل التتبع بالتوازي مع البوت
  scanner_thread = threading.Thread(target=tradingview_scanner, daemon=True)
  scanner_thread.start()

  print("البوت يعمل الآن ويتتبع كافة الأزواج العالمية...")
  bot.infinity_polling(none_stop=True)
