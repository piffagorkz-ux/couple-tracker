const DAILY_QUESTIONS = [
  { key: "q1", en: "What made you feel loved by your partner recently?", ru: "Что в последнее время дало тебе почувствовать любовь партнера?" },
  { key: "q2", en: "What would make this week warmer for the two of you?", ru: "Что сделало бы эту неделю теплее для вас двоих?" },
  { key: "q3", en: "What little ritual would you like to build together?", ru: "Какой маленький ритуал тебе хотелось бы создать вместе?" },
  { key: "q4", en: "What is one thing you admire in your partner right now?", ru: "Что ты сейчас особенно ценишь в своем партнере?" },
  { key: "q5", en: "What kind of support would feel best today?", ru: "Какая поддержка сегодня ощущалась бы самой нужной?" },
  { key: "q6", en: "What memory of the two of you still makes you smile?", ru: "Какое ваше общее воспоминание до сих пор вызывает улыбку?" },
  { key: "q7", en: "What do you want more of in your relationship this month?", ru: "Чего тебе хочется больше в ваших отношениях в этом месяце?" },
  { key: "q8", en: "What simple date would make you happy this week?", ru: "Какое простое свидание сделало бы тебя счастливее на этой неделе?" }
];

const ACTIVITY_POOL = [
  { code: "cook_together", en: "Cook dinner together", ru: "Приготовить ужин вместе" },
  { code: "walk_evening", en: "Go for an evening walk", ru: "Пойти на вечернюю прогулку" },
  { code: "movie_night", en: "Plan a movie night", ru: "Устроить вечер кино" },
  { code: "voice_note", en: "Send a heartfelt voice note", ru: "Отправить теплое голосовое сообщение" },
  { code: "tea_talk", en: "Have tea and talk for 20 minutes", ru: "Попить чай и поговорить 20 минут" },
  { code: "mini_gift", en: "Prepare a tiny surprise gift", ru: "Подготовить маленький сюрприз" },
  { code: "photo_memory", en: "Share a favorite photo together", ru: "Поделиться любимой совместной фотографией" },
  { code: "dance_home", en: "Dance together at home", ru: "Потанцевать вместе дома" },
  { code: "phone_free", en: "Spend 30 minutes without phones", ru: "Провести 30 минут без телефонов" },
  { code: "shared_breakfast", en: "Have breakfast together", ru: "Позавтракать вместе" },
  { code: "plan_trip", en: "Dream about a future trip", ru: "Помечтать о будущем путешествии" },
  { code: "story_swap", en: "Tell a childhood story", ru: "Рассказать историю из детства" },
  { code: "hug_minute", en: "Hold a long one-minute hug", ru: "Обняться на целую минуту" },
  { code: "sunset_watch", en: "Watch the sunset together", ru: "Посмотреть закат вместе" },
  { code: "music_share", en: "Share one meaningful song", ru: "Поделиться значимой песней" },
  { code: "coffee_date", en: "Make a mini coffee date", ru: "Устроить маленькое кофейное свидание" }
];

const UI = {
  en: {
    appName: "Lovio",
    login: "Log in",
    register: "Create account",
    email: "Email",
    username: "Username",
    password: "Password",
    name: "Name",
    gender: "Gender",
    female: "Female",
    male: "Male",
    home: "Home",
    partner: "Partner",
    goals: "Goals",
    dates: "Dates",
    wishes: "Wishes",
    importantDates: "Important dates",
    save: "Save",
    logout: "Log out",
    sendInvite: "Send invite",
    invitePlaceholder: "Partner email",
    answerQuestion: "Daily question",
    mood: "Mood",
    answer: "Answer",
    activities: "Today's activities",
    noCouple: "Invite your partner to unlock the couple dashboard.",
    addGoal: "Add goal",
    addDate: "Plan date",
    addWish: "Add wish",
    addImportantDate: "Add important date",
    language: "Language",
    plannedFor: "Planned for",
    price: "Price",
    dateTitle: "Title",
    description: "Description",
    dateValue: "Date",
    pendingInvites: "Pending invites",
    accept: "Accept",
    decline: "Decline",
    submit: "Submit",
    dashboard: "Dashboard",
    dailyRevealWaiting: "Answers will open after both partners reply.",
    dailyRevealReady: "Both answers are unlocked.",
    chosenToday: "Chosen today",
    statusPending: "Pending",
    statusAccepted: "Accepted",
    statusDeclined: "Declined",
    expiresIn: "Expires in",
    noItems: "Nothing here yet.",
    you: "You",
    done: "Done"
  },
  ru: {
    appName: "Lovio",
    login: "Войти",
    register: "Регистрация",
    email: "Почта",
    username: "Логин",
    password: "Пароль",
    name: "Имя",
    gender: "Пол",
    female: "Девушка",
    male: "Парень",
    home: "Главная",
    partner: "Партнер",
    goals: "Цели",
    dates: "Свидания",
    wishes: "Желания",
    importantDates: "Важные даты",
    save: "Сохранить",
    logout: "Выйти",
    sendInvite: "Отправить приглашение",
    invitePlaceholder: "Почта партнера",
    answerQuestion: "Вопрос дня",
    mood: "Настроение",
    answer: "Ответ",
    activities: "Активности на сегодня",
    noCouple: "Пригласи партнера, чтобы открыть парный дашборд.",
    addGoal: "Добавить цель",
    addDate: "Назначить свидание",
    addWish: "Добавить желание",
    addImportantDate: "Добавить важную дату",
    language: "Язык",
    plannedFor: "Запланировано на",
    price: "Цена",
    dateTitle: "Название",
    description: "Описание",
    dateValue: "Дата",
    pendingInvites: "Ожидают ответа",
    accept: "Принять",
    decline: "Отклонить",
    submit: "Сохранить",
    dashboard: "Главная",
    dailyRevealWaiting: "Ответы откроются, когда ответят оба.",
    dailyRevealReady: "Оба ответа уже открыты.",
    chosenToday: "Выбрано сегодня",
    statusPending: "Ожидает",
    statusAccepted: "Принято",
    statusDeclined: "Отклонено",
    expiresIn: "Исчезнет через",
    noItems: "Пока пусто.",
    you: "You",
    done: "Done"
  }
};

