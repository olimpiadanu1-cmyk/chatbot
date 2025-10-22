import re
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, CommandHandler, filters
from pathlib import Path
import json


REPLY_TEXT = (
    "Скачать можно по ссылке - ragerussia.online\n"
    "Если возникнут проблемы с установкой напишите в ЛС - t.me/crmp_manager или в тех.раздел(forum.ragerussia.online)"
)
REPLY_FORUM = "Ссылка на форум - forum.ragerussia.online"
REPLY_DONATE = "Задонатить можно через сайт - ragerussia.online/donate.html"
REPLY_PC = (
    "Скачать игру на ПК можно только через эмулятор\n"
    "Тема с гайдом на форуме - https://forum.ragerussia.online/threads/368/post-6799"
)

ADMIN_USER_ID = 6293484470
TRIGGERS_FILE = Path(__file__).with_name("triggers.json")

# Компилируем паттерны для быстрых проверок (регистронезависимо)
DOWNLOAD_PATTERNS = [
    re.compile(r"^\s*как\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+rage\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+rage\s+russia\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+рейджи\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+рейдж\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+rage\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+rage\s+russia\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+рейдж\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+реджи\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+рейджи\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+эту\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+эту\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*помогите\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*помогите\s+скачать\s+эту\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+ссылку\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+ссылку\s+скачать\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+ссылку\s+скачать\s+рейдж\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    # Новые варианты на скачивание
    re.compile(r"^\s*пж\s+кто-то\s+киньте\s+сылку\s+на\s+скачивание\s+в\s+лс\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+чтоб\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+на\s+скачивание\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+ссылку\s+чтоб\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+ссылку\s+на\s+скачивание\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+на\s+скачивание\s+в\s+лс\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+на\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+на\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+на\s+скачивание\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+чтоб\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+скачать\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+ссылку\s+скачать\s+рейдж\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+скачать\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*киньте\s+сылку\s+скачать\s+рейдж\s+рашу\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+то\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+то\s+скачать\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+качать\s+то\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+качать\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+установить\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+загрузить\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
]

# Точные паттерны запросов про установку/скачивание на ПК
PC_DOWNLOAD_PATTERNS = [
    re.compile(r"^\s*как\s+скачать\s+игру\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+игру\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скачать\s+игру\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скачать\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+рейдж\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+рейдж\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+скачать\s+рейдж\s+рашу\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+скачать\s+рейдж\s+рашу\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скачать\s+рейдж\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скачать\s+рейдж\s+рашу\s+на\s+пк\s*\??\s*$", re.IGNORECASE | re.UNICODE),
]

FORUM_PATTERNS = [
    re.compile(r"^\s*скиньте\s+ссылку\s+на\s+форум\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скинь\s+ссылку\s+на\s+форум\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+форум\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скиньте\s+форум\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*скинь\s+форум\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+форум\s+рейдж\s+раш[аи]\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+форум\s+rage\s+russia\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+форум\s+рейджа\s*\??\s*$", re.IGNORECASE | re.UNICODE),
]

DONATE_PATTERNS = [
    re.compile(r"^\s*где\s+задонатить\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+задонатить\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+задонатить\s+сюда\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+задонатить\s+в\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+задонатить\s+в\s+игру\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*как\s+задонатить\s+в\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*где\s+задонатить\s+в\s+рейдж\s*\??\s*$", re.IGNORECASE | re.UNICODE),
]


# ===== Динамические фразы (редактируются админом) =====
# Хранятся в triggers.json; совпадение строгое (как у статических): пробелы по краям игнорируются,
# опциональный вопросительный знак в конце допускается.
DYN_DOWNLOAD = []  # type: list[str]
DYN_PC = []        # type: list[str]
DYN_FORUM = []     # type: list[str]
DYN_DONATE = []    # type: list[str]


def _phrase_to_regex(phrase: str) -> re.Pattern:
    esc = re.escape(phrase.strip())
    return re.compile(rf"^\s*{esc}\s*\??\s*$", re.IGNORECASE | re.UNICODE)


def _load_triggers() -> None:
    global DYN_DOWNLOAD, DYN_PC, DYN_FORUM, DYN_DONATE
    if TRIGGERS_FILE.exists():
        try:
            data = json.loads(TRIGGERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        DYN_DOWNLOAD = list(dict.fromkeys(map(str, data.get("download", []))))
        DYN_PC = list(dict.fromkeys(map(str, data.get("pc", []))))
        DYN_FORUM = list(dict.fromkeys(map(str, data.get("forum", []))))
        DYN_DONATE = list(dict.fromkeys(map(str, data.get("donate", []))))
    else:
        DYN_DOWNLOAD, DYN_PC, DYN_FORUM, DYN_DONATE = [], [], [], []


def _save_triggers() -> None:
    data = {
        "download": DYN_DOWNLOAD,
        "pc": DYN_PC,
        "forum": DYN_FORUM,
        "donate": DYN_DONATE,
    }
    TRIGGERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_reply(text: str) -> str | None:
    if not text:
        return None
    t = text.strip()
    # Сначала проверяем запросы про ПК
    # Динамические ПК-фразы
    for s in DYN_PC:
        if _phrase_to_regex(s).search(t):
            return REPLY_PC
    for p in PC_DOWNLOAD_PATTERNS:
        if p.search(t):
            return REPLY_PC
    # Динамические общие скачивания
    for s in DYN_DOWNLOAD:
        if _phrase_to_regex(s).search(t):
            return REPLY_TEXT
    for p in DOWNLOAD_PATTERNS:
        if p.search(t):
            return REPLY_TEXT
    # Динамические форум
    for s in DYN_FORUM:
        if _phrase_to_regex(s).search(t):
            return REPLY_FORUM
    for p in FORUM_PATTERNS:
        if p.search(t):
            return REPLY_FORUM
    # Динамические донат
    for s in DYN_DONATE:
        if _phrase_to_regex(s).search(t):
            return REPLY_DONATE
    for p in DONATE_PATTERNS:
        if p.search(t):
            return REPLY_DONATE
    return None


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not message.text:
        return
    chat = update.effective_chat
    if not chat or chat.type == "private":
        return

    reply = get_reply(message.text)
    if reply:
        await message.reply_text(reply)


def _is_admin(update: Update) -> bool:
    try:
        return ADMIN_USER_ID != 0 and update.effective_user and update.effective_user.id == ADMIN_USER_ID
    except Exception:
        return False


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type != "private":
        return
    if not _is_admin(update):
        return
    def _patterns_to_lines(title: str, pats: list[re.Pattern]) -> list[str]:
        lines = [f"[{title}] ({len(pats)})"]
        for p in pats:
            lines.append(p.pattern)
        return lines
    # Собираем список
    lines: list[str] = []
    lines += _patterns_to_lines("DOWNLOAD (static)", DOWNLOAD_PATTERNS)
    lines += ["DOWNLOAD (dynamic):"] + [f"- {s}" for s in DYN_DOWNLOAD]
    lines += _patterns_to_lines("PC (static)", PC_DOWNLOAD_PATTERNS)
    lines += ["PC (dynamic):"] + [f"- {s}" for s in DYN_PC]
    lines += _patterns_to_lines("FORUM (static)", FORUM_PATTERNS)
    lines += ["FORUM (dynamic):"] + [f"- {s}" for s in DYN_FORUM]
    lines += _patterns_to_lines("DONATE (static)", DONATE_PATTERNS)
    lines += ["DONATE (dynamic):"] + [f"- {s}" for s in DYN_DONATE]
    text = "\n".join(lines)
    # Делим при необходимости на части по 3500 символов
    chunk_size = 3500
    for i in range(0, len(text), chunk_size):
        await update.effective_message.reply_text(text[i:i+chunk_size])


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type != "private":
        return
    if not _is_admin(update):
        return
    # Ожидается: /add <категория> <фраза>
    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text(
            "Использование: /add <download|pc|forum|donate> <фраза>"
        )
        return
    category = (context.args[0] or "").strip().lower()
    phrase = " ".join(context.args[1:]).strip()
    if not phrase:
        await update.effective_message.reply_text("Пустая фраза не допускается")
        return
    added = False
    if category == "download":
        if phrase not in DYN_DOWNLOAD:
            DYN_DOWNLOAD.append(phrase)
            added = True
    elif category == "pc":
        if phrase not in DYN_PC:
            DYN_PC.append(phrase)
            added = True
    elif category == "forum":
        if phrase not in DYN_FORUM:
            DYN_FORUM.append(phrase)
            added = True
    elif category == "donate":
        if phrase not in DYN_DONATE:
            DYN_DONATE.append(phrase)
            added = True
    else:
        await update.effective_message.reply_text("Неизвестная категория. Доступны: download, pc, forum, donate")
        return
    if added:
        _save_triggers()
        await update.effective_message.reply_text(f"Добавлено в {category}: {phrase}")
    else:
        await update.effective_message.reply_text("Такой вариант уже есть")


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type != "private":
        return
    if not _is_admin(update):
        return
    # Ожидается: /remove <категория> <фраза>
    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text(
            "Использование: /remove <download|pc|forum|donate> <фраза>"
        )
        return
    category = (context.args[0] or "").strip().lower()
    phrase = " ".join(context.args[1:]).strip()
    if not phrase:
        await update.effective_message.reply_text("Пустая фраза не допускается")
        return
    removed = False
    if category == "download":
        if phrase in DYN_DOWNLOAD:
            DYN_DOWNLOAD.remove(phrase)
            removed = True
    elif category == "pc":
        if phrase in DYN_PC:
            DYN_PC.remove(phrase)
            removed = True
    elif category == "forum":
        if phrase in DYN_FORUM:
            DYN_FORUM.remove(phrase)
            removed = True
    elif category == "donate":
        if phrase in DYN_DONATE:
            DYN_DONATE.remove(phrase)
            removed = True
    else:
        await update.effective_message.reply_text("Неизвестная категория. Доступны: download, pc, forum, donate")
        return
    if removed:
        _save_triggers()
        await update.effective_message.reply_text(f"Удалено из {category}: {phrase}")
    else:
        await update.effective_message.reply_text("Такой фразы нет в динамическом списке")


def main() -> None:
    token = "7738883966:AAF2kZulAtdEyQd2lgz9GoGsRjtoVVeS6QE"

    _load_triggers()
    app = Application.builder().token(token).build()

    # Обрабатываем все текстовые сообщения (кроме команд)
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, on_message))
    # Команды администратора только в ЛС
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("remove", cmd_remove))

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling(allowed_updates=["message"])  # простейший polling


if __name__ == "__main__":
    main()
