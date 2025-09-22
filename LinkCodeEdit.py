"""
LinkCodeEdit - Многофункциональный редактор кода и веб-инструментов

Автор приложения: Савин Евгений Олегович
Сайт автора: https://www.linkfirst.ru
Сайт программы: https://linkcodeedit.com
Email: b2b@linkfirst.ru
Лицензия: MIT License

Используемые сторонние компоненты:

1. PySide6
   - Лицензия: LGPLv3
   - Автор: The Qt Company Ltd.
   - Сайт: https://pypi.org/project/PySide6/
   - Версия: >=6.0.0

2. Pillow (PIL Fork)
   - Лицензия: PIL Software License
   - Автор: Secret Labs AB, Fredrik Lundh
   - Сайт: https://pypi.org/project/Pillow/
   - Версия: >=9.0.0
   - Примечание: Опциональная зависимость для генерации favicon

3. Стандартные библиотеки Python
   - Лицензия: Python Software Foundation License
   - Автор: Python Software Foundation
"""
from __future__ import annotations
import os, sys, re, json, base64, tempfile, random, string, webbrowser
from typing import List, Tuple, Optional
from pathlib import Path
def _install_crash_guard():
    import sys, traceback, tempfile
    from pathlib import Path as _Path
    def _hook(exctype, value, tb):
        txt = ''.join(traceback.format_exception(exctype, value, tb))
        try:
            p = _Path(tempfile.gettempdir()) / "linkcodeedit_crash.log"
            p.write_text(txt, encoding="utf-8")
        except Exception:
            pass
        try:            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Fatal error", txt[:2000] + "\n\nПолный лог: linkcodeedit_crash.log")
        except Exception:
            pass        
        sys.__excepthook__(exctype, value, tb)
    sys.excepthook = _hook
def resource_path(*parts) -> Path:    
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base.joinpath(*parts)
ASSETS_DIR = resource_path("assets")
ICON_CANDIDATES = [    
    resource_path("favicon.ico"),
    resource_path("favicon.png"),
    resource_path("icon.ico"),
    resource_path("icon.png"),    
    ASSETS_DIR / "favicon.ico",
    ASSETS_DIR / "favicon.png",
    ASSETS_DIR / "icon.ico",
    ASSETS_DIR / "icon.png",    
    Path(__file__).parent / "favicon.ico",
    Path(__file__).parent / "favicon.png",
    Path(__file__).parent / "icon.ico",
    Path(__file__).parent / "icon.png",
]
def _find_first_icon(paths) -> Optional[Path]:
    for p in paths:
        try:
            if p and p.exists():
                return p
        except Exception:
            pass
    return None
APP_ICON_PATH = _find_first_icon(ICON_CANDIDATES)

OG_ICON_CANDIDATES = [
    Path(__file__).parent / "og.ico",
    Path(__file__).parent / "og.png",
    ASSETS_DIR / "og.ico",
    ASSETS_DIR / "og.png",
]
OG_ICON_PATH = ASSETS_DIR / "og.png"
APP_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_FILE_DIR not in sys.path:
    sys.path.insert(0, APP_FILE_DIR)
PARENT_DIR = os.path.dirname(APP_FILE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
APP_ORG  = "LinkCodeEdit"
APP_NAME = "LinkCodeEdit"
APP_VER  = "1"
from PySide6.QtCore import (
    Qt, QSettings, QObject, Signal, QSize, QTimer, QRect, QSignalBlocker, QUrl,
    QThread,         
)

from PySide6.QtGui import (
    QAction, QKeySequence, QShortcut, QFont, QTextOption, QColor, QPainter,
    QTextCharFormat, QIcon, QDesktopServices
    
)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QStatusBar, QMenu,
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QRadioButton,
    QWidget, QHBoxLayout, QSplitter, QPlainTextEdit, QMessageBox,
    QCheckBox, QPushButton, QSpinBox, QComboBox, QLineEdit,
    QFileDialog, QTextBrowser,
    QDoubleSpinBox,     
)

from html.parser import HTMLParser


TR = {
    "ru": {        
        "app.title": "LinkCodeEdit",
        "menu.file": "&Файл",
        "menu.edit": "&Правка",
        "menu.lang": "&Язык",
        "menu.help": "&Справка",
        "act.open": "Открыть…",
        "act.save": "Сохранить результат…",
        "act.exit": "Выход",
        "act.copy": "Копировать результат",
        "act.paste": "Вставить во вход",
        "act.swap": "Поменять Вход↔Выход",
        "act.clear": "Очистить оба поля",        
        "act.help.instructions": "Инструкция",
        "act.about": "О программе",
        "help.fallback": "Добро пожаловать в LinkCodeEdit. Инструкция не найдена.",        
        "tab.clean": "🧹 Комментарии (All)",
        "tab.format": "✨ Форматирование",
        "tab.link": "🔗 JS-ссылка",
        "tab.obf": "🕵️ Обфускация",
        "tab.utm":  "🏷️ UTM-метки",
        "tab.slug": "🔤 ЧПУ (slug)",
        "tab.stats":"🔢 Количество символов",
        "tab.pass": "🔐 Генератор паролей",
        "tab.batch":"📦 Пакетная обработка",        
        "clean.header": "Удаление комментариев",
        "clean.mode": "Режим:",
        "clean.mode.all": "All (все типы комментариев)",
        "clean.mode.html": "HTML/XML",
        "clean.mode.css": "CSS",
        "clean.mode.js": "JavaScript",
        "clean.mode.php": "PHP",
        "clean.mode.json": "JSON",
        "clean.mode.py": "Python",
        "clean.run": "Удалить комментарии",
        "clean.copy": "Скопировать результат",        
        "fmt.header": "Форматирование / Минификация",
        "fmt.tabs": "Табы",
        "fmt.indent": "Отступ",
        "fmt.sort": "JSON: сортировать ключи",
        "fmt.pretty": "Форматировать",
        "fmt.minify": "Минифицировать",        
        "js.header": "Генератор закодированной ссылки (JS)",
        "js.url": "URL:",
        "js.text": "Текст:",
        "js.view": "Вид:",
        "js.gen": "Сгенерировать",
        "js.open": "Проверить (открыть)",        
        "obf.header": "Обфускация / Деобфускация",
        "obf.method": "Метод:",
        "obf.m.eval64": "JS: eval(Base64)",
        "obf.m.hex": "JS: Hex-escape + eval",
        "obf.m.container": "Base64-контейнер (по языку)",
        "obf.comment": "Комментарий:",
        "obf.run": "Обфусцировать",
        "obf.deobf": "Деобфусцировать",
        "obf.addc": "Добавить комментарий к результату",
        "obf.test": "Тест JS в браузере",        
        "status.copied": "Результат скопирован",
        "status.cleared": "Очищено",
        "tab.utm": "UTM-метки",
        "tab.slug": "ЧПУ (slug)",
        "tab.stats": "Количество символов",
        "tab.pass": "Генератор паролей",
        "tab.batch": "Пакетная обработка",
        "utm.header": "UTM-метки",
        "utm.url": "URL:",
        "utm.override": "Перезаписывать существующие",
        "utm.gen": "Сгенерировать",
        "utm.open": "Открыть",
        "utm.url_empty": "Укажите базовый URL",
        "utm.link_text": "Ссылка с UTM",
        "slug.header": "Генератор slug",
        "slug.lower": "нижний регистр",
        "slug.translit": "транслитерация (RU→EN)",
        "slug.sep": "разделитель",
        "slug.max": "макс. длина",
        "slug.make": "Сделать slug",
        "stats.header": "Подсчёт символов",
        "stats.count": "Посчитать",
        "stats.total": "Всего символов",
        "stats.no_spaces": "Без пробельных",
        "stats.spaces": "Пробелы",
        "stats.tabs": "Табы",
        "stats.newlines": "Переводы строк",
        "stats.words": "Слова",
        "stats.lines": "Строки",
        "stats.letters": "Буквы",
        "stats.digits": "Цифры",
        "stats.punct": "Знаки препинания",
        "stats.unique": "Уникальные символы",
        "stats.done": "Готово",
        "pass.header": "Генератор паролей",
        "pass.length": "Длина",
        "pass.count": "Кол-во",
        "pass.lower": "строчные",
        "pass.upper": "прописные",
        "pass.digits": "цифры",
        "pass.symbols": "символы",
        "pass.no_amb": "без неоднозначных",
        "pass.gen": "Сгенерировать",
        "batch.header": "Пакетная обработка",
        "batch.placeholder": "Здесь появится пакетная обработка файлов (в разработке).",        
        "ui.lang": "Язык",
        "ui.in": "Вход",
        "ui.out": "Выход",
        "ui.diff": "Разн.",
        "act.license": "Лицензионное соглашение",
        "utm.source": "Источник",
        "utm.medium": "Канал",
        "utm.campaign": "Кампания",
        "utm.term": "Ключевое слово",
        "utm.content": "Контент",
        "tab.og": "🧩 OG Метатеги",
        "og.header": "Open Graph — генератор мета-тегов",
        "og.type": "Тип страницы",
        "og.title": "Заголовок",
        "og.desc": "Описание",
        "og.image": "Картинка (URL)",
        "og.url": "Постоянный URL",
        "og.site_name": "Имя сайта",
        "og.locale": "Язык (locale)",
        "og.app_id": "ID соц. сети (fb:app_id)",
        "og.video": "Видео (URL)",
        "og.extra": "Доп. метаданные",
        "og.gen": "Сгенерировать",
        "og.bot": "Сброс OG кэша: @WebpageBot",
        "act.donate": "Поддержать проект ❤️",
        "about.support": "Поддержать развитие проекта:",
        "clean.mode.custom": "Выборочно",
        "clean.sel_types": "Удалять:",
        "clean.type.html": "HTML <!-- -->",
        "clean.type.cblock": "/* ... */",
        "clean.type.cline": "// ...",
        "clean.type.hash": "# ...",
        "fmt.blank": "Пустые строки (макс.)",
        "fmt.trim": "Убирать пробелы в конце строк",
        "tab.favicon": "🖼️ Favicon",
        "fav.header": "Генератор фавиконок",
        "fav.src": "Источник (PNG/JPG/ICO)",
        "fav.outdir": "Папка сохранения",
        "fav.urlprefix": "URL-префикс (href)",
        "fav.themecolor": "Цвет темы (#rrggbb)",
        "fav.appname": "Имя приложения",
        "fav.pickimg": "Выбрать...",
        "fav.pickdir": "Папка...",
        "fav.generate": "Сгенерировать",
        "fav.open": "Открыть папку",
        "fav.copy": "Скопировать сниппет",
        "tab.sitemap": "🗺️ Sitemap",
        "smap.header": "Sitemap — генератор карты сайта",
        "smap.mode": "Режим",
        "smap.mode.list": "Из списка URL/путей",
        "smap.mode.scan": "Сканировать папку (HTML)",
        "smap.mode.http": "Сканировать сайт (HTTP)",
        "smap.base": "Базовый URL",
        "smap.folder": "Папка",
        "smap.pickdir": "Папка...",
        "smap.freq": "changefreq",
        "smap.prio": "priority",
        "smap.lastmod": "lastmod",
        "smap.lastmod.today": "Сегодня для всех",
        "smap.lastmod.mtime": "Из mtime файлов",
        "smap.keepquery": "С query-параметрами",
        "smap.samehost": "Только этот хост",
        "smap.robots": "Учитывать robots.txt",
        "smap.maxpages": "Макс. страниц",
        "smap.maxdepth": "Макс. глубина",
        "smap.delay": "Задержка, мс",
        "smap.timeout": "Таймаут, сек",
        "smap.ua": "User-Agent",
        "smap.generate": "Сгенерировать",
        "smap.save": "Сохранить…",
        "smap.copy": "Скопировать",
        "smap.open": "Открыть папку",
        "smap.placeholder": "Один URL или путь на строку. Пустые/с # игнорируются.",
        "smap.base_empty": "Укажите базовый URL (например, https://example.com)",
        "smap.scan_warn": "Укажите папку для сканирования",
        "smap.done": "Готово",
        "smap.too_many": "Внимание: >50 000 URL — разбейте на несколько файлов",
        "smap.progress": "Скан: {done}/{limit}",
        "smap.stop": "Остановить",
        "tab.robots": "🤖 robots.txt",
        "robots.header": "robots.txt — шаблоны",
        "robots.preset": "Шаблон",
        "robots.host": "Host",
        "robots.sitemap": "Sitemap",
        "robots.crawl": "Crawl-delay (сек.)",
        "robots.cleanparam": "Clean-param (Яндекс)",
        "robots.extra": "Доп. правила",
        "robots.generate": "Сгенерировать",
        "robots.copy": "Скопировать",
        "robots.presets.basic": "Базовый (разрешить всё)",
        "robots.presets.blockall": "Запретить всё",
        "robots.presets.wordpress": "WordPress",
        "robots.presets.bitrix": "1C-Битрикс",
        "robots.note": "Поддерживаются: Host, Sitemap, Clean-param, Crawl-delay",

    },
    "en": {
        "app.title": "LinkCodeEdit",
        "menu.file": "&File",
        "menu.edit": "&Edit",
        "menu.lang": "&Language",
        "menu.help": "&Help",
        "act.open": "Open…",
        "act.save": "Save result…",
        "act.exit": "Exit",
        "act.copy": "Copy result",
        "act.paste": "Paste to input",
        "act.swap": "Swap In↔Out",
        "act.clear": "Clear both",
        "act.license": "License Agreement",
        "act.help.instructions": "Instructions",
        "act.about": "About",
        "help.fallback": "Welcome to LinkCodeEdit. Instructions not found.",
        "tab.clean": "🧹 Comments (All)",
        "tab.format": "✨ Formatting",
        "tab.link": "🔗 JS Link",
        "tab.obf": "🕵️ Obfuscation",
        "tab.utm":  "🏷️ UTM Tags",
        "tab.slug": "🔤 Slug",
        "tab.stats":"🔢 Character Count",
        "tab.pass": "🔐 Password Generator",
        "tab.batch":"📦 Batch",
        "clean.header": "Remove Comments",
        "clean.mode": "Mode:",
        "clean.mode.all": "All (remove all kinds)",
        "clean.mode.html": "HTML/XML",
        "clean.mode.css": "CSS",
        "clean.mode.js": "JavaScript",
        "clean.mode.php": "PHP",
        "clean.mode.json": "JSON",
        "clean.mode.py": "Python",
        "clean.run": "Strip comments",
        "clean.copy": "Copy result",
        "fmt.header": "Formatting / Minification",
        "fmt.tabs": "Tabs",
        "fmt.indent": "Indent",
        "fmt.sort": "JSON: sort keys",
        "fmt.pretty": "Format",
        "fmt.minify": "Minify",
        "js.header": "Encoded Link Generator (JS)",
        "js.url": "URL:",
        "js.text": "Text:",
        "js.view": "View:",
        "js.gen": "Generate",
        "js.open": "Open (test)",
        "obf.header": "Obfuscation / Deobfuscation",
        "obf.method": "Method:",
        "obf.m.eval64": "JS: eval(Base64)",
        "obf.m.hex": "JS: Hex-escape + eval",
        "obf.m.container": "Base64 container (per language)",
        "obf.comment": "Comment:",
        "obf.run": "Obfuscate",
        "obf.deobf": "Deobfuscate",
        "obf.addc": "Append comment to result",
        "obf.test": "Test JS in browser",
        "status.copied": "Result copied",
        "status.cleared": "Cleared",
        "tab.utm": "UTM Tags",
        "tab.slug": "Slug",
        "tab.stats": "Character Count",
        "tab.pass": "Password Generator",
        "tab.batch": "Batch",
        "utm.header": "UTM Tags",
        "utm.url": "URL:",
        "utm.override": "Override existing",
        "utm.gen": "Generate",
        "utm.open": "Open",
        "utm.url_empty": "Enter base URL",
        "utm.link_text": "Link with UTM",
        "slug.header": "Slug Generator",
        "slug.lower": "lowercase",
        "slug.translit": "transliterate (RU→EN)",
        "slug.sep": "separator",
        "slug.max": "max length",
        "slug.make": "Make slug",
        "stats.header": "Character count",
        "stats.count": "Count",
        "stats.total": "Total chars",
        "stats.no_spaces": "Non-whitespace",
        "stats.spaces": "Spaces",
        "stats.tabs": "Tabs",
        "stats.newlines": "Newlines",
        "stats.words": "Words",
        "stats.lines": "Lines",
        "stats.letters": "Letters",
        "stats.digits": "Digits",
        "stats.punct": "Punctuation",
        "stats.unique": "Unique chars",
        "stats.done": "Done",
        "pass.header": "Password generator",
        "pass.length": "Length",
        "pass.count": "Count",
        "pass.lower": "lower",
        "pass.upper": "upper",
        "pass.digits": "digits",
        "pass.symbols": "symbols",
        "pass.no_amb": "no ambiguous",
        "pass.gen": "Generate",
        "batch.header": "Batch processing",
        "batch.placeholder": "Batch file processing will appear here (WIP).",        
        "ui.lang": "Language",
        "ui.in": "In",
        "ui.out": "Out",
        "ui.diff": "Diff",
        "utm.source": "Source",
        "utm.medium": "Medium",
        "utm.campaign": "Campaign",
        "utm.term": "Term",
        "utm.content": "Content",
        "tab.og": "🧩 OG Meta Tags",
        "og.header": "Open Graph — meta generator",
        "og.type": "Type",
        "og.title": "Title",
        "og.desc": "Description",
        "og.image": "Image (URL)",
        "og.url": "Canonical URL",
        "og.site_name": "Site name",
        "og.locale": "Locale",
        "og.app_id": "App ID (fb:app_id)",
        "og.video": "Video (URL)",
        "og.extra": "Extra meta",
        "og.gen": "Generate",
        "og.bot": "Purge OG cache: @WebpageBot",
        "act.donate": "Donate ❤️",
        "about.support": "Support the project:",
        "clean.mode.custom": "Custom",
        "clean.sel_types": "Remove:",
        "clean.type.html": "HTML <!-- -->",
        "clean.type.cblock": "/* ... */",
        "clean.type.cline": "// ...",
        "clean.type.hash": "# ...",        
        "fmt.blank": "Blank lines (max.)",
        "fmt.trim": "Trim trailing spaces",
        "tab.favicon": "🖼️ Favicon",
        "fav.header": "Favicon Generator",
        "fav.src": "Source (PNG/JPG/ICO)",
        "fav.outdir": "Output folder",
        "fav.urlprefix": "URL prefix (href)",
        "fav.themecolor": "Theme color (#rrggbb)",
        "fav.appname": "App name",
        "fav.pickimg": "Browse…",
        "fav.pickdir": "Folder…",
        "fav.generate": "Generate",
        "fav.open": "Open folder",
        "fav.copy": "Copy snippet",
        "tab.sitemap": "🗺️ Sitemap",
        "smap.header": "Sitemap — generator",
        "smap.mode": "Mode",
        "smap.mode.list": "From URL/path list",
        "smap.mode.scan": "Scan folder (HTML)",
        "smap.mode.http": "Scan website (HTTP)",
        "smap.base": "Base URL",
        "smap.folder": "Folder",
        "smap.pickdir": "Folder…",
        "smap.freq": "changefreq",
        "smap.prio": "priority",
        "smap.lastmod": "lastmod",
        "smap.lastmod.today": "Today for all",
        "smap.lastmod.mtime": "From files mtime",
        "smap.keepquery": "Keep query params",
        "smap.samehost": "Same host only",
        "smap.robots": "Respect robots.txt",
        "smap.maxpages": "Max pages",
        "smap.maxdepth": "Max depth",
        "smap.delay": "Delay, ms",
        "smap.timeout": "Timeout, s",
        "smap.ua": "User-Agent",
        "smap.generate": "Generate",
        "smap.save": "Save…",
        "smap.copy": "Copy",
        "smap.open": "Open folder",
        "smap.placeholder": "One URL or path per line. Blank/# lines ignored.",
        "smap.base_empty": "Enter base URL (e.g. https://example.com)",
        "smap.scan_warn": "Pick a folder to scan",
        "smap.done": "Done",
        "smap.too_many": "Warning: >50,000 URLs — split into multiple files",
        "smap.progress": "Scan: {done}/{limit}",
        "smap.stop": "Stop",
        "tab.robots": "🤖 robots.txt",
        "robots.header": "robots.txt — templates",
        "robots.preset": "Preset",
        "robots.host": "Host",
        "robots.sitemap": "Sitemap",
        "robots.crawl": "Crawl-delay (sec)",
        "robots.cleanparam": "Clean-param (Yandex)",
        "robots.extra": "Extra rules",
        "robots.generate": "Generate",
        "robots.copy": "Copy",
        "robots.presets.basic": "Basic (allow all)",
        "robots.presets.blockall": "Block all",
        "robots.presets.wordpress": "WordPress",
        "robots.presets.bitrix": "1C-Bitrix",
        "robots.note": "Supports: Host, Sitemap, Clean-param, Crawl-delay",
    },
}
class I18N(QObject):
    language_changed = Signal(str)
    def __init__(self):
        super().__init__()
        self._lang = "ru"
        self._cache = {}
        self._callbacks = []
    def load(self, lang: str):
        import json
        lang = (lang or "ru").lower()
        path = ASSETS_DIR / f"i18n_{lang}.json"
        fallback = ASSETS_DIR / "i18n_en.json"
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
        if not data and fallback.exists():
            with open(fallback, "r", encoding="utf-8") as f:
                data = json.load(f)
        self._cache = data
        self._lang = lang
        self.language_changed.emit(lang)
        for cb in self._callbacks:
            try:
                cb(lang)
            except Exception:
                pass
    def t(self, key: str) -> str:
        if not self._cache:
            self.load(self._lang)
        return (
            self._cache.get(key)
            or TR.get(self._lang, {}).get(key)
            or TR.get("en", {}).get(key)
            or key
        )
    def lang(self) -> str:
        return self._lang
    def on_change(self, cb):
        self._callbacks.append(cb)