const QUESTIONS = [
  { key: "q1", en: "What made you feel loved by your partner recently?", ru: "\u0427\u0442\u043e \u043d\u0435\u0434\u0430\u0432\u043d\u043e \u0434\u0430\u043b\u043e \u0442\u0435\u0431\u0435 \u043f\u043e\u0447\u0443\u0432\u0441\u0442\u0432\u043e\u0432\u0430\u0442\u044c \u043b\u044e\u0431\u043e\u0432\u044c \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430?" },
  { key: "q2", en: "What would make this week warmer for the two of you?", ru: "\u0427\u0442\u043e \u0441\u0434\u0435\u043b\u0430\u043b\u043e \u0431\u044b \u044d\u0442\u0443 \u043d\u0435\u0434\u0435\u043b\u044e \u0442\u0435\u043f\u043b\u0435\u0435 \u0434\u043b\u044f \u0432\u0430\u0441 \u0434\u0432\u043e\u0438\u0445?" },
  { key: "q3", en: "What little ritual would you like to build together?", ru: "\u041a\u0430\u043a\u043e\u0439 \u043c\u0430\u043b\u0435\u043d\u044c\u043a\u0438\u0439 \u0440\u0438\u0442\u0443\u0430\u043b \u0442\u0435\u0431\u0435 \u0445\u043e\u0442\u0435\u043b\u043e\u0441\u044c \u0431\u044b \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u0432\u043c\u0435\u0441\u0442\u0435?" },
  { key: "q4", en: "What is one thing you admire in your partner right now?", ru: "\u0427\u0442\u043e \u0442\u044b \u0441\u0435\u0439\u0447\u0430\u0441 \u043e\u0441\u043e\u0431\u0435\u043d\u043d\u043e \u0446\u0435\u043d\u0438\u0448\u044c \u0432 \u0441\u0432\u043e\u0435\u043c \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0435?" },
  { key: "q5", en: "What kind of support would feel best today?", ru: "\u041a\u0430\u043a\u0430\u044f \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u0441\u0435\u0433\u043e\u0434\u043d\u044f \u043e\u0449\u0443\u0449\u0430\u043b\u0430\u0441\u044c \u0431\u044b \u0441\u0430\u043c\u043e\u0439 \u043d\u0443\u0436\u043d\u043e\u0439?" },
  { key: "q6", en: "What memory of the two of you still makes you smile?", ru: "\u041a\u0430\u043a\u043e\u0435 \u0432\u0430\u0448\u0435 \u043e\u0431\u0449\u0435\u0435 \u0432\u043e\u0441\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435 \u0434\u043e \u0441\u0438\u0445 \u043f\u043e\u0440 \u0432\u044b\u0437\u044b\u0432\u0430\u0435\u0442 \u0443\u043b\u044b\u0431\u043a\u0443?" },
  { key: "q7", en: "What do you want more of in your relationship this month?", ru: "\u0427\u0435\u0433\u043e \u0442\u0435\u0431\u0435 \u0445\u043e\u0447\u0435\u0442\u0441\u044f \u0431\u043e\u043b\u044c\u0448\u0435 \u0432 \u0432\u0430\u0448\u0438\u0445 \u043e\u0442\u043d\u043e\u0448\u0435\u043d\u0438\u044f\u0445 \u0432 \u044d\u0442\u043e\u043c \u043c\u0435\u0441\u044f\u0446\u0435?" },
  { key: "q8", en: "What simple date would make you happy this week?", ru: "\u041a\u0430\u043a\u043e\u0435 \u043f\u0440\u043e\u0441\u0442\u043e\u0435 \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u0435 \u0441\u0434\u0435\u043b\u0430\u043b\u043e \u0431\u044b \u0442\u0435\u0431\u044f \u0441\u0447\u0430\u0441\u0442\u043b\u0438\u0432\u0435\u0435 \u043d\u0430 \u044d\u0442\u043e\u0439 \u043d\u0435\u0434\u0435\u043b\u0435?" }
];

const ACTIVITIES = [
  { code: "cook_together", en: "Cook dinner together", ru: "\u041f\u0440\u0438\u0433\u043e\u0442\u043e\u0432\u0438\u0442\u044c \u0443\u0436\u0438\u043d \u0432\u043c\u0435\u0441\u0442\u0435" },
  { code: "walk_evening", en: "Go for an evening walk", ru: "\u041f\u043e\u0439\u0442\u0438 \u043d\u0430 \u0432\u0435\u0447\u0435\u0440\u043d\u044e\u044e \u043f\u0440\u043e\u0433\u0443\u043b\u043a\u0443" },
  { code: "movie_night", en: "Plan a movie night", ru: "\u0423\u0441\u0442\u0440\u043e\u0438\u0442\u044c \u0432\u0435\u0447\u0435\u0440 \u043a\u0438\u043d\u043e" },
  { code: "voice_note", en: "Send a heartfelt voice note", ru: "\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0442\u0435\u043f\u043b\u043e\u0435 \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435" },
  { code: "tea_talk", en: "Have tea and talk for 20 minutes", ru: "\u041f\u043e\u043f\u0438\u0442\u044c \u0447\u0430\u0439 \u0438 \u043f\u043e\u0433\u043e\u0432\u043e\u0440\u0438\u0442\u044c 20 \u043c\u0438\u043d\u0443\u0442" },
  { code: "mini_gift", en: "Prepare a tiny surprise gift", ru: "\u041f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u0438\u0442\u044c \u043c\u0430\u043b\u0435\u043d\u044c\u043a\u0438\u0439 \u0441\u044e\u0440\u043f\u0440\u0438\u0437" },
  { code: "photo_memory", en: "Share a favorite photo together", ru: "\u041f\u043e\u0434\u0435\u043b\u0438\u0442\u044c\u0441\u044f \u043b\u044e\u0431\u0438\u043c\u043e\u0439 \u0441\u043e\u0432\u043c\u0435\u0441\u0442\u043d\u043e\u0439 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0435\u0439" },
  { code: "dance_home", en: "Dance together at home", ru: "\u041f\u043e\u0442\u0430\u043d\u0446\u0435\u0432\u0430\u0442\u044c \u0432\u043c\u0435\u0441\u0442\u0435 \u0434\u043e\u043c\u0430" },
  { code: "phone_free", en: "Spend 30 minutes without phones", ru: "\u041f\u0440\u043e\u0432\u0435\u0441\u0442\u0438 30 \u043c\u0438\u043d\u0443\u0442 \u0431\u0435\u0437 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u043e\u0432" },
  { code: "shared_breakfast", en: "Have breakfast together", ru: "\u041f\u043e\u0437\u0430\u0432\u0442\u0440\u0430\u043a\u0430\u0442\u044c \u0432\u043c\u0435\u0441\u0442\u0435" },
  { code: "plan_trip", en: "Dream about a future trip", ru: "\u041f\u043e\u043c\u0435\u0447\u0442\u0430\u0442\u044c \u043e \u0431\u0443\u0434\u0443\u0449\u0435\u043c \u043f\u0443\u0442\u0435\u0448\u0435\u0441\u0442\u0432\u0438\u0438" },
  { code: "story_swap", en: "Tell a childhood story", ru: "\u0420\u0430\u0441\u0441\u043a\u0430\u0437\u0430\u0442\u044c \u0438\u0441\u0442\u043e\u0440\u0438\u044e \u0438\u0437 \u0434\u0435\u0442\u0441\u0442\u0432\u0430" },
  { code: "hug_minute", en: "Hold a long one-minute hug", ru: "\u041e\u0431\u043d\u044f\u0442\u044c\u0441\u044f \u043d\u0430 \u0446\u0435\u043b\u0443\u044e \u043c\u0438\u043d\u0443\u0442\u0443" },
  { code: "sunset_watch", en: "Watch the sunset together", ru: "\u041f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0437\u0430\u043a\u0430\u0442 \u0432\u043c\u0435\u0441\u0442\u0435" },
  { code: "music_share", en: "Share one meaningful song", ru: "\u041f\u043e\u0434\u0435\u043b\u0438\u0442\u044c\u0441\u044f \u0437\u043d\u0430\u0447\u0438\u043c\u043e\u0439 \u043f\u0435\u0441\u043d\u0435\u0439" },
  { code: "coffee_date", en: "Make a mini coffee date", ru: "\u0423\u0441\u0442\u0440\u043e\u0438\u0442\u044c \u043c\u0430\u043b\u0435\u043d\u044c\u043a\u043e\u0435 \u043a\u043e\u0444\u0435\u0439\u043d\u043e\u0435 \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u0435" }
];

