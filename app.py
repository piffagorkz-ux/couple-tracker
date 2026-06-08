from datetime import date, datetime, timedelta
from functools import wraps
import os
import random

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from config import config
from models import (
    Activity,
    Couple,
    CoupleInvitation,
    DailyPromptResponse,
    DatePlan,
    Goal,
    ImportantDate,
    Notification,
    Place,
    User,
    Wish,
    db,
)

load_dotenv()

DAILY_QUESTIONS = [
    {"en": "What is one small thing your partner did recently that made you feel loved?", "ru": "Какой маленький поступок партнера недавно заставил тебя почувствовать любовь?"},
    {"en": "What do you want more of in your relationship this week?", "ru": "Чего тебе хочется больше в ваших отношениях на этой неделе?"},
    {"en": "What memory with your partner still makes you smile?", "ru": "Какое воспоминание с партнером до сих пор вызывает у тебя улыбку?"},
    {"en": "What would make today feel special for the two of you?", "ru": "Что сделало бы сегодняшний день особенным для вас двоих?"},
    {"en": "What quality of your partner do you admire most right now?", "ru": "Какое качество партнера ты сейчас особенно ценишь?"},
    {"en": "What do you want to thank your partner for today?", "ru": "За что ты хочешь поблагодарить партнера сегодня?"},
    {"en": "How can your partner support you best today?", "ru": "Как партнер может лучше всего поддержать тебя сегодня?"},
    {"en": "What date idea would you love to try soon?", "ru": "Какую идею для свидания тебе хочется попробовать в ближайшее время?"},
    {"en": "What helps you feel emotionally close to your partner?", "ru": "Что помогает тебе чувствовать эмоциональную близость с партнером?"},
    {"en": "What is something new you want to learn about your partner?", "ru": "Что нового тебе хочется узнать о партнере?"},
    {"en": "What song, film, or place reminds you of your relationship?", "ru": "Какая песня, фильм или место напоминают тебе о ваших отношениях?"},
    {"en": "What would you like to improve together this month?", "ru": "Что вам хотелось бы улучшить вместе в этом месяце?"},
]

ACTIVITY_POOL = [
    {"code": "cook_together", "en": "Cook dinner together", "ru": "Приготовить ужин вместе"},
    {"code": "walk_evening", "en": "Go for an evening walk", "ru": "Пойти на вечернюю прогулку"},
    {"code": "movie_night", "en": "Plan a movie night", "ru": "Устроить вечер кино"},
    {"code": "voice_note", "en": "Send a heartfelt voice note", "ru": "Отправить теплое голосовое сообщение"},
    {"code": "tea_talk", "en": "Have tea and talk for 20 minutes", "ru": "Попить чай и поговорить 20 минут"},
    {"code": "mini_gift", "en": "Prepare a tiny surprise gift", "ru": "Подготовить маленький сюрприз"},
    {"code": "photo_memory", "en": "Share a favorite photo together", "ru": "Поделиться любимой совместной фотографией"},
    {"code": "dance_home", "en": "Dance together at home", "ru": "Потанцевать вместе дома"},
    {"code": "phone_free", "en": "Spend 30 minutes without phones", "ru": "Провести 30 минут без телефонов"},
    {"code": "love_message", "en": "Write a sweet message", "ru": "Написать нежное сообщение"},
    {"code": "compliment_three", "en": "Say three genuine compliments", "ru": "Сказать три искренних комплимента"},
    {"code": "shared_breakfast", "en": "Have breakfast together", "ru": "Позавтракать вместе"},
    {"code": "plan_trip", "en": "Dream about a future trip", "ru": "Помечтать о будущем путешествии"},
    {"code": "story_swap", "en": "Tell a childhood story", "ru": "Рассказать историю из детства"},
    {"code": "hug_minute", "en": "Hold a long one-minute hug", "ru": "Обняться на целую минуту"},
    {"code": "wishlist_chat", "en": "Talk about personal wishes", "ru": "Поговорить о личных желаниях"},
    {"code": "sunset_watch", "en": "Watch the sunset together", "ru": "Посмотреть закат вместе"},
    {"code": "music_share", "en": "Share one meaningful song", "ru": "Поделиться значимой песней"},
    {"code": "gratitude_round", "en": "Name one thing you appreciate", "ru": "Назвать то, что ценишь друг в друге"},
    {"code": "deep_question", "en": "Ask one deep question", "ru": "Задать один глубокий вопрос"},
    {"code": "coffee_date", "en": "Make a mini coffee date", "ru": "Устроить маленькое кофейное свидание"},
    {"code": "future_home", "en": "Talk about your dream home", "ru": "Поговорить о доме мечты"},
    {"code": "favorite_food", "en": "Order or cook a favorite dish", "ru": "Заказать или приготовить любимое блюдо"},
    {"code": "memory_lane", "en": "Revisit an old memory together", "ru": "Вспомнить старое совместное воспоминание"},
    {"code": "support_check", "en": "Ask how to support each other", "ru": "Спросить, как лучше поддержать друг друга"},
    {"code": "no_rush_evening", "en": "Slow down for a calm evening", "ru": "Замедлиться и провести спокойный вечер"},
    {"code": "laugh_together", "en": "Watch something funny together", "ru": "Посмотреть что-то смешное вместе"},
    {"code": "dream_list", "en": "Make a list of dreams together", "ru": "Составить список общих мечт"},
    {"code": "bedtime_talk", "en": "Talk before sleep without distractions", "ru": "Поговорить перед сном без отвлечений"},
    {"code": "dessert_moment", "en": "Share a dessert", "ru": "Разделить десерт"},
    {"code": "kind_act", "en": "Do one kind act for your partner", "ru": "Сделать одно доброе дело для партнера"},
    {"code": "mini_workout", "en": "Do a short workout together", "ru": "Сделать короткую тренировку вместе"},
    {"code": "date_plan", "en": "Plan your next date", "ru": "Запланировать следующее свидание"},
    {"code": "photo_walk", "en": "Take a short photo walk", "ru": "Сходить на фотопрогулку"},
    {"code": "memory_box", "en": "Save one memory from today", "ru": "Сохранить одно воспоминание о сегодняшнем дне"},
    {"code": "read_aloud", "en": "Read something aloud to each other", "ru": "Почитать что-то друг другу вслух"},
    {"code": "game_round", "en": "Play one short game together", "ru": "Поиграть в короткую игру вместе"},
    {"code": "kitchen_help", "en": "Help each other with chores", "ru": "Помочь друг другу с делами"},
    {"code": "soft_checkin", "en": "Ask how your partner really feels", "ru": "Спросить, что партнер правда чувствует"},
    {"code": "future_question", "en": "Discuss one future goal", "ru": "Обсудить одну цель на будущее"},
]

