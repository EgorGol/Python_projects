from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import TelegramBot_TOKEN
from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

# подключаемся к chatGPT
chat_gpt = ChatGptService(ChatGPT_TOKEN)

# создаем объект приложения для взаимодействия с ботом
app = ApplicationBuilder()\
    .token(TelegramBot_TOKEN)\
    .build()

# создаем объект фактически пустого класса с заглушкой, который позволяет нам иметь глобальную переменную.
dialog = Dialog()
dialog.mode = None
dialog.right_answers = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'start'
    text = load_message('start')
    await send_image(update, context, 'start')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
        # Добавить команду в меню можно так:
        # 'command': 'button text'
    })


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка и рапределение сообщений пользователя
    :param update:
    :param context:
    :return: None
    """
    if dialog.mode is None:
        await start(update, context)
    elif dialog.mode == 'gpt':
        await gpt_ask(update, context)
    elif dialog.mode == 'talk':
        await talk(update, context)
    elif dialog.mode == 'quiz':
        await quiz(update, context)
    else:
        await start(update, context)


async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /random и отправка в качестве ответа рандомного факта сгенерированного чатом GPT
    :param update:
    :param context:
    :return: None
    """
    # оправляем картинку и текст с реакцией на команду
    prompt = load_prompt('random')
    message = load_message('random')
    await send_image(update, context, 'random')
    message = await send_text(update, context, message)

    # оправляем ответ чата GPT, исправляя предыдущее сообщение
    gpt_reply = await chat_gpt.send_question(prompt, '')
    await message.edit_text(gpt_reply)


async def gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция отсылает пользователю картинку и сообщение с просьбой ввести свой вопрос к GPT
    :param update:
    :param context:
    :return: None
    """
    dialog.mode = 'gpt'
    message = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)


async def gpt_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text  # принимает сообщение пользователя
    prompt = load_prompt('gpt')  # подсказка для чата GPT
    gpt_reply = await chat_gpt.send_question(prompt, user_text)
    await send_text(update, context, gpt_reply)  # отсылает ответ GPT в чат


async def talk_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки команды /talk
    :param update:
    :param context:
    :return: None
    """
    dialog.mode = 'talk'
    message = load_message('talk')
    companions = {
        'talk_to_cobain': 'Курт Кобейн 🎸',
        'talk_to_queen': 'Елизавета II 👑',
        'talk_to_tolkien': 'Джон Толкиен 📖',
        'talk_to_nietzsche': 'Фридрих Ницше 🧠',
        'talk_to_hawking': 'Стивен Хокинг 🔬',
    }
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, companions)

async def talk_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки кнопок в режиме talk
    :param update:
    :param context:
    :return:
    """
    await update.callback_query.answer()
    button = update.callback_query.data
    chat_gpt.set_prompt(button)  # подсказка для чата GPT
    await send_image(update, context, button)
    message = 'Контакст с личностью установлен. Напиши что-нибудь, чтобы начать диалог'
    await send_text(update, context, message)  # отсылает ответ GPT в чат


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для общения пользователя с чатом GPT в режиме talk (после выбора собеседника)
    :param update:
    :param context:
    :return:
    """
    user_text = update.message.text  # принимает сообщение пользователя
    prompt = load_prompt('gpt')  # подсказка для чата GPT
    gpt_reply = await chat_gpt.add_message(user_text)
    await send_text(update, context, gpt_reply)  # отсылает ответ GPT в чат

async def quiz_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки команды /quiz
    :param update:
    :param context:
    :return: None
    """
    dialog.mode = 'quiz'
    dialog.right_answers = 0
    message = load_message('quiz')
    topics = {
        'quiz_prog': 'Программирование (Python)',
        'quiz_math': 'Математика',
        'quiz_biology': 'Биология',
    }
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, topics)


async def quiz_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для обработки кнопок в режиме quiz
    :param update:
    :param context:
    :return:
    """
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'quiz_more':
        question = await chat_gpt.add_message(f'Следующий вопрос {button}?')
        await send_text(update, context, question)  # отсылает ответ GPT в чат
    else:
        question = await chat_gpt.send_question('quiz', f'Я выбираю эту тему {button}. Задавай вопрос?')
        await send_text(update, context, question)  # отсылает ответ GPT в чат

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для общения пользователя с чатом GPT в режиме quiz (после выбора темы)
    :param update:
    :param context:
    :return:
    """
    user_text = update.message.text  # принимает сообщение пользователя
    one_more_question = 'Для получения следующего вопроса нажмите кнопку'
    gpt_reply = await chat_gpt.add_message(user_text)
    if 'Правильно' in gpt_reply or 'Верно' in gpt_reply:
        dialog.right_answers += 1
    await send_text(update, context, gpt_reply)  # отсылает ответ GPT в чат
    await send_text(update, context, f'Количество правильных ответов - {dialog.right_answers}')
    await send_text_buttons(update, context, one_more_question, {'quiz_more':'Давай следующий вопрос'})

# вывод меню с основными командами
app.add_handler(CommandHandler('start', start))

# ЗАДАЧА 1. Создание обработчика сообщений пользователя
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# ЗАДАЧА 2. Создание обработчика команды /random, для генерации рандомных фактов
app.add_handler(CommandHandler('random', random_fact))

# ЗАДАЧА 3. Создание обработчика команды /gpt, для общения с chat GPT
app.add_handler(CommandHandler('gpt', gpt_mode))

# ЗАДАЧА 4. Создание обработчика команды /talk, для общения с chat GPT
app.add_handler(CommandHandler('talk', talk_mode))

# Задача 4. Обработчик кнопок для режима talk
app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_to_.*'))

# ЗАДАЧА 5. Создание обработчика команды /quiz, для общения с chat GPT
app.add_handler(CommandHandler('quiz', quiz_mode))

# Задача 5. Обработчик кнопок для режима quiz
app.add_handler(CallbackQueryHandler(quiz_buttons, pattern='^quiz_.*'))
'''
каманда add_handler добавляет новый обработчик:
MessageHandler - обрабатывает все текстовые сообщения, которые приходят в бот.
    - filters - указываем формат сообщений, которые будут обрабатываться.
    - второй аргумент - коррутина, которая будет выполняться после получении сообщения.
    коррутина должна обязательно принимать 2 аргумента (update: Update, context: ContextTypes.DEFAUL_TYPE)
CommandHandler - обрабатывает команды
CallbackQueryHandler -обрабатывает нажатия на кнопки.
'''

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
# app.add_handler(CallbackQueryHandler(default_callback_handler))

# Метод, отвечающий за поддержание работы бота
app.run_polling()