i18n = I18N()
VOID_HTML = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
INLINE_HTML = {"a","abbr","b","bdi","bdo","cite","code","data","dfn","em","i","kbd","label","mark","q","rp","rt","rtc","ruby","s","samp","small","span","strong","sub","sup","time","u","var","wbr"}
def detect_language(sample: str, _limit: int = 8192) -> str:
    s = (sample or "")
    if len(s) > _limit:
        s = s[:_limit]
    s = s.strip()
    if not s: return "Plain"
    if s[:1] in "{[":
        try:
            json.loads(s); return "JSON"
        except Exception:
            pass
    if s.startswith("<?php") or "<?php" in s: return "PHP"
    if s.startswith("<"):
        if re.match(r"^<!DOCTYPE|^<html|^<svg|^<\?xml", s, re.I): return "HTML/XML"
        if re.match(r"^<\w+[^>]*>", s): return "HTML/XML"
    if re.search(r"(^|\n)\s*#|^\s*(def|class)\s+\w+|^\s*import\s+\w+", s):
        return "Python"
    if re.search(r"\b(function|let|const|var|=>|import\s+.*from)\b", s):
        return "JavaScript"
    if re.search(r"[.#][\w-]+\s*\{|@media|:root\s*\{", s):
        return "CSS"
    return "Plain"
def _strip_c_like(code: str, allow_hash=False, allow_backtick=True) -> str:
    out: List[str] = []
    i, n = 0, len(code)
    in_str = False; delim=''; esc=False
    in_line=False; in_block=False
    in_bt=False; tmpl_depth=0
    line_had_code = True
    block_had_code_before = True

    def had_code_on_line() -> bool:
        j = len(out) - 1
        while j >= 0 and out[j] != '\n':
            if not out[j].isspace():
                return True
            j -= 1
        return False

    def pop_line_indent():
        while out and out[-1] != '\n' and out[-1] in ' \t':
            out.pop()

    while i<n:
        c=code[i]

       
        if in_line:
            if c=='\n':
                in_line=False
                if line_had_code:
                    out.append('\n')
                i+=1; continue
            i+=1; continue

        if in_block:
            if c=='*' and i+1<n and code[i+1]=='/':
                in_block=False; i+=2
                if not block_had_code_before:
                  
                    j=i
                    while j<n and code[j] in ' \t': j+=1
                    if j<n and code[j]=='\n':
                        i=j+1
                continue
            i+=1; continue

        if in_bt:
            out.append(c)
            if c=='\\':
                if i+1<n:
                    out.append(code[i+1]); i+=2; continue
            if c=='`' and tmpl_depth==0:
                in_bt=False; i+=1; continue
            if c=='$' and i+1<n and code[i+1]=='{':
                tmpl_depth+=1; out.append('{'); i+=2; continue
            if c=='}' and tmpl_depth>0:
                tmpl_depth-=1; i+=1; continue
            i+=1; continue

        if in_str:
            out.append(c)
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==delim: in_str=False
            i+=1; continue

        if c in ('"',"'"):
            in_str=True; delim=c; out.append(c); i+=1; continue
        if allow_backtick and c=='`':
            in_bt=True; tmpl_depth=0; out.append(c); i+=1; continue

        
        if c=='/' and i+1<n:
            nxt=code[i+1]
            if nxt=='/':
                line_had_code = had_code_on_line()
                if line_had_code:
                    while out and out[-1] in ' \t': out.pop()
                else:
                    pop_line_indent()
                in_line=True; i+=2; continue
            if nxt=='*':
                block_had_code_before = had_code_on_line()
                if block_had_code_before:
                    while out and out[-1] in ' \t': out.pop()
                else:
                    pop_line_indent()
                in_block=True; i+=2; continue

        if allow_hash and c=='#':
            line_had_code = had_code_on_line()
            if line_had_code:
                while out and out[-1] in ' \t': out.pop()
            else:
                pop_line_indent()
            in_line=True; i+=1; continue

      
        out.append(c); i+=1

    return ''.join(out)


def _strip_html(code: str) -> str:   
    s = re.sub(r'(?ms)^[ \t]*<!--(?!\[if).*?-->[ \t]*(?:\r?\n|$)', '', code)   
    s = re.sub(r'(?s)<!--(?!\[if).*?-->', '', s)   
    s = re.sub(r'[ \t]+(?=\r?\n)', '', s)
    return s

def strip_comments_python_strict(code: str) -> str:
    out = []
    i = 0
    n = len(code)
    in_str = False
    delim = ''
    triple = False
    esc = False

    def only_ws_on_current_line() -> bool:
        j = len(out) - 1
        while j >= 0 and out[j] != '\n':
            if not out[j].isspace():
                return False
            j -= 1
        return True

    def pop_line_indent():
        while out and out[-1] != '\n' and out[-1] in ' \t':
            out.pop()

    while i < n:
        c = code[i]
        if in_str:
            out.append(c)
            if triple:
                if c == delim and i + 2 < n and code[i+1] == delim and code[i+2] == delim:
                    out.append(code[i+1]); out.append(code[i+2])
                    in_str = False; triple = False
                    i += 3
                else:
                    i += 1
                continue
            else:
                if esc:
                    esc = False; i += 1; continue
                if c == '\\':
                    esc = True; i += 1; continue
                if c == delim:
                    in_str = False; i += 1; continue
                i += 1; continue

        if c in ("'", '"'):
            if i + 2 < n and code[i+1] == c and code[i+2] == c:
                in_str = True; delim = c; triple = True
                out.extend(c*3); i += 3; continue
            else:
                in_str = True; delim = c; triple = False
                out.append(c); i += 1; continue

        if c == '#':
            full_line = only_ws_on_current_line()
            if full_line:
                pop_line_indent()
            else:
              
                while out and out[-1] in ' \t':
                    out.pop()
  
            while i < n and code[i] != '\n':
                i += 1
           
            if i < n and code[i] == '\n':
                if not full_line:
                    out.append('\n')
                i += 1
            continue

        out.append(c); i += 1

    return ''.join(out)

def _strip_by_markers(
    code: str,
    *,
    rm_html=False,
    rm_c_block=False,
    rm_c_line=False,
    rm_hash=False,
    allow_backtick=True
) -> str:
    s = code
    if rm_html:
        s = _strip_html(s)

    out = []
    i = 0
    n = len(s)
    in_str = False
    delim = ''
    esc = False
    in_bt = False
    tmpl = 0
    in_line = False
    in_block = False
    line_had_code = True
    block_had_code_before = True

    def had_code_on_line() -> bool:
        j = len(out) - 1
        while j >= 0 and out[j] != '\n':
            if not out[j].isspace():
                return True
            j -= 1
        return False

    def pop_line_indent():
        while out and out[-1] != '\n' and out[-1] in ' \t':
            out.pop()

    while i < n:
        c = s[i]

        if in_line:
            if c == '\n':
                in_line = False
                if line_had_code:
                    out.append('\n')
                i += 1; continue
            i += 1; continue

        if in_block:
            if c == '*' and i + 1 < n and s[i+1] == '/':
                in_block = False
                i += 2
                if not block_had_code_before:
                    j = i
                    while j < n and s[j] in ' \t': j += 1
                    if j < n and s[j] == '\n':
                        i = j + 1
                continue
            i += 1; continue

        if in_str:
            out.append(c)
            if esc: esc = False
            else:
                if c == '\\': esc = True
                elif c == delim: in_str = False
            i += 1; continue

        if in_bt:
            out.append(c)
            if c == '\\':
                if i + 1 < n:
                    out.append(s[i+1]); i += 2; continue
            if c == '`' and tmpl == 0:
                in_bt = False; i += 1; continue
            if c == '$' and i + 1 < n and s[i+1] == '{':
                tmpl += 1; out.append('{'); i += 2; continue
            if c == '}' and tmpl > 0:
                tmpl -= 1; i += 1; continue
            i += 1; continue

        if c in ("'", '"'):
            in_str = True; delim = c; out.append(c); i += 1; continue
        if allow_backtick and c == '`':
            in_bt = True; tmpl = 0; out.append(c); i += 1; continue

        if rm_c_line and c == '/' and i + 1 < n and s[i+1] == '/':
            line_had_code = had_code_on_line()
            if line_had_code:
                while out and out[-1] in ' \t': out.pop()
            else:
                pop_line_indent()
            in_line = True; i += 2; continue

        if rm_c_block and c == '/' and i + 1 < n and s[i+1] == '*':
            block_had_code_before = had_code_on_line()
            if block_had_code_before:
                while out and out[-1] in ' \t': out.pop()
            else:
                pop_line_indent()
            in_block = True; i += 2; continue

        if rm_hash and c == '#':
            line_had_code = had_code_on_line()
            if line_had_code:
                while out and out[-1] in ' \t': out.pop()
            else:
                pop_line_indent()
            in_line = True; i += 1; continue

        out.append(c); i += 1

    return ''.join(out)

def strip_comments_custom(code: str, *, html=False, c_block=False, c_line=False, py_hash=False) -> str:
    s = code
    if html:
        s = _strip_html(s)
    if c_block or c_line or py_hash:
        s = _strip_by_markers(s, rm_c_block=c_block, rm_c_line=c_line, rm_hash=py_hash)
    return s
def strip_comments(code: str, lang: str) -> str:
    if lang == "HTML/XML": return _strip_html(code)
    if lang == "CSS": return _strip_c_like(code, allow_hash=False, allow_backtick=False)
    if lang == "JavaScript": return _strip_c_like(code, allow_hash=False, allow_backtick=True)
    if lang == "PHP": return _strip_c_like(code, allow_hash=True, allow_backtick=True)
    if lang == "JSON": return _strip_c_like(code, allow_hash=False, allow_backtick=False)
    if lang == "Python":
        return strip_comments_python_strict(code)
    return _strip_c_like(code, allow_hash=False, allow_backtick=False)
def strip_comments_all(code: str) -> str:
    s = code

 
    s = re.sub(r'(?ms)^[ \t]*<!--(?!\[if).*?-->[ \t]*(?:\r?\n|$)', '', s)  
    s = re.sub(r'(?s)<!--(?!\[if).*?-->', '', s)

 
    s = re.sub(r'(?ms)^[ \t]*/\*.*?\*/[ \t]*(?:\r?\n|$)', '', s)         
    s = re.sub(r'(?s)/\*.*?\*/', '', s)                              

    
    s = re.sub(r'(?m)^[ \t]*//[^\n]*(?:\r?\n|$)', '', s) 
    s = re.sub(r'//[^\n]*', '', s)


    s = re.sub(r'(?m)^[ \t]*#[^\n]*(?:\r?\n|$)', '', s)  
    s = re.sub(r'(?m)(?<!["\'`])#[^\n]*', '', s)             

   
    s = re.sub(r'[ \t]+(?=\r?\n)', '', s)
    return s

def _collapse_ws_outside_strings(code: str) -> str:
    out=[]; i=0; n=len(code); in_str=False; d=''; esc=False; ws=False
    def push_space():
        if not out or not (isinstance(out[-1], str) and out[-1].isspace()):
            out.append(' ')
    while i<n:
        c=code[i]
        if in_str:
            out.append(c)
            if esc: esc=False
            else:
                if c=='\\': esc=True
                elif c==d: in_str=False
            i+=1; continue
        if c in ("'",'"','`'):
            in_str=True; d=c; out.append(c); ws=False; i+=1; continue
        if c.isspace():
            ws=True; i+=1; continue
        if ws: push_space(); ws=False
        out.append(c); i+=1
    return ''.join(out)
def _tighten_punct_ws(code: str) -> str:
    out=[]; i=0; n=len(code); in_str=False; d=''; esc=False
    punct=set(";,:{}()[]=+-*/<>|&!%^?,.")
    while i<n:
        c=code[i]
        if in_str:
            out.append(c)
            if esc: esc=False
            else:
                if c=='\\': esc=True
                elif c==d: in_str=False
            i+=1; continue
        if c in ("'",'"','`'):
            in_str=True; d=c; out.append(c); i+=1; continue
        if c in punct:
            while out and isinstance(out[-1], str) and out[-1]==' ': out.pop()
            out.append(c)
            j=i+1
            while j<n and code[j]==' ': j+=1
            i=j; continue
        out.append(c); i+=1
    return ''.join(out)