EXTRA_DAILY_QUESTIONS = [
    {"en": "What makes you feel safest in this relationship?", "ru": "Что помогает тебе чувствовать себя в безопасности в этих отношениях?"},
    {"en": "What is one habit of your partner that makes your days better?", "ru": "Какая привычка партнера делает твои дни лучше?"},
    {"en": "When did you last feel especially proud of your partner?", "ru": "Когда ты в последний раз особенно гордился или гордилась своим партнером?"},
    {"en": "What kind of support do you need more often from your partner?", "ru": "Какой поддержки тебе хотелось бы чаще от партнера?"},
    {"en": "What simple date would make you happy this week?", "ru": "Какое простое свидание сделало бы тебя счастливее на этой неделе?"},
    {"en": "What part of your relationship feels strongest right now?", "ru": "Какая часть ваших отношений сейчас ощущается самой сильной?"},
    {"en": "What do you miss most when you spend time apart?", "ru": "По чему ты скучаешь больше всего, когда вы не рядом?"},
    {"en": "What helps you calm down after a hard day?", "ru": "Что помогает тебе успокоиться после тяжелого дня?"},
    {"en": "What would you love to celebrate together soon?", "ru": "Что тебе хотелось бы скоро отпраздновать вместе?"},
    {"en": "What was your first impression of your partner?", "ru": "Каким было твое первое впечатление о партнере?"},
    {"en": "What conversation should the two of you make more time for?", "ru": "Для какого разговора вам стоит чаще находить время?"},
    {"en": "What always makes you laugh in your relationship?", "ru": "Что в ваших отношениях почти всегда заставляет тебя смеяться?"},
    {"en": "What would make you feel more seen by your partner today?", "ru": "Что помогло бы тебе сегодня почувствовать больше внимания от партнера?"},
    {"en": "What little ritual would you like to create together?", "ru": "Какой маленький ритуал тебе хотелось бы создать вместе?"},
    {"en": "What is one thing your partner understands about you better than most people?", "ru": "Что партнер понимает в тебе лучше, чем большинство людей?"},
    {"en": "What dream would you like to work toward together?", "ru": "К какой мечте тебе хотелось бы идти вместе?"},
    {"en": "What place would you love to visit together one day?", "ru": "Какое место тебе хотелось бы однажды посетить вместе?"},
    {"en": "What helps you feel closer after a disagreement?", "ru": "Что помогает тебе снова почувствовать близость после ссоры?"},
    {"en": "What do you want your relationship to feel like this summer?", "ru": "Какими тебе хочется ощущать ваши отношения этим летом?"},
    {"en": "What is a tiny act of care you notice and remember?", "ru": "Какой маленький знак заботы ты замечаешь и запоминаешь?"},
    {"en": "What adventure would be fun even if it is a little spontaneous?", "ru": "Какое приключение было бы классным, даже если оно будет немного спонтанным?"},
    {"en": "What part of your everyday life do you most enjoy sharing?", "ru": "Какой частью повседневной жизни тебе больше всего нравится делиться?"},
    {"en": "What has your partner taught you about love?", "ru": "Чему партнер научил тебя о любви?"},
    {"en": "What do you want to be more intentional about as a couple?", "ru": "В чем вам хотелось бы быть более осознанными как паре?"},
    {"en": "What makes a day feel emotionally warm for you?", "ru": "Что делает день эмоционально теплым для тебя?"},
    {"en": "What compliment from your partner stays with you the longest?", "ru": "Какой комплимент от партнера запоминается тебе надолго?"},
    {"en": "What would make your next weekend feel meaningful together?", "ru": "Что сделало бы ваши следующие выходные по-настоящему ценными вместе?"},
    {"en": "What part of your relationship feels playful right now?", "ru": "Какая часть ваших отношений сейчас ощущается особенно игривой?"},
    {"en": "What are you grateful to be building together?", "ru": "За что ты благодарен или благодарна в том, что вы строите вместе?"},
    {"en": "What do you hope the two of you remember about this season of life?", "ru": "Что тебе хочется, чтобы вы запомнили об этом периоде жизни?"},
    {"en": "What is one thing you would like your partner to ask you about more often?", "ru": "О чем тебе хотелось бы, чтобы партнер спрашивал тебя чаще?"},
    {"en": "What gives you confidence in your future together?", "ru": "Что дает тебе уверенность в вашем общем будущем?"},
    {"en": "What is something ordinary that feels special only because it is with your partner?", "ru": "Что из обычного становится особенным только потому, что это происходит с партнером?"},
    {"en": "What kind of memory would you love to create this month?", "ru": "Какое воспоминание тебе хотелось бы создать в этом месяце?"},
    {"en": "What does being a good partner mean to you right now?", "ru": "Что для тебя сейчас значит быть хорошим партнером?"},
    {"en": "What part of your partner's personality feels especially beautiful lately?", "ru": "Какая часть личности партнера особенно прекрасна для тебя в последнее время?"},
    {"en": "What is one thing you want to say more often but sometimes forget?", "ru": "Что тебе хотелось бы говорить чаще, но ты иногда забываешь?"},
    {"en": "What kind of shared evening always feels comforting?", "ru": "Какой совместный вечер всегда ощущается для тебя уютным?"},
]