const UI_TEXT = {
  en: {
    appName: "Lovio",
    appTagline: "Relationship dashboard",
    login: "Log in",
    register: "Create account",
    email: "Email",
    username: "Username",
    password: "Password",
    name: "Name",
    gender: "Gender",
    female: "Female",
    male: "Male",
    home: "Home",
    promptTab: "Question",
    goals: "Goals",
    dates: "Dates",
    wishes: "Wishes",
    places: "Places",
    importantDates: "Important dates",
    save: "Save",
    logout: "Log out",
    sendInvite: "Send invite",
    invitePlaceholder: "Partner email",
    answerQuestion: "Daily question",
    dailyPromptTitle: "Question of the day",
    mood: "Mood",
    answer: "Answer",
    activities: "Today's activity",
    noCouple: "Invite your partner to unlock the couple dashboard.",
    addGoal: "Add goal",
    addPlace: "Add place",
    addDate: "Plan date",
    addWish: "Add wish",
    addImportantDate: "Add important date",
    plannedFor: "Planned for",
    price: "Price",
    dateTitle: "Title",
    description: "Description",
    dateValue: "Date",
    pendingInvites: "Pending invites",
    accept: "Accept",
    decline: "Decline",
    submit: "Save",
    dashboard: "Dashboard",
    dailyRevealWaiting: "Answers will open after both partners reply.",
    dailyRevealReady: "Both answers are unlocked.",
    chosenToday: "Chosen today",
    statusPending: "Pending",
    statusAccepted: "Accepted",
    statusDeclined: "Declined",
    expiresIn: "Expires in",
    noItems: "Nothing here yet.",
    you: "You",
    done: "Done",
    visited: "Visited",
    markVisited: "Mark visited",
    activityLocked: "Today's activity is already chosen.",
    statsTitle: "Relationship stats",
    statsSubtitle: "A quick view of your shared rhythm and progress.",
    statsPromptTogether: "Questions answered together",
    statsGoalsDone: "Completed goals",
    statsPlacesVisited: "Visited places",
    statsDatesPlanned: "Planned dates",
    sendHeart: "Send a heart",
    heartSent: "Heart sent",
    heartReceived: "A heart is waiting for you",
    back: "Back",
    blocksTitle: "Shared spaces",
    authBadge: "Private space for two",
    authTitle: "Feel closer every day",
    authSubtitle: "Questions, plans, places, and small rituals in one beautiful rhythm.",
    authAlt: "private access",
    authHint1: "Daily questions, shared plans, soft rituals",
    authHint2: "Designed first for iPhone-style mobile flow",
    emailPlaceholder: "you@email.com",
    passwordPlaceholder: "Your password",
    namePlaceholder: "Your name",
    usernamePlaceholder: "your_username",
    connectedState: "Connected",
    soloState: "Solo"
  },
  ru: {
    appName: "Lovio",
    appTagline: "\u041f\u0440\u043e\u0441\u0442\u0440\u0430\u043d\u0441\u0442\u0432\u043e \u0434\u043b\u044f \u0434\u0432\u043e\u0438\u0445",
    login: "\u0412\u043e\u0439\u0442\u0438",
    register: "\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f",
    email: "\u041f\u043e\u0447\u0442\u0430",
    username: "\u041b\u043e\u0433\u0438\u043d",
    password: "\u041f\u0430\u0440\u043e\u043b\u044c",
    name: "\u0418\u043c\u044f",
    gender: "\u041f\u043e\u043b",
    female: "\u0414\u0435\u0432\u0443\u0448\u043a\u0430",
    male: "\u041f\u0430\u0440\u0435\u043d\u044c",
    home: "\u0413\u043b\u0430\u0432\u043d\u0430\u044f",
    promptTab: "\u0412\u043e\u043f\u0440\u043e\u0441",
    goals: "\u0426\u0435\u043b\u0438",
    dates: "\u0421\u0432\u0438\u0434\u0430\u043d\u0438\u044f",
    wishes: "\u0416\u0435\u043b\u0430\u043d\u0438\u044f",
    places: "\u041c\u0435\u0441\u0442\u0430",
    importantDates: "\u0412\u0430\u0436\u043d\u044b\u0435 \u0434\u0430\u0442\u044b",
    save: "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
    logout: "\u0412\u044b\u0439\u0442\u0438",
    sendInvite: "\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0435\u043d\u0438\u0435",
    invitePlaceholder: "\u041f\u043e\u0447\u0442\u0430 \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430",
    answerQuestion: "\u0412\u043e\u043f\u0440\u043e\u0441 \u0434\u043d\u044f",
    dailyPromptTitle: "\u0412\u043e\u043f\u0440\u043e\u0441 \u0434\u043d\u044f",
    mood: "\u041d\u0430\u0441\u0442\u0440\u043e\u0435\u043d\u0438\u0435",
    answer: "\u041e\u0442\u0432\u0435\u0442",
    activities: "\u0410\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u043d\u0430 \u0441\u0435\u0433\u043e\u0434\u043d\u044f",
    noCouple: "\u041f\u0440\u0438\u0433\u043b\u0430\u0441\u0438 \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430, \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u043e\u0431\u0449\u0435\u0435 \u043f\u0440\u043e\u0441\u0442\u0440\u0430\u043d\u0441\u0442\u0432\u043e.",
    addGoal: "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0446\u0435\u043b\u044c",
    addPlace: "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043c\u0435\u0441\u0442\u043e",
    addDate: "\u041d\u0430\u0437\u043d\u0430\u0447\u0438\u0442\u044c \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u0435",
    addWish: "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0436\u0435\u043b\u0430\u043d\u0438\u0435",
    addImportantDate: "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0432\u0430\u0436\u043d\u0443\u044e \u0434\u0430\u0442\u0443",
    plannedFor: "\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043e \u043d\u0430",
    price: "\u0426\u0435\u043d\u0430",
    dateTitle: "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435",
    description: "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435",
    dateValue: "\u0414\u0430\u0442\u0430",
    pendingInvites: "\u041e\u0436\u0438\u0434\u0430\u044e\u0442 \u043e\u0442\u0432\u0435\u0442\u0430",
    accept: "\u041f\u0440\u0438\u043d\u044f\u0442\u044c",
    decline: "\u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c",
    submit: "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
    dashboard: "\u0413\u043b\u0430\u0432\u043d\u0430\u044f",
    dailyRevealWaiting: "\u041e\u0442\u0432\u0435\u0442\u044b \u043e\u0442\u043a\u0440\u043e\u044e\u0442\u0441\u044f, \u043a\u043e\u0433\u0434\u0430 \u043e\u0442\u0432\u0435\u0442\u044f\u0442 \u043e\u0431\u0430.",
    dailyRevealReady: "\u041e\u0431\u0430 \u043e\u0442\u0432\u0435\u0442\u0430 \u0443\u0436\u0435 \u043e\u0442\u043a\u0440\u044b\u0442\u044b.",
    chosenToday: "\u0412\u044b\u0431\u0440\u0430\u043d\u043e \u0441\u0435\u0433\u043e\u0434\u043d\u044f",
    statusPending: "\u041e\u0436\u0438\u0434\u0430\u0435\u0442",
    statusAccepted: "\u041f\u0440\u0438\u043d\u044f\u0442\u043e",
    statusDeclined: "\u041e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u043e",
    expiresIn: "\u0418\u0441\u0447\u0435\u0437\u043d\u0435\u0442 \u0447\u0435\u0440\u0435\u0437",
    noItems: "\u041f\u043e\u043a\u0430 \u043f\u0443\u0441\u0442\u043e.",
    you: "\u0412\u044b",
    done: "\u0413\u043e\u0442\u043e\u0432\u043e",
    visited: "\u041f\u043e\u0441\u0435\u0449\u0435\u043d\u043e",
    markVisited: "\u041e\u0442\u043c\u0435\u0442\u0438\u0442\u044c",
    activityLocked: "\u0410\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u043d\u0430 \u0441\u0435\u0433\u043e\u0434\u043d\u044f \u0443\u0436\u0435 \u0432\u044b\u0431\u0440\u0430\u043d\u0430.",
    statsTitle: "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043e\u0442\u043d\u043e\u0448\u0435\u043d\u0438\u0439",
    statsSubtitle: "\u041a\u043e\u0440\u043e\u0442\u043a\u0438\u0439 \u0441\u0440\u0435\u0437 \u0432\u0430\u0448\u0435\u0439 \u043e\u0431\u0449\u0435\u0439 \u0434\u0438\u043d\u0430\u043c\u0438\u043a\u0438 \u0438 \u0440\u0438\u0442\u043c\u0430.",
    statsPromptTogether: "\u0412\u043e\u043f\u0440\u043e\u0441\u044b \u0434\u043d\u044f \u0432\u043c\u0435\u0441\u0442\u0435",
    statsGoalsDone: "\u0412\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0435 \u0446\u0435\u043b\u0438",
    statsPlacesVisited: "\u041f\u043e\u0441\u0435\u0449\u0435\u043d\u043d\u044b\u0435 \u043c\u0435\u0441\u0442\u0430",
    statsDatesPlanned: "\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f",
    sendHeart: "\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0441\u0435\u0440\u0434\u0435\u0447\u043a\u043e",
    heartSent: "\u0421\u0435\u0440\u0434\u0435\u0447\u043a\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e",
    heartReceived: "\u0422\u0435\u0431\u0435 \u043f\u0440\u0438\u0448\u043b\u043e \u0441\u0435\u0440\u0434\u0435\u0447\u043a\u043e",
    back: "\u041d\u0430\u0437\u0430\u0434",
    blocksTitle: "\u041e\u0431\u0449\u0438\u0435 \u0431\u043b\u043e\u043a\u0438",
    authBadge: "\u041b\u0438\u0447\u043d\u043e\u0435 \u043f\u0440\u043e\u0441\u0442\u0440\u0430\u043d\u0441\u0442\u0432\u043e \u0434\u043b\u044f \u0434\u0432\u043e\u0438\u0445",
    authTitle: "\u0421\u0432\u044f\u0437\u044c, \u043a \u043a\u043e\u0442\u043e\u0440\u043e\u0439 \u0445\u043e\u0447\u0435\u0442\u0441\u044f \u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0430\u0442\u044c\u0441\u044f",
    authSubtitle: "\u0412\u043e\u043f\u0440\u043e\u0441\u044b, \u043f\u043b\u0430\u043d\u044b, \u043c\u0435\u0441\u0442\u0430 \u0438 \u043c\u0430\u043b\u0435\u043d\u044c\u043a\u0438\u0435 \u0440\u0438\u0442\u0443\u0430\u043b\u044b \u0432 \u043e\u0434\u043d\u043e\u043c \u043a\u0440\u0430\u0441\u0438\u0432\u043e\u043c \u0440\u0438\u0442\u043c\u0435.",
    authAlt: "\u043b\u0438\u0447\u043d\u044b\u0439 \u0432\u0445\u043e\u0434",
    authHint1: "\u0412\u043e\u043f\u0440\u043e\u0441 \u0434\u043d\u044f, \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f \u0438 \u043e\u0431\u0449\u0438\u0435 \u043c\u0435\u0447\u0442\u044b",
    authHint2: "\u041c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0439 \u0440\u0438\u0442\u043c \u0432 \u0434\u0443\u0445\u0435 iPhone",
    emailPlaceholder: "you@email.com",
    passwordPlaceholder: "\u041f\u0430\u0440\u043e\u043b\u044c",
    namePlaceholder: "\u0412\u0430\u0448\u0435 \u0438\u043c\u044f",
    usernamePlaceholder: "\u0432\u0430\u0448_\u043b\u043e\u0433\u0438\u043d",
    connectedState: "\u0412\u043c\u0435\u0441\u0442\u0435",
    soloState: "\u041e\u0434\u0438\u043d"
  }
};