def minify_code(code: str, lang: str) -> str:
    if lang == "JSON":
        try:
            obj=json.loads(code)
            return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
        except Exception:
            pass
    s = strip_comments(code, lang)
    s = _collapse_ws_outside_strings(s)
    s = _tighten_punct_ws(s)
    s = re.sub(r"\s*\n\s*", "", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()
def _indent_str(use_tabs: bool, size: int) -> str:
    return "\t" if use_tabs else (" " * max(1, size))

def pretty_json(code: str, indent: str, sort_keys=False) -> Optional[str]:
    try:
        obj = json.loads(code)
        
        return json.dumps(obj, indent=4, sort_keys=sort_keys, ensure_ascii=False)
    except Exception:
        return None

def pretty_braces(code: str, indent: str) -> str:
    out=[]; i=0; n=len(code); in_str=False; d=''; esc=False; lvl=0; paren=0

    def nl():
        out.append('\n'); out.append(indent*lvl)

    while i<n:
        c=code[i]
        if in_str:
            out.append(c)
            if esc: esc=False
            else:
                if c=='\\': esc=True
                elif c==d: in_str=False
            i+=1; continue

        if c in ("'",'"','`'):
            in_str=True; d=c; out.append(c); i+=1; continue

        if c=='{':
            out.append('{'); lvl+=1; nl(); i+=1; continue

        if c=='}':
           
            lvl=max(0,lvl-1)
            while out and isinstance(out[-1], str) and out[-1].strip()=="" and '\n' not in out[-1]:
                out.pop()
            out.append('\n'); out.append(indent*lvl); out.append('}')
            i+=1

           
            j=i
            while j<n and code[j].isspace(): j+=1

            def copy_parens(pos: int) -> int:
                if pos>=n or code[pos] != '(':
                    return pos
                depth = 0
                k = pos
                while k<n:
                    ch = code[k]
                    out.append(ch)
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                        if depth == 0:
                            k += 1
                            break
                    k += 1
                return k

            def maybe_open_brace(pos: int) -> int:
                nonlocal lvl
                m = pos
                while m<n and code[m].isspace(): m+=1
                if m<n and code[m] == '{':
                    out.append(' {')
                    lvl += 1
                    m += 1
                    nl()
                    return m
                nl()
                return pos

          
            if j<n and code.startswith('else', j):
                out.append(' else')
                j += 4
                k = j
                while k<n and code[k].isspace(): k+=1
                if k<n and code.startswith('if', k):
                    out.append(' if')
                    k += 2
                    while k<n and code[k].isspace(): k+=1
                    if k<n and code[k]=='(':
                        k = copy_parens(k)
                i = maybe_open_brace(k)
                continue

         
            if j<n and code.startswith('catch', j):
                out.append(' catch')
                j += 5
                k = j
                while k<n and code[k].isspace(): k+=1
                if k<n and code[k]=='(':
                    k = copy_parens(k)
                i = maybe_open_brace(k)
                continue

      
            if j<n and code.startswith('finally', j):
                out.append(' finally')
                j += 7
                i = maybe_open_brace(j)
                continue

  
            if j<n and code[j] in (';', ','):
                out.append(code[j]); i = j+1
                nl(); continue

            nl(); continue

        if c=='(':
            paren+=1; out.append('('); i+=1; continue
        if c==')':
            paren=max(0,paren-1); out.append(')'); i+=1; continue

        if c==';':
            out.append(';'); i+=1
            if paren==0: nl()
            continue

        if c=='\n':
            if out and not (isinstance(out[-1], str) and out[-1].endswith('\n')):
                out.append('\n'); out.append(indent*lvl)
            i+=1; continue

        if c.isspace():
            if out and out[-1] != ' ' and not (isinstance(out[-1], str) and out[-1].endswith('\n')):
                out.append(' ')
            i+=1; continue

        out.append(c); i+=1

    res=''.join(out)


    res = re.sub(r'(?m)^[ \t]*\}[ \t]*\r?\n[ \t]*(else\b(?:\s+if\b[^{\r\n]*?)?)', r'} \1', res)
    res = re.sub(r'(?m)^[ \t]*\}[ \t]*\r?\n[ \t]*(catch\b[^{\r\n]*?)',             r'} \1', res)
    res = re.sub(r'(?m)^[ \t]*\}[ \t]*\r?\n[ \t]*(finally\b)',                    r'} \1', res)

    res = re.sub(r'(?m)\}[ \t]+(else\b(?:\s+if\b[^{\r\n]*?)?)', r'} \1', res)
    res = re.sub(r'(?m)\}[ \t]+(catch\b[^{\r\n]*?)',             r'} \1', res)
    res = re.sub(r'(?m)\}[ \t]+(finally\b)',                    r'} \1', res)


    res = res.replace('}\n else',  '} else')
    res = res.replace('}\r\n else','} else')

    res = re.sub(r"\n{3,}", "\n\n", res).rstrip()
    return res




def pretty_html_xml(code: str, indent: str) -> str:
    tokens = re.findall(r"(<!--.*?-->|<!\[CDATA\[.*?\]\]>|</?[^>]+>|[^<]+)", code, flags=re.S)
    lvl = 0
    out: list[str] = []
    tag_stack: list[str] = []
    inc_stack: list[bool] = []
    raw_stack: list[str] = []
    inline_depth = 0
    last_was_inline_open = False
    allow_inline_flow = False

    RAW_TAGS = {"script", "style", "pre", "code", "textarea"}

    def tag_name(tag: str) -> str:
        return re.sub(r"^</?\s*([\w:-]+).*", r"\1", tag).lower()

    def is_self_tag(nm: str, tok: str) -> bool:
        return tok.endswith("/>") or nm in VOID_HTML

    def append_line(txt: str):
        nonlocal last_was_inline_open, allow_inline_flow
        out.append(f"{indent*lvl}{txt.strip()}")
        last_was_inline_open = False
        allow_inline_flow = False

    def append_inline(txt: str, add_space: bool):
        nonlocal last_was_inline_open
        txt = txt.strip()
        if not out:
            out.append(f"{indent*lvl}{txt}")
        else:
            if add_space and out[-1] and not out[-1].endswith((" ", "\t")):
                out[-1] += " "
            out[-1] += txt
        last_was_inline_open = False

    for t in tokens:
        if not t:
            continue

        if t.startswith("<!--") and t.endswith("-->"):
            append_line(t); continue
        if t.startswith("<![CDATA["):
            append_line(t); continue

        if t.startswith("</"):
            nm = tag_name(t)
            if inline_depth > 0 and nm in INLINE_HTML:
                append_inline(t, add_space=False)
                if tag_stack and tag_stack[-1] == nm:
                    tag_stack.pop()
                    if inc_stack: inc_stack.pop()
                    inline_depth = max(0, inline_depth - 1)
                if inline_depth == 0:
                    allow_inline_flow = True
                continue

            if raw_stack and raw_stack[-1] == nm:
                raw_stack.pop()

            if tag_stack and tag_stack[-1] == nm:
                if inc_stack and inc_stack[-1]:
                    lvl = max(0, lvl - 1)
                tag_stack.pop()
                if inc_stack: inc_stack.pop()
            append_line(t)
            continue

        if t.startswith("<"):
            nm = tag_name(t)
            self_closing = is_self_tag(nm, t)

            if inline_depth > 0 or nm in INLINE_HTML or allow_inline_flow:
                add_space = not last_was_inline_open
                append_inline(t, add_space=add_space)
                if not self_closing:
                    tag_stack.append(nm); inc_stack.append(False)
                    inline_depth += 1
                    last_was_inline_open = True
                allow_inline_flow = inline_depth == 0
                continue

            append_line(t)
            if not self_closing:
                tag_stack.append(nm); inc_stack.append(True)
                if nm in RAW_TAGS:
                    raw_stack.append(nm)
                lvl += 1
            continue

      
        if raw_stack:
            lines = t.splitlines()
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            for ln in lines:
                append_line(ln.rstrip())
        else:
            txt = t.strip()
            if not txt:
                continue
            txt = re.sub(r"\s+", " ", txt)
            if inline_depth > 0 or allow_inline_flow:
                no_space_chars = ".,;:!?)]}"
                add_space = not last_was_inline_open and not (txt and txt[0] in no_space_chars)
                append_inline(txt, add_space=add_space)
                allow_inline_flow = True
            else:
                append_line(txt)

    return "\n".join(out).rstrip()

def pretty_python(code: str, indent: str) -> str:
    lines = code.splitlines()
    res = []
    lvl = 0

    dedent_heads = re.compile(r"^(elif\b.*:|else:|except\b.*:|finally:)\s*$")

    for raw in lines:
        ln = raw.rstrip()
        stripped = ln.lstrip()
        if stripped == "":
            continue
        if dedent_heads.match(stripped):
            lvl = max(0, lvl - 1)

        res.append((indent * lvl) + stripped)

        if stripped.endswith(":") and not stripped.strip().startswith("#"):
            lvl += 1

    return "\n".join(res).rstrip()





def _jsphp_format(code: str, indent: str) -> str:
    s = code.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    i = 0
    n = len(s)
    lvl = 0
    paren = 0
    bracket = 0
    in_str = False
    str_delim = ""
    esc = False
    in_line_comment = False
    in_block_comment = False
    in_backtick = False
    tmpl_depth = 0

    def nl():
        if out and out[-1] != "\n":
            out.append("\n")
        if not out or out[-1] == "\n":
            out.append(indent * max(0, lvl))

    def prev_non_ws() -> str:
        j = len(out) - 1
        while j >= 0:
            ch = out[j]
            if ch.strip() != "":
                return ch
            j -= 1
        return ""

    starters = set("({[=:+-*/%&|^!~?,;<")
    keyword_starters = {"return", "case", "throw", "delete", "typeof", "instanceof", "in", "of", "new", "do", "else"}

    last_word = ""

    while i < n:
        c = s[i]

        if in_line_comment:
            out.append(c)
            if c == "\n":
                in_line_comment = False
                out.append(indent * max(0, lvl))
            i += 1
            continue

        if in_block_comment:
            out.append(c)
            if c == "*" and i + 1 < n and s[i+1] == "/":
                out.append("/")
                i += 2
                in_block_comment = False
            else:
                i += 1
            continue

        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == str_delim:
                in_str = False
            i += 1
            continue

        if in_backtick:
            out.append(c)
            if c == "\\":
                i += 1
                if i < n:
                    out.append(s[i])
                    i += 1
                continue
            if c == "`" and tmpl_depth == 0:
                in_backtick = False
                i += 1
                continue
            if c == "$" and i + 1 < n and s[i+1] == "{":
                tmpl_depth += 1
                i += 2
                out.append("{")
                continue
            if c == "}" and tmpl_depth > 0:
                tmpl_depth -= 1
                i += 1
                continue
            i += 1
            continue

        if c in " \t":
     
            j = i
            while j < n and s[j] in " \t":
                j += 1
            nextc = s[j] if j < n else ""
            if out and out[-1].endswith((" ", "\n")):
                i = j
            else:
                if nextc and nextc not in ")}];,.:?":
                    out.append(" ")
                i = j
            continue

        if c == "\n":
            nl()
            i += 1
            continue

        if c == "/" and i + 1 < n:
            nx = s[i+1]
            if nx == "/":
                in_line_comment = True
                out.append("//")
                i += 2
                continue
            if nx == "*":
                in_block_comment = True
                out.append("/*")
                i += 2
                continue

        if c in ("'", '"'):
            in_str = True
            str_delim = c
            out.append(c)
            i += 1
            continue

        if c == "`":
            in_backtick = True
            tmpl_depth = 0
            out.append(c)
            i += 1
            continue

        if c == "(":
            paren += 1
            out.append("(")
            i += 1
            continue
        if c == ")":
            paren = max(0, paren - 1)
            out.append(")")
            i += 1
            continue
        if c == "[":
            bracket += 1
            out.append("[")
            i += 1
            continue
        if c == "]":
            bracket = max(0, bracket - 1)
            out.append("]")
            i += 1
            continue

        if c == "{":
            if out and out[-1] not in (" ", "\n", "(" , "[", "{"):
                out.append(" ")
            out.append("{")
            lvl += 1
            nl()
            i += 1
            last_word = ""
            continue
        if c == "}":
            lvl = max(0, lvl - 1)
            nl()
            while out and out[-1] == " ":
                out.pop()
            if out and out[-1] != "\n":
                nl()
            out.append("}")
            nl()
            i += 1
            last_word = ""
            continue

        if c == ";":
            out.append(";")
            i += 1
            if paren == 0:
                nl()
            last_word = ""
            continue

        if c == ",":
            out.append(", ")
            i += 1
            last_word = ""
            continue

        if c == ":":
            out.append(":")
            i += 1
            if last_word == "case":
                nl()
                last_word = ""
            continue

        if c == "/":
            p = prev_non_ws()
            starts = (p in starters) or (last_word in keyword_starters) or (p == "" or p == "\n")
            if starts:
                out.append("/")
                i += 1
                esc2 = False
                while i < n:
                    ch = s[i]
                    out.append(ch)
                    if esc2:
                        esc2 = False
                    elif ch == "\\":
                        esc2 = True
                    elif ch == "/":
                        i += 1
                        break
                    i += 1
                while i < n and s[i].isalpha():
                    out.append(s[i]); i += 1
                last_word = ""
                continue

        if c.isalpha() or c == "_" or c == "$":
            j = i + 1
            while j < n and (s[j].isalnum() or s[j] in "_$"):
                j += 1
            word = s[i:j]
            if out and out[-1] not in ("", " ", "\n", "(" , "[", "{", "!", "~", "."):
                out.append(" ")
            out.append(word)
            last_word = word
            i = j
            continue

        if c in "=+-*/%&|^!~<>?.":
            if c in ".!~":
                out.append(c)
            else:
                if out and out[-1] not in ("", " ", "\n", "(" , "[", "{"):
                    out.append(" ")
                out.append(c)
                if i + 1 < n and s[i+1] in "=|&><*":
                    out.append(s[i+1]); i += 1
                    if i + 1 < n and s[i+1] == "=" and s[i] in ("=", "!", "<", ">", "*"):
                        out.append("="); i += 1
                out.append(" ")
            i += 1
            last_word = ""
            continue

        out.append(c)
        last_word = "" if not c.isalnum() else last_word
        i += 1

    res = "".join(out)
    res = re.sub(r"[ \t]+\n", "\n", res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    return res.rstrip()


def pretty_css(code: str, indent: str) -> str:
    s = strip_comments(code, "CSS").strip()
    tokens = re.findall(
        r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|[{};]|[^{};\'"]+',
        s, flags=re.S
    )

    def norm_sel(t: str) -> str:
        t = re.sub(r'\s+', ' ', t)
        t = re.sub(r'\s*,\s*', ', ', t)
        t = re.sub(r'\(\s*', '(', t)
        t = re.sub(r'\s*\)', ')', t)
        t = re.sub(r':\s*', ':', t)
        return t.strip()

    def norm_prop(t: str) -> str:
        t = re.sub(r'\s+', ' ', t)
        t = re.sub(r'\s*:\s*', ': ', t)
        t = re.sub(r'\s*,\s*', ', ', t)
        return t.strip()

    lvl = 0
    out: list[str] = []
    buf: list[str] = []

    for tok in tokens:
        if not tok:
            continue
        if tok == '{':
            sel = norm_sel(''.join(buf)); buf.clear()
            out.append(f"{indent*lvl}{sel} {{")
            lvl += 1
        elif tok == '}':
            if ''.join(buf).strip():
                line = norm_prop(''.join(buf)).rstrip(';')
                out.append(f"{indent*lvl}{line};")
                buf.clear()
            lvl = max(0, lvl-1)
            out.append(f"{indent*lvl}}}")
        elif tok == ';':
            line = norm_prop(''.join(buf)); buf.clear()
            out.append(f"{indent*lvl}{line};")
        else:
            buf.append(tok)

    if ''.join(buf).strip():
        line = norm_prop(''.join(buf)).rstrip(';')
        out.append(f"{indent*lvl}{line};")

    return "\n".join(out).rstrip()




def tidy_whitespace(text: str, max_blank_lines: int = 1, trim_trailing: bool = True) -> str:
    """
    Сжимает серии пустых строк до max_blank_lines,
    убирает хвостовые пробелы/табы и нормализует переводы строк.
    Также убирает ведущие/замыкающие пустые строки.
    """
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if trim_trailing:
        text = re.sub(r"[ \t]+(?=\n)", "", text) 
        text = re.sub(r"[ \t]+$", "", text, flags=re.M)

    out_lines = []
    blanks = 0
    for ln in text.split("\n"):
        if ln.strip() == "":
            blanks += 1
            if blanks <= max_blank_lines:
                out_lines.append("")
        else:
            blanks = 0
            out_lines.append(ln.rstrip())

    while out_lines and out_lines[0] == "":
        out_lines.pop(0)
    while out_lines and out_lines[-1] == "":
        out_lines.pop()

    return "\n".join(out_lines)




def pretty_js(code: str, indent: str) -> str:
    """
    JS/PHP formatter:
    - переносы формируются только правилами форматтера (исходные \n снаружи строк/комментов игнорируются);
    - '} else/catch/finally' — на одной строке;
    - ';' даёт перенос только вне круглых скобок (не ломаем for(...;...;...));
    - идемпотентность.
    """
    s = code.replace("\r\n", "\n").replace("\r", "\n")
    n = len(s); i = 0

    out: list[str] = []
    lvl = 0
    paren = 0
    brack = 0

    in_line = False
    in_block = False
    in_str = False
    str_delim = ""
    esc = False

    in_backtick = False
    tmpl_depth = 0

    last_word = ""

    keyword_starters = {"return", "case", "throw", "delete", "typeof", "instanceof", "in", "of", "new", "do", "else"}
    regex_starters = set("({[=:+-*/%&|^!~?,;<")

    def buf() -> str:
        return "".join(out)

    def prev_non_ws_char() -> str:
        b = buf()
        j = len(b) - 1
        while j >= 0:
            ch = b[j]
            if ch not in " \t\n":
                return ch
            j -= 1
        return ""

    def drop_trailing_indent_element():
   
        while out and out[-1] and all(ch in " \t" for ch in out[-1]):
            out.pop()

    def ensure_nl():

        if not out:
            out.append("\n")
        elif not out[-1].endswith("\n"):
            out.append("\n")
        out.append(indent * max(0, lvl))

    def write(tok: str):
        out.append(tok)

    while i < n:
        c = s[i]

        
        if in_line:
            write(c)
            if c == "\n":
                in_line = False
                ensure_nl()
            i += 1
            continue

        if in_block:
            write(c)
            if c == "*" and i + 1 < n and s[i + 1] == "/":
                write("/")
                i += 2
                in_block = False
            else:
                i += 1
            continue

    
        if in_str:
            write(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == str_delim:
                in_str = False
            i += 1
            continue

   
        if in_backtick:
            write(c)
            if c == "\\":
                if i + 1 < n:
                    i += 1
                    write(s[i])
                    i += 1
                else:
                    i += 1
                continue
            if c == "`" and tmpl_depth == 0:
                in_backtick = False
                i += 1
                continue
            if c == "$" and i + 1 < n and s[i + 1] == "{":
                tmpl_depth += 1
                i += 2
                write("{")
                continue
            if c == "}" and tmpl_depth > 0:
                tmpl_depth -= 1
                i += 1
                continue
            i += 1
            continue

   
        if c in " \t":
            j = i
            while j < n and s[j] in " \t":
                j += 1
            nextc = s[j] if j < n else ""
            b = buf()
            if not b or b.endswith((" ", "\n", "\t")):
                i = j
            else:
                if nextc and nextc not in ")}];,.:?":
                    write(" ")
                i = j
            continue

        if c == "\n":
            i += 1
            continue

        if c == "/" and i + 1 < n:
            nx = s[i + 1]
            if nx == "/":
                write("//"); in_line = True; i += 2; continue
            if nx == "*":
                write("/*"); in_block = True; i += 2; continue

  
        if c in ("'", '"'):
            in_str = True; str_delim = c; write(c); i += 1
            last_word = ""
            continue

  
        if c == "`":
            in_backtick = True; tmpl_depth = 0; write(c); i += 1
            last_word = ""
            continue

      
        if c == "(":
            if last_word in {"if", "for", "while", "switch", "catch"} and not buf().endswith((" ", "\n", "\t")):
                write(" ")
            paren += 1; write("("); i += 1; continue

        if c == ")":
            paren = max(0, paren - 1); write(")"); i += 1; last_word = ""; continue

        if c == "[":
            brack += 1; write("["); i += 1; continue

        if c == "]":
            brack = max(0, brack - 1); write("]"); i += 1; continue

      
        if c == "{":
            if not buf().endswith((" ", "\n", "\t", "(", "[", "{")):
                write(" ")
            write("{"); lvl += 1; ensure_nl(); i += 1
            last_word = ""
            continue

        if c == "}":
       
            drop_trailing_indent_element()
       
            if not buf().endswith("\n"):
                out.append("\n")
            lvl = max(0, lvl - 1)
            out.append(indent * max(0, lvl))
            write("}")
            i += 1
            ensure_nl()
            last_word = ""
            continue

  
        if c == ";":
            write(";"); i += 1
            if paren == 0:
                ensure_nl()
            last_word = ""
            continue

      
        if c == ",":
            write(","); i += 1; write(" ")
            last_word = ""
            continue

        
        if c == ":":
            write(":"); i += 1
            if last_word == "case":
                ensure_nl(); last_word = ""
            else:
                write(" ")
            continue

     
        if c == "/":
            p = prev_non_ws_char()
            starts = (p in regex_starters) or (last_word in keyword_starters) or (p == "" or p == "\n")
            if starts:
                write("/")
                i += 1
                esc2 = False
                while i < n:
                    ch = s[i]; write(ch)
                    if esc2: esc2 = False
                    elif ch == "\\": esc2 = True
                    elif ch == "/":
                        i += 1; break
                    i += 1
                while i < n and s[i].isalpha():
                    write(s[i]); i += 1
                last_word = ""
                continue

      
        if c.isalpha() or c == "_" or c == "$":
            j = i + 1
            while j < n and (s[j].isalnum() or s[j] in "_$"):
                j += 1
            word = s[i:j]

            if buf() and not buf().endswith((" ", "\n", "\t", "(", "[", "{", "!", "~", ".", "?", ":", "+", "-", "*", "/", "%", "&", "|", "^", "=")):
                write(" ")

       
            if word in {"else", "catch", "finally"} and prev_non_ws_char() == "}":
             
                while out:
                    t = out[-1]
                    if t == "" or all(ch in " \t" for ch in t):
                        out.pop(); continue
                    if t.endswith("\n"):
                        out[-1] = t.rstrip("\n")
                        if out[-1] == "" or all(ch in " \t" for ch in out[-1]):
                            out.pop()
                        continue
                    break
                write(" ")

            write(word)
            last_word = word; i = j
            continue

     
        if c.isdigit():
            j = i + 1
            while j < n and (s[j].isdigit() or s[j] in "._xXbBeE+-"):
                j += 1
            num = s[i:j]
            if buf() and not buf().endswith((" ", "\n", "\t", "(", "[", "{", "+", "-", "*", "/", "%", "&", "|", "^", "!", "~", "?", ":", "=")):
                write(" ")
            write(num)
            last_word = ""; i = j
            continue


        if c in "=!<>+-*/%&|^~?.": 
            j = i + 1
            op = c
            while j < n and s[j] in "=!<>+-*/%&|^~?.:":
                op += s[j]; j += 1

            candidates = [">>>=", ">>>", ">>=", "<<=", "===", "!==", "&&", "||", ">>", "<<", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "=>"]
            matched = ""
            for cand in candidates:
                if op.startswith(cand):
                    matched = cand; break
            if not matched:
                if op.startswith("++") or op.startswith("--"):
                    matched = op[:2]
                else:
                    matched = op[:1]

            if matched in (".", "?."):
                write(matched)
            elif matched in ("++", "--"):
                write(matched)
            elif matched == "=>":
                write(" => ")
            else:
                if buf() and not buf().endswith((" ", "\n", "\t")):
                    write(" ")
                write(matched)
                write(" ")

            i += len(matched)
            last_word = ""
            continue

     
        write(c); i += 1

    txt = buf()
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"\n[ \t]*\n([ \t]*)\}", r"\n\1}", txt)
    return txt.rstrip()





def pretty_format(code: str, lang: str, use_tabs: bool, indent_size: int, sort_json_keys=False) -> str:
    indent = "\t" if use_tabs else (" " * max(1, indent_size))
    if lang == "JSON":
        r = pretty_json(code, indent, sort_json_keys)
        if r is not None:
            return r
    if lang == "HTML/XML":
        return pretty_html_xml(code, indent)
    if lang == "CSS":
        return pretty_css(code, indent)
    if lang in ("JavaScript", "PHP"):
        return pretty_js(code, indent)
    if lang == "Python":
        return pretty_python(code, indent)
    return pretty_js(code, indent) 



def b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")
_b64_call_pat = re.compile(r"(?:atob|base64_decode|b64decode)\s*\(\s*['\"]([A-Za-z0-9+/=_-]+)['\"]\s*\)", re.I)
_hex_byte_pat = re.compile(r"\\x([0-9A-Fa-f]{2})")
_data_uri_pat = re.compile(r"data:[^;]+;base64,([A-Za-z0-9+/=_-]+)", re.I)
_html_ent_pat = re.compile(r"&#(x[0-9A-Fa-f]+|\d+);")
_css_hex_pat  = re.compile(r"\\([0-9A-Fa-f]{1,6})(?:\s)?")

def _decode_html_entities(s: str) -> Optional[str]:
    if "&#" not in s:
        return None
    def repl(m):
        g = m.group(1)
        try:
            cp = int(g[1:], 16) if g.lower().startswith('x') else int(g)
            return chr(cp)
        except Exception:
            return m.group(0)
    out = _html_ent_pat.sub(repl, s)
    return out if out != s else None

def _decode_css_hex_escapes(s: str) -> Optional[str]:
    if "\\" not in s:
        return None
    used = False
    def repl(m):
        nonlocal used
        try:
            used = True
            return chr(int(m.group(1), 16))
        except Exception:
            return m.group(0)
    out = _css_hex_pat.sub(repl, s)
    return out if used else None

_oct_pat = re.compile(r"\\([0-7]{1,3})")

def _decode_c_escapes(fragment: str, *, in_double_quotes: bool = True) -> str:
    r"""
    Декодирует C/PHP-подобные экранирования в отдельном фрагменте строки.
    Поддержка: \n \r \t \v \f \\ \' \" \xHH \NNN (восьмеричные, 1-3 цифры)
    """
  

    out = []
    i, n = 0, len(fragment)
    while i < n:
        c = fragment[i]
        if c != '\\':
            out.append(c); i += 1; continue
        i += 1
        if i >= n:
            out.append('\\'); break
        ch = fragment[i]; i += 1

        if ch in "nrvtf\\'\"ab":
            mapping = {
                'n':'\n','r':'\r','v':'\v','t':'\t','f':'\f','\\':'\\',
                '"':'"', "'":"'", 'a':'\a','b':'\b'
            }
            out.append(mapping.get(ch, ch))
            continue

        if ch in "xX": 
            j = i
            h = []
            while j < n and len(h) < 2 and fragment[j] in "0123456789abcdefABCDEF":
                h.append(fragment[j]); j += 1
            if h:
                out.append(chr(int(''.join(h), 16)))
                i = j
            else:
                out.append('\\x')
            continue

        if ch in "01234567":  
            j = i - 1
            k = j + 1
            while k < n and (k - j) <= 3 and fragment[k] in "01234567":
                k += 1
            try:
                out.append(chr(int(fragment[j:k], 8)))
            except Exception:
                out.append(fragment[j:k])
            i = k
            continue
        out.append('\\' + ch)
    return ''.join(out)


def _decode_php_like_string_literals(code: str) -> str:
    r"""
    Проходит по коду и декодирует содержимое строк:
    - двойные кавычки: полноценные escape-последовательности (\xHH, \NNN, \n, ...)
    - одинарные кавычки: только \\ и \'
    Учитываем // и /* */ комментарии, чтобы не ломать структуру.
    """

    out = []
    i, n = 0, len(code)
    in_s = False       
    in_d = False       
    in_lc = False      
    in_bc = False     
    esc = False

    while i < n:
        c = code[i]
        if in_lc:
            out.append(c)
            if c == '\n':
                in_lc = False
            i += 1
            continue
        if in_bc:
            out.append(c)
            if c == '*' and i + 1 < n and code[i+1] == '/':
                out.append('/'); i += 2; in_bc = False
            else:
                i += 1
            continue

 
        if in_s:
            if esc:
                if c in ("'", "\\"):
                    out.append(c)
                else:
                    out.append('\\' + c)
                esc = False; i += 1; continue
            if c == '\\':
                esc = True; i += 1; continue
            if c == "'":
                in_s = False; out.append(c); i += 1; continue
            out.append(c); i += 1; continue

        if in_d:
            
            j = i
            buf = []
            while j < n:
                ch = code[j]
                if ch == '\\':
                    if j + 1 < n:
                        buf.append('\\' + code[j+1]); j += 2
                    else:
                        buf.append('\\'); j += 1
                    continue
                if ch == '"':
                    break
                buf.append(ch); j += 1
           
            out.append(_decode_c_escapes(''.join(buf), in_double_quotes=True))
            if j < n and code[j] == '"':
                out.append('"'); in_d = False; i = j + 1
            else:
                i = j
            continue

      
        if c == "'":
            in_s = True; out.append(c); i += 1; continue
        if c == '"':
            in_d = True; out.append(c); i += 1; continue

        if c == '/' and i + 1 < n:
            if code[i+1] == '/':
                in_lc = True; out.append('//'); i += 2; continue
            if code[i+1] == '*':
                in_bc = True; out.append('/*'); i += 2; continue

        out.append(c); i += 1

    return ''.join(out)

_goto_stmt_re  = re.compile(r'^\s*goto\s+([A-Za-z_]\w*)\s*;\s*$', re.I)

def deobfuscate_php_goto(code: str) -> Optional[str]:
    """
    Уплощает верхнеуровневые goto/label в PHP.
    Не лезет внутрь функций/классов (блоки { ... } просто копируются),
    поэтому безопасен для «спагетти» на верхнем уровне.
    """
    s = code.replace("\r\n", "\n").replace("\r", "\n")
    n = len(s); i = 0


    in_s = in_d = in_lc = in_bc = False
    depth = 0


    nodes: list[tuple[str, str]] = []
    cur: list[str] = []

    def flush_stmt():
        txt = ''.join(cur)
        if txt.strip():
            nodes.append(("stmt", txt))
        cur.clear()

    while i < n:
        c = s[i]

       
        if in_lc:
            cur.append(c)
            if c == '\n': in_lc = False
            i += 1; continue
        if in_bc:
            cur.append(c)
            if c == '*' and i+1 < n and s[i+1] == '/':
                cur.append('/'); i += 2; in_bc = False
            else:
                i += 1
            continue

      
        if in_s:
            cur.append(c)
            if c == '\\' and i+1 < n:
                cur.append(s[i+1]); i += 2; continue
            if c == "'": in_s = False
            i += 1; continue

        if in_d:
            cur.append(c)
            if c == '\\' and i+1 < n:
                cur.append(s[i+1]); i += 2; continue
            if c == '"': in_d = False
            i += 1; continue

      
        if c == '/' and i+1 < n:
            if s[i+1] == '/':
                cur.append('//'); i += 2; in_lc = True; continue
            if s[i+1] == '*':
                cur.append('/*'); i += 2; in_bc = True; continue
        if c == "'":
            cur.append(c); in_s = True; i += 1; continue
        if c == '"':
            cur.append(c); in_d = True; i += 1; continue

        
        if c == '{':
            depth += 1
            cur.append(c); i += 1; continue
        if c == '}':
            depth = max(0, depth - 1)
            cur.append(c); i += 1
            if depth == 0:
                flush_stmt()
            continue

      
        if depth == 0 and c == ';':
            cur.append(';'); i += 1; flush_stmt(); continue

       
        if depth == 0 and c == ':':
            buf = ''.join(cur).rstrip()
            m = re.search(r'([A-Za-z_]\w*)\s*$', buf)
            if m:
          
                cut_at = m.start(1)
                cur = list(buf[:cut_at])
                flush_stmt()
                nodes.append(("label", m.group(1)))
                i += 1
              
                while i < n and s[i].isspace():
                    i += 1
                continue

        cur.append(c); i += 1

    if ''.join(cur).strip():
        nodes.append(("stmt", ''.join(cur)))


    label_to_idx: dict[str, int] = {}
    for idx, (kind, val) in enumerate(nodes):
        if kind == "label":
            j = idx + 1
            while j < len(nodes) and nodes[j][0] == "label":
                j += 1
            label_to_idx[val] = j


    pc = 0
    steps = 0
    visit_count: dict[int, int] = {}
    out: list[str] = []

    while pc < len(nodes) and steps < 10000:
        steps += 1
        kind, val = nodes[pc]
        if kind == "label":
            pc += 1
            continue

        m = _goto_stmt_re.match(val.strip())
        if m:
            tgt = label_to_idx.get(m.group(1))
            if tgt is None:
                out.append(val)  
                pc += 1
            else:
                visit_count[pc] = visit_count.get(pc, 0) + 1
                if visit_count[pc] > 3:
                 
                    out.extend(v for k, v in nodes[pc:] if k == "stmt")
                    break
                pc = tgt
        else:
            out.append(val)
            pc += 1

    linear = ''.join(out)
   
    try:
        linear = _decode_php_like_string_literals(linear)
    except Exception:
        pass

    linear = re.sub(r'[ \t]+\n', '\n', linear)
    linear = linear.strip()
    return linear if linear and linear != code else None

def deobfuscate(text: str) -> Optional[str]:
    s = (text or "").strip()
    if not s:
        return None

   
    m = _data_uri_pat.search(s)
    if m:
        try:
            raw = base64.b64decode(m.group(1) + "=" * ((-len(m.group(1))) % 4))
            return raw.decode("utf-8", errors="replace")
        except Exception:
            pass

  
    m = re.search(r"eval\s*\(\s*(['\"])((?:\\x[0-9A-Fa-f]{2})+)\1\s*\)\s*;?", s)
    if m:
        try:
            payload = m.group(2)
            bs = bytes(int(payload[i+2:i+4], 16) for i in range(0, len(payload), 4))
            return bs.decode("utf-8", errors="replace")
        except Exception:
            return None

   
    m = _b64_call_pat.search(s)
    if m:
        b = m.group(1)
        try:
            raw = base64.b64decode(b + "=" * ((-len(b)) % 4))
            try:
                return raw.decode("utf-8")
            except Exception:
                return raw.decode("latin1", errors="replace")
        except Exception:
            pass

    looks_like_code = ("<?php" in s) or re.search(r"\b(function|goto|header|var|let|const|class|style|<\w+)\b", s)
    has_escapes = ("\\x" in s) or bool(re.search(r"\\[0-7]{1,3}", s))
    if looks_like_code and has_escapes:
        try:
            return _decode_php_like_string_literals(s)
        except Exception:
            pass


    if re.fullmatch(r"(?:\\x[0-9A-Fa-f]{2}\s*)+", s):
        try:
            parts = re.findall(r"\\x([0-9A-Fa-f]{2})", s)
            bs = bytes(int(h, 16) for h in parts)
            return bs.decode("utf-8", errors="replace")
        except Exception:
            return None


    ent = _decode_html_entities(s)
    if ent is not None:
        return ent


    css = _decode_css_hex_escapes(s)
    if css is not None:
        return css


    s_clean = re.sub(r"[^A-Za-z0-9+/=]", "", s)
    if len(s_clean) >= 12 and all(ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for ch in s_clean):
        try:
            raw = base64.b64decode(s_clean + "=" * ((-len(s_clean)) % 4))
            return raw.decode("utf-8", errors="replace")
        except Exception:
            pass

  
    if "\\x" in s and not _hex_byte_pat.search(s):
        return None

    return None


def slugify(text: str) -> str:
    t=text.lower()
    t=re.sub(r"[^\w\s-]+", "", t, flags=re.U)
    t=re.sub(r"\s+", "-", t, flags=re.U)
    t=re.sub(r"-{2,}", "-", t).strip("-")
    return t
def random_password(length=16, use_upper=True, use_digits=True, use_symbols=False) -> str:
    chars = list(string.ascii_lowercase)
    if use_upper: chars += list(string.ascii_uppercase)
    if use_digits: chars += list(string.digits)
    if use_symbols: chars += list("!@#$%^&*()_+-=[]{};:,.?/|")
    random.SystemRandom().shuffle(chars)
    return "".join(random.SystemRandom().choice(chars) for _ in range(max(4, length)))
def count_chars_stats(text: str) -> dict:
    total=len(text)
    spaces=sum(1 for ch in text if ch == ' ')
    tabs=sum(1 for ch in text if ch == '\t')
    newlines=text.count('\n')
    nonspace=sum(1 for ch in text if not ch.isspace())
    return {
        "total": total,
        "spaces": spaces,
        "tabs": tabs,
        "newlines": newlines,
        "nonspace": nonspace
    }
from PySide6.QtGui import QSyntaxHighlighter, QColor
class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language: str = "Plain"):
        super().__init__(document)
        self.language = language
        self.rules: List[Tuple[re.Pattern, QTextCharFormat]] = []
        self.ml: List[Tuple[str, str, QTextCharFormat, int]] = []
        self._build_rules()
    def setLanguage(self, lang: str):
        self.language = lang
        self._build_rules()
        self.rehighlight()
    def _fmt(self, color: str, bold=False, italic=False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold: f.setFontWeight(QFont.Bold)
        if italic: f.setFontItalic(True)
        return f
    def _add(self, pattern: str, fmt: QTextCharFormat, flags=0):
        self.rules.append((re.compile(pattern, flags), fmt))
    def _add_ml(self, start: str, end: str, fmt: QTextCharFormat, state: int):
        self.ml.append((start, end, fmt, state))
    def _build_rules(self):
        self.rules.clear(); self.ml.clear()
        lang = self.language
        kw  = self._fmt("#0b56d6", bold=True)
        strf= self._fmt("#0a8f5b")
        numf= self._fmt("#aa00aa")
        comf= self._fmt("#8a8f98", italic=True)
        tagf= self._fmt("#1e66b2", bold=True)
        attr= self._fmt("#7c4dff")
        valf= self._fmt("#0a8f5b")
        if lang == "Python":
            self._add(r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b", kw)
            self._add(r"\b(def|class)\s+\w+", self._fmt("#b8007f", bold=True))
            self._add(r"#[^\n]*", comf)
            self._add(r"\"[^\"\\]*(\\.[^\"\\]*)*\"", strf); self._add(r"'[^'\\]*(\\.[^'\\]*)*'", strf)
            self._add(r"\b\d+(\.\d+)?\b", numf)
            self._add_ml("'''","'''", strf, 10); self._add_ml('"""','"""', strf, 11)
        elif lang == "JSON":
            self._add(r"\"([^\"\\]|\\.)*\"(?=\s*:)", self._fmt("#1e66b2", bold=True))
            self._add(r":\s*\"([^\"\\]|\\.)*\"", valf)
            self._add(r"\b(true|false|null)\b", kw)
            self._add(r"[-+]?\b\d+(\.\d+)?([eE][-+]?\d+)?\b", numf)
        elif lang == "HTML/XML":
            self._add(r"</?\w[\w:-]*", tagf)
            self._add(r"\b[\w:-]+(?=\=)", attr)
            self._add(r"=(\"[^\"]*\"|'[^']*')", valf)
            self._add_ml("<!--","-->", comf, 20)
        elif lang == "CSS":
            self._add(r"[#\.]?[a-zA-Z_][\w\-\.:#]*\s*(?=\{)", self._fmt("#1e66b2", bold=True))
            self._add(r"\b[a-zA-Z\-]+(?=\s*:)", attr)
            self._add(r":\s*[^;{}]+", valf)
            self._add(r"\"[^\"\\]*(\\.[^\"\\]*)*\"|'[^'\\]*(\\.[^'\\]*)*'", strf)
            self._add(r"\b\d+(\.\d+)?(px|em|rem|%|vh|vw|s|ms)?\b", numf)
            self._add_ml("/*","*/", comf, 30)
        elif lang in ("JavaScript", "PHP"):
            self._add(r"\b(function|return|var|let|const|if|else|for|while|do|switch|case|break|continue|new|try|catch|finally|throw|class|extends|super|this|import|from|export|default|await|async|typeof|instanceof|in|of|delete|void|yield)\b", kw)
            self._add(r"//[^\n]*", comf)
            self._add(r"\"[^\"\\]*(\\.[^\"\\]*)*\"", strf)
            self._add(r"'[^'\\]*(\\.[^'\\]*)*'", strf)
            self._add(r"`[^`\\]*(\\.[^`\\]*)*`", strf)
            self._add(r"\b\d+(\.\d+)?\b", numf)
            self._add_ml("/*","*/", comf, 40)
        else:
            self._add(r"//[^\n]*|#[^\n]*", comf)
            self._add(r"/\*.*?\*/", comf, re.S)
            self._add(r"\"[^\"\\]*(\\.[^\"\\]*)*\"|'[^'\\]*(\\.[^'\\]*)*'|`[^`\\]*(\\.[^`\\]*)*`", strf)
            self._add(r"\b\d+(\.\d+)?\b", numf)
    def highlightBlock(self, text: str):
        for rx, fmt in self.rules:
            for m in rx.finditer(text):
                self.setFormat(m.start(), m.end()-m.start(), fmt)
        prev_state = self.previousBlockState()
        self.setCurrentBlockState(0)
        for start, end, fmt, state in self.ml:
            if prev_state == state:
                start_index = 0
            else:
                start_index = text.find(start, 0)
            while start_index >= 0:
                end_index = text.find(end, start_index + len(start))
                if end_index == -1:
                    self.setFormat(start_index, len(text) - start_index, fmt)
                    self.setCurrentBlockState(state)
                    return
                else:
                    length = end_index + len(end) - start_index
                    self.setFormat(start_index, length, fmt)
                    start_index = text.find(start, end_index + len(end))
            if prev_state == state:
                self.setCurrentBlockState(state)
                return
class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor); self._editor = editor
    def sizeHint(self): return QSize(self._editor.line_number_area_width(), 0)
    def paintEvent(self, event): self._editor.line_number_area_paint_event(event)
class CodeEditor(QPlainTextEdit):
    BIG_PASTE_THRESHOLD = 80_000
    HL_DISABLE_THRESHOLD = 120_000
    HL_REENABLE_THRESHOLD = 80_000
    VERY_BIG_DOC = 400_000

    def __init__(self):
        super().__init__()
        self._line_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)


        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        f = QFont("Consolas, Menlo, Monaco, Courier New", 11)
        f.setStyleHint(QFont.Monospace)
        self.setFont(f)

        self.highlighter = CodeHighlighter(self.document(), "Plain")
        self.setAcceptDrops(True)
        self._hl_enabled = True
        self._current_line_color = QColor(200, 220, 255, 60)

    def setHighlightLanguage(self, lang: str):
        try:
            if not self._hl_enabled or not self.highlighter:
                return
           
            if getattr(self.highlighter, "language", None) == lang:
                return
            self.highlighter.setLanguage(lang)
        except Exception:
            pass

    def set_highlighting_enabled(self, on: bool):
        self._hl_enabled = on
        if on:
            self.highlighter.setDocument(self.document())
            self.highlighter.rehighlight()
        else:
            self.highlighter.setDocument(None)

    def setPlainTextFast(self, text: str):
        hl = self.highlighter
        if hl:
            hl.setDocument(None)
        self.setUpdatesEnabled(False)
        sb = QSignalBlocker(self)
        try:
            super().setPlainText(text)
        finally:
            del sb
            self.setUpdatesEnabled(True)

        doc_len = len(text)
 
        if doc_len >= self.HL_DISABLE_THRESHOLD and self._hl_enabled:
            self.set_highlighting_enabled(False)
            return

      
        if self._hl_enabled and hl:
            hl.setDocument(self.document())
            QTimer.singleShot(0, hl.rehighlight)

    def insertFromMimeData(self, source):
        try:
            if source and source.hasText():
                txt = source.text()
                if txt and len(txt) >= self.BIG_PASTE_THRESHOLD:
                    self._bulk_replace_selection_or_insert(txt)
                    return
                cur = self.textCursor()
                full_len = len(self.toPlainText())
                if txt and (full_len == 0 or (cur.hasSelection() and cur.selectionStart() == 0 and cur.selectionEnd() == full_len)):
                    self.setPlainTextFast(txt)
                    return
        except Exception:
            pass
        try:
            return super().insertFromMimeData(source)
        except Exception:
            return

    def _bulk_replace_selection_or_insert(self, txt: str):
        try:
            self.setUpdatesEnabled(False)
            was_hl = self._hl_enabled
            if was_hl:
                self.set_highlighting_enabled(False)
            sb = QSignalBlocker(self)
            cur = self.textCursor()
            cur.insertText(txt)
            del sb
        except Exception:
            try:
                super().setPlainText(txt)
            except Exception:
                pass
        finally:
            self.setUpdatesEnabled(True)
            try:
                if len(self.toPlainText()) <= self.VERY_BIG_DOC:
                    if self._hl_enabled and self.highlighter and self.highlighter.document() is None:
                        self.highlighter.setDocument(self.document())
                        self.highlighter.rehighlight()
            except Exception:
                pass

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("#f0f2f8"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#8b94a6"))
                fm = self.fontMetrics()
                painter.drawText(0, top, self._line_area.width()-6, fm.height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def paintEvent(self, event):
        super().paintEvent(event)
        try:
            cur = self.textCursor()
            blk = cur.block()
            if not blk.isValid():
                return
            r = self.blockBoundingGeometry(blk).translated(self.contentOffset())
            if r.isValid():
                painter = QPainter(self.viewport())
                painter.fillRect(0, int(r.top()), self.viewport().width(), int(r.height()), self._current_line_color)
        except Exception:
            pass


SUPPORTED_LANGS = ["HTML/XML", "CSS", "JavaScript", "PHP", "JSON", "Python", "Plain"]
class CodePane(QWidget):
    def __init__(self, title_key: str, show_lang: bool = True, show_io_stats: bool = True):
        super().__init__()
        self.title_key = title_key
        v = QVBoxLayout(self)
        self.header = QLabel(i18n.t(title_key)); self.header.setObjectName("paneHeader"); v.addWidget(self.header)
        self.splitter = QSplitter(Qt.Horizontal)
        self.input = CodeEditor()
        self.output = CodeEditor(); self.output.setReadOnly(True)
        self.input.setPlaceholderText("...")
        self.output.setPlaceholderText("...")
        self.splitter.addWidget(self.input); self.splitter.addWidget(self.output)
        self.splitter.setSizes([900, 900]); v.addWidget(self.splitter, 1)
        bottom = QHBoxLayout()
        self.lblLang = QLabel(i18n.t("ui.lang") + ":")
        self.lang = QComboBox(); self.lang.addItems(SUPPORTED_LANGS)
        self.stats = QLabel("—"); self.stats.setMinimumWidth(360)
        bottom.addWidget(self.lblLang); bottom.addWidget(self.lang)
        bottom.addStretch(1); bottom.addWidget(self.stats)
        v.addLayout(bottom)        
        if not show_lang:
            self.lblLang.hide()
            self.lang.hide()
        if not show_io_stats:
            self.stats.hide()
        if show_lang:
            self.lang.currentTextChanged.connect(self._on_lang_changed)
        self.input.textChanged.connect(self._on_input_changed)
        self._stats_timer = QTimer(self); self._stats_timer.setSingleShot(True)
        self._stats_timer.timeout.connect(self._update_stats_now)
        self.input.textChanged.connect(lambda: self._stats_timer.start(120))
        self.output.textChanged.connect(lambda: self._stats_timer.start(120))
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        self.header.setText(i18n.t(self.title_key))
        self.lblLang.setText(i18n.t("ui.lang") + ":")
    def run_action(self):  
        pass
    def act_open(self):
        path, _ = QFileDialog.getOpenFileName(self, i18n.t("act.open"), "", "All files (*.*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    self.input.setPlainTextFast(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open:\n{e}")
    def act_save(self):
        path, _ = QFileDialog.getSaveFileName(self, i18n.t("act.save"), "result.txt", "All files (*.*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    self.output.document().setModified(False)
                    f.write(self.output.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot save:\n{e}")
    def act_copy(self):
        sb = self._sb()
        if sb: sb.showMessage(i18n.t("status.copied"), 1200)
        self.window().clipboard().setText(self.output.toPlainText())
    def act_paste(self):
        txt = self.window().clipboard().text()
        if txt:
            self.input.setPlainTextFast(txt)
    def act_swap(self):
        a, b = self.input.toPlainText(), self.output.toPlainText()
        self.input.setPlainTextFast(b); self.output.setPlainTextFast(a)
    def act_clear(self):
        self.input.clear(); self.output.clear(); self.window().statusBar().showMessage(i18n.t("status.cleared"), 800)
    def _on_lang_changed(self, t: str):
        self.input.setHighlightLanguage(t); self.output.setHighlightLanguage(t)
    def _on_input_changed(self):
        try:            
            win = self.window()
            tabs = getattr(win, "tabs", None)
            if tabs is not None and tabs.currentWidget() is not self:
                return
            doc_len = max(0, self.input.document().characterCount() - 1)
            if doc_len > 200_000:
                use_lang = "Plain"
            else:
                txt = self.input.toPlainText()
                use_lang = detect_language(txt[:8192])
            self.input.setHighlightLanguage(use_lang)
            self.output.setHighlightLanguage(use_lang)
        except Exception:
            pass
    def _update_stats_now(self):
        try:
            win = self.window()
            tabs = getattr(win, "tabs", None)
            if tabs is not None and tabs.currentWidget() is not self:
                return
            a = max(0, self.input.document().characterCount() - 1)
            b = max(0, self.output.document().characterCount() - 1)
            delta = a - b
            self.stats.setText(f"{i18n.t('ui.in')}: {a} | {i18n.t('ui.out')}: {b} | {i18n.t('ui.diff')}: {delta:+d}")
        except Exception:
            pass    
    def _sb(self):
        """Безопасно вернуть статусбар главного окна (или None, если его ещё нет)."""
        w = self.window()
        from PySide6.QtWidgets import QMainWindow
        return w.statusBar() if isinstance(w, QMainWindow) else None
class CommentsAllTab(CodePane):
    def __init__(self):
        super().__init__("clean.header", show_lang=False)        
        row = QHBoxLayout()
        self.cmbMode = QComboBox()
        self.cmbMode.addItems([
            i18n.t("clean.mode.all"),
            i18n.t("clean.mode.custom"),
            i18n.t("clean.mode.html"),
            i18n.t("clean.mode.css"),
            i18n.t("clean.mode.js"),
            i18n.t("clean.mode.php"),
            i18n.t("clean.mode.json"),
            i18n.t("clean.mode.py"),
        ])
        self.btnRun  = QPushButton(i18n.t("clean.run"))
        self.btnCopy = QPushButton(i18n.t("clean.copy"))
        for w in (self.cmbMode, self.btnRun, self.btnCopy):
            w.setCursor(Qt.PointingHandCursor)
        row.addWidget(QLabel(i18n.t("clean.mode"))); row.addWidget(self.cmbMode); row.addStretch(1)
        row.addWidget(self.btnRun); row.addWidget(self.btnCopy)
        self.layout().insertLayout(1, row)        
        self._customRowW = QWidget()
        crow = QHBoxLayout(self._customRowW); crow.setContentsMargins(0, 0, 0, 0)
        self.lblSel = QLabel(i18n.t("clean.sel_types"))
        self.cbHTML   = QCheckBox(i18n.t("clean.type.html"))
        self.cbCBlock = QCheckBox(i18n.t("clean.type.cblock"))
        self.cbCLine  = QCheckBox(i18n.t("clean.type.cline"))
        self.cbHash   = QCheckBox(i18n.t("clean.type.hash"))
        for w in (self.cbHTML, self.cbCBlock, self.cbCLine, self.cbHash):
            w.setCursor(Qt.PointingHandCursor)
        crow.addWidget(self.lblSel)
        crow.addWidget(self.cbHTML)
        crow.addWidget(self.cbCBlock)
        crow.addWidget(self.cbCLine)
        crow.addWidget(self.cbHash)
        crow.addStretch(1)
        self.layout().insertWidget(2, self._customRowW)
        self._customRowW.hide()        
        self.cmbMode.currentIndexChanged.connect(self._on_mode_changed)
        self.btnRun.clicked.connect(self.run_action)
        self.btnCopy.clicked.connect(self.act_copy)
        i18n.on_change(lambda _: self.retranslate())
    def _on_mode_changed(self, idx: int):
        self._customRowW.setVisible(idx == 1)
    def retranslate(self):
        self.header.setText(i18n.t(self.title_key))
        cur = self.cmbMode.currentIndex()
        self.cmbMode.clear()
        self.cmbMode.addItems([
            i18n.t("clean.mode.all"),
            i18n.t("clean.mode.custom"),
            i18n.t("clean.mode.html"),
            i18n.t("clean.mode.css"),
            i18n.t("clean.mode.js"),
            i18n.t("clean.mode.php"),
            i18n.t("clean.mode.json"),
            i18n.t("clean.mode.py"),
        ])
        self.cmbMode.setCurrentIndex(max(0, cur))
        self.btnRun.setText(i18n.t("clean.run"))
        self.btnCopy.setText(i18n.t("clean.copy"))
        self.lblSel.setText(i18n.t("clean.sel_types"))
        self.cbHTML.setText(i18n.t("clean.type.html"))
        self.cbCBlock.setText(i18n.t("clean.type.cblock"))
        self.cbCLine.setText(i18n.t("clean.type.cline"))
        self.cbHash.setText(i18n.t("clean.type.hash"))
    def run_action(self):
        code = self.input.toPlainText()
        idx = self.cmbMode.currentIndex()
        if idx == 0:  
            res = strip_comments_all(code)
        elif idx == 1:  
            res = strip_comments_custom(
                code,
                html=self.cbHTML.isChecked(),
                c_block=self.cbCBlock.isChecked(),
                c_line=self.cbCLine.isChecked(),
                py_hash=self.cbHash.isChecked(),
            )
        else:
            map_lang = {
                2: "HTML/XML", 3: "CSS", 4: "JavaScript",
                5: "PHP", 6: "JSON", 7: "Python"
            }
            res = strip_comments(code, map_lang[idx])
        use_lang = detect_language(code)
        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage(use_lang)
        self.window().statusBar().showMessage(i18n.t("clean.run"), 1000)
class FormattingTab(CodePane):
    def __init__(self):
        super().__init__("fmt.header", show_lang=True)

        self.cbTabs   = QCheckBox(i18n.t("fmt.tabs"))
        self.spIndent = QSpinBox(); self.spIndent.setRange(1, 12); self.spIndent.setValue(4)
        self.cbSort   = QCheckBox(i18n.t("fmt.sort"))
        self.lblIndent = QLabel(i18n.t("fmt.indent") + ":")
        self.lblBlank  = QLabel(i18n.t("fmt.blank") + ":")
        self.spBlank   = QSpinBox(); self.spBlank.setRange(0, 10); self.spBlank.setValue(1)
        self.cbTrim    = QCheckBox(i18n.t("fmt.trim")); self.cbTrim.setChecked(True)
        self.btnPretty = QPushButton(i18n.t("fmt.pretty"))
        self.btnMinify = QPushButton(i18n.t("fmt.minify"))

        for w in (self.cbTabs, self.cbSort, self.cbTrim, self.btnPretty, self.btnMinify):
            w.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout()
        row.addWidget(self.lblIndent); row.addWidget(self.spIndent)
        row.addWidget(self.cbTabs)
        row.addSpacing(12)
        row.addWidget(self.lblBlank); row.addWidget(self.spBlank)
        row.addWidget(self.cbTrim)
        row.addStretch(1)
        row.addWidget(self.cbSort)
        row.addWidget(self.btnPretty)
        row.addWidget(self.btnMinify)
        self.layout().insertLayout(1, row)

        self.btnPretty.clicked.connect(self._do_pretty)
        self.btnMinify.clicked.connect(self._do_minify)
        i18n.on_change(lambda _: self.retranslate())

    def retranslate(self):
        super().retranslate()
        self.cbTabs.setText(i18n.t("fmt.tabs"))
        self.cbSort.setText(i18n.t("fmt.sort"))
        self.cbTrim.setText(i18n.t("fmt.trim"))
        self.btnPretty.setText(i18n.t("fmt.pretty"))
        self.btnMinify.setText(i18n.t("fmt.minify"))
        self.lblIndent.setText(i18n.t("fmt.indent") + ":")
        self.lblBlank.setText(i18n.t("fmt.blank") + ":")

    def _apply_ws_options(self, text: str) -> str:
        max_blank = self.spBlank.value()
        trim_tail = self.cbTrim.isChecked()
        return tidy_whitespace(text, max_blank_lines=max_blank, trim_trailing=trim_tail)

    def _do_pretty(self):
        code = self.input.toPlainText()

      
        sel_lang = self.lang.currentText()
        detected = detect_language(code[:8192])

        def pick_lang(sel: str, det: str) -> str:
            if sel == "Plain":
                return det
            if sel == "HTML/XML" and det in ("JavaScript", "CSS"):
                return det
            if sel in ("JavaScript", "CSS") and det == "HTML/XML":
                return det
            return sel

        lang = pick_lang(sel_lang, detected)

        res = pretty_format(
            code,
            lang,
            self.cbTabs.isChecked(),
            self.spIndent.value(),
            self.cbSort.isChecked()
        )
        res = res.rstrip("\r\n")
        res = self._apply_ws_options(res)

        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage(lang)
        self.window().statusBar().showMessage(i18n.t("fmt.pretty"), 1000)

    def _do_minify(self):
        code = self.input.toPlainText()
        lang = self.lang.currentText()
        res = minify_code(code, lang).rstrip("\r\n")
        res = self._apply_ws_options(res)
        use_lang = detect_language(code[:8192])
        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage(use_lang)
        self.window().statusBar().showMessage(i18n.t("fmt.minify"), 1000)

    def run_action(self):
        self._do_pretty()



def obfuscate_js_eval_base64(code: str) -> str:
    b = b64(code)
 
    return ("(function(){"
            "const d=(s)=>{try{return decodeURIComponent(escape(s))}catch(e){return s}};"
            "eval(d(atob('%s')));"
            "})();") % b


def obfuscate_hex_js(code: str) -> str:
    """
    Обфускация через \\xNN: берём UTF-8 байты исходного текста
    и экранируем каждый байт. Так deobfuscate сможет вернуть
    исходную строку с Unicode.
    """
    bs = code.encode("utf-8")
    esc = ''.join('\\x%02x' % b for b in bs)
  
    return "eval('%s');" % esc
def obfuscate_generic_base64(code: str, lang: str) -> str:
    b = b64(code)
    if lang == "Python":
        return f"import base64;exec(base64.b64decode('{b}').decode('utf-8'))"
    if lang == "PHP":
        return f"<?php eval(base64_decode('{b}'));"
    if lang == "HTML/XML":
        return (f"<script>(()=>{{const s=atob('{b}');try{{document.write(decodeURIComponent(escape(s)))}}"
                f"catch(e){{document.write(s)}}}})();</script>")
    if lang == "CSS":
        return (f"<script>(()=>{{const css=(()=>{{const s=atob('{b}');try{{return decodeURIComponent(escape(s))}}"
                f"catch(e){{return s}}}})();const st=document.createElement('style');st.textContent=css;"
                f"document.head.appendChild(st);}})();</script>")
    return b
def append_comment(code: str, lang: str, comment: str) -> str:
    c = comment.strip()
    if not c: return code
    if lang in ("JavaScript", "PHP", "CSS", "Plain", "JSON"):
        return f"/* {c} */\n{code}"
    if lang == "Python":
        lines = "\n".join(f"# {ln}" if ln.strip() else "#" for ln in c.splitlines())
        return f"{lines}\n{code}"
    if lang == "HTML/XML":
        return f"<!-- {c} -->\n{code}"
    return code
class ObfuscateTab(CodePane):
    def __init__(self):
        super().__init__("obf.header", show_lang=True)
        row = QHBoxLayout()
        self.cmbMethod = QComboBox(); self.cmbMethod.addItems([
            i18n.t("obf.m.eval64"), i18n.t("obf.m.hex"), i18n.t("obf.m.container")
        ])
        self.edComment = QPlainTextEdit(); self.edComment.setPlaceholderText(i18n.t("obf.comment")); self.edComment.setFixedHeight(64)
        self.btnObf  = QPushButton(i18n.t("obf.run"))
        self.btnDeobf= QPushButton(i18n.t("obf.deobf"))
        self.btnAddComment = QPushButton(i18n.t("obf.addc"))
        self.btnTest = QPushButton(i18n.t("obf.test"))
        for w in (self.cmbMethod, self.btnObf, self.btnDeobf, self.btnAddComment, self.btnTest):
            w.setCursor(Qt.PointingHandCursor)
        self._lblMethod  = QLabel(i18n.t("obf.method"))
        self._lblComment = QLabel(i18n.t("obf.comment"))
        row.addWidget(self._lblMethod); row.addWidget(self.cmbMethod); row.addStretch(1)
        row2 = QHBoxLayout(); row2.addWidget(self._lblComment); row2.addWidget(self.edComment)
        row3 = QHBoxLayout(); row3.addWidget(self.btnObf); row3.addWidget(self.btnDeobf); row3.addWidget(self.btnAddComment); row3.addWidget(self.btnTest)
        self.layout().insertLayout(1, row)
        self.layout().insertLayout(2, row2)
        self.layout().insertLayout(3, row3)
        self.btnObf.clicked.connect(self._do_obf)
        self.btnDeobf.clicked.connect(self._do_deobf)
        self.btnAddComment.clicked.connect(self._apply_comment_to_output)
        self.btnTest.clicked.connect(self._test_js_in_browser)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        cur = self.cmbMethod.currentIndex()
        self.cmbMethod.clear()
        self.cmbMethod.addItems([i18n.t("obf.m.eval64"), i18n.t("obf.m.hex"), i18n.t("obf.m.container")])
        self.cmbMethod.setCurrentIndex(max(0, cur))
        self.btnObf.setText(i18n.t("obf.run"))
        self.btnDeobf.setText(i18n.t("obf.deobf"))
        self.btnAddComment.setText(i18n.t("obf.addc"))
        self.btnTest.setText(i18n.t("obf.test"))
        self._lblMethod.setText(i18n.t("obf.method"))
        self._lblComment.setText(i18n.t("obf.comment"))
    def _do_obf(self):
        code = self.input.toPlainText()
        lang = self.lang.currentText()
        method = self.cmbMethod.currentIndex()
        if method == 0:
            res = obfuscate_js_eval_base64(code); out_lang = "JavaScript"
        elif method == 1:
            res = obfuscate_hex_js(code); out_lang = "JavaScript"
        else:
            res = obfuscate_generic_base64(code, lang)
            out_lang = "JavaScript" if lang in ("HTML/XML", "CSS") else lang
        res = append_comment(res, out_lang, self.edComment.toPlainText())
        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage(out_lang)
        self.window().statusBar().showMessage(i18n.t("obf.run"), 1000)
    def _do_deobf(self):
        s = self.input.toPlainText() or self.output.toPlainText()
        if not s:
            QMessageBox.information(self, "Info", "Insert obfuscated code in input or get result first.")
            return
        res = deobfuscate(s)
        if res is None:
            QMessageBox.information(self, "Info", "Nothing recognizable to decode.")
            return
        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage(detect_language(res))
        self.window().statusBar().showMessage(i18n.t("obf.deobf"), 1000)
    def _apply_comment_to_output(self):
        res = self.output.toPlainText()
        if not res: return
        lang = self.lang.currentText()
        self.output.setPlainTextFast(append_comment(res, lang, self.edComment.toPlainText()))
    def _test_js_in_browser(self):
        js = self.output.toPlainText().strip() or self.input.toPlainText().strip()
        if not js:
            QMessageBox.information(self, "Info", "Nothing to test.")
            return
        html = f"<!doctype html><meta charset='utf-8'><title>Test</title><script>{js}</script>"
        fd, path = tempfile.mkstemp(prefix="lce_test_", suffix=".html")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open_new_tab(path)
from PySide6.QtWidgets import QLineEdit
class JsLinkTab(CodePane):
    def __init__(self):
        super().__init__("js.header", show_lang=False)
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.edUrl  = QLineEdit()
        self.edUrl.setPlaceholderText(i18n.t("js.url"))
        self.edText = QLineEdit()
        self.edText.setPlaceholderText(i18n.t("js.text"))
        self.cmbView = QComboBox()
        self.cmbView.addItems([
            "Bookmarklet",
            "HTML <a>",
            "JS open()"
        ])
        self.btnGen  = QPushButton(i18n.t("js.gen"))
        self.btnOpen = QPushButton(i18n.t("js.open"))
        for w in (self.edUrl, self.edText, self.cmbView, self.btnGen, self.btnOpen):
            if hasattr(w, "setCursor"):
                w.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout()
        self._lblUrl  = QLabel(i18n.t("js.url"))
        self._lblText = QLabel(i18n.t("js.text"))
        self._lblView = QLabel(i18n.t("js.view"))
        row.addWidget(self._lblUrl);  row.addWidget(self.edUrl, 2)
        row.addWidget(self._lblText); row.addWidget(self.edText, 1)
        row.addWidget(self._lblView); row.addWidget(self.cmbView)
        row.addWidget(self.btnGen); row.addWidget(self.btnOpen)
        self.layout().insertLayout(1, row)
        self.btnGen.clicked.connect(self._do_generate)
        self.btnOpen.clicked.connect(self._do_open)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        cur = self.cmbView.currentIndex()
        self.cmbView.clear()
        self.cmbView.addItems(["Bookmarklet", "HTML <a>", "JS open()"])
        self.cmbView.setCurrentIndex(max(0, cur))
        self.btnGen.setText(i18n.t("js.gen"))
        self.btnOpen.setText(i18n.t("js.open"))
        self.edUrl.setPlaceholderText(i18n.t("js.url"))
        self.edText.setPlaceholderText(i18n.t("js.text"))
        self._lblUrl.setText(i18n.t("js.url"))
        self._lblText.setText(i18n.t("js.text"))
        self._lblView.setText(i18n.t("js.view"))
    def _mk_bookmarklet(self, url: str) -> str:
        b = b64(url)
        js = "(()=>{const u=atob('%s');location.href=u})();" % b
        return "javascript:" + js
    def _mk_html_anchor(self, url: str, text: str) -> str:
        href = self._mk_bookmarklet(url)
        caption = text.strip() or url
        return f'<a href="{href}">{caption}</a>'
    def _mk_js_open(self, url: str) -> str:
        b = b64(url)
        return "(()=>{const u=atob('%s');window.open(u,'_blank')})();" % b
    def _do_generate(self):
        url = self.edUrl.text().strip()
        if not url:
            QMessageBox.information(self, "Info", "URL is empty.")
            return
        mode = self.cmbView.currentIndex()
        if mode == 0:
            out = self._mk_bookmarklet(url)
            out_lang = "JavaScript"
        elif mode == 1:
            out = self._mk_html_anchor(url, self.edText.text())
            out_lang = "HTML/XML"
        else:
            out = self._mk_js_open(url)
            out_lang = "JavaScript"
        self.output.setPlainTextFast(out)
        self.output.setHighlightLanguage(out_lang)
        self.window().statusBar().showMessage(i18n.t("js.gen"), 1000)
    def _do_open(self):
        url = self.edUrl.text().strip()
        if not url:
            QMessageBox.information(self, "Info", "URL is empty.")
            return
        webbrowser.open_new_tab(url)
import webbrowser, urllib.parse, secrets, string, unicodedata
class UtmTab(CodePane):
    def __init__(self):
        super().__init__("utm.header", show_lang=False)
        self.edUrl = QLineEdit()
        self.edUrl.setPlaceholderText(i18n.t("utm.url"))
        self.edSrc = QLineEdit();  self.edSrc.setPlaceholderText("utm_source")
        self.edMed = QLineEdit();  self.edMed.setPlaceholderText("utm_medium")
        self.edCmp = QLineEdit();  self.edCmp.setPlaceholderText("utm_campaign")
        self.edTrm = QLineEdit();  self.edTrm.setPlaceholderText("utm_term")
        self.edCnt = QLineEdit();  self.edCnt.setPlaceholderText("utm_content")
        self.cbOverride = QCheckBox(i18n.t("utm.override"))
        self.btnGen = QPushButton(i18n.t("utm.gen"))
        self.btnOpen = QPushButton(i18n.t("utm.open"))
        for w in (self.btnGen, self.btnOpen):
            w.setCursor(Qt.PointingHandCursor)
        self._lblUrl      = QLabel(i18n.t("utm.url"))
        self._lblSource   = QLabel(i18n.t("utm.source") + ":")
        self._lblMedium   = QLabel(i18n.t("utm.medium") + ":")
        self._lblCampaign = QLabel(i18n.t("utm.campaign") + ":")
        self._lblTerm     = QLabel(i18n.t("utm.term") + ":")
        self._lblContent  = QLabel(i18n.t("utm.content") + ":")
        row1 = QHBoxLayout()
        row1.addWidget(self._lblUrl); row1.addWidget(self.edUrl, 3)
        row1.addWidget(self.cbOverride)
        row1.addWidget(self.btnGen); row1.addWidget(self.btnOpen)
        self.layout().insertLayout(1, row1)
        row2 = QHBoxLayout()
        row2.addWidget(self._lblSource);   row2.addWidget(self.edSrc)
        row2.addWidget(self._lblMedium);   row2.addWidget(self.edMed)
        row2.addWidget(self._lblCampaign); row2.addWidget(self.edCmp)
        self.layout().insertLayout(2, row2)
        row3 = QHBoxLayout()
        row3.addWidget(self._lblTerm);    row3.addWidget(self.edTrm)
        row3.addWidget(self._lblContent); row3.addWidget(self.edCnt)
        self.layout().insertLayout(3, row3)
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.output.setHighlightLanguage("HTML/XML")
        self.btnGen.clicked.connect(self._do_generate)
        self.btnOpen.clicked.connect(self._do_open)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        self.header.setText(i18n.t("utm.header"))
        self._lblUrl.setText(i18n.t("utm.url"))
        self._lblSource.setText(i18n.t("utm.source") + ":")
        self._lblMedium.setText(i18n.t("utm.medium") + ":")
        self._lblCampaign.setText(i18n.t("utm.campaign") + ":")
        self._lblTerm.setText(i18n.t("utm.term") + ":")
        self._lblContent.setText(i18n.t("utm.content") + ":")
        self.cbOverride.setText(i18n.t("utm.override"))
        self.btnGen.setText(i18n.t("utm.gen"))
        self.btnOpen.setText(i18n.t("utm.open"))
        self.edUrl.setPlaceholderText(i18n.t("utm.url"))
        self.edSrc.setPlaceholderText("utm_source")
        self.edMed.setPlaceholderText("utm_medium")
        self.edCmp.setPlaceholderText("utm_campaign")
        self.edTrm.setPlaceholderText("utm_term")
        self.edCnt.setPlaceholderText("utm_content")
    def _merge_params(self, base_url: str, new_params: dict, override: bool) -> str:
        parts = urllib.parse.urlsplit(base_url)
        q = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
        for k, v in new_params.items():
            if not v:
                continue
            if override or k not in q:
                q[k] = v
        new_query = urllib.parse.urlencode(q, doseq=True)
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    def _do_generate(self):
        url = (self.edUrl.text() or "").strip()
        if not url:
            QMessageBox.information(self, "Info", i18n.t("utm.url_empty"))
            return
        params = {
            "utm_source":   self.edSrc.text().strip(),
            "utm_medium":   self.edMed.text().strip(),
            "utm_campaign": self.edCmp.text().strip(),
            "utm_term":     self.edTrm.text().strip(),
            "utm_content":  self.edCnt.text().strip(),
        }
        out = self._merge_params(url, params, self.cbOverride.isChecked())
        anchor = f'<a href="{out}">{i18n.t("utm.link_text")}</a>\n\n{out}'
        self.output.setPlainTextFast(anchor)
        self.output.setHighlightLanguage("HTML/XML")
        self.window().statusBar().showMessage(i18n.t("utm.gen"), 1200)
    def _do_open(self):
        txt = self.output.toPlainText().strip()
        if not txt:
            self._do_generate()
            txt = self.output.toPlainText().strip()
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        url = lines[-1] if lines else ""
        if url:
            webbrowser.open_new_tab(url)
class OgTab(CodePane):
    def __init__(self):
        super().__init__("og.header", show_lang=False)
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.output.setReadOnly(True)
        self.output.setHighlightLanguage("HTML/XML")
        self._types = [
            ("Сайт",        "website"),
            ("Статья",      "article"),
            ("Место",       "place"),
            ("Бизнес",      "business.business"),
            ("Продукт",     "product"),
            ("Ресторан",    "restaurant.restaurant"),
        ]
        self.cmbType = QComboBox()
        for title, val in self._types:
            self.cmbType.addItem(title, userData=val)
        self.cmbType.setCurrentIndex(0)
        self.edTitle   = QLineEdit()
        self.edDesc    = QLineEdit()
        self.edImage   = QLineEdit()
        self.edUrl     = QLineEdit()
        self.edSite    = QLineEdit()
        self.edLocale  = QLineEdit("ru_RU")
        self.edAppId   = QLineEdit()
        self.edVideo   = QLineEdit()
        self.edExtra   = QPlainTextEdit(); self.edExtra.setFixedHeight(70)
        self.edExtra.setPlaceholderText("Примеры:\nog:audio: https://...\ntwitter:card=summary_large_image\n<meta name=\"twitter:site\" content=\"@site\">")
        self.btnGen  = QPushButton(i18n.t("og.gen"))
        self.btnCopy = QPushButton(i18n.t("act.copy"))
        self.btnGen.setCursor(Qt.PointingHandCursor)
        self.btnCopy.setCursor(Qt.PointingHandCursor)
        self.lblBot = QLabel(f'<a href="https://t.me/WebpageBot">{i18n.t("og.bot")}</a>')
        self.lblBot.setOpenExternalLinks(True)
        r1 = QHBoxLayout()
        self._lblType  = QLabel(i18n.t("og.type"))
        self._lblTitle = QLabel(i18n.t("og.title"))
        self._lblUrl   = QLabel(i18n.t("og.url"))
        r1.addWidget(self._lblType);  r1.addWidget(self.cmbType, 1)
        r1.addWidget(self._lblTitle); r1.addWidget(self.edTitle, 3)
        r1.addWidget(self._lblUrl);   r1.addWidget(self.edUrl, 3)
        self.layout().insertLayout(1, r1)
        r2 = QHBoxLayout()
        self._lblDesc  = QLabel(i18n.t("og.desc"))
        self._lblImage = QLabel(i18n.t("og.image"))
        self._lblVideo = QLabel(i18n.t("og.video"))
        r2.addWidget(self._lblDesc);  r2.addWidget(self.edDesc, 3)
        r2.addWidget(self._lblImage); r2.addWidget(self.edImage, 2)
        r2.addWidget(self._lblVideo); r2.addWidget(self.edVideo, 2)
        self.layout().insertLayout(2, r2)
        r3 = QHBoxLayout()
        self._lblSite   = QLabel(i18n.t("og.site_name"))
        self._lblLocale = QLabel(i18n.t("og.locale"))
        self._lblAppId  = QLabel(i18n.t("og.app_id"))
        r3.addWidget(self._lblSite);   r3.addWidget(self.edSite, 3)
        r3.addWidget(self._lblLocale); r3.addWidget(self.edLocale, 1)
        r3.addWidget(self._lblAppId);  r3.addWidget(self.edAppId, 2)
        self.layout().insertLayout(3, r3)
        r4 = QHBoxLayout()
        self._lblExtra = QLabel(i18n.t("og.extra"))
        r4.addWidget(self._lblExtra); r4.addWidget(self.edExtra, 1)
        self.layout().insertLayout(4, r4)
        r5 = QHBoxLayout()
        r5.addWidget(self.btnGen); r5.addWidget(self.btnCopy)
        r5.addStretch(1); r5.addWidget(self.lblBot)
        self.layout().insertLayout(5, r5)
        self.btnGen.clicked.connect(self._do_generate)
        self.btnCopy.clicked.connect(self.act_copy)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        self.header.setText(i18n.t("og.header"))
        self.btnGen.setText(i18n.t("og.gen"))
        self.btnCopy.setText(i18n.t("act.copy"))
        self._lblType.setText(i18n.t("og.type"))
        self._lblTitle.setText(i18n.t("og.title"))
        self._lblDesc.setText(i18n.t("og.desc"))
        self._lblImage.setText(i18n.t("og.image"))
        self._lblUrl.setText(i18n.t("og.url"))
        self._lblSite.setText(i18n.t("og.site_name"))
        self._lblLocale.setText(i18n.t("og.locale"))
        self._lblAppId.setText(i18n.t("og.app_id"))
        self._lblVideo.setText(i18n.t("og.video"))
        self._lblExtra.setText(i18n.t("og.extra"))
        self.lblBot.setText(f'<a href="https://t.me/WebpageBot">{i18n.t("og.bot")}</a>')
    def _do_generate(self):
        def esc(s: str) -> str:
            return (s.replace("&","&amp;")
                     .replace('"',"&quot;")
                     .replace("<","&lt;")
                     .replace(">","&gt;"))
        typ   = self.cmbType.currentData() or "website"
        title = self.edTitle.text().strip()
        desc  = self.edDesc.text().strip()
        url   = self.edUrl.text().strip()
        img   = self.edImage.text().strip()
        site  = self.edSite.text().strip()
        loc   = self.edLocale.text().strip() or "ru_RU"
        appid = self.edAppId.text().strip()
        video = self.edVideo.text().strip()
        extra = self.edExtra.toPlainText().splitlines()
        lines = ["<!-- Open Graph Generated: a.pr-cy.ru -->"]
        def add(prop, val):
            if val:
                lines.append(f'<meta property="{prop}" content="{esc(val)}">')
        add("og:type", typ)
        add("og:title", title)
        add("og:description", desc)
        add("og:url", url)
        add("og:image", img)
        add("og:site_name", site)
        add("og:locale", loc)
        add("og:video", video)
        if appid:
            lines.append(f'<meta property="fb:app_id" content="{esc(appid)}">')
        for raw in extra:
            ln = raw.strip()
            if not ln:
                continue
            if ln.startswith("<"):
                lines.append(ln)
                continue
            if "=" in ln:
                k, v = ln.split("=", 1)
            elif ":" in ln:
                k, v = ln.split(":", 1)
            else:  
                continue
            k = k.strip(); v = v.strip()
            if not k or not v:
                continue            
            if k.lower().startswith("name "):  
                k = k[5:].strip()
            if k.lower().startswith("name"):
                pass            
            if k.lower().startswith("twitter:"):
                lines.append(f'<meta name="{k}" content="{esc(v)}">')
            else:
                lines.append(f'<meta property="{k}" content="{esc(v)}">')
        out = "\n".join(lines)
        self.output.setPlainTextFast(out)
        self.output.setHighlightLanguage("HTML/XML")
        sb = self._sb()
        if sb: sb.showMessage(i18n.t("og.gen"), 1000)

class FaviconTab(CodePane):
    """
    Генерирует набор иконок, favicon.ico и manifest.json.
    Нужен Pillow: pip install pillow
    """
    def __init__(self):
        super().__init__("fav.header", show_lang=False)
    
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.output.setReadOnly(True)
        self.output.setHighlightLanguage("HTML/XML")

        self.edSrc  = QLineEdit();  self.btnSrc  = QPushButton(i18n.t("fav.pickimg"))
        self.edDir  = QLineEdit();  self.btnDir  = QPushButton(i18n.t("fav.pickdir"))
        self.edPref = QLineEdit("/"); 
        self.edColor= QLineEdit("#ffffff")
        self.edName = QLineEdit(APP_NAME)

        self.btnGen = QPushButton(i18n.t("fav.generate"))
        self.btnOpen= QPushButton(i18n.t("fav.open"))
        self.btnCopy= QPushButton(i18n.t("fav.copy"))
        for w in (self.btnSrc, self.btnDir, self.btnGen, self.btnOpen, self.btnCopy):
            w.setCursor(Qt.PointingHandCursor)

 
        r1 = QHBoxLayout()
        r1.addWidget(QLabel(i18n.t("fav.src")));     r1.addWidget(self.edSrc, 1);   r1.addWidget(self.btnSrc)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel(i18n.t("fav.outdir")));  r2.addWidget(self.edDir, 1);   r2.addWidget(self.btnDir)
        r3 = QHBoxLayout()
        r3.addWidget(QLabel(i18n.t("fav.urlprefix"))); r3.addWidget(self.edPref)
        r3.addWidget(QLabel(i18n.t("fav.themecolor"))); r3.addWidget(self.edColor)
        r3.addWidget(QLabel(i18n.t("fav.appname")));    r3.addWidget(self.edName, 1)
        r4 = QHBoxLayout()
        r4.addWidget(self.btnGen); r4.addWidget(self.btnCopy); r4.addStretch(1); r4.addWidget(self.btnOpen)

        self.layout().insertLayout(1, r1)
        self.layout().insertLayout(2, r2)
        self.layout().insertLayout(3, r3)
        self.layout().insertLayout(4, r4)

   
        self.btnSrc.clicked.connect(self._pick_img)
        self.btnDir.clicked.connect(self._pick_dir)
        self.btnGen.clicked.connect(self._do_generate)
        self.btnOpen.clicked.connect(self._open_dir)
        self.btnCopy.clicked.connect(self.act_copy)

        i18n.on_change(lambda _: self.retranslate())

    def retranslate(self):
        super().retranslate()
        self.header.setText(i18n.t("fav.header"))
        self.btnSrc.setText(i18n.t("fav.pickimg"))
        self.btnDir.setText(i18n.t("fav.pickdir"))
        self.btnGen.setText(i18n.t("fav.generate"))
        self.btnOpen.setText(i18n.t("fav.open"))
        self.btnCopy.setText(i18n.t("fav.copy"))


    def _pick_img(self):
        path, _ = QFileDialog.getOpenFileName(self, i18n.t("fav.pickimg"), "", "Images (*.png *.jpg *.jpeg *.ico)")
        if path:
            self.edSrc.setText(path)

    def _pick_dir(self):
        path = QFileDialog.getExistingDirectory(self, i18n.t("fav.pickdir"), "")
        if path:
            self.edDir.setText(path)

    def _open_dir(self):
        d = (self.edDir.text() or "").strip()
        if d and os.path.isdir(d):
            QDesktopServices.openUrl(QUrl.fromLocalFile(d))

  
    def _normalize_prefix(self, p: str) -> str:
        p = (p or "/").strip()
        if not p.startswith("/"): p = "/" + p
        p = p.rstrip("/")
        return p

    def _load_image(self, path: str):
        try:
            from PIL import Image
        except Exception:
            QMessageBox.critical(self, "Error", "Pillow (PIL) не установлен.\nУстановите: pip install pillow")
            return None
        try:
            img = Image.open(path).convert("RGBA")
            return img
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Не удалось открыть изображение:\n{e}")
            return None

    def _square_resize(self, img, size: int):
      
        from PIL import Image
        w, h = img.size
        L = max(w, h)
        canvas = Image.new("RGBA", (L, L), (0,0,0,0))
        canvas.paste(img, ((L - w)//2, (L - h)//2))
        return canvas.resize((size, size), Image.LANCZOS)

    def _save_png(self, img, path: str, size: int):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im = self._square_resize(img, size)
            im.save(path, format="PNG")
        except Exception as e:
            raise RuntimeError(f"PNG {size}x{size}: {e}")

    def _save_ico(self, img, path: str, sizes=(16, 32, 48, 64)):
        try:
            from PIL import Image
            os.makedirs(os.path.dirname(path), exist_ok=True)
            icons = [self._square_resize(img, s) for s in sizes]

            base = icons[0]
            base.save(path, format="ICO", sizes=[(s, s) for s in sizes])
        except Exception as e:
            raise RuntimeError(f"ICO: {e}")

    def _make_snippet(self, prefix: str, theme: str) -> str:
        p = self._normalize_prefix(prefix)
        lines = [
            f'<link rel="shortcut icon" href="{p}/favicon.ico" type="image/x-icon">',
            f'<link rel="icon" href="{p}/favicon.ico" type="image/x-icon">',
            f'<link rel="apple-touch-icon" sizes="57x57" href="{p}/apple-icon-57x57.png">',
            f'<link rel="apple-touch-icon" sizes="60x60" href="{p}/apple-icon-60x60.png">',
            f'<link rel="apple-touch-icon" sizes="72x72" href="{p}/apple-icon-72x72.png">',
            f'<link rel="apple-touch-icon" sizes="76x76" href="{p}/apple-icon-76x76.png">',
            f'<link rel="apple-touch-icon" sizes="114x114" href="{p}/apple-icon-114x114.png">',
            f'<link rel="apple-touch-icon" sizes="120x120" href="{p}/apple-icon-120x120.png">',
            f'<link rel="apple-touch-icon" sizes="144x144" href="{p}/apple-icon-144x144.png">',
            f'<link rel="apple-touch-icon" sizes="152x152" href="{p}/apple-icon-152x152.png">',
            f'<link rel="apple-touch-icon" sizes="180x180" href="{p}/apple-icon-180x180.png">',
            f'<link rel="icon" type="image/png" sizes="192x192"  href="{p}/android-icon-192x192.png">',
            f'<link rel="icon" type="image/png" sizes="32x32" href="{p}/favicon-32x32.png">',
            f'<link rel="icon" type="image/png" sizes="96x96" href="{p}/favicon-96x96.png">',
            f'<link rel="icon" type="image/png" sizes="16x16" href="{p}/favicon-16x16.png">',
            f'<link rel="manifest" href="{p}/manifest.json">',
            f'<meta name="msapplication-TileColor" content="{theme}">',
            f'<meta name="msapplication-TileImage" content="{p}/ms-icon-144x144.png">',
            f'<meta name="theme-color" content="{theme}">',
        ]
        return "\n".join(lines)

    def _write_manifest(self, folder: str, prefix: str, appname: str, theme: str):
        data = {
            "name": appname or "App",
            "short_name": appname or "App",
            "icons": [
                {"src": f"{prefix}/android-icon-192x192.png", "sizes": "192x192", "type": "image/png"},
                {"src": f"{prefix}/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
            ],
            "theme_color": theme,
            "background_color": theme,
            "display": "standalone"
        }
        path = os.path.join(folder, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _do_generate(self):
        src = (self.edSrc.text() or "").strip()
        outdir = (self.edDir.text() or "").strip()
        pref = self._normalize_prefix(self.edPref.text())
        color = (self.edColor.text() or "#ffffff").strip()
        appn = (self.edName.text() or APP_NAME).strip()

        if not src or not os.path.isfile(src):
            QMessageBox.information(self, "Info", "Укажите исходное изображение (PNG/JPG/ICO).")
            return
        if not outdir:
            QMessageBox.information(self, "Info", "Укажите папку для сохранения.")
            return
        os.makedirs(outdir, exist_ok=True)

        img = self._load_image(src)
        if img is None:
            return


        apple = [57,60,72,76,114,120,144,152,180]
        fav_png = [16,32,96]
        android = [192]
        chrome512 = 512
        ms = [144]
        ico_sizes = (16, 32, 48, 64)

        errors = []
        def try_call(fn):
            try:
                fn()
            except Exception as e:
                errors.append(str(e))

   
        try_call(lambda: self._save_ico(img, os.path.join(outdir, "favicon.ico"), sizes=ico_sizes))
   
        for s in fav_png:
            try_call(lambda s=s: self._save_png(img, os.path.join(outdir, f"favicon-{s}x{s}.png"), s))
   
        for s in apple:
            try_call(lambda s=s: self._save_png(img, os.path.join(outdir, f"apple-icon-{s}x{s}.png"), s))
    
        for s in android:
            try_call(lambda s=s: self._save_png(img, os.path.join(outdir, f"android-icon-{s}x{s}.png"), s))

        for s in ms:
            try_call(lambda s=s: self._save_png(img, os.path.join(outdir, f"ms-icon-{s}x{s}.png"), s))
    
        try_call(lambda: self._save_png(img, os.path.join(outdir, "android-chrome-512x512.png"), chrome512))

        try:
            self._write_manifest(outdir, pref, appn, color)
        except Exception as e:
            errors.append(f"manifest.json: {e}")

    
        snippet = self._make_snippet(pref, color)
        if errors:
            snippet += "\n\n<!-- WARNINGS -->\n" + "\n".join(f"<!-- {e} -->" for e in errors)

        self.output.setPlainTextFast(snippet)
        self.output.setHighlightLanguage("HTML/XML")
        sb = self._sb()
        if sb: sb.showMessage(i18n.t("fav.generate"), 1200)


class SitemapTab(CodePane):
    """
    Генерирует sitemap.xml:
    - Режим 1: из списка URL/путей (левый input)
    - Режим 2: скан папки (html/htm/xhtml) с lastmod из mtime
    - Режим 3: скан сайта по HTTP (обходит ссылки, уважает robots.txt)
    """
    def __init__(self):
        super().__init__("smap.header", show_lang=False)
        from PySide6.QtWidgets import QDoubleSpinBox
        from PySide6.QtCore import QThread, Signal

        self.output.setReadOnly(True)
        self.output.setHighlightLanguage("HTML/XML")
        self.input.setPlaceholderText(i18n.t("smap.placeholder"))

        # --- Контролы общие ---
        self.cmbMode = QComboBox()
        self.cmbMode.addItems([i18n.t("smap.mode.list"),
                               i18n.t("smap.mode.scan"),
                               i18n.t("smap.mode.http")])

        self.edBase = QLineEdit()
        self.edBase.setPlaceholderText("https://example.com")

        # --- Для режима 'папка' ---
        self.edFolder = QLineEdit()
        self.btnFolder = QPushButton(i18n.t("smap.pickdir"))

        # --- SEO опции (общие для всех режимов) ---
        self.cmbFreq = QComboBox()
        self.cmbFreq.addItems(["", "always", "hourly", "daily", "weekly", "monthly", "yearly", "never"])

        self.spPrio = QDoubleSpinBox()
        self.spPrio.setRange(0.0, 1.0); self.spPrio.setSingleStep(0.1)
        self.spPrio.setValue(0.5); self.spPrio.setDecimals(1)

        self.cbLastmodToday = QCheckBox(i18n.t("smap.lastmod.today"))
        self.cbLastmodMtime = QCheckBox(i18n.t("smap.lastmod.mtime"))
        self.cbLastmodToday.setChecked(True)
        self.cbLastmodMtime.setChecked(False)

        # --- Для режима 'HTTP-скан' ---
        self.cbSameHost   = QCheckBox(i18n.t("smap.samehost"));  self.cbSameHost.setChecked(True)
        self.cbKeepQuery  = QCheckBox(i18n.t("smap.keepquery")); self.cbKeepQuery.setChecked(False)
        self.cbRobots     = QCheckBox(i18n.t("smap.robots"));    self.cbRobots.setChecked(True)

        self.spMaxPages = QSpinBox(); self.spMaxPages.setRange(1, 100000); self.spMaxPages.setValue(500)
        self.spMaxDepth = QSpinBox(); self.spMaxDepth.setRange(0, 10);     self.spMaxDepth.setValue(3)
        self.spDelayMs  = QSpinBox(); self.spDelayMs.setRange(0, 5000);    self.spDelayMs.setValue(300)
        self.spTimeout  = QSpinBox(); self.spTimeout.setRange(1, 60);      self.spTimeout.setValue(10)
        self.edUA       = QLineEdit("LinkCodeEdit SitemapBot/1.0")

        self._lblProg = QLabel("")
        self.btnStop  = QPushButton(i18n.t("smap.stop")); self.btnStop.setEnabled(False)

        # --- Кнопки ---
        self.btnGen  = QPushButton(i18n.t("smap.generate"))
        self.btnSave = QPushButton(i18n.t("smap.save"))
        self.btnCopy = QPushButton(i18n.t("smap.copy"))
        self.btnOpen = QPushButton(i18n.t("smap.open"))
        for w in (self.btnFolder, self.btnGen, self.btnSave, self.btnCopy, self.btnOpen, self.btnStop):
            w.setCursor(Qt.PointingHandCursor)

        # --- Размещение ---
        r1 = QHBoxLayout()
        r1.addWidget(QLabel(i18n.t("smap.mode")));  r1.addWidget(self.cmbMode)
        r1.addSpacing(12)
        r1.addWidget(QLabel(i18n.t("smap.base")));  r1.addWidget(self.edBase, 2)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel(i18n.t("smap.folder"))); r2.addWidget(self.edFolder, 2); r2.addWidget(self.btnFolder)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel(i18n.t("smap.freq")));  r3.addWidget(self.cmbFreq)
        r3.addSpacing(12)
        r3.addWidget(QLabel(i18n.t("smap.prio")));  r3.addWidget(self.spPrio)
        r3.addSpacing(12)
        r3.addWidget(QLabel(i18n.t("smap.lastmod"))); r3.addWidget(self.cbLastmodToday); r3.addWidget(self.cbLastmodMtime)
        r3.addStretch(1)

        r4 = QHBoxLayout()  # настройки HTTP-сканера
        r4.addWidget(self.cbSameHost); r4.addWidget(self.cbKeepQuery); r4.addWidget(self.cbRobots)
        r4.addSpacing(12)
        r4.addWidget(QLabel(i18n.t("smap.maxpages"))); r4.addWidget(self.spMaxPages)
        r4.addWidget(QLabel(i18n.t("smap.maxdepth"))); r4.addWidget(self.spMaxDepth)
        r4.addWidget(QLabel(i18n.t("smap.delay")));    r4.addWidget(self.spDelayMs)
        r4.addWidget(QLabel(i18n.t("smap.timeout")));  r4.addWidget(self.spTimeout)
        r4.addStretch(1)

        r5 = QHBoxLayout()
        r5.addWidget(QLabel(i18n.t("smap.ua"))); r5.addWidget(self.edUA)
        r5.addStretch(1)
        r5.addWidget(self._lblProg); r5.addWidget(self.btnStop)

        r6 = QHBoxLayout()
        r6.addWidget(self.btnGen); r6.addWidget(self.btnCopy)
        r6.addStretch(1)
        r6.addWidget(self.btnSave); r6.addWidget(self.btnOpen)

        self.layout().insertLayout(1, r1)
        self.layout().insertLayout(2, r2)
        self.layout().insertLayout(3, r3)
        self.layout().insertLayout(4, r4)
        self.layout().insertLayout(5, r5)
        self.layout().insertLayout(6, r6)

        # Показ/скрытие разных рядов по режиму
        self._update_mode_ui(self.cmbMode.currentIndex())
        self.cmbMode.currentIndexChanged.connect(self._update_mode_ui)

        # Сигналы
        self.btnFolder.clicked.connect(self._pick_dir)
        self.btnGen.clicked.connect(self._do_generate)
        self.btnCopy.clicked.connect(self.act_copy)
        self.btnSave.clicked.connect(self._do_save)
        self.btnOpen.clicked.connect(self._open_dir)
        self.btnStop.clicked.connect(self._stop_scan)

        self._crawler = None  # QThread worker
        i18n.on_change(lambda _: self.retranslate())

    # ---------- UI helpers ----------
    def retranslate(self):
        self.header.setText(i18n.t("smap.header"))
        cur = self.cmbMode.currentIndex()
        self.cmbMode.clear()
        self.cmbMode.addItems([i18n.t("smap.mode.list"),
                               i18n.t("smap.mode.scan"),
                               i18n.t("smap.mode.http")])
        self.cmbMode.setCurrentIndex(max(0, cur))
        self.input.setPlaceholderText(i18n.t("smap.placeholder"))
        self.btnFolder.setText(i18n.t("smap.pickdir"))
        self.btnGen.setText(i18n.t("smap.generate"))
        self.btnSave.setText(i18n.t("smap.save"))
        self.btnCopy.setText(i18n.t("smap.copy"))
        self.btnOpen.setText(i18n.t("smap.open"))
        self.btnStop.setText(i18n.t("smap.stop"))

    def _update_mode_ui(self, idx: int):
        as_list = (idx == 0)
        scan_dir = (idx == 1)
        scan_http = (idx == 2)

        # левый редактор нужен в режиме «список»
        self.input.setVisible(as_list)
        self.splitter.setSizes([900 if as_list else 0, 900])

        self.edFolder.setEnabled(scan_dir)
        self.btnFolder.setEnabled(scan_dir)
        self.cbLastmodMtime.setEnabled(scan_dir)

        # HTTP-настройки
        for w in (self.cbSameHost, self.cbKeepQuery, self.cbRobots,
                  self.spMaxPages, self.spMaxDepth, self.spDelayMs, self.spTimeout,
                  self.edUA, self.btnStop):
            w.setEnabled(scan_http)

        self.cbLastmodToday.setEnabled(as_list or scan_http)  # в http-режиме можно подставлять «сегодня»

    def _pick_dir(self):
        path = QFileDialog.getExistingDirectory(self, i18n.t("smap.pickdir"), "")
        if path:
            self.edFolder.setText(path)

    def _open_dir(self):
        d = (self.edFolder.text() or "").strip()
        if d and os.path.isdir(d):
            QDesktopServices.openUrl(QUrl.fromLocalFile(d))

    # ---------- Core helpers ----------
    def _norm_join(self, base: str, raw: str) -> Optional[str]:
        import urllib.parse
        raw = (raw or "").strip()
        if not raw or raw.startswith("#"):
            return None
        u = urllib.parse.urljoin(base, raw)
        parts = list(urllib.parse.urlsplit(u))
        parts[4] = ""  # fragment
        # нормализуем путь/квери
        parts[2] = urllib.parse.quote(parts[2], safe="/%._-~")
        parts[3] = "&".join(
            f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
            for k, v in urllib.parse.parse_qsl(parts[3], keep_blank_values=True)
        )
        return urllib.parse.urlunsplit(parts)

    def _collect_from_list(self, base: str) -> list[str]:
        lines = self.input.toPlainText().splitlines()
        out, seen = [], set()
        for ln in lines:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            if ln.startswith(("http://", "https://")):
                u = self._norm_join("", ln)
            else:
                u = self._norm_join(base, ln)
            if u and u not in seen:
                seen.add(u); out.append(u)
        return out

    def _collect_from_folder(self, base: str, folder: str) -> list[tuple[str, Optional[str]]]:
        import datetime
        urls = []
        exts = {".html", ".htm", ".xhtml"}
        root = os.path.abspath(folder)
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in exts: continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace("\\", "/")
                if fn.lower() in ("index.html", "index.htm", "index.xhtml"):
                    rel_url = "/" + os.path.dirname(rel).strip("/").replace("\\", "/") + "/"
                    rel_url = rel_url.replace("//", "/")
                else:
                    rel_url = "/" + rel
                u = self._norm_join(base, rel_url)
                lm = None
                if self.cbLastmodMtime.isChecked():
                    try:
                        d = datetime.date.fromtimestamp(os.path.getmtime(full))
                        lm = d.isoformat()
                    except Exception:
                        pass
                if u:
                    urls.append((u, lm))
        urls.sort(key=lambda t: (t[0].count("/"), t[0]))
        seen = set(); uniq=[]
        for u,lm in urls:
            if u in seen: continue
            seen.add(u); uniq.append((u,lm))
        return uniq

    def _build_xml(self, items: list[tuple[str, Optional[str]]], changefreq: str, priority: Optional[float]) -> str:
        def esc(s: str) -> str:
            return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]
        for (loc, lastmod) in items:
            lines.append("  <url>")
            lines.append(f"    <loc>{esc(loc)}</loc>")
            if lastmod:    lines.append(f"    <lastmod>{lastmod}</lastmod>")
            if changefreq: lines.append(f"    <changefreq>{changefreq}</changefreq>")
            if priority is not None:
                lines.append(f"    <priority>{priority:.1f}</priority>")
            lines.append("  </url>")
        lines.append("</urlset>")
        return "\n".join(lines)

    # ---------- HTTP crawler ----------
    def _stop_scan(self):
        if self._crawler and getattr(self._crawler, "stop", None):
            self._crawler.stop()

    def _do_generate(self):
        import datetime
        base = (self.edBase.text() or "").strip()
        if not base:
            QMessageBox.information(self, "Info", i18n.t("smap.base_empty"))
            return

        mode = self.cmbMode.currentIndex()
        freq = (self.cmbFreq.currentText() or "").strip()
        prio = self.spPrio.value()
        priority = prio if prio >= 0.0 else None

        if mode == 0:
            urls = self._collect_from_list(base)
            today = datetime.date.today().isoformat() if self.cbLastmodToday.isChecked() else None
            items = [(u, today) for u in urls]
            txt = self._build_xml(items, freq, priority)
            if len(items) > 50000:
                txt += f"\n<!-- {i18n.t('smap.too_many')} -->"
            self.output.setPlainTextFast(txt)
            self.output.setHighlightLanguage("HTML/XML")
            sb = self._sb();  sb and sb.showMessage(i18n.t("smap.done"), 1200)
            return

        if mode == 1:
            folder = (self.edFolder.text() or "").strip()
            if not folder or not os.path.isdir(folder):
                QMessageBox.information(self, "Info", i18n.t("smap.scan_warn"))
                return
            items = self._collect_from_folder(base, folder)
            txt = self._build_xml(items, freq, priority)
            if len(items) > 50000:
                txt += f"\n<!-- {i18n.t('smap.too_many')} -->"
            self.output.setPlainTextFast(txt)
            self.output.setHighlightLanguage("HTML/XML")
            sb = self._sb();  sb and sb.showMessage(i18n.t("smap.done"), 1200)
            return

        # --- режим HTTP-сканера в отдельном потоке ---
        self._lblProg.setText(i18n.t("smap.progress").format(done=0, limit=self.spMaxPages.value()))
        self.btnGen.setEnabled(False); self.btnStop.setEnabled(True)

        # Внутренний воркер
        _HTMLParser = HTMLParser
        class _HttpCrawler(QThread):
            progress = Signal(int)
            finished = Signal(list)
            def __init__(self, start_url: str, *,
                         max_pages: int, max_depth: int, delay_ms: int,
                         same_host: bool, keep_query: bool, respect_robots: bool,
                         timeout: int, ua: str, lastmod_today_fallback: bool):
                super().__init__()
                self.start_url = start_url
                self.max_pages = max_pages
                self.max_depth = max_depth
                self.delay_ms  = delay_ms
                self.same_host = same_host
                self.keep_query= keep_query
                self.respect_robots = respect_robots
                self.timeout = timeout
                self.ua = ua
                self.lastmod_today_fallback = lastmod_today_fallback
                self._stop = False
            def stop(self): self._stop = True

            # ---- helpers ----
            def _host(self, url):
                import urllib.parse
                return urllib.parse.urlsplit(url).netloc.lower()

            def _normalize(self, url, keep_query):
                import urllib.parse
                try:
                    p = list(urllib.parse.urlsplit(url))
                    if p[0] not in ("http","https"): return None
                    p[4] = ""  # fragment
                    if not keep_query:
                        p[3] = ""
                    p[2] = urllib.parse.quote(p[2], safe="/%._-~")
                    return urllib.parse.urlunsplit(p)
                except Exception:
                    return None

            class _LinkParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.hrefs = []
                    self.base  = None
                    self.canon = None
                def handle_starttag(self, tag, attrs):
                    d = dict(attrs)
                    if tag == "a" and "href" in d:
                        self.hrefs.append(d.get("href"))
                    elif tag == "base" and "href" in d and not self.base:
                        self.base = d.get("href")
                    elif tag == "link" and d.get("rel","").lower() == "canonical" and "href" in d:
                        self.canon = d.get("href")

            def _extract_links(self, html_bytes, page_url):
                import urllib.parse
                try:
                    text = html_bytes.decode("utf-8", errors="ignore")
                except Exception:
                    text = str(html_bytes, "latin1", errors="ignore")
                p = self._LinkParser(); p.feed(text)
                base_for_join = p.base or page_url
                out = []
                for raw in (p.canon, *(p.hrefs or [])):
                    if not raw: continue
                    if raw.startswith(("javascript:", "mailto:", "tel:", "data:")):
                        continue
                    absu = urllib.parse.urljoin(base_for_join, raw)
                    out.append(absu)
                return out

            def _can_fetch(self, rp, url):
                if rp is None: return True
                try:
                    return rp.can_fetch(self.ua, url)
                except Exception:
                    return True

            def run(self):
                import time, urllib.request, urllib.parse, urllib.robotparser, email.utils, datetime
                start = self._normalize(self.start_url, keep_query=True)
                if not start:
                    self.finished.emit([]); return
                start_host = self._host(start)
                rp = None
                if self.respect_robots:
                    try:
                        base = urllib.parse.urlsplit(start)
                        robots_url = f"{base.scheme}://{base.netloc}/robots.txt"
                        rp = urllib.robotparser.RobotFileParser()
                        rp.set_url(robots_url); rp.read()
                    except Exception:
                        rp = None

                headers = {
                    "User-Agent": self.ua or "Mozilla/5.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en,ru;q=0.9",
                }
                opener = urllib.request.build_opener()
                opener.addheaders = list(headers.items())

                from collections import deque
                queue = deque([(start, 0)])
                seen  = set([start])
                results = []

                while queue and len(results) < self.max_pages and not self._stop:
                    url, depth = queue.popleft()
                    if self.respect_robots and not self._can_fetch(rp, url):
                        continue
                    try:
                        with opener.open(url, timeout=self.timeout) as resp:
                            ct = (resp.headers.get_content_type() or "").lower()
                            lm_hdr = resp.headers.get("Last-Modified")
                            lastmod = None
                            if lm_hdr:
                                try:
                                    dt = email.utils.parsedate_to_datetime(lm_hdr)
                                    lastmod = dt.date().isoformat()
                                except Exception:
                                    lastmod = None
                            data = resp.read() if "html" in ct else b""
                    except Exception:
                        # не удалось открыть — пропустим
                        continue

                    # lastmod fallback «сегодня»
                    if not lastmod and self.lastmod_today_fallback:
                        lastmod = datetime.date.today().isoformat()

                    results.append((url, lastmod))
                    self.progress.emit(len(results))

                    # ссылки только с HTML-страниц и если глубина позволяет
                    if data and depth < self.max_depth:
                        links = self._extract_links(data, url)
                        for lk in links:
                            nlk = self._normalize(lk, keep_query=self.keep_query)
                            if not nlk: continue
                            if self.same_host and self._host(nlk) != start_host:
                                continue
                            if nlk in seen: continue
                            seen.add(nlk)
                            if len(seen) > self.max_pages * 3:  # защита от взрыва очереди
                                continue
                            queue.append((nlk, depth + 1))

                    if self.delay_ms > 0:
                        time.sleep(self.delay_ms / 1000.0)

                self.finished.emit(results)

        # Запуск воркера
        self._crawler = _HttpCrawler(
            base,
            max_pages=self.spMaxPages.value(),
            max_depth=self.spMaxDepth.value(),
            delay_ms=self.spDelayMs.value(),
            same_host=self.cbSameHost.isChecked(),
            keep_query=self.cbKeepQuery.isChecked(),
            respect_robots=self.cbRobots.isChecked(),
            timeout=self.spTimeout.value(),
            ua=self.edUA.text().strip(),
            lastmod_today_fallback=self.cbLastmodToday.isChecked()
        )

        def on_progress(n):
            self._lblProg.setText(i18n.t("smap.progress").format(done=n, limit=self.spMaxPages.value()))

        def on_finished(items):
            self.btnGen.setEnabled(True); self.btnStop.setEnabled(False)
            self._lblProg.setText(i18n.t("smap.progress").format(done=len(items), limit=self.spMaxPages.value()))
            txt = self._build_xml(items, freq, priority)
            if len(items) > 50000:
                txt += f"\n<!-- {i18n.t('smap.too_many')} -->"
            self.output.setPlainTextFast(txt)
            self.output.setHighlightLanguage("HTML/XML")
            sb = self._sb();  sb and sb.showMessage(i18n.t("smap.done"), 1200)
            self._crawler = None

        self._crawler.progress.connect(on_progress)
        self._crawler.finished.connect(on_finished)
        self._crawler.start()

    def _do_save(self):
        path, _ = QFileDialog.getSaveFileName(self, i18n.t("smap.save"), "sitemap.xml", "XML (*.xml);;All files (*.*)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output.toPlainText())
            sb = self._sb(); sb and sb.showMessage(i18n.t("smap.save"), 1000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot save:\n{e}")





class RobotsTxtTab(CodePane):
    """
    🤖 robots.txt — генератор по шаблонам.
    Управление:
      • Пресет (Basic / Block all / WordPress / 1C-Bitrix)
      • Host, Sitemap (можно несколько через пробел или запятую)
      • Crawl-delay (0 — не выводить)
      • Clean-param (Яндекс), например: utm_source&utm_medium&utm_campaign&utm_term&utm_content
      • Доп. правила (строки Disallow:/Allow:/User-agent:)
    """
    def __init__(self):
        super().__init__("robots.header", show_lang=False, show_io_stats=False)

      
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.output.setReadOnly(True)
        self.output.setHighlightLanguage("Plain")

    
        self.cmbPreset = QComboBox()
        self.cmbPreset.addItems([
            i18n.t("robots.presets.basic"),
            i18n.t("robots.presets.blockall"),
            i18n.t("robots.presets.wordpress"),
            i18n.t("robots.presets.bitrix"),
        ])

        self.edHost = QLineEdit();     self.edHost.setPlaceholderText("example.com")
        self.edMap  = QLineEdit();     self.edMap.setPlaceholderText("https://example.com/sitemap.xml")
        self.spDelay= QSpinBox();      self.spDelay.setRange(0, 60); self.spDelay.setValue(0)
        self.edClean= QLineEdit();     self.edClean.setPlaceholderText("utm_source&utm_medium&utm_campaign&utm_term&utm_content")
        self.edExtra= QPlainTextEdit(); self.edExtra.setPlaceholderText("User-agent: Googlebot-Image\nDisallow: /private/\nAllow: /wp-content/uploads/\n...")

        self.btnGen  = QPushButton(i18n.t("robots.generate"))
        self.btnCopy = QPushButton(i18n.t("robots.copy"))
        for w in (self.btnGen, self.btnCopy, self.cmbPreset):
            w.setCursor(Qt.PointingHandCursor)

     
        r1 = QHBoxLayout()
        r1.addWidget(QLabel(i18n.t("robots.preset")));  r1.addWidget(self.cmbPreset, 1)
        r1.addStretch(1)
        r1.addWidget(self.btnGen); r1.addWidget(self.btnCopy)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel(i18n.t("robots.host")));      r2.addWidget(self.edHost, 1)
        r2.addWidget(QLabel(i18n.t("robots.sitemap")));   r2.addWidget(self.edMap, 2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel(i18n.t("robots.crawl")));     r3.addWidget(self.spDelay)
        r3.addSpacing(12)
        r3.addWidget(QLabel(i18n.t("robots.cleanparam"))); r3.addWidget(self.edClean, 1)

        r4 = QVBoxLayout()
        r4.addWidget(QLabel(i18n.t("robots.extra")))
        r4.addWidget(self.edExtra)

        self.layout().insertLayout(1, r1)
        self.layout().insertLayout(2, r2)
        self.layout().insertLayout(3, r3)
        self.layout().insertLayout(4, r4)


        self.btnGen.clicked.connect(self.run_action)
        self.btnCopy.clicked.connect(self.act_copy)

        i18n.on_change(lambda _: self.retranslate())

    def retranslate(self):
        self.header.setText(i18n.t("robots.header"))
        cur = self.cmbPreset.currentIndex()
        self.cmbPreset.clear()
        self.cmbPreset.addItems([
            i18n.t("robots.presets.basic"),
            i18n.t("robots.presets.blockall"),
            i18n.t("robots.presets.wordpress"),
            i18n.t("robots.presets.bitrix"),
        ])
        self.cmbPreset.setCurrentIndex(max(0, cur))
        self.btnGen.setText(i18n.t("robots.generate"))
        self.btnCopy.setText(i18n.t("robots.copy"))


    def _preset_rules(self, preset_idx: int) -> tuple[list[str], list[str]]:
        """
        Возвращает (allows, disallows) для User-agent: *
        """
        if preset_idx == 1: 
            return ([], ["/"])
        if preset_idx == 2:  
            allows = ["/wp-admin/admin-ajax.php", "/wp-content/uploads/"]
            disallows = [
                "/wp-admin/",
                "/wp-includes/",
                "/xmlrpc.php",
                "/wp-login.php",
                "/wp-register.php",
                "/*?s=*",
                "/*?replytocom=*",
                "/?*",
            ]
            return (allows, disallows)
        if preset_idx == 3: 
            allows = ["/upload/", "/local/templates/", "/local/components/"]
            disallows = [
                "/bitrix/",
                "/auth/",
                "/search/",
                "/upload/resize_cache/",
                "/*?print=1",
                "/*?utm_*",
                "/*?PAGEN_*",
                "/*?sort=*",
                "/*?view=*",
                "/*?login=yes",
                "/*?logout=*",
            ]
            return (allows, disallows)
     
        return ([], [""])  

    
    def run_action(self):
        preset = self.cmbPreset.currentIndex()
        allows, disallows = self._preset_rules(preset)

        host = (self.edHost.text() or "").strip()
        smap_raw = (self.edMap.text() or "").strip().replace(",", " ")
        maps = [u for u in smap_raw.split() if u]

        delay = int(self.spDelay.value() or 0)
        clean = (self.edClean.text() or "").strip()

        extra = self.edExtra.toPlainText().replace("\r\n", "\n").strip("\n")

        lines = []
        lines.append("# robots.txt generated by LinkCodeEdit")
        lines.append("# " + i18n.t("robots.note"))

        
        lines.append("\nUser-agent: *")
        if allows:
            for p in allows:
                lines.append(f"Allow: {p}")
        if disallows:
            for p in disallows:
               
                if p == "":
                    lines.append("Disallow:")
                else:
                    lines.append(f"Disallow: {p}")
        if delay > 0:
            lines.append(f"Crawl-delay: {delay}")
        if clean:
            lines.append(f"Clean-param: {clean}")

      
        if host:
            lines.append(f"Host: {host}")
        for u in maps:
            lines.append(f"Sitemap: {u}")

       
        if extra:
            lines.append("")  
            lines.append(extra)

        txt = "\n".join(lines).strip() + "\n"
        self.output.setPlainTextFast(txt)
        self.output.setHighlightLanguage("Plain")
        sb = self._sb(); sb and sb.showMessage(i18n.t("robots.generate"), 1200)






class SlugTab(CodePane):
    def __init__(self):
        super().__init__("slug.header", show_lang=False)
        self.cbLower = QCheckBox(i18n.t("slug.lower"))
        self.cbTrans = QCheckBox(i18n.t("slug.translit"))
        self.cbTrans.setChecked(True)
        self.edSep = QLineEdit("-"); self.edSep.setMaxLength(1); self.edSep.setFixedWidth(28)
        self.spMax = QSpinBox(); self.spMax.setRange(1, 400); self.spMax.setValue(80)
        self.btnMake = QPushButton(i18n.t("slug.make"))
        for w in (self.cbLower, self.cbTrans, self.btnMake):
            w.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout()
        row.addWidget(self.cbLower)
        row.addWidget(self.cbTrans)
        self._lblSep = QLabel(i18n.t("slug.sep"))
        self._lblMax = QLabel(i18n.t("slug.max"))
        row.addWidget(self._lblSep); row.addWidget(self.edSep)
        row.addWidget(self._lblMax); row.addWidget(self.spMax)
        row.addStretch(1); row.addWidget(self.btnMake)
        self.layout().insertLayout(1, row)
        self.btnMake.clicked.connect(self.run_action)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        self.cbLower.setText(i18n.t("slug.lower"))
        self.cbTrans.setText(i18n.t("slug.translit"))
        self.btnMake.setText(i18n.t("slug.make"))
        self._lblSep.setText(i18n.t("slug.sep"))
        self._lblMax.setText(i18n.t("slug.max"))
    _RU = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l',
        'м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'c','ч':'ch','ш':'sh',
        'щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
    }
    def _slugify(self, text: str, sep: str, lower: bool, translit: bool, maxlen: int) -> str:
        s = text.strip()
        if translit:
            tmp = []
            for ch in s:
                lo = ch.lower()
                if lo in self._RU:
                    rep = self._RU[lo]
                    tmp.append(rep.upper() if ch.isupper() else rep)
                else:
                    tmp.append(ch)
            s = ''.join(tmp)
        s = unicodedata.normalize("NFKD", s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
        out = []
        prev_sep = False
        for ch in s:
            if ch.isalnum():
                out.append(ch)
                prev_sep = False
            else:
                if not prev_sep:
                    out.append(sep)
                    prev_sep = True
        res = ''.join(out).strip(sep)
        if lower:
            res = res.lower()
        if len(res) > maxlen:
            res = res[:maxlen].rstrip(sep)
        return res
    def run_action(self):
        sep = (self.edSep.text() or "-")[0]
        txt = self.input.toPlainText()
        lower = self.cbLower.isChecked()
        translit = self.cbTrans.isChecked()
        maxlen = self.spMax.value()

        lines_out = []
        for ln in txt.splitlines():
            if not ln.strip():
                continue 
            slug = self._slugify(ln, sep, lower, translit, maxlen)
            lines_out.append(slug)

        res = "\n".join(lines_out)
        self.output.setPlainTextFast(res)
        self.output.setHighlightLanguage("Прочее")
        self.window().statusBar().showMessage(i18n.t("slug.make"), 1000)

class StatsTab(CodePane):
    def __init__(self):
        super().__init__("stats.header")
        self.lang.hide()
        for lbl in self.findChildren(QLabel):
            t = (lbl.text() or "").strip().lower()
            if t.startswith("lang") or "язык" in t:
                lbl.hide()
        self.btnCopy = QPushButton(i18n.t("act.copy"))
        self.btnCopy.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btnCopy)
        self.layout().insertLayout(1, row)        
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setWordWrapMode(QTextOption.NoWrap)

        self.input.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

   
        self.report.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.report.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        f = QFont("Consolas, Menlo, Monaco, Courier New", 11)
        f.setStyleHint(QFont.Monospace)
        self.report.setFont(f)
        self.output.hide()                  
        self.splitter.insertWidget(1, self.report)  
        self.splitter.setSizes([2, 1])           
        self._count_timer = QTimer(self)
        self._count_timer.setSingleShot(True)
        self._count_timer.timeout.connect(self._do_count)
        self.input.textChanged.connect(lambda: self._count_timer.start(100))
        self.report.textChanged.connect(lambda: self._stats_timer.start(80))
        self.btnCopy.clicked.connect(self._copy_report)
        i18n.on_change(lambda _: self.retranslate())
        QTimer.singleShot(0, self._do_count)
    def _copy_report(self):
        self.window().clipboard().setText(self.report.toPlainText())
        self.window().statusBar().showMessage(i18n.t("status.copied"), 1200)
    def retranslate(self):
        super().retranslate()
        self.btnCopy.setText(i18n.t("act.copy"))
        QTimer.singleShot(0, self._do_count)
    def _update_stats_now(self):
        a = len(self.input.toPlainText())
        b = len(self.report.toPlainText())
        delta = a - b
        sign = "-" if delta >= 0 else "+"
        self.stats.setText(f"In: {a} | Out: {b} | Diff: {sign}{abs(delta)}")
    def _do_count(self):
        s = self.input.toPlainText()
        total = len(s)
        spaces = s.count(' ')
        tabs = s.count('\t')
        newlines = s.count('\n')
        digits = sum(ch.isdigit() for ch in s)
        letters = sum(ch.isalpha() for ch in s)
        alnum = sum(ch.isalnum() for ch in s)
        punct_chars = r"""!@#$%^&*()_+-={}[]|\:;"'<>,.?/~`"""
        punct = sum(ch in punct_chars for ch in s)
        no_spaces = total - spaces - tabs - newlines
        words = len([w for w in re.findall(r"\w+", s, flags=re.UNICODE) if w])
        lines = s.count('\n') + (1 if s and not s.endswith('\n') else 0)
        uniq = len(set(s))
        report_lines = [
            f"{i18n.t('stats.total')}: {total}",
            f"{i18n.t('stats.no_spaces')}: {no_spaces}",
            f"{i18n.t('stats.spaces')}: {spaces}",
            f"{i18n.t('stats.tabs')}: {tabs}",
            f"{i18n.t('stats.newlines')}: {newlines}",
            f"{i18n.t('stats.words')}: {words}",
            f"{i18n.t('stats.lines')}: {lines}",
            f"{i18n.t('stats.letters')}: {letters}",
            f"{i18n.t('stats.digits')}: {digits}",
            f"{i18n.t('stats.punct')}: {punct}",
            f"{i18n.t('stats.unique')}: {uniq}",
        ]
        self.report.setPlainText("\n".join(report_lines))
        self._update_stats_now()
        sb = self._sb()
        if sb: sb.showMessage(i18n.t("stats.done"), 600)
class PasswordTab(CodePane):
    def __init__(self):
        super().__init__("pass.header", show_lang=False)
        self.spLen = QSpinBox(); self.spLen.setRange(4, 256); self.spLen.setValue(16)
        self.spCount = QSpinBox(); self.spCount.setRange(1, 100); self.spCount.setValue(10)
        self.cbLower = QCheckBox(i18n.t("pass.lower")); self.cbLower.setChecked(True)
        self.cbUpper = QCheckBox(i18n.t("pass.upper")); self.cbUpper.setChecked(True)
        self.cbDigits= QCheckBox(i18n.t("pass.digits")); self.cbDigits.setChecked(True)
        self.cbSymb  = QCheckBox(i18n.t("pass.symbols")); self.cbSymb.setChecked(True)
        self.cbNoAmb = QCheckBox(i18n.t("pass.no_amb"));  self.cbNoAmb.setChecked(True)
        self.btnGen = QPushButton(i18n.t("pass.gen"))
        for w in (self.btnGen,):
            w.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout()
        self._lblLen   = QLabel(i18n.t("pass.length"))
        self._lblCount = QLabel(i18n.t("pass.count"))
        row.addWidget(self._lblLen);   row.addWidget(self.spLen)
        row.addWidget(self._lblCount); row.addWidget(self.spCount)
        row.addWidget(self.cbLower); row.addWidget(self.cbUpper); row.addWidget(self.cbDigits); row.addWidget(self.cbSymb); row.addWidget(self.cbNoAmb)
        row.addStretch(1); row.addWidget(self.btnGen)
        self.layout().insertLayout(1, row)
        self.input.hide()
        self.splitter.setSizes([0, 1])
        self.btnGen.clicked.connect(self.run_action)
        i18n.on_change(lambda _: self.retranslate())
    def retranslate(self):
        super().retranslate()
        self.cbLower.setText(i18n.t("pass.lower"))
        self.cbUpper.setText(i18n.t("pass.upper"))
        self.cbDigits.setText(i18n.t("pass.digits"))
        self.cbSymb.setText(i18n.t("pass.symbols"))
        self.cbNoAmb.setText(i18n.t("pass.no_amb"))
        self.btnGen.setText(i18n.t("pass.gen"))
        self._lblLen.setText(i18n.t("pass.length"))
        self._lblCount.setText(i18n.t("pass.count"))
    def _alphabet(self) -> str:
        amb = set("O0oIl1|`'\"{}[]()/\\;:,._-")
        chars = ""
        if self.cbLower.isChecked(): chars += string.ascii_lowercase
        if self.cbUpper.isChecked(): chars += string.ascii_uppercase
        if self.cbDigits.isChecked():chars += string.digits
        if self.cbSymb.isChecked():  chars += "!@#$%^&*+=?~"
        if not chars:
            chars = string.ascii_letters + string.digits
        if self.cbNoAmb.isChecked():
            chars = ''.join(ch for ch in chars if ch not in amb)
        return chars
    def _ensure_policy(self, pwd: list[str]) -> list[str]:
        pools = []
        if self.cbLower.isChecked(): pools.append(string.ascii_lowercase)
        if self.cbUpper.isChecked(): pools.append(string.ascii_uppercase)
        if self.cbDigits.isChecked():pools.append(string.digits)
        if self.cbSymb.isChecked():  pools.append("!@#$%^&*+=?~")
        if not pools:
            return pwd
        for pool in pools:
            idx = secrets.randbelow(len(pwd))
            pwd[idx] = secrets.choice(pool)
        return pwd
    def run_action(self):
        n = self.spCount.value()
        L = self.spLen.value()
        alphabet = self._alphabet()
        lines = []
        for _ in range(n):
            pwd = [secrets.choice(alphabet) for __ in range(L)]
            pwd = self._ensure_policy(pwd)
            lines.append(''.join(pwd))
        out = "\n".join(lines)
        self.output.setPlainTextFast(out)
        self.output.setHighlightLanguage("Прочее")
        self.window().statusBar().showMessage(i18n.t("pass.gen"), 1000)
def _build_tabs_with_extras(self: "MainWindow"):
    self.tabs = QTabWidget()  
    self.tabFmt    = FormattingTab()
    self.tabClean  = CommentsAllTab()
    self.tabOG     = OgTab()
    self.tabFav = FaviconTab()                         
    self.tabs.addTab(self.tabFav, i18n.t("tab.favicon")) 
    self.tabSmap = SitemapTab()
    self.tabs.addTab(self.tabSmap, i18n.t("tab.sitemap"))
    self.tabRobots = RobotsTxtTab()
    self.tabs.addTab(self.tabRobots,i18n.t("tab.robots"))

    self.tabUtm    = UtmTab()
    self.tabSlug   = SlugTab()
    self.tabLink   = JsLinkTab()
    self.tabFavicon = FaviconTab()
    self.tabObf    = ObfuscateTab()
    self.tabStats  = StatsTab()
    self.tabPass   = PasswordTab()   
    self._tab_map = {
        "format": (self.tabFmt,  "tab.format"),
        "clean":  (self.tabClean,"tab.clean"),
        "og":     (self.tabOG,   "tab.og"),
        "utm":    (self.tabUtm,  "tab.utm"),
        "slug":   (self.tabSlug, "tab.slug"),
        "link":   (self.tabLink, "tab.link"),
        "obf":    (self.tabObf,  "tab.obf"),
        "stats":  (self.tabStats,"tab.stats"),
        "pass":   (self.tabPass, "tab.pass"),
        "favicon":(self.tabFav,  "tab.favicon"), 
        "sitemap": (self.tabSmap, "tab.sitemap"),
        "robots":  (self.tabRobots,"tab.robots"),
    }
    settings = QSettings(APP_ORG, APP_NAME)
    default_ids = list(self._tab_map.keys())
    saved_ids = settings.value("ui/tab_order", default_ids)   
    if isinstance(saved_ids, str):
        try:
            import json as _json
            saved_ids = _json.loads(saved_ids)
        except Exception:
            saved_ids = default_ids
    if not isinstance(saved_ids, (list, tuple)):
        saved_ids = default_ids  
    add_order = [tid for tid in saved_ids if tid in self._tab_map]
    add_order += [tid for tid in default_ids if tid not in add_order]    
    for tid in add_order:
        w, key = self._tab_map[tid]
        if tid == "og":
            og_icon = _find_first_icon(OG_ICON_CANDIDATES)
            if og_icon:
                self.tabs.addTab(w, QIcon(str(og_icon)), i18n.t(key))
            else:
                self.tabs.addTab(w, i18n.t(key))
        else:
            self.tabs.addTab(w, i18n.t(key))
    self.tabs.setMovable(True)
    self.tabs.tabBar().tabMoved.connect(lambda _f, _t: self._tab_save_timer.start(200))
    self.setCentralWidget(self.tabs)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        if APP_ICON_PATH:
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))       
        try:
            if APP_ICON_PATH:
                self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        except Exception as e:
            print("setWindowIcon failed:", e)       
        self._tab_save_timer = QTimer(self)
        self._tab_save_timer.setSingleShot(True)
        self._tab_save_timer.timeout.connect(self._save_tab_order)
        self.setMinimumSize(QSize(1080, 680))
        self._clipboard = QApplication.clipboard()
        self._build_tabs()
        self._tab_save_timer = QTimer(self)
        self._tab_save_timer.setSingleShot(True)
        self._tab_save_timer.timeout.connect(self._save_tab_order)
        self._build_menubar()
        self.setStatusBar(QStatusBar())
        self.setStyleSheet(self._style_qss())
        self._retranslate()
        i18n.on_change(lambda _: self._retranslate())
    def clipboard(self):
        return self._clipboard
    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabClean  = CommentsAllTab()
        self.tabFmt    = FormattingTab()
        self.tabLink   = JsLinkTab()
        self.tabObf    = ObfuscateTab()
        self.tabFav    = FaviconTab()
        self.tabs.addTab(self.tabClean,  i18n.t("tab.clean"))
        self.tabs.addTab(self.tabFmt,    i18n.t("tab.format"))
        self.tabs.addTab(self.tabLink,   i18n.t("tab.link"))
        self.tabs.addTab(self.tabObf,    i18n.t("tab.obf"))
        self.tabs.addTab(self.tabFav,    i18n.t("tab.favicon"))
        self.tabs.addTab(self.tabFavicon, i18n.t("tab.favicon"))
        self.setCentralWidget(self.tabs)
    def _build_menubar(self):
        m = self.menuBar()
        fileMenu = m.addMenu(i18n.t("menu.file"))
        actOpen = QAction(i18n.t("act.open"), self)
        actSave = QAction(i18n.t("act.save"), self)
        actExit = QAction(i18n.t("act.exit"), self)
        actOpen.triggered.connect(lambda: self._call_active("act_open"))
        actSave.triggered.connect(lambda: self._call_active("act_save"))
        actExit.triggered.connect(self.close)
        fileMenu.addActions([actOpen, actSave]); fileMenu.addSeparator(); fileMenu.addAction(actExit)
        editMenu = m.addMenu(i18n.t("menu.edit"))
        for key, name in [("act.copy","act_copy"), ("act.paste","act_paste"), ("act.swap","act_swap"), ("act.clear","act_clear")]:
            act = QAction(i18n.t(key), self)
            act.triggered.connect(lambda checked=False, n=name: self._call_active(n))
            editMenu.addAction(act)
        langMenu = m.addMenu(i18n.t("menu.lang"))
        self._lang_actions = {
            "ru": QAction("Русский", self, checkable=True),
            "en": QAction("English", self, checkable=True),
        }
        settings = QSettings(APP_ORG, APP_NAME)
        current = settings.value("ui/lang", "ru")
        for code, act in self._lang_actions.items():
            act.setChecked(code == current)
            act.triggered.connect(lambda checked=False, c=code: self._set_lang(c))
            langMenu.addAction(act)
        helpMenu = m.addMenu(i18n.t("menu.help"))
        actInstr  = QAction(i18n.t("act.help.instructions"), self)
        actLic    = QAction(i18n.t("act.license"), self)
        actAbout  = QAction(i18n.t("act.about"), self)
        actDonate = QAction(i18n.t("act.donate"), self)  
        actInstr.triggered.connect(self._show_instructions)
        actLic.triggered.connect(self._show_license)
        actAbout.triggered.connect(self._about)
        actDonate.triggered.connect(self._donate)
        helpMenu.addActions([actInstr, actLic, actAbout, actDonate])
    def _call_active(self, name: str):
        w = self.tabs.currentWidget()
        if hasattr(w, name):
            getattr(w, name)()
    def _set_lang(self, code: str):
        for c, act in self._lang_actions.items():
            act.setChecked(c == code)
        i18n.load(code)
        settings = QSettings(APP_ORG, APP_NAME)
        settings.setValue("ui/lang", code)
        self._retranslate()
    def _retranslate(self):
        self.setWindowTitle(i18n.t("app.title"))
        m = self.menuBar()
        m.clear()
        self._build_menubar()
        if hasattr(self, "_tab_map"):
            for tid, (w, key) in self._tab_map.items():
                idx = self.tabs.indexOf(w)
                if idx != -1:
                    self.tabs.setTabText(idx, i18n.t(key))
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "retranslate"):
                w.retranslate()
    def _about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.t("act.about"))
        lay = QVBoxLayout(dlg)
        html = """
        <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; font-size:14px; line-height:1.6;">
        <h2 style="margin:0 0 6px;">LinkCodeEdit v.1.0.0</h2>
        <div style="color:#666; margin-bottom:10px;">Лицензия MIT</div>

        <div><b>Автор:</b> Савин Евгений Олегович</div>
        <div><b>Сайт автора:</b> <a href="https://www.linkfirst.ru">www.linkfirst.ru</a></div>
        <div><b>E-mail автора:</b> <a href="mailto:b2b@linkfirst.ru">b2b@linkfirst.ru</a></div>
        <br>
        <div><b>Сайт программы:</b> <a href="https://linkcodeedit.com">linkcodeedit.com</a></div>

        <hr style="border:none; border-top:1px solid #e5e5ee; margin:12px 0;">
        <div>
            <b>Поддержать проект ❤️</b><br><br>
            — <a href="https://yoomoney.ru/to/410011663886937">YooMoney</a><br>
            — <a href="https://boosty.to/linkfirst">Boosty</a><br>
        </div>
        </div>
        """
        lbl = QLabel(html, dlg)
        lbl.setOpenExternalLinks(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setWordWrap(True)
        lay.addWidget(lbl)
        btns = QDialogButtonBox(QDialogButtonBox.Ok, dlg)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns, alignment=Qt.AlignRight)
        dlg.resize(520, 280)
        dlg.exec()            
    def _show_instructions(self):
        lang = i18n.lang()
        path = ASSETS_DIR / f"instructions_{lang}.txt"
        if not path.exists():
            path = ASSETS_DIR / "instructions_en.txt"
        try:
            txt = path.read_text(encoding="utf-8")
        except Exception as e:
            txt = f"Cannot load instructions:\n{e}"
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, i18n.t("act.help.instructions"), txt)
    def _donate(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.t("act.donate"))  
        lay = QVBoxLayout(dlg)
        lbl = QLabel(
            f"<div style='font-size:14px;'>"
            f"<b>{i18n.t('about.support')}</b><br>"
            f"<a href='https://yoomoney.ru/to/410011663886937'>YooMoney</a>"
            f"</div>"
        )
        lbl.setOpenExternalLinks(True)
        lay.addWidget(lbl)
        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(dlg.reject)  
        lay.addWidget(btns, alignment=Qt.AlignRight)
        dlg.resize(420, 160)
        dlg.exec()    
    def _show_instructions(self):
        html = self._load_instructions_html()
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.t("act.help.instructions"))
        lay = QVBoxLayout(dlg)
        view = QTextBrowser()
        view.setOpenExternalLinks(True)
        view.setHtml(html)
        lay.addWidget(view)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns, alignment=Qt.AlignRight)
        dlg.resize(860, 640)
        dlg.exec()
    def _load_instructions_html(self) -> str:
        lang = i18n.lang()
        candidates = [
            ASSETS_DIR / f"instructions_{lang}.html",
            ASSETS_DIR / "instructions_en.html",
        ]
        for p in candidates:
            if p.exists():
                try:
                    return p.read_text(encoding="utf-8")
                except Exception:
                    pass        
        return """<div style='font-family:system-ui; font-size:14px; line-height:1.7;'>
        <h2 style='margin:0 0 12px;'>LinkCodeEdit — Инструкция</h2>
        <p>Приложение бесплатно, MIT. Использование — на ваш риск (“AS IS”).</p>
        <ul>
            <li>🧹 <b>Комментарии (All)</b> — удаление комментариев.</li>
            <li>✨ <b>Форматирование</b> — выравнивание и минификация.</li>
            <li>🔗 <b>JS-ссылка</b> — Bookmarklet / &lt;a&gt; / open().</li>
            <li>🕵️ <b>Обфускация</b> — eval(Base64), hex, деобфуск.</li>
            <li>🖼️ <b>OG Метатеги</b> — генератор &lt;meta property="og:*"&gt;.</li>
            <li>🏷️ <b>UTM-метки</b> — добавление utm_* к URL.</li>
            <li>🔤 <b>ЧПУ (slug)</b> — транслит RU→EN, регистр, длина.</li>
            <li>🔢 <b>Количество символов</b> — подробная статистика.</li>
            <li>🔐 <b>Генератор паролей</b> — гибкие правила.</li>
        </ul>
        <h3>Поддержать проект</h3>
        <p>
            <a href='https://yoomoney.ru/to/410011663886937'>YooMoney #1</a> ·
            <a href='https://yoomoney.ru/to/410011663886938'>YooMoney #2</a>
        </p>
        </div>"""
    def _load_license_text(self) -> str:
        """Читает license_ru.txt / license_en.txt из assets, иначе дефолт."""
        lang = i18n.lang()
        candidates = [
            ASSETS_DIR / f"license_{lang}.txt",
            ASSETS_DIR / "license_en.txt",
            ASSETS_DIR / "LICENSE.txt",
        ]
        for p in candidates:
            if p.exists():
                try:
                    return p.read_text(encoding="utf-8")
                except Exception:
                    pass
        return (
            "LinkCodeEdit — License\n\n"
            "Software is provided “as is”, without warranty of any kind. "
            "Use at your own risk.\n"
        )
    def _show_license(self):
        txt = self._load_license_text()
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.t("act.license"))
        lay = QVBoxLayout(dlg)
        view = QTextBrowser()
        view.setPlainText(txt)
        lay.addWidget(view)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns, alignment=Qt.AlignRight)
        dlg.resize(820, 560)
        dlg.exec()    
    def _style_qss(self) -> str:
        return """
        QMainWindow { background: #f7f7fb; color: #222; }
        QLabel { color: #222; }
        QPlainTextEdit { background: #ffffff; color: #111; border: 1px solid #dcdce4; border-radius: 8px; padding: 8px; }
        QLineEdit { background: #ffffff; color: #111; border: 1px solid #dcdce4; border-radius: 8px; padding: 6px 8px; }
        QTabWidget::pane { border: 1px solid #dcdce4; border-radius: 8px; }
        QTabBar::tab { background: #f0f2f8; color: #333; padding: 8px 14px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
        QTabBar::tab:selected { background: #ffffff; }
        QPushButton { background: #2f6fed; color: white; border: none; padding: 8px 12px; border-radius: 8px; }
        QPushButton:hover { background: #3e7cff; }
        QPushButton:disabled { background: #e6e6ee; color: #9a9a9a; }
        QToolBar { background: #ffffff; border-bottom: 1px solid #e8e8f0; }
        QStatusBar { background: #ffffff; color: #444; }
        #paneHeader { font-weight: 700; font-size: 14px; color: #2f6fed; margin: 4px 0 8px; }
        """   
    def _current_tab_order_ids(self) -> list[str]:        
        rev = {w: tid for tid, (w, _key) in getattr(self, "_tab_map", {}).items()}
        ids = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            tid = rev.get(w)
            if tid:
                ids.append(tid)
        return ids
    def _save_tab_order(self):
        try:
            ids = self._current_tab_order_ids()
            settings = QSettings(APP_ORG, APP_NAME)
            settings.setValue("ui/tab_order", ids)            
        except Exception:
            pass
    def closeEvent(self, e):
        try:
            self._save_tab_order()
        except Exception:
            pass
        super().closeEvent(e)