EXTRA_ACTIVITY_POOL = [
    {"code": "sunrise_photo", "en": "Take a sunrise or morning photo for each other", "ru": "Сделать друг для друга утреннее фото"},
    {"code": "gratitude_note", "en": "Write one short gratitude note", "ru": "Написать короткую записку благодарности"},
    {"code": "living_room_picnic", "en": "Have a living room picnic", "ru": "Устроить пикник дома"},
    {"code": "memory_song", "en": "Choose a song for this week together", "ru": "Выбрать песню недели вместе"},
    {"code": "future_trip_board", "en": "Collect ideas for a future trip", "ru": "Собрать идеи для будущего путешествия"},
    {"code": "kind_question", "en": "Ask what would make today easier", "ru": "Спросить, что сделает сегодняшний день легче"},
    {"code": "five_minute_cuddle", "en": "Spend five quiet minutes cuddling", "ru": "Провести пять тихих минут в объятиях"},
    {"code": "share_childhood_photo", "en": "Share a childhood photo and a story", "ru": "Поделиться детским фото и историей"},
    {"code": "make_playlist", "en": "Add three songs to a shared playlist", "ru": "Добавить три песни в общий плейлист"},
    {"code": "micro_date", "en": "Plan a 20-minute micro date", "ru": "Запланировать мини-свидание на 20 минут"},
    {"code": "favorite_snack", "en": "Bring your partner a favorite snack", "ru": "Принести партнеру любимый перекус"},
    {"code": "window_talk", "en": "Sit by the window and talk", "ru": "Посидеть у окна и поговорить"},
    {"code": "question_jar", "en": "Ask one question from a couple's jar", "ru": "Задать один вопрос из банки вопросов"},
    {"code": "tiny_cleanup", "en": "Do a 10-minute cleanup together", "ru": "Сделать 10-минутную уборку вместе"},
    {"code": "favorite_memory_voice", "en": "Record a voice note about a favorite memory", "ru": "Записать голосовое про любимое воспоминание"},
    {"code": "small_surprise_plan", "en": "Plan a tiny surprise for later this week", "ru": "Придумать маленький сюрприз на эту неделю"},
    {"code": "night_drive", "en": "Go for a short evening drive", "ru": "Прокатиться вечером на машине"},
    {"code": "slow_breakfast", "en": "Make a slow breakfast with no rush", "ru": "Устроить неторопливый завтрак"},
    {"code": "walk_new_route", "en": "Walk somewhere you do not usually go", "ru": "Прогуляться новым маршрутом"},
    {"code": "exchange_recommendations", "en": "Exchange one film or song recommendation", "ru": "Обменяться рекомендацией фильма или песни"},
    {"code": "support_message", "en": "Send a midday support message", "ru": "Отправить сообщение поддержки в середине дня"},
    {"code": "favorite_place_story", "en": "Tell the story of a favorite place", "ru": "Рассказать историю о любимом месте"},
    {"code": "make_dessert", "en": "Make a simple dessert together", "ru": "Приготовить простой десерт вместе"},
    {"code": "rainy_day_plan", "en": "Create a cozy rainy-day plan", "ru": "Придумать уютный план на дождливый день"},
    {"code": "celebrate_small_win", "en": "Celebrate one small win together", "ru": "Отпраздновать одну маленькую победу вместе"},
    {"code": "three_hugs", "en": "Give each other three long hugs today", "ru": "Подарить друг другу три долгих объятия за день"},
    {"code": "dream_evening", "en": "Talk about your dream evening", "ru": "Поговорить об идеальном совместном вечере"},
    {"code": "favorite_drink_date", "en": "Share coffee, tea, or your favorite drink", "ru": "Разделить кофе, чай или любимый напиток"},
    {"code": "write_future_note", "en": "Write a note to read together next month", "ru": "Написать записку, которую вы прочтете через месяц"},
    {"code": "compliment_game", "en": "Take turns giving playful compliments", "ru": "По очереди говорить друг другу игривые комплименты"},
    {"code": "cook_new_recipe", "en": "Try a new recipe together", "ru": "Попробовать новый рецепт вместе"},
    {"code": "make_home_cozier", "en": "Make one corner of home cozier", "ru": "Сделать один уголок дома уютнее"},
    {"code": "photo_collage", "en": "Choose photos for a small collage", "ru": "Выбрать фото для маленького коллажа"},
    {"code": "two_truths_memory", "en": "Share two true memories and one detail to guess", "ru": "Поделиться двумя воспоминаниями и одной деталью для угадывания"},
    {"code": "wishlist_swap", "en": "Swap one wish for this month", "ru": "Обменяться одним желанием на этот месяц"},
    {"code": "sunset_message", "en": "Send a sunset message or photo", "ru": "Отправить сообщение или фото заката"},
    {"code": "dance_one_song", "en": "Dance together for one song", "ru": "Потанцевать вместе под одну песню"},
    {"code": "mini_stretch", "en": "Do a five-minute stretch together", "ru": "Сделать пятиминутную растяжку вместе"},
    {"code": "favorite_childhood_food", "en": "Talk about favorite childhood food", "ru": "Поговорить о любимой еде из детства"},
    {"code": "thank_you_text", "en": "Send a thank-you text for something specific", "ru": "Отправить благодарность за что-то конкретное"},
    {"code": "mirror_affirmation", "en": "Say one kind affirmation to each other", "ru": "Сказать друг другу по одной доброй поддерживающей фразе"},
    {"code": "choose_next_weekend", "en": "Choose one idea for next weekend", "ru": "Выбрать одну идею на следующие выходные"},
    {"code": "mini_photo_session", "en": "Take two cute photos together", "ru": "Сделать вместе две милые фотографии"},
    {"code": "write_shared_goal", "en": "Write one shared goal for the month", "ru": "Записать одну общую цель на месяц"},
    {"code": "late_night_snack", "en": "Share a late-night snack", "ru": "Разделить поздний перекус"},
    {"code": "listen_without_fixing", "en": "Listen for ten minutes without giving advice", "ru": "Послушать десять минут без советов"},
    {"code": "favorite_outfit", "en": "Tell your partner what outfit you love on them", "ru": "Сказать партнеру, какой образ тебе особенно нравится"},
    {"code": "random_memory", "en": "Pick a random old photo and talk about it", "ru": "Выбрать случайное старое фото и обсудить его"},
    {"code": "pillow_talk", "en": "Have a soft pillow talk before sleep", "ru": "Устроить нежный разговор перед сном"},
    {"code": "one_room_reset", "en": "Reset one room together in 15 minutes", "ru": "Привести в порядок одну комнату за 15 минут вместе"},
    {"code": "shared_bucket_list", "en": "Add one item each to your bucket list", "ru": "Добавить по одному пункту в список мечт"},
    {"code": "favorite_smell", "en": "Talk about a smell that reminds you of home", "ru": "Поговорить о запахе, который напоминает о доме"},
    {"code": "future_anniversary", "en": "Imagine your next anniversary together", "ru": "Представить вашу следующую годовщину"},
    {"code": "gentle_checkin", "en": "Ask what your partner needs emotionally tonight", "ru": "Спросить, что партнеру нужно эмоционально сегодня вечером"},
    {"code": "make_toast", "en": "Make a toast to your relationship", "ru": "Сказать тост за ваши отношения"},
    {"code": "wishlist_windowshop", "en": "Window-shop online for something fun together", "ru": "Вместе посмотреть что-то интересное онлайн без покупки"},
    {"code": "five_favorites", "en": "Share five current favorite things", "ru": "Поделиться пятью любимыми вещами прямо сейчас"},
    {"code": "blanket_evening", "en": "Spend the evening under one blanket", "ru": "Провести вечер под одним пледом"},
    {"code": "gratitude_walk", "en": "Take a walk and name things you appreciate", "ru": "Погулять и назвать то, что вы цените"},
    {"code": "color_of_day", "en": "Describe today using one color and why", "ru": "Описать сегодняшний день одним цветом и почему"},
    {"code": "future_message", "en": "Write a message to your future selves", "ru": "Написать сообщение себе в будущее как паре"},
]

DAILY_QUESTIONS.extend(EXTRA_DAILY_QUESTIONS)
ACTIVITY_POOL.extend(EXTRA_ACTIVITY_POOL)

QUESTION_TONE_SEQUENCE = ["light", "romantic", "deep", "playful", "light", "deep", "romantic"]
BASE_QUESTION_TONES = [
    "romantic", "deep", "light", "romantic", "romantic", "romantic",
    "deep", "playful", "deep", "playful", "light", "deep",
]
EXTRA_QUESTION_TONES = [
    "deep", "light", "romantic", "deep", "light", "deep", "romantic", "light",
    "romantic", "playful", "deep", "playful", "deep", "romantic", "deep", "romantic",
    "playful", "deep", "light", "romantic", "playful", "light", "romantic", "deep",
    "light", "romantic", "light", "playful", "romantic", "deep", "deep", "light",
    "romantic", "deep", "romantic", "light", "romantic", "light",
]
ALL_QUESTION_TONES = BASE_QUESTION_TONES + EXTRA_QUESTION_TONES

if len(ALL_QUESTION_TONES) != len(DAILY_QUESTIONS):
    raise ValueError("Question tone mapping must match question count")

for question, tone in zip(DAILY_QUESTIONS, ALL_QUESTION_TONES):
    question["tone"] = tone