const SESSION_COOKIE = "lovio_session";
const SESSION_DAYS = 30;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      return handleApi(request, env, url);
    }
    return env.ASSETS.fetch(request);
  }
};

async function handleApi(request, env, url) {
  try {
    const user = await getSessionUser(request, env);

    if (url.pathname === "/api/register" && request.method === "POST") {
      return api(await register(request, env));
    }
    if (url.pathname === "/api/login" && request.method === "POST") {
      return api(await login(request, env));
    }
    if (url.pathname === "/api/logout" && request.method === "POST") {
      return api({ ok: true }, 200, clearSessionCookie());
    }
    if (!user) {
      return api({ error: "Unauthorized" }, 401);
    }
    if (url.pathname === "/api/me" && request.method === "GET") {
      return api(await getDashboardPayload(env, user));
    }
    if (url.pathname === "/api/language" && request.method === "POST") {
      const body = await request.json();
      const language = body.language === "en" ? "en" : "ru";
      await env.DB.prepare("UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(language, user.id).run();
      return api({ ok: true, language });
    }
    if (url.pathname === "/api/heart-ping" && request.method === "POST") {
      return api(await sendHeartPing(env, user));
    }
    if (url.pathname === "/api/heart-pings/seen" && request.method === "POST") {
      return api(await markHeartPingsSeen(env, user));
    }
    if (url.pathname.match(/^\/api\/sections\/[^/]+\/seen$/) && request.method === "POST") {
      const sectionKey = url.pathname.split("/")[3];
      return api(await markSectionSeen(env, user, sectionKey));
    }
    if (url.pathname === "/api/invite/send" && request.method === "POST") {
      return api(await sendInvite(request, env, user));
    }
    if (url.pathname.match(/^\/api\/invite\/\d+\/respond$/) && request.method === "POST") {
      const invitationId = Number(url.pathname.split("/")[3]);
      return api(await respondInvite(request, env, user, invitationId));
    }
    if (url.pathname === "/api/daily-prompt/answer" && request.method === "POST") {
      return api(await answerDailyPrompt(request, env, user));
    }
    if (url.pathname === "/api/activities/select" && request.method === "POST") {
      return api(await selectActivity(request, env, user));
    }
    if (url.pathname === "/api/goals" && request.method === "POST") {
      return api(await addGoal(request, env, user));
    }
    if (url.pathname.match(/^\/api\/goals\/\d+\/complete$/) && request.method === "POST") {
      const goalId = Number(url.pathname.split("/")[3]);
      return api(await completeGoal(env, user, goalId));
    }
    if (url.pathname === "/api/places" && request.method === "POST") {
      return api(await addPlace(request, env, user));
    }
    if (url.pathname.match(/^\/api\/places\/\d+\/visit$/) && request.method === "POST") {
      const placeId = Number(url.pathname.split("/")[3]);
      return api(await visitPlace(env, user, placeId));
    }
    if (url.pathname === "/api/dates" && request.method === "POST") {
      return api(await addDatePlan(request, env, user));
    }
    if (url.pathname.match(/^\/api\/dates\/\d+\/respond$/) && request.method === "POST") {
      const dateId = Number(url.pathname.split("/")[3]);
      return api(await respondDate(request, env, user, dateId));
    }
    if (url.pathname === "/api/wishes" && request.method === "POST") {
      return api(await addWish(request, env, user));
    }
    if (url.pathname === "/api/important-dates" && request.method === "POST") {
      return api(await addImportantDate(request, env, user));
    }
    return api({ error: "Not found" }, 404);
  } catch (error) {
    return api({ error: error.message || "Server error" }, 400);
  }
}

function api(payload, status = 200, headers = {}) {
  const responseHeaders = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    ...(payload && payload._headers ? payload._headers : {}),
    ...headers
  };
  if (payload && typeof payload === "object" && payload._headers) {
    delete payload._headers;
  }
  return new Response(JSON.stringify(payload), {
    status,
    headers: responseHeaders
  });
}

