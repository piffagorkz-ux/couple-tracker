# Lovio App Pack

Полный пак того, что нужно приложению Lovio, чтобы выглядеть как цельный продукт и быть готовым к нормальному релизу.

## 1. Brand Pack

- Основной логотип
- Иконка приложения
- Favicon / web icon
- Splash / launch logo
- Светлая версия логотипа
- Темная версия логотипа
- Мини-иконка без текста

### Цвета

- Primary coral
- Secondary blush
- Accent berry
- Male palette blue / teal
- Neutral background
- Text primary / secondary
- Success / error / warning

### Типографика

- Основной шрифт интерфейса
- Размеры заголовков
- Размеры текста кнопок
- Размеры текста карточек
- Мобильные размеры

## 2. Product Pack

### Core flow

- Регистрация
- Вход
- Привязка пары
- Вопрос дня
- Настроение
- Активности дня
- Цели
- Места
- Свидания
- Желания
- Важные даты
- Настройки

### Daily ritual pack

- 50+ вопросов дня
- Категории вопросов:
  - light
  - deep
  - romantic
  - playful
- Логика reveal после двух ответов
- История ответов
- Weekly recap

### Activities pack

- 100+ активностей
- Категории активностей:
  - home
  - talk
  - romantic
  - playful
  - outdoor
  - care
- Правило не повторять 7 дней
- 6 активностей в день

## 3. UI Pack

### Общие экраны

- Dashboard
- Goals
- Places
- Dates
- Activities
- Wishes
- Important Dates
- Settings
- Login
- Register
- 404
- 500

### Состояния экранов

- Empty state
- Loading state
- Error state
- Success state
- New notification state
- Paired / not paired state

### Mobile polish

- Safe-area
- Bottom nav
- Header spacing
- Tap targets
- Modal behavior
- Long Russian text fit
- iPhone-first spacing

## 4. Localization Pack

### Languages

- Russian
- English

### Что должно быть переведено полностью

- Заголовки
- Кнопки
- Placeholder-тексты
- Ошибки
- Alert-уведомления
- Статусы
- Onboarding copy
- Settings
- Notification text

## 5. App Store Pack

### Metadata

- App name
- Subtitle
- Short description
- Full description
- Keywords
- Category

### Visuals

- App icon 1024x1024
- iPhone screenshots
- iPad screenshots, если нужны
- Promotional graphic
- Optional preview video

### Store text

- Privacy copy
- Support URL
- Marketing URL
- Version notes

## 6. Technical Pack

### Backend

- Production config
- Stable DATABASE_URL
- SECRET_KEY
- Error handling
- CSRF
- Notification logic

### Database

- Postgres
- Migrations
- Seed strategy for questions / activities
- Backup awareness

### Deployment

- Render config
- Procfile / start command
- wsgi entry
- Env vars
- Domain / subdomain

## 7. Trust Pack

- Privacy Policy
- Terms of Use
- Data deletion policy
- Contact email
- Support page

## 8. Launch Pack

- Test checklist
- Beta feedback form
- Bug report template
- Release checklist
- Rollback checklist

## 9. Analytics Pack

- Registration complete
- Paired complete
- Daily question answered
- Activity selected
- Date accepted
- Goal completed
- Retention checkpoints:
  - Day 1
  - Day 7
  - Day 30

## 10. Priority Build Order

1. Brand pack finalization
2. UI polish on all live screens
3. Full localization
4. Daily ritual history
5. Weekly recap
6. Activities balancing
7. Dates memory flow
8. Onboarding cleanup
9. Store assets
10. Release prep

## 11. What “release-ready” means for Lovio

Lovio можно считать собранным как приложение, когда выполнены все условия:

- Есть финальный логотип и иконка
- Все живые вкладки выглядят единообразно
- Русский и английский работают без хвостов
- Пара может пройти полный сценарий без ошибки
- Данные сохраняются в production database
- Есть store assets и basic legal pages
- Есть 10-20 тестовых пользователей или пар