LEVEL_LABELS = {
    "en": {
        "NEWBIES": "Newbies",
        "IN_LOVE": "In Love",
        "SOUL_MATES": "Soul Mates",
        "PERFECT_PAIR": "Perfect Pair",
        "LEGENDARY": "Legendary",
    },
    "ru": {
        "NEWBIES": "Новички",
        "IN_LOVE": "Влюбленные",
        "SOUL_MATES": "Родные души",
        "PERFECT_PAIR": "Идеальная пара",
        "LEGENDARY": "Легендарная пара",
        "goals_page_title": "Цели",
        "goals_heading": "Цели",
        "goals_add_title": "Добавить цель",
        "goals_placeholder": "Какой цели вы хотите достичь вместе?",
        "goals_add_button": "Добавить цель",
        "goals_list_title": "Ваши цели",
        "goals_complete_button": "Завершить цель",
        "goals_completed": "Завершено",
        "goal_added": "Цель добавлена! +2 XP",
        "goal_completed": "Цель завершена! +25 XP",
        "places_page_title": "Места",
        "places_heading": "Места",
        "places_add_title": "Добавить место",
        "places_placeholder": "Название места",
        "places_add_button": "Добавить место",
        "places_list_title": "Места, которые хотите посетить",
        "places_visit_button": "Отметить как посещенное",
        "places_visited": "Посещено",
        "place_added": "Место добавлено! +2 XP",
        "place_visited": "Место отмечено как посещенное! +10 XP",
        "dates_page_title": "Свидания",
        "dates_heading": "Запланировать свидание",
        "dates_add_title": "Предложить свидание",
        "dates_title_placeholder": "Название свидания",
        "dates_description_placeholder": "Описание (необязательно)",
        "dates_add_button": "Предложить свидание",
        "dates_list_title": "Свидания",
        "dates_status": "Статус",
        "dates_waiting": "Ждем ответа партнера.",
        "dates_accept": "Принять",
        "dates_decline": "Отклонить",
        "dates_proposed": "Свидание предложено! +5 XP",
        "dates_accepted": "Свидание принято!",
        "dates_declined": "Свидание отклонено.",
        "dates_timer": "Осталось времени",
        "status_pending": "Ожидает ответа",
        "status_accepted": "Принято",
        "status_declined": "Отклонено",
        "status_completed": "Завершено",
        "wishes_page_title": "Желания",
        "wishes_heading": "Список желаний",
        "wishes_add_title": "Добавить желание",
        "wishes_placeholder": "Что ты хочешь?",
        "wishes_price_placeholder": "Цена (необязательно)",
        "wishes_add_button": "Добавить желание",
        "wishes_list_title": "Желания",
        "wishes_gift_button": "Отметить как подаренное",
        "wishes_gifted": "Подарено!",
        "wish_added": "Желание добавлено! +2 XP",
        "wish_gifted": "Желание отмечено как подаренное! +30 XP",
        "important_page_title": "Важные даты",
        "important_heading": "Важные даты",
        "important_add_title": "Добавить важную дату",
        "important_placeholder": "День рождения, годовщина и т.д.",
        "important_add_button": "Добавить дату",
        "important_list_title": "Сохраненные даты",
        "important_added": "Дата добавлена!",
    },
}

TRANSLATIONS = {
    "en": {
        "home": "Home",
        "settings": "Settings",
        "language": "Language",
        "english": "English",
        "russian": "Russian",
        "save": "Save",
        "saved": "Saved",
        "hello": "Hello",
        "days_together": "Days Together",
        "memories": "Daily Answers",
        "closeness": "Closeness",
        "streak": "Streak",
        "daily_ritual": "Daily Ritual",
        "goals": "Goals",
        "places": "Places",
        "dates": "Dates",
        "activities": "Activities",
        "wishes": "Wishes",
        "important": "Important",
        "activities_title": "Today's Activities",
        "choose_activity_card": "Choose one of six activities",
        "recent_activities": "Recent Activities",
        "activity_selected": "Activity selected! +8 XP",
        "daily_question": "Question of the day",
        "your_answer": "Your answer",
        "answer_placeholder": "Write your answer here",
        "your_mood": "How do you feel today?",
        "send_answer": "Send answer",
        "waiting_partner": "Waiting for your partner to answer",
        "answers_revealed": "Your answers for today",
        "you": "You",
        "partner_answered": "Your partner answered the daily question.",
        "ritual_answered": "Your answer is saved for today.",
        "welcome": "Welcome to LOVIO!",
        "not_in_couple": "You're not in a couple yet. Let's change that!",
        "send_invitation_label": "Send an invitation to your partner:",
        "partner_username": "Enter partner's username",
        "send_invitation": "Send Invitation",
        "partner_register_first": "Your partner needs to be registered first!",
        "profile": "Profile",
        "username": "Username",
        "email": "Email",
        "name": "Name",
        "total_xp": "Total XP",
        "couple_status": "Couple Status",
        "partner": "Partner",
        "together_since": "Together since",
        "couple_xp": "Couple XP",
        "relationship_level": "Relationship Level",
        "find_partner": "Find Your Partner",
        "pending_invitations": "Pending Invitations",
        "accept": "Accept",
        "decline": "Decline",
        "log_out": "Log Out",
        "choose_focus": "Choose what to do today",
        "waiting_activity": "You already picked an activity today.",
        "error_prefix": "Error: ",
        "invitation_sent": "Invitation sent! Wait for your partner to accept.",
        "goals_page_title": "Goals",
        "goals_heading": "Goals",
        "goals_add_title": "Add a Goal",
        "goals_placeholder": "What goal do you want to achieve together?",
        "goals_add_button": "Add Goal",
        "goals_list_title": "Your Goals",
        "goals_complete_button": "Complete Goal",
        "goals_completed": "Completed",
        "goal_added": "Goal added! +2 XP",
        "goal_completed": "Goal completed! +25 XP",
        "places_page_title": "Places",
        "places_heading": "Places",
        "places_add_title": "Add a Place",
        "places_placeholder": "Place name",
        "places_add_button": "Add Place",
        "places_list_title": "Places to Visit",
        "places_visit_button": "Mark as Visited",
        "places_visited": "Visited",
        "place_added": "Place added! +2 XP",
        "place_visited": "Place marked as visited! +10 XP",
        "dates_page_title": "Dates",
        "dates_heading": "Plan a Date",
        "dates_add_title": "Propose a Date",
        "dates_title_placeholder": "Date title",
        "dates_description_placeholder": "Description (optional)",
        "dates_add_button": "Propose Date",
        "dates_list_title": "Dates",
        "dates_status": "Status",
        "dates_waiting": "Waiting for your partner's answer.",
        "dates_accept": "Accept",
        "dates_decline": "Decline",
        "dates_proposed": "Date proposed! +5 XP",
        "dates_accepted": "Date accepted!",
        "dates_declined": "Date declined.",
        "dates_timer": "Time left",
        "status_pending": "Pending",
        "status_accepted": "Accepted",
        "status_declined": "Declined",
        "status_completed": "Completed",
        "wishes_page_title": "Wishes",
        "wishes_heading": "Wishlist",
        "wishes_add_title": "Add to Wishlist",
        "wishes_placeholder": "What do you want?",
        "wishes_price_placeholder": "Price (optional)",
        "wishes_add_button": "Add Wish",
        "wishes_list_title": "Wishes",
        "wishes_gift_button": "Mark as Gifted",
        "wishes_gifted": "Gifted!",
        "wish_added": "Wish added! +2 XP",
        "wish_gifted": "Wish marked as gifted! +30 XP",
        "important_page_title": "Important Dates",
        "important_heading": "Important Dates",
        "important_add_title": "Add Important Date",
        "important_placeholder": "Birthday, Anniversary, etc.",
        "important_add_button": "Add Date",
        "important_list_title": "Saved Dates",
        "important_added": "Date added!",
    },
    "ru": {
        "home": "Главная",
        "settings": "Настройки",
        "language": "Язык",
        "english": "Английский",
        "russian": "Русский",
        "save": "Сохранить",
        "saved": "Сохранено",
        "hello": "Привет",
        "days_together": "Дней вместе",
        "memories": "Ответов вместе",
        "closeness": "Близость",
        "streak": "Серия",
        "daily_ritual": "Ритуал дня",
        "goals": "Цели",
        "places": "Места",
        "dates": "Свидания",
        "activities": "Активности",
        "wishes": "Желания",
        "important": "Важное",
        "activities_title": "Активности на сегодня",
        "choose_activity_card": "Выбери одну из шести активностей",
        "recent_activities": "Последние активности",
        "activity_selected": "Активность выбрана! +8 XP",
        "daily_question": "Вопрос дня",
        "your_answer": "Твой ответ",
        "answer_placeholder": "Напиши свой ответ",
        "your_mood": "Какое у тебя сегодня настроение?",
        "send_answer": "Отправить ответ",
        "waiting_partner": "Ждем ответ партнера",
        "answers_revealed": "Ваши ответы на сегодня",
        "you": "Ты",
        "partner_answered": "Партнер ответил на вопрос дня.",
        "ritual_answered": "Твой ответ на сегодня сохранен.",
        "welcome": "Добро пожаловать в LOVIO!",
        "not_in_couple": "Ты пока не в паре. Давайте это исправим!",
        "send_invitation_label": "Отправь приглашение партнеру:",
        "partner_username": "Введи username партнера",
        "send_invitation": "Отправить приглашение",
        "partner_register_first": "Партнер должен сначала зарегистрироваться!",
        "profile": "Профиль",
        "username": "Username",
        "email": "Email",
        "name": "Имя",
        "total_xp": "Всего XP",
        "couple_status": "Статус пары",
        "partner": "Партнер",
        "together_since": "Вместе с",
        "couple_xp": "XP пары",
        "relationship_level": "Уровень отношений",
        "find_partner": "Найти партнера",
        "pending_invitations": "Ожидающие приглашения",
        "accept": "Принять",
        "decline": "Отклонить",
        "log_out": "Выйти",
        "choose_focus": "Выбери, чем заняться сегодня",
        "waiting_activity": "Ты уже выбрал активность на сегодня.",
        "error_prefix": "Ошибка: ",
        "invitation_sent": "Приглашение отправлено! Жди ответа партнера.",
    },
}

