# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import settings
import telebot
from telebot.types import (ReplyKeyboardMarkup,
                           ReplyKeyboardRemove,
                           KeyboardButton,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)


USER_REPLIES = {}
MSGS_DB = {}


bot = telebot.TeleBot(settings.BOT_TOKEN, parse_mode='HTML')


def initial_markup():
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton(settings.BTN_SUGGEST_POST),
               KeyboardButton(settings.BTN_FEEDBACK))
    return markup


def cancel_markup():
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton(settings.BTN_CANCEL))
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "<b>👋 Добро пожаловать в предложку!</b>\n\n"
                     "Этот бот поможет предложить пост в канал, а также связаться с админами.\n"
                     "Пропала клавиатура? Напиши /start.", reply_markup=initial_markup())


# Suggestions

@bot.message_handler(func=lambda message: settings.BTN_SUGGEST_POST in message.text)
def suggest_post_step_one(message):
    msg = bot.send_message(message.from_user.id, "<b>Пришли мне пост, который ты хочешь отправить</b>\n\n"
                           "Пост должен соответствовать правилам. По умолчанию посты анонимные. "
                           "Если желаешь, можешь оставить свой @ник в тексте поста.", reply_markup=cancel_markup())
    bot.register_next_step_handler(msg, suggest_post_step_two)


def suggest_post_step_two(message):
    if message.text == settings.BTN_CANCEL:
        bot.send_message(message.from_user.id, "<b>Создание поста отменено.</b>\n\n",
                         reply_markup=initial_markup())
        return

    for admin_id in settings.ADMINS:

        fw_msg = bot.forward_message(
            admin_id, message.from_user.id, message.id)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('✅ Запостить в канал', callback_data=f'post-{fw_msg.id}-{message.from_user.id}'),
        )

        bot.send_message(admin_id, f"{message.from_user.full_name} прислал пост. Запостить его в канал сейчас?",
                         reply_markup=markup)

        MSGS_DB[str(fw_msg.id)] = fw_msg.text or fw_msg.caption or ''

    bot.send_message(message.from_user.id, "<b>✅ Пост отправлен на проверку.</b>\n\n"
                     "Я пришлю уведомление, когда его опубликуют.",
                     reply_markup=initial_markup())


# Feedback

@bot.message_handler(func=lambda message: settings.BTN_FEEDBACK in message.text)
def feedback_step_one(message):
    msg = bot.send_message(
        message.from_user.id, "<b>Напиши сообщение админам и я перешлю его.</b>\n\n",
        reply_markup=cancel_markup())
    bot.register_next_step_handler(msg, feedback_step_two)


def feedback_step_two(message):
    if message.text == settings.BTN_CANCEL:
        bot.send_message(message.from_user.id, "<b>Ок, как хочешь.</b>\n\n",
                         reply_markup=initial_markup())
        return

    for admin_id in settings.ADMINS:

        bot.forward_message(admin_id, message.from_user.id, message.id)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('💬 Ответить', callback_data=f'fb-{message.id}-{message.from_user.id}'),
        )

        bot.send_message(admin_id, f"{message.from_user.full_name} прислал отзыв. Нажми кнопку ниже, чтобы ответить...",
                         reply_markup=markup)

    bot.send_message(message.from_user.id, "<b>✅ Сообщение отправлено!</b>\n\n"
                     "Я пришлю ответ, как только он появится.",
                     reply_markup=initial_markup())


def feedback_step_reply(message):
    if message.text == settings.BTN_CANCEL:
        USER_REPLIES.pop(message.from_user.id)
        bot.send_message(message.from_user.id, "<b>Ок, как хочешь.</b>\n\n",
                         reply_markup=initial_markup())
        return

    bot.send_message(USER_REPLIES[message.from_user.id][1], '<i>Пришёл ответ</i>\n\n' + message.text,
                     reply_to_message_id=USER_REPLIES[message.from_user.id][0])

    bot.send_message(message.from_user.id, "<b>Готово</b>\n\n",
                     reply_markup=ReplyKeyboardRemove())

    USER_REPLIES.pop(message.from_user.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global MSGS_DB, USER_REPLIES

    if not call.from_user.id in settings.ADMINS:
        return

    data = call.data.split('-')
    if data[0] == "post":
        bot.answer_callback_query(call.id, "Отправлено!")
        ch_msg = bot.copy_message(
            settings.CHANNEL_ID, call.from_user.id, data[1])
        if data[1] in MSGS_DB:
            cp = MSGS_DB[data[1]]
            try:
                bot.edit_message_caption(
                    cp+settings.ADDED_CAPTION, settings.CHANNEL_ID, ch_msg.message_id)
            except Exception:
                bot.edit_message_text(
                    cp+settings.ADDED_CAPTION, settings.CHANNEL_ID, ch_msg.message_id, disable_web_page_preview=True)
            MSGS_DB.pop(data[1])
        bot.send_message(data[2],
                         f"<b>🎉 <a href='http://t.me/c/{settings.CHANNEL_ID*-1}/{ch_msg.message_id}'>Твой пост</a> только что опубликовали!</b>\n\n")

    elif data[0] == "fb":
        bot.answer_callback_query(call.id, "Пиши ответ")
        msg = bot.send_message(call.from_user.id, "<b>Напиши ответ пользователю (только текст)</b>\n\n",
                               reply_markup=cancel_markup())
        USER_REPLIES[call.from_user.id] = [data[1], data[2]]
        bot.register_next_step_handler(msg, feedback_step_reply)

# Bootstrap


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