MainWindow._build_tabs = _build_tabs_with_extras
def _ensure_eula(settings: QSettings) -> bool:
    accepted = settings.value("eula/accepted", False, bool)
    if accepted:
        return True
    dlg = QDialog()
    dlg.setWindowTitle("EULA / " + i18n.t("act.license"))
    lay = QVBoxLayout(dlg)
    view = QTextBrowser() 
    def _load_license_text() -> str:
        lang = i18n.lang()
        candidates = [
            ASSETS_DIR / f"license_{lang}.txt",
            ASSETS_DIR / "license_en.txt",
            ASSETS_DIR / "LICENSE.txt",
        ]
        for p in candidates:
            if p.exists():
                try:
                    return p.read_text(encoding="utf-8")
                except Exception:
                    pass
        return (
            "LinkCodeEdit — License\n\n"
            "Software is provided “as is”, without warranty of any kind. "
            "Use at your own risk.\n"
        )
    view.setPlainText(_load_license_text())
    lay.addWidget(view)
    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    btns.button(QDialogButtonBox.Ok).setText("Принять")
    btns.button(QDialogButtonBox.Cancel).setText("Отклонить")
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    lay.addWidget(btns, alignment=Qt.AlignRight)
    dlg.resize(820, 560)
    if dlg.exec() == QDialog.Accepted:
        settings.setValue("eula/accepted", True)
        return True
    return False