EXTRA_UI_TEXT = {
    "en": {
        "goals_page_title": "Goals",
        "goals_heading": "Goals",
        "goals_add_title": "Add a Goal",
        "goals_placeholder": "What goal do you want to achieve together?",
        "goals_add_button": "Add Goal",
        "goals_list_title": "Your Goals",
        "goals_complete_button": "Complete Goal",
        "goals_completed": "Completed",
        "goal_added": "Goal added! +2 XP",
        "goal_completed": "Goal completed! +25 XP",
        "places_page_title": "Places",
        "places_heading": "Places",
        "places_add_title": "Add a Place",
        "places_placeholder": "Place name",
        "places_add_button": "Add Place",
        "places_list_title": "Places to Visit",
        "places_visit_button": "Mark as Visited",
        "places_visited": "Visited",
        "place_added": "Place added! +2 XP",
        "place_visited": "Place marked as visited! +10 XP",
        "dates_page_title": "Dates",
        "dates_heading": "Plan a Date",
        "dates_add_title": "Propose a Date",
        "dates_title_placeholder": "Date title",
        "dates_description_placeholder": "Description (optional)",
        "dates_add_button": "Propose Date",
        "dates_list_title": "Dates",
        "dates_status": "Status",
        "dates_waiting": "Waiting for your partner's answer.",
        "dates_accept": "Accept",
        "dates_decline": "Decline",
        "dates_proposed": "Date proposed! +5 XP",
        "dates_accepted": "Date accepted!",
        "dates_declined": "Date declined.",
        "dates_timer": "Time left",
        "status_pending": "Pending",
        "status_accepted": "Accepted",
        "status_declined": "Declined",
        "status_completed": "Completed",
        "wishes_page_title": "Wishes",
        "wishes_heading": "Wishlist",
        "wishes_add_title": "Add to Wishlist",
        "wishes_placeholder": "What do you want?",
        "wishes_price_placeholder": "Price (optional)",
        "wishes_add_button": "Add Wish",
        "wishes_list_title": "Wishes",
        "wishes_gift_button": "Mark as Gifted",
        "wishes_gifted": "Gifted!",
        "wish_added": "Wish added! +2 XP",
        "wish_gifted": "Wish marked as gifted! +30 XP",
        "important_page_title": "Important Dates",
        "important_heading": "Important Dates",
        "important_add_title": "Add Important Date",
        "important_placeholder": "Birthday, Anniversary, etc.",
        "important_add_button": "Add Date",
        "important_list_title": "Saved Dates",
        "important_added": "Date added!",
    },
    "ru": {
        "goals_page_title": "Цели",
        "goals_heading": "Цели",
        "goals_add_title": "Добавить цель",
        "goals_placeholder": "Какой цели вы хотите достичь вместе?",
        "goals_add_button": "Добавить цель",
        "goals_list_title": "Ваши цели",
        "goals_complete_button": "Завершить цель",
        "goals_completed": "Завершено",
        "goal_added": "Цель добавлена! +2 XP",
        "goal_completed": "Цель завершена! +25 XP",
        "places_page_title": "Места",
        "places_heading": "Места",
        "places_add_title": "Добавить место",
        "places_placeholder": "Название места",
        "places_add_button": "Добавить место",
        "places_list_title": "Места, которые хотите посетить",
        "places_visit_button": "Отметить как посещенное",
        "places_visited": "Посещено",
        "place_added": "Место добавлено! +2 XP",
        "place_visited": "Место отмечено как посещенное! +10 XP",
        "dates_page_title": "Свидания",
        "dates_heading": "Запланировать свидание",
        "dates_add_title": "Предложить свидание",
        "dates_title_placeholder": "Название свидания",
        "dates_description_placeholder": "Описание (необязательно)",
        "dates_add_button": "Предложить свидание",
        "dates_list_title": "Свидания",
        "dates_status": "Статус",
        "dates_waiting": "Ждем ответа партнера.",
        "dates_accept": "Принять",
        "dates_decline": "Отклонить",
        "dates_proposed": "Свидание предложено! +5 XP",
        "dates_accepted": "Свидание принято!",
        "dates_declined": "Свидание отклонено.",
        "dates_timer": "Осталось времени",
        "status_pending": "Ожидает ответа",
        "status_accepted": "Принято",
        "status_declined": "Отклонено",
        "status_completed": "Завершено",
        "wishes_page_title": "Желания",
        "wishes_heading": "Список желаний",
        "wishes_add_title": "Добавить желание",
        "wishes_placeholder": "Что ты хочешь?",
        "wishes_price_placeholder": "Цена (необязательно)",
        "wishes_add_button": "Добавить желание",
        "wishes_list_title": "Желания",
        "wishes_gift_button": "Отметить как подаренное",
        "wishes_gifted": "Подарено!",
        "wish_added": "Желание добавлено! +2 XP",
        "wish_gifted": "Желание отмечено как подаренное! +30 XP",
        "important_page_title": "Важные даты",
        "important_heading": "Важные даты",
        "important_add_title": "Добавить важную дату",
        "important_placeholder": "День рождения, годовщина и т.д.",
        "important_add_button": "Добавить дату",
        "important_list_title": "Сохраненные даты",
        "important_added": "Дата добавлена!",
    },
}