async function register(request, env) {
  const body = await request.json();
  const username = clean(body.username);
  const email = clean(body.email).toLowerCase();
  const password = String(body.password || "");
  const name = clean(body.name);
  const gender = body.gender === "male" ? "male" : "female";
  if (!username || !email || !password || !name) {
    throw new Error("Missing required fields");
  }
  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ? OR username = ?").bind(email, username).first();
  if (existing) {
    throw new Error("User already exists");
  }
  const passwordHash = await hashPassword(password);
  const result = await env.DB.prepare(
    "INSERT INTO users (username, email, password_hash, name, gender, language) VALUES (?, ?, ?, ?, ?, 'ru')"
  ).bind(username, email, passwordHash, name, gender).run();
  const userId = result.meta.last_row_id;
  const session = await createSession(env, userId);
  return {
    ok: true,
    user: await getUserById(env, userId),
    _headers: session.headers
  };
}

async function login(request, env) {
  const body = await request.json();
  const email = clean(body.email).toLowerCase();
  const password = String(body.password || "");
  const user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
  if (!user || !(await verifyPassword(password, user.password_hash))) {
    throw new Error("Invalid credentials");
  }
  const session = await createSession(env, user.id);
  return {
    ok: true,
    user: await getUserById(env, user.id),
    _headers: session.headers
  };
}