def main():
    _install_crash_guard()

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f"{APP_ORG}.{APP_NAME}.{APP_VER}"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)

    if APP_ICON_PATH:
        ic = QIcon(str(APP_ICON_PATH))
        app.setWindowIcon(ic)

    app.setOrganizationName(APP_ORG)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VER)

    settings = QSettings(APP_ORG, APP_NAME)
    lang = settings.value("ui/lang", "ru", str)
    i18n.load(lang)

    if not _ensure_eula(settings):
        return  

    w = MainWindow()
    if APP_ICON_PATH:
        w.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    w.show()


    if sys.platform == "win32" and APP_ICON_PATH and str(APP_ICON_PATH).lower().endswith(".ico"):
        try:
            import ctypes
            WM_SETICON = 0x0080
            ICON_SMALL, ICON_BIG = 0, 1
            LR_LOADFROMFILE = 0x0010
            IMAGE_ICON = 1
            user32 = ctypes.windll.user32
            hbig = user32.LoadImageW(None, str(APP_ICON_PATH), IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
            hsmall = user32.LoadImageW(None, str(APP_ICON_PATH), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
            if hbig:
                user32.SendMessageW(int(w.winId()), WM_SETICON, ICON_BIG, hbig)
            if hsmall:
                user32.SendMessageW(int(w.winId()), WM_SETICON, ICON_SMALL, hsmall)
        except Exception:
            pass
    sys.exit(app.exec())
if __name__ == "__main__":
    main()