def create_app(config_name=None):
    config_name = config_name or os.getenv("FLASK_ENV", "development")

    flask_app = Flask(__name__)
    flask_app.config.from_object(config[config_name])

    db.init_app(flask_app)
    Migrate(flask_app, db)
    CSRFProtect(flask_app)

    login_manager = LoginManager(flask_app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    def normalize_language(language):
        return language if language in TRANSLATIONS else "en"

    def tr(language, key):
        language = normalize_language(language)
        if key in EXTRA_UI_TEXT[language]:
            return EXTRA_UI_TEXT[language][key]
        if key in EXTRA_UI_TEXT["en"]:
            return EXTRA_UI_TEXT["en"][key]
        return TRANSLATIONS[language].get(key, TRANSLATIONS["en"].get(key, key))

    def current_couple():
        if not current_user.is_authenticated or not current_user.couple_id:
            return None
        return db.session.get(Couple, current_user.couple_id)

    def partner_for(couple):
        return couple.get_partner(current_user.id) if couple else None

    def require_couple_json(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            couple = current_couple()
            if not couple:
                return jsonify({"error": "Must be in a couple"}), 400
            return f(couple, *args, **kwargs)
        return wrapper

    def json_data():
        return request.get_json(silent=True) or {}

    def parse_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def add_notification(user_id, notif_type, text):
        db.session.add(Notification(user_id=user_id, notif_type=notif_type, text=text))

    def notify_partner(couple, notif_type, text):
        partner = partner_for(couple)
        if partner:
            add_notification(partner.id, notif_type, text)

    def add_xp(couple, amount):
        current_user.xp += amount
        couple.xp += amount
        couple.update_level()

    def mark_section_read(*notif_types):
        if not current_user.is_authenticated or not notif_types:
            return
        Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.notif_type.in_(notif_types),
            Notification.read.is_(False),
        ).update({"read": True}, synchronize_session=False)
        db.session.commit()

    def get_daily_question_tone(target_date):
        return QUESTION_TONE_SEQUENCE[target_date.toordinal() % len(QUESTION_TONE_SEQUENCE)]

    def get_daily_question_entry(couple, target_date=None):
        target_date = target_date or date.today()
        preferred_tone = get_daily_question_tone(target_date)
        matching_questions = [question for question in DAILY_QUESTIONS if question.get("tone") == preferred_tone]
        question_pool = matching_questions or DAILY_QUESTIONS
        index = (target_date.toordinal() + couple.id) % len(question_pool)
        return question_pool[index]

    def get_daily_question_index(couple, target_date):
        entry = get_daily_question_entry(couple, target_date)
        return DAILY_QUESTIONS.index(entry)

    def get_daily_question_text(couple, language, target_date=None):
        target_date = target_date or date.today()
        return get_daily_question_entry(couple, target_date)[normalize_language(language)]

    def get_prompt_responses(couple, target_date=None):
        target_date = target_date or date.today()
        return DailyPromptResponse.query.filter_by(
            couple_id=couple.id,
            question_date=target_date,
        ).order_by(DailyPromptResponse.created_at.asc()).all()

    def get_daily_prompt_state(couple):
        today = date.today()
        question_text = get_daily_question_text(couple, current_user.language, today)
        responses = get_prompt_responses(couple, today)
        current_response = next((item for item in responses if item.user_id == current_user.id), None)
        partner_response = next((item for item in responses if item.user_id != current_user.id), None)
        return {
            "question_text": question_text,
            "current_response": current_response,
            "partner_response": partner_response,
            "show_prompt": current_response is None,
            "revealed": current_response is not None and partner_response is not None,
        }

    def normalize_activity_code(task_value):
        for item in ACTIVITY_POOL:
            if task_value in {item["code"], item["en"], item["ru"]}:
                return item["code"]
        return task_value

    def get_activity_label(code, language):
        language = normalize_language(language)
        for item in ACTIVITY_POOL:
            if code in {item["code"], item["en"], item["ru"]}:
                return item[language]
        return code

    def get_date_status_label(status_value, language):
        return tr(language, f"status_{status_value}")

    def get_visible_dates(couple):
        accepted_cutoff = datetime.utcnow() - timedelta(days=1)
        accepted_rows = DatePlan.query.filter_by(couple_id=couple.id, status="accepted").all()
        changed = False
        for row in accepted_rows:
            accepted_at = row.updated_at or row.created_at
            if accepted_at and accepted_at <= accepted_cutoff:
                row.status = "completed"
                changed = True
        if changed:
            db.session.commit()

        visible_rows = DatePlan.query.filter(
            DatePlan.couple_id == couple.id,
            DatePlan.status != "completed",
        ).order_by(DatePlan.created_at.desc()).all()

        prepared = []
        for row in visible_rows:
            expires_in_seconds = None
            if row.status == "accepted":
                accepted_at = row.updated_at or row.created_at
                remaining = timedelta(days=1) - (datetime.utcnow() - accepted_at)
                expires_in_seconds = max(0, int(remaining.total_seconds()))
            prepared.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "planned_date": row.planned_date,
                    "status": row.status,
                    "status_label": get_date_status_label(row.status, current_user.language),
                    "proposer_id": row.proposer_id,
                    "expires_in_seconds": expires_in_seconds,
                }
            )
        return prepared

    def get_daily_activity_choices(couple):
        today = date.today()
        recent_cutoff = today - timedelta(days=6)
        recent_rows = Activity.query.filter(
            Activity.couple_id == couple.id,
            Activity.activity_date >= recent_cutoff,
        ).all()
        recent_codes = {normalize_activity_code(row.task) for row in recent_rows}
        available = [item for item in ACTIVITY_POOL if item["code"] not in recent_codes]
        if len(available) < 6:
            available = ACTIVITY_POOL[:]
        rng = random.Random(f"{couple.id}-{today.isoformat()}")
        chosen = rng.sample(available, 6)
        language = normalize_language(current_user.language)
        return [{"code": item["code"], "label": item[language]} for item in chosen]

    @flask_app.context_processor
    def inject_globals():
        language = normalize_language(getattr(current_user, "language", "en")) if current_user.is_authenticated else "en"
        merged_translations = dict(TRANSLATIONS[language])
        merged_translations.update(EXTRA_UI_TEXT[language])
        notification_counts = {}
        if current_user.is_authenticated:
            unread_notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
            for notification in unread_notifications:
                notification_counts[notification.notif_type] = notification_counts.get(notification.notif_type, 0) + 1
        return {
            "lang": language,
            "tr": merged_translations,
            "notification_counts": notification_counts,
            "level_labels": LEVEL_LABELS[language],
            "date_status_labels": {
                "pending": merged_translations["status_pending"],
                "accepted": merged_translations["status_accepted"],
                "declined": merged_translations["status_declined"],
                "completed": merged_translations["status_completed"],
            },
        }

    @flask_app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @flask_app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            name = request.form.get("name", "").strip()
            gender = request.form.get("gender", "female")

            if not all([username, email, password, confirm_password, name]):
                flash("All fields are required", "error")
                return redirect(url_for("register"))
            if len(username) < 3 or len(username) > 80:
                flash("Username must be 3-80 characters", "error")
                return redirect(url_for("register"))
            if len(password) < 8:
                flash("Password must be at least 8 characters", "error")
                return redirect(url_for("register"))
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect(url_for("register"))
            if "@" not in email or len(email) > 120:
                flash("Invalid email", "error")
                return redirect(url_for("register"))
            if User.query.filter_by(username=username).first():
                flash("Username already exists", "error")
                return redirect(url_for("register"))
            if User.query.filter_by(email=email).first():
                flash("Email already registered", "error")
                return redirect(url_for("register"))

            user = User(username=username, email=email, name=name, gender=gender)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("auth/register.html")

    @flask_app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user, remember=bool(request.form.get("remember")))
                user.update_last_login()
                if user.last_check_in != date.today():
                    user.xp += 1
                    user.last_check_in = date.today()
                    db.session.commit()
                next_page = request.args.get("next")
                return redirect(next_page if next_page and next_page.startswith("/") else url_for("dashboard"))

            flash("Invalid username or password", "error")

        return render_template("auth/login.html")

    @flask_app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @flask_app.route("/dashboard")
    @login_required
    def dashboard():
        couple = current_couple()
        partner = partner_for(couple)
        prompt_state = get_daily_prompt_state(couple) if couple else None
        stats = {
            "xp": current_user.xp,
            "streak": calculate_streak(current_user),
            "couple_xp": couple.xp if couple else 0,
            "relationship_level": couple.relationship_level if couple else None,
            "closeness": couple.closeness if couple else 50,
            "days_together": (date.today() - couple.couple_since).days if couple else 0,
            "daily_answers_count": DailyPromptResponse.query.filter_by(couple_id=couple.id).count() if couple else 0,
            "goals_count": Goal.query.filter_by(couple_id=couple.id, completed=True).count() if couple else 0,
            "prompt_state": prompt_state,
        }
        return render_template("dashboard.html", partner=partner, **stats)

    @flask_app.route("/goals")
    @login_required
    def goals():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("goal")
        goals_list = Goal.query.filter_by(couple_id=couple.id).order_by(Goal.created_at.desc()).all()
        return render_template("goals.html", goals=goals_list)

    @flask_app.route("/places")
    @login_required
    def places():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("place")
        places_list = Place.query.filter_by(couple_id=couple.id).order_by(Place.created_at.desc()).all()
        return render_template("places.html", places=places_list)

    @flask_app.route("/dates")
    @login_required
    def dates():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("date")
        dates_list = get_visible_dates(couple)
        return render_template("dates.html", dates=dates_list)

    @flask_app.route("/activities")
    @login_required
    def activities():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("activity")
        activities_list = Activity.query.filter_by(couple_id=couple.id).order_by(Activity.created_at.desc()).all()
        localized_history = [
            {
                "user_name": item.user.name,
                "task_label": get_activity_label(item.task, current_user.language),
                "activity_date": item.activity_date,
            }
            for item in activities_list
        ]
        return render_template(
            "activities.html",
            activities=localized_history,
            tasks=get_daily_activity_choices(couple),
            already_selected=Activity.query.filter_by(user_id=current_user.id, activity_date=date.today()).first() is not None,
        )

    @flask_app.route("/wishes")
    @login_required
    def wishes():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("wish")
        wishes_list = Wish.query.filter_by(couple_id=couple.id).order_by(Wish.created_at.desc()).all()
        return render_template("wishes.html", wishes=wishes_list)

    @flask_app.route("/important-dates")
    @login_required
    def important_dates():
        couple = current_couple()
        if not couple:
            return redirect(url_for("dashboard"))
        mark_section_read("important_date")
        dates_list = ImportantDate.query.filter_by(couple_id=couple.id).order_by(ImportantDate.date_value.asc()).all()
        return render_template("important-dates.html", important_dates=dates_list)

    @flask_app.route("/settings")
    @login_required
    def settings():
        couple = current_couple()
        pending_invitations = CoupleInvitation.query.filter_by(receiver_id=current_user.id, status="pending").all()
        mark_section_read("invitation", "couple")
        return render_template(
            "settings.html",
            couple=couple,
            partner=partner_for(couple),
            pending_invitations=pending_invitations,
        )

    @flask_app.route("/api/settings/language", methods=["POST"])
    @login_required
    def update_language():
        language = normalize_language(json_data().get("language", "en"))
        current_user.language = language
        db.session.commit()
        return jsonify({"success": True})

    @flask_app.route("/api/invite/send", methods=["POST"])
    @login_required
    def send_invitation():
        if current_user.has_couple():
            return jsonify({"error": "You are already in a couple"}), 400

        receiver_username = json_data().get("username", "").strip()
        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            return jsonify({"error": "User not found"}), 404
        if receiver.id == current_user.id:
            return jsonify({"error": "Cannot invite yourself"}), 400
        if receiver.has_couple():
            return jsonify({"error": "User is already in a couple"}), 400

        existing = CoupleInvitation.query.filter_by(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            status="pending",
        ).first()
        if existing:
            return jsonify({"error": "Invitation already sent"}), 400

        db.session.add(CoupleInvitation(sender_id=current_user.id, receiver_id=receiver.id))
        add_notification(receiver.id, "invitation", f"{current_user.name} invited you to be partners!")
        db.session.commit()
        return jsonify({"success": True})

    @flask_app.route("/api/invite/<int:invitation_id>/accept", methods=["POST"])
    @login_required
    def accept_invitation(invitation_id):
        invitation = db.session.get(CoupleInvitation, invitation_id)
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({"error": "Invalid invitation"}), 404
        if invitation.status != "pending":
            return jsonify({"error": "Invitation already processed"}), 400
        if current_user.has_couple() or invitation.sender.has_couple():
            return jsonify({"error": "One user is already in a couple"}), 400

        couple = invitation.accept()
        sender = db.session.get(User, invitation.sender_id)
        current_user.couple_id = couple.id
        sender.couple_id = couple.id
        add_notification(sender.id, "couple", f"{current_user.name} accepted your invitation!")
        db.session.commit()
        return jsonify({"success": True, "couple_id": couple.id})

    @flask_app.route("/api/invite/<int:invitation_id>/decline", methods=["POST"])
    @login_required
    def decline_invitation(invitation_id):
        invitation = db.session.get(CoupleInvitation, invitation_id)
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({"error": "Invalid invitation"}), 404
        if invitation.status != "pending":
            return jsonify({"error": "Invitation already processed"}), 400
        invitation.decline()
        add_notification(invitation.sender_id, "invitation", f"{current_user.name} declined your invitation.")
        db.session.commit()
        return jsonify({"success": True})

    @flask_app.route("/api/daily-prompt/answer", methods=["POST"])
    @login_required
    @require_couple_json
    def answer_daily_prompt(couple):
        payload = json_data()
        answer_text = payload.get("answer_text", "").strip()
        mood_level = parse_int(payload.get("mood_level"), 0)
        if not answer_text or len(answer_text) > 2000:
            return jsonify({"error": "Answer must be 1-2000 characters"}), 400
        if mood_level < 1 or mood_level > 10:
            return jsonify({"error": "Mood must be 1-10"}), 400

        today = date.today()
        existing = DailyPromptResponse.query.filter_by(user_id=current_user.id, question_date=today).first()
        if existing:
            return jsonify({"error": "You already answered today"}), 400

        response = DailyPromptResponse(
            couple_id=couple.id,
            user_id=current_user.id,
            question_date=today,
            question_text=get_daily_question_text(couple, "en", today),
            answer_text=answer_text,
            mood_level=mood_level,
        )
        db.session.add(response)
        add_xp(couple, 4)

        other_response = DailyPromptResponse.query.filter(
            DailyPromptResponse.couple_id == couple.id,
            DailyPromptResponse.question_date == today,
            DailyPromptResponse.user_id != current_user.id,
        ).first()
        if other_response:
            notify_partner(couple, "daily_prompt", tr(current_user.language, "partner_answered"))
        else:
            notify_partner(couple, "daily_prompt", tr(current_user.language, "ritual_answered"))

        db.session.commit()
        return jsonify({"success": True})

    @flask_app.route("/api/activity/select", methods=["POST"])
    @login_required
    @require_couple_json
    def select_activity(couple):
        task_code = normalize_activity_code(json_data().get("task", "").strip())
        if not any(item["code"] == task_code for item in ACTIVITY_POOL):
            return jsonify({"error": "Invalid task"}), 400
        if Activity.query.filter_by(user_id=current_user.id, activity_date=date.today()).first():
            return jsonify({"error": "You already selected activity today"}), 400

        db.session.add(Activity(couple_id=couple.id, user_id=current_user.id, task=task_code))
        add_xp(couple, 8)
        notify_partner(couple, "activity", f"{current_user.name} selected a new activity")
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "You already selected activity today"}), 400
        return jsonify({"success": True, "xp_gained": 8})

    @flask_app.route("/api/goals/add", methods=["POST"])
    @login_required
    @require_couple_json
    def add_goal(couple):
        text = json_data().get("text", "").strip()
        if not text or len(text) > 500:
            return jsonify({"error": "Goal must be 1-500 characters"}), 400
        db.session.add(Goal(couple_id=couple.id, creator_id=current_user.id, text=text))
        add_xp(couple, 2)
        notify_partner(couple, "goal", f"{current_user.name} added a new goal")
        db.session.commit()
        return jsonify({"success": True, "xp_gained": 2})

    @flask_app.route("/api/goals/complete/<int:goal_id>", methods=["POST"])
    @login_required
    @require_couple_json
    def complete_goal(couple, goal_id):
        goal = Goal.query.filter_by(id=goal_id, couple_id=couple.id).first()
        if not goal:
            return jsonify({"error": "Goal not found"}), 404
        if not goal.completed:
            goal.completed = True
            goal.completed_at = datetime.utcnow()
            add_xp(couple, 25)
            notify_partner(couple, "goal", f"{current_user.name} completed a goal")
            db.session.commit()
        return jsonify({"success": True, "xp_gained": 25})

    @flask_app.route("/api/places/add", methods=["POST"])
    @login_required
    @require_couple_json
    def add_place(couple):
        name = json_data().get("name", "").strip()
        if not name or len(name) > 200:
            return jsonify({"error": "Place name must be 1-200 characters"}), 400
        db.session.add(Place(couple_id=couple.id, creator_id=current_user.id, name=name))
        add_xp(couple, 2)
        notify_partner(couple, "place", f"{current_user.name} added a new place")
        db.session.commit()
        return jsonify({"success": True, "xp_gained": 2})

    @flask_app.route("/api/places/visit", methods=["POST"])
    @login_required
    @require_couple_json
    def visit_place(couple):
        name = json_data().get("name", "").strip()
        place = Place.query.filter_by(couple_id=couple.id, name=name).first()
        if not place:
            return jsonify({"error": "Place not found"}), 404
        if not place.visited:
            place.visited = True
            place.visited_at = datetime.utcnow()
            add_xp(couple, 10)
            notify_partner(couple, "place", f"{current_user.name} marked a place as visited")
            db.session.commit()
        return jsonify({"success": True, "xp_gained": 10})

    @flask_app.route("/api/dates/add", methods=["POST"])
    @login_required
    @require_couple_json
    def add_date(couple):
        payload = json_data()
        title = payload.get("title", "").strip()
        planned_date = payload.get("planned_date", "")
        description = payload.get("description", "").strip()
        if not title or len(title) > 200:
            return jsonify({"error": "Date title must be 1-200 characters"}), 400
        try:
            parsed_date = datetime.fromisoformat(planned_date)
        except ValueError:
            return jsonify({"error": "Invalid date"}), 400

        date_plan = DatePlan(
            couple_id=couple.id,
            proposer_id=current_user.id,
            title=title,
            description=description[:1000],
            planned_date=parsed_date,
        )
        db.session.add(date_plan)
        add_xp(couple, 5)
        notify_partner(couple, "date", f"{current_user.name} proposed a new date")
        db.session.commit()
        return jsonify({"success": True, "xp_gained": 5})

    @flask_app.route("/api/dates/<int:date_id>/respond", methods=["POST"])
    @login_required
    @require_couple_json
    def respond_date(couple, date_id):
        date_plan = DatePlan.query.filter_by(id=date_id, couple_id=couple.id).first()
        status = json_data().get("status")
        if not date_plan:
            return jsonify({"error": "Date not found"}), 404
        if date_plan.proposer_id == current_user.id:
            return jsonify({"error": "Only your partner can respond"}), 400
        if status not in {"accepted", "declined"}:
            return jsonify({"error": "Invalid status"}), 400
        date_plan.status = status
        if status == "accepted":
            add_xp(couple, 20)
            add_notification(date_plan.proposer_id, "date", f"{current_user.name} accepted your date")
        else:
            add_notification(date_plan.proposer_id, "date", f"{current_user.name} declined your date")
        db.session.commit()
        return jsonify({"success": True})

    @flask_app.route("/api/dates/<int:date_id>/complete", methods=["POST"])
    @login_required
    @require_couple_json
    def complete_date(couple, date_id):
        date_plan = DatePlan.query.filter_by(id=date_id, couple_id=couple.id).first()
        if not date_plan:
            return jsonify({"error": "Date not found"}), 404
        date_plan.status = "completed"
        add_xp(couple, 50)
        db.session.commit()
        return jsonify({"success": True, "xp_gained": 50})

    @flask_app.route("/api/wishes/add", methods=["POST"])
    @login_required
    @require_couple_json
    def add_wish(couple):
        payload = json_data()
        text_value = payload.get("text", "").strip()
        price = max(0, parse_int(payload.get("price"), 0))
        if not text_value or len(text_value) > 300:
            return jsonify({"error": "Wish must be 1-300 characters"}), 400
        db.session.add(Wish(couple_id=couple.id, creator_id=current_user.id, text=text_value, price=price))
        add_xp(couple, 2)
        notify_partner(couple, "wish", f"{current_user.name} added a new wish")
        db.session.commit()
        return jsonify({"success": True, "xp_gained": 2})

    @flask_app.route("/api/wishes/gift", methods=["POST"])
    @login_required
    @require_couple_json
    def gift_wish(couple):
        text_value = json_data().get("text", "").strip()
        wish = Wish.query.filter_by(couple_id=couple.id, text=text_value).first()
        if not wish:
            return jsonify({"error": "Wish not found"}), 404
        if not wish.gifted:
            wish.gifted = True
            wish.gifted_at = datetime.utcnow()
            add_xp(couple, 30)
            notify_partner(couple, "wish", f"{current_user.name} marked a wish as gifted")
            db.session.commit()
        return jsonify({"success": True, "xp_gained": 30})

    @flask_app.route("/api/important-dates/add", methods=["POST"])
    @login_required
    @require_couple_json
    def add_important_date(couple):
        payload = json_data()
        title = payload.get("title", "").strip()
        raw_date = payload.get("date", "")
        if not title or len(title) > 200:
            return jsonify({"error": "Title must be 1-200 characters"}), 400
        try:
            parsed_date = date.fromisoformat(raw_date)
        except ValueError:
            return jsonify({"error": "Invalid date"}), 400
        db.session.add(
            ImportantDate(
                couple_id=couple.id,
                creator_id=current_user.id,
                title=title,
                date_value=parsed_date,
            )
        )
        notify_partner(couple, "important_date", f"{current_user.name} added an important date")
        db.session.commit()
        return jsonify({"success": True})

    @flask_app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @flask_app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @flask_app.cli.command()
    def init_db():
        db.create_all()
        ensure_schema()
        print("Database initialized.")

    with flask_app.app_context():
        db.create_all()
        ensure_schema()

    return flask_app


def ensure_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "language" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(2) DEFAULT 'en'"))
        db.session.commit()


def calculate_streak(user):
    if not user.has_couple():
        return 0
    couple = db.session.get(Couple, user.couple_id)
    if not couple:
        return 0
    streak = 0
    current_date = date.today()
    while Activity.query.filter_by(
        user_id=user.id,
        couple_id=couple.id,
        activity_date=current_date,
    ).first():
        streak += 1
        current_date -= timedelta(days=1)
    return streak


app = create_app(os.getenv("FLASK_ENV", "production"))


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)