async function sendInvite(request, env, user) {
  if (user.couple_id) {
    throw new Error("You are already in a couple");
  }
  const body = await request.json();
  const email = clean(body.email).toLowerCase();
  const partner = await env.DB.prepare("SELECT id, couple_id FROM users WHERE email = ?").bind(email).first();
  if (!partner || partner.id === user.id) {
    throw new Error("Partner not found");
  }
  if (partner.couple_id) {
    throw new Error("Partner is already in a couple");
  }
  await env.DB.prepare(
    "INSERT INTO invitations (sender_id, receiver_id, status) VALUES (?, ?, 'pending')"
  ).bind(user.id, partner.id).run();
  return { ok: true };
}

async function respondInvite(request, env, user, invitationId) {
  const body = await request.json();
  const action = body.action === "accept" ? "accept" : "decline";
  const invitation = await env.DB.prepare(
    "SELECT * FROM invitations WHERE id = ? AND receiver_id = ? AND status = 'pending'"
  ).bind(invitationId, user.id).first();
  if (!invitation) {
    throw new Error("Invitation not found");
  }
  if (action === "decline") {
    await env.DB.prepare(
      "UPDATE invitations SET status = 'declined', responded_at = CURRENT_TIMESTAMP WHERE id = ?"
    ).bind(invitationId).run();
    return { ok: true };
  }

  const sender = await env.DB.prepare("SELECT id, couple_id FROM users WHERE id = ?").bind(invitation.sender_id).first();
  const receiver = await env.DB.prepare("SELECT id, couple_id FROM users WHERE id = ?").bind(invitation.receiver_id).first();
  if (sender.couple_id || receiver.couple_id) {
    throw new Error("One of users is already in a couple");
  }

  const createCouple = await env.DB.prepare(
    "INSERT INTO couples (user1_id, user2_id, xp) VALUES (?, ?, 0)"
  ).bind(sender.id, receiver.id).run();
  const coupleId = createCouple.meta.last_row_id;

  await env.DB.batch([
    env.DB.prepare("UPDATE users SET couple_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(coupleId, sender.id),
    env.DB.prepare("UPDATE users SET couple_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(coupleId, receiver.id),
    env.DB.prepare("UPDATE invitations SET status = 'accepted', responded_at = CURRENT_TIMESTAMP WHERE id = ?").bind(invitationId)
  ]);
  return { ok: true };
}

async function answerDailyPrompt(request, env, user) {
  ensureCouple(user);
  const today = isoDate(new Date());
  const body = await request.json();
  const answerText = clean(body.answerText, 1200);
  const moodLevel = clamp(Number(body.moodLevel || 3), 1, 5);
  if (!answerText) {
    throw new Error("Answer is required");
  }
  const question = getDailyQuestion(user.couple_id, today, user.language);
  await env.DB.prepare(
    `INSERT INTO daily_prompt_responses (couple_id, user_id, question_date, question_key, answer_text, mood_level)
     VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(user_id, question_date) DO UPDATE SET answer_text = excluded.answer_text, mood_level = excluded.mood_level`
  ).bind(user.couple_id, user.id, today, question.key, answerText, moodLevel).run();
  return { ok: true };
}

async function selectActivity(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const code = clean(body.code);
  const today = isoDate(new Date());
  const existing = await env.DB.prepare(
    "SELECT id FROM activities WHERE user_id = ? AND activity_date = ?"
  ).bind(user.id, today).first();
  if (existing) {
    throw new Error((UI_TEXT[user.language || "ru"] || UI_TEXT.ru).activityLocked);
  }
  const choices = await getActivityChoices(env, user.couple_id, user.language, today);
  if (!choices.find((item) => item.code === code)) {
    throw new Error("Activity is not available today");
  }
  await env.DB.prepare(
    `INSERT INTO activities (couple_id, user_id, task_code, activity_date)
     VALUES (?, ?, ?, ?)`
  ).bind(user.couple_id, user.id, code, today).run();
  return { ok: true };
}

async function addGoal(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const text = clean(body.text, 300);
  if (!text) {
    throw new Error("Goal text is required");
  }
  await env.DB.prepare(
    "INSERT INTO goals (couple_id, creator_id, text) VALUES (?, ?, ?)"
  ).bind(user.couple_id, user.id, text).run();
  return { ok: true };
}

async function completeGoal(env, user, goalId) {
  ensureCouple(user);
  await env.DB.prepare(
    "UPDATE goals SET completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ? AND couple_id = ?"
  ).bind(goalId, user.couple_id).run();
  return { ok: true };
}

async function addPlace(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const name = clean(body.name, 200);
  if (!name) {
    throw new Error("Place name is required");
  }
  await env.DB.prepare(
    "INSERT INTO places (couple_id, creator_id, name) VALUES (?, ?, ?)"
  ).bind(user.couple_id, user.id, name).run();
  return { ok: true };
}

async function visitPlace(env, user, placeId) {
  ensureCouple(user);
  await env.DB.prepare(
    "UPDATE places SET visited = 1, visited_at = CURRENT_TIMESTAMP WHERE id = ? AND couple_id = ?"
  ).bind(placeId, user.couple_id).run();
  return { ok: true };
}

async function addDatePlan(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const title = clean(body.title, 200);
  const description = clean(body.description, 1000);
  const plannedDate = clean(body.plannedDate);
  if (!title || !plannedDate) {
    throw new Error("Title and date are required");
  }
  await env.DB.prepare(
    "INSERT INTO date_plans (couple_id, proposer_id, title, description, planned_date) VALUES (?, ?, ?, ?, ?)"
  ).bind(user.couple_id, user.id, title, description, plannedDate).run();
  return { ok: true };
}

async function respondDate(request, env, user, dateId) {
  ensureCouple(user);
  const body = await request.json();
  const action = body.action === "accept" ? "accepted" : "declined";
  const acceptedAt = action === "accepted" ? new Date().toISOString() : null;
  await env.DB.prepare(
    "UPDATE date_plans SET status = ?, accepted_at = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND couple_id = ?"
  ).bind(action, acceptedAt, dateId, user.couple_id).run();
  return { ok: true };
}

async function addWish(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const text = clean(body.text, 300);
  const price = clamp(Number(body.price || 0), 0, 1000000000);
  if (!text) {
    throw new Error("Wish is required");
  }
  await env.DB.prepare(
    "INSERT INTO wishes (couple_id, creator_id, text, price) VALUES (?, ?, ?, ?)"
  ).bind(user.couple_id, user.id, text, price).run();
  return { ok: true };
}

async function addImportantDate(request, env, user) {
  ensureCouple(user);
  const body = await request.json();
  const title = clean(body.title, 200);
  const dateValue = clean(body.dateValue);
  if (!title || !dateValue) {
    throw new Error("Title and date are required");
  }
  await env.DB.prepare(
    "INSERT INTO important_dates (couple_id, creator_id, title, date_value) VALUES (?, ?, ?, ?)"
  ).bind(user.couple_id, user.id, title, dateValue).run();
  return { ok: true };
}

async function sendHeartPing(env, user) {
  ensureCouple(user);
  await env.DB.prepare(
    "UPDATE couples SET xp = xp + 2 WHERE id = ?"
  ).bind(user.couple_id).run();
  return { ok: true, xpBoost: 2 };
}

async function markHeartPingsSeen(env, user) {
  ensureCouple(user);
  await env.DB.prepare(
    "UPDATE heart_pings SET seen_at = CURRENT_TIMESTAMP WHERE receiver_id = ? AND seen_at IS NULL"
  ).bind(user.id).run();
  return { ok: true };
}

async function markSectionSeen(env, user, sectionKey) {
  ensureCouple(user);
  const allowed = new Set(["goals", "places", "dates", "activities", "wishes", "importantDates"]);
  if (!allowed.has(sectionKey)) {
    throw new Error("Unknown section");
  }
  await env.DB.prepare(
    "INSERT INTO section_views (user_id, section_key, last_seen_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(user_id, section_key) DO UPDATE SET last_seen_at = CURRENT_TIMESTAMP"
  ).bind(user.id, sectionKey).run();
  return { ok: true, sectionKey };
}

async function getDashboardPayload(env, user) {
  const freshUser = await getUserById(env, user.id);
  const language = freshUser.language || "ru";
  const t = UI_TEXT[language] || UI_TEXT.ru;

  const pendingInvitations = await env.DB.prepare(
    "SELECT i.id, u.name, u.email FROM invitations i JOIN users u ON u.id = i.sender_id WHERE i.receiver_id = ? AND i.status = 'pending' ORDER BY i.created_at DESC"
  ).bind(freshUser.id).all();

  const dashboard = {
    user: freshUser,
    t,
    invitations: pendingInvitations.results || []
  };

  if (!freshUser.couple_id) {
    return dashboard;
  }

  const partner = await getPartner(env, freshUser);
  const couple = await env.DB.prepare("SELECT xp FROM couples WHERE id = ?").bind(freshUser.couple_id).first();
  const today = isoDate(new Date());
  const prompt = await getPromptState(env, freshUser, today);
  const activities = await getActivityBlock(env, freshUser, today);
  const unreadCounts = await getUnreadCounts(env, freshUser, today);
  const goals = await env.DB.prepare(
    "SELECT * FROM goals WHERE couple_id = ? ORDER BY completed ASC, created_at DESC LIMIT 12"
  ).bind(freshUser.couple_id).all();
  const places = await env.DB.prepare(
    "SELECT * FROM places WHERE couple_id = ? ORDER BY visited ASC, created_at DESC LIMIT 12"
  ).bind(freshUser.couple_id).all();
  const dates = await getVisibleDates(env, freshUser.couple_id);
  const wishes = await env.DB.prepare(
    "SELECT * FROM wishes WHERE couple_id = ? ORDER BY gifted ASC, created_at DESC LIMIT 12"
  ).bind(freshUser.couple_id).all();
  const importantDates = await env.DB.prepare(
    "SELECT * FROM important_dates WHERE couple_id = ? ORDER BY date_value ASC LIMIT 12"
  ).bind(freshUser.couple_id).all();

  return {
    ...dashboard,
    partner,
    coupleXp: Number(couple?.xp || 0),
    prompt,
    activities,
    unreadCounts,
    goals: goals.results || [],
    places: places.results || [],
    dates,
    wishes: wishes.results || [],
    importantDates: importantDates.results || []
  };
}

async function getPromptState(env, user, today) {
  const question = getDailyQuestion(user.couple_id, today, user.language);
  const rows = await env.DB.prepare(
    "SELECT user_id, answer_text, mood_level, created_at FROM daily_prompt_responses WHERE couple_id = ? AND question_date = ? ORDER BY created_at ASC"
  ).bind(user.couple_id, today).all();
  const responses = rows.results || [];
  const mine = responses.find((row) => row.user_id === user.id) || null;
  const bothAnswered = responses.length >= 2;
  return {
    question: question.text,
    key: question.key,
    myResponse: mine,
    bothAnswered,
    responses: bothAnswered ? responses : []
  };
}

async function getActivityBlock(env, user, today) {
  const choices = await getActivityChoices(env, user.couple_id, user.language, today);
  const selected = await env.DB.prepare(
    "SELECT user_id, task_code FROM activities WHERE couple_id = ? AND activity_date = ? ORDER BY created_at ASC"
  ).bind(user.couple_id, today).all();
  const selectedRows = selected.results || [];
  const mySelection = selectedRows.find((row) => row.user_id === user.id) || null;
  return {
    choices: mySelection ? [] : choices,
    mySelection: mySelection
      ? {
          user_id: mySelection.user_id,
          code: mySelection.task_code,
          label: translateActivity(mySelection.task_code, user.language)
        }
      : null,
    selected: selectedRows.map((row) => ({
      user_id: row.user_id,
      code: row.task_code,
      label: translateActivity(row.task_code, user.language)
    }))
  };
}

async function getActivityChoices(env, coupleId, language, today) {
  const cooldownCutoff = isoDate(addDays(new Date(today), -7));
  const usedRows = await env.DB.prepare(
    "SELECT DISTINCT task_code FROM activities WHERE couple_id = ? AND activity_date >= ?"
  ).bind(coupleId, cooldownCutoff).all();
  const used = new Set((usedRows.results || []).map((row) => row.task_code));
  const available = ACTIVITIES.filter((item) => !used.has(item.code));
  const source = available.length >= 6 ? available : ACTIVITIES;
  const seeded = [...source]
    .map((item) => ({ item, score: seededNumber(`${coupleId}:${today}:${item.code}`) }))
    .sort((a, b) => a.score - b.score)
    .slice(0, 6)
    .map(({ item }) => ({ code: item.code, label: item[language] || item.en }));
  return seeded;
}

async function getUnreadCounts(env, user, today) {
  const viewsRows = await env.DB.prepare(
    "SELECT section_key, last_seen_at FROM section_views WHERE user_id = ?"
  ).bind(user.id).all();
  const views = Object.fromEntries((viewsRows.results || []).map((row) => [row.section_key, row.last_seen_at]));
  const since = (key) => views[key] || "1970-01-01T00:00:00.000Z";

  const [goals, places, dates, wishes, importantDates, activities] = await Promise.all([
    scalarCount(env, "SELECT COUNT(*) AS count FROM goals WHERE couple_id = ? AND creator_id != ? AND created_at > ?", [user.couple_id, user.id, since("goals")]),
    scalarCount(env, "SELECT COUNT(*) AS count FROM places WHERE couple_id = ? AND creator_id != ? AND created_at > ?", [user.couple_id, user.id, since("places")]),
    scalarCount(env, "SELECT COUNT(*) AS count FROM date_plans WHERE couple_id = ? AND proposer_id != ? AND created_at > ?", [user.couple_id, user.id, since("dates")]),
    scalarCount(env, "SELECT COUNT(*) AS count FROM wishes WHERE couple_id = ? AND creator_id != ? AND created_at > ?", [user.couple_id, user.id, since("wishes")]),
    scalarCount(env, "SELECT COUNT(*) AS count FROM important_dates WHERE couple_id = ? AND creator_id != ? AND created_at > ?", [user.couple_id, user.id, since("importantDates")]),
    scalarCount(env, "SELECT COUNT(*) AS count FROM activities WHERE couple_id = ? AND user_id != ? AND activity_date = ? AND created_at > ?", [user.couple_id, user.id, today, since("activities")])
  ]);

  return { goals, places, dates, wishes, importantDates, activities };
}

async function getHeartUnreadCount(env, user) {
  const row = await env.DB.prepare(
    "SELECT COUNT(*) AS count FROM heart_pings WHERE receiver_id = ? AND seen_at IS NULL"
  ).bind(user.id).first();
  return Number(row?.count || 0);
}

async function scalarCount(env, sql, params) {
  const row = await env.DB.prepare(sql).bind(...params).first();
  return Number(row?.count || 0);
}

async function getVisibleDates(env, coupleId) {
  const rows = await env.DB.prepare(
    "SELECT * FROM date_plans WHERE couple_id = ? ORDER BY planned_date ASC, created_at DESC"
  ).bind(coupleId).all();
  const now = Date.now();
  const visible = [];
  for (const row of rows.results || []) {
    if (row.status === "accepted" && row.accepted_at) {
      const expiresAt = new Date(row.accepted_at).getTime() + 24 * 60 * 60 * 1000;
      if (expiresAt <= now) {
        await env.DB.prepare(
          "UPDATE date_plans SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        ).bind(row.id).run();
        continue;
      }
      row.expires_in_seconds = Math.max(0, Math.floor((expiresAt - now) / 1000));
    }
    if (row.status !== "completed") {
      visible.push(row);
    }
  }
  return visible;
}

async function getSessionUser(request, env) {
  const token = getCookie(request.headers.get("cookie") || "", SESSION_COOKIE);
  if (!token) {
    return null;
  }
  const session = await env.DB.prepare(
    "SELECT user_id, expires_at FROM sessions WHERE id = ?"
  ).bind(token).first();
  if (!session || new Date(session.expires_at).getTime() < Date.now()) {
    return null;
  }
  return getUserById(env, session.user_id);
}

async function createSession(env, userId) {
  const token = crypto.randomUUID();
  const expires = new Date(Date.now() + SESSION_DAYS * 24 * 60 * 60 * 1000).toISOString();
  await env.DB.prepare(
    "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)"
  ).bind(token, userId, expires).run();
  return {
    headers: {
      "Set-Cookie": `${SESSION_COOKIE}=${token}; HttpOnly; Path=/; SameSite=Lax; Max-Age=${SESSION_DAYS * 24 * 60 * 60}`
    }
  };
}

function clearSessionCookie() {
  return {
    "Set-Cookie": `${SESSION_COOKIE}=; HttpOnly; Path=/; SameSite=Lax; Max-Age=0`
  };
}

async function getUserById(env, userId) {
  return env.DB.prepare(
    "SELECT id, username, email, name, gender, language, couple_id, created_at FROM users WHERE id = ?"
  ).bind(userId).first();
}

async function getPartner(env, user) {
  const couple = await env.DB.prepare("SELECT * FROM couples WHERE id = ?").bind(user.couple_id).first();
  if (!couple) {
    return null;
  }
  const partnerId = couple.user1_id === user.id ? couple.user2_id : couple.user1_id;
  return getUserById(env, partnerId);
}

function getDailyQuestion(coupleId, dateText, language) {
  const index = seededNumber(`${coupleId}:${dateText}:question`) % QUESTIONS.length;
  const question = QUESTIONS[index];
  return { key: question.key, text: question[language] || question.en };
}

function translateActivity(code, language) {
  const item = ACTIVITIES.find((entry) => entry.code === code);
  return item ? item[language] || item.en : code;
}

function ensureCouple(user) {
  if (!user.couple_id) {
    throw new Error("Couple is required");
  }
}

function clean(value, max = 200) {
  return String(value || "").trim().slice(0, max);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function addDays(date, amount) {
  const copy = new Date(date);
  copy.setUTCDate(copy.getUTCDate() + amount);
  return copy;
}

function isoDate(date) {
  return new Date(date).toISOString().slice(0, 10);
}

function getCookie(cookieHeader, name) {
  const parts = cookieHeader.split(/;\s*/);
  for (const part of parts) {
    const [key, ...rest] = part.split("=");
    if (key === name) {
      return rest.join("=");
    }
  }
  return "";
}

function seededNumber(input) {
  let hash = 2166136261;
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash >>> 0);
}

async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    key,
    256
  );
  return `${toBase64(salt)}.${toBase64(new Uint8Array(bits))}`;
}

async function verifyPassword(password, stored) {
  const [saltBase64, hashBase64] = String(stored || "").split(".");
  if (!saltBase64 || !hashBase64) {
    return false;
  }
  const salt = fromBase64(saltBase64);
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    key,
    256
  );
  return toBase64(new Uint8Array(bits)) === hashBase64;
}

function toBase64(bytes) {
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

function fromBase64(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}
