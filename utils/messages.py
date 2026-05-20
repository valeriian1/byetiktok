def escape_markdown(text: str | None) -> str:
    """Escapes Markdown V1 special characters (*, _, `, [) to prevent Telegram parsing errors"""
    if not text:
        return ""
    return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")

def get_start_message(display_name: str) -> str:
    """Atmospheric registration message in dark academia style"""
    escaped_name = escape_markdown(display_name)
    return (
        f"🏛️ *Вітаємо у Братстві Уваги, {escaped_name}!*\n\n"
        "Ти став частиною спільноти, яка вирішила кинути виклик найвитонченішому викрадачу людського часу — безкінечному скролінгу.\n\n"
        "🕯️ *Наша філософія:*\n"
        "Алгоритми TikTok, Instagram Reels та YouTube Shorts створені для того, щоб висмоктувати твою увагу та перетворювати твій час на прибуток корпорацій. Тут ми повертаємо собі контроль над своїм розумом.\n\n"
        "📅 *Правила виклику:*\n"
        "• Щодня о *21:00* бот надсилатиме у цей чат (або в твої приватні повідомлення) опитування.\n"
        "• Твоє завдання — чесно відповісти, чи вдалося тобі провести день без коротких відео.\n"
        "• Кожен чистий день приносить тобі *+10 XP* та збільшує твій *стрік* (серію днів).\n"
        "• Зрив скидає стрік до нуля.\n"
        "• Кожен має *1 заморозку стріку* (`/freeze`) на старті. Використовуй її з розумом, коли спокуса занадто велика.\n\n"
        "🧠 *Початковий статус:*\n"
        "• Рівень: `1 (Mind Beginner 🌱)`\n"
        "• Заморозки: `❄️ x1`\n\n"
        "_Починаємо детокс від нескінченного скролу. Нехай твій фокус буде непохитним._"
    )

def get_help_message() -> str:
    """Detailed manual of commands and rules"""
    return (
        "📜 *Маніфест та Інструкція Братства Уваги*\n\n"
        "Цей бот допомагає тобі та твоїм друзям тримати стрік життя без TikTok, Reels та коротких відео.\n\n"
        "🏛️ *Доступні команди:*\n"
        "• /start — приєднатися до виклику та зареєструватися\n"
        "• /stats — переглянути свою детальну дофамінову статистику\n"
        "• /leaderboard — подивитися топ учасників\n"
        "• /freeze — активувати заморозку на сьогодні (зберігає стрік, якщо не можеш встояти)\n"
        "• /help — відкрити цю інструкцію\n\n"
        "⏳ *Логіка роботи:*\n"
        "• Опитування з'являється щодня о *21:00*.\n"
        "• Відповісти на нього можна лише один раз на добу.\n"
        "• За чисті дні ти отримуєш XP та підвищуєш свій Рівень:\n"
        "  1. `Mind Beginner` 🌱\n"
        "  2. `Focus Keeper` 🛡️\n"
        "  3. `Attention Guardian` 👁️\n"
        "  4. `Dopamine Master` ⚡\n"
        "  5. `Scroll Destroyer` 🔥\n\n"
        "❄️ *Механіка заморозки:*\n"
        "• Команда `/freeze` рятує твій стрік від згорання.\n"
        "• Додаткові заморозки нараховуються за досягнення нових рівнів та розблокування ачивок.\n\n"
        "_«Твоя увага — твій найцінніший ресурс. Не віддавай його задешево.»_"
    )

def get_stats_message(stats: dict) -> str:
    """Formatted personal user statistics"""
    badges_str = "\n".join([f"• {escape_markdown(b)}" for b in stats["badges"]]) if stats["badges"] else "_Немає розблокованих ачивок_"
    username_part = f" (@{escape_markdown(stats['username'])})" if stats['username'] else ""
    escaped_name = escape_markdown(stats['display_name'])
    escaped_lvl_title = escape_markdown(stats['level_title'])
    
    return (
        f"📊 *Дофамінова статистика | {escaped_name}*{username_part}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎖️ *Ранг:* `{escaped_lvl_title}` (Рівень `{stats['level']}`)\n"
        f"⚡ *Досвід:* `{stats['xp']} XP`\n\n"
        f"🔥 *Поточний стрік:* `{stats['current_streak']} днів`\n"
        f"🏆 *Найкращий стрік:* `{stats['best_streak']} днів`\n"
        f"❄️ *Доступні заморозки:* `{stats['freezes_available']} шт.`\n\n"
        f"✅ *Успішних днів:* `{stats['clean_count']}`\n"
        f"❌ *Зривів:* `{stats['relapse_count']}`\n"
        f"📈 *Коефіцієнт успіху:* `{stats['success_percentage']}%`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏅 *Досягнення ({len(stats['badges'])}):*\n"
        f"{badges_str}\n\n"
        f"_«Алгоритми сьогодні програли.»_"
    )

def get_leaderboard_message(users: list, sort_by: str) -> str:
    """Leaderboard page formatting"""
    title_map = {
        "best_streak": "🔥 Найкращий стрік (всі часи)",
        "current_streak": "⚡ Поточний стрік",
        "xp": "🏆 Досвід та Ранг (XP)"
    }
    
    header = f"🏛️ *Зал Слави Братства Уваги*\n"
    header += f"📊 Сортування: *{title_map.get(sort_by, sort_by)}*\n"
    header += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    rows = []
    for idx, u in enumerate(users):
        medal = medals[idx] if idx < len(medals) else "•"
        
        # Display details based on sort type
        if sort_by == "current_streak":
            detail = f"`{u.current_streak} дн` (найкр: `{u.best_streak}`)"
        elif sort_by == "xp":
            detail = f"`{u.xp_points} XP` (Lvl `{u.level}`)"
        else:
            detail = f"`{u.best_streak} дн` (пот: `{u.current_streak}`)"
            
        username_part = f" (@{escape_markdown(u.username)})" if u.username else ""
        escaped_name = escape_markdown(u.display_name)
        rows.append(f"{medal} *{escaped_name}*{username_part}\n    └ {detail}")
        
    if not rows:
        return header + "_У залі слави поки порожньо. Почни свій стрік зараз!_"
        
    return header + "\n\n".join(rows)

def get_daily_checkin_message() -> str:
    """Atmospheric poll message triggered daily at 21:00"""
    return (
        "⏳ *Вечірній звіт Братства Уваги*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "День добігає кінця. Час заглянути всередину себе і відповісти чесно:\n\n"
        "❓ *Чи заходив ти сьогодні в TikTok, Instagram Reels або YouTube Shorts?*\n\n"
        "_«Твоя увага — це твій ресурс. Алгоритми хочуть продати його. Що вибрав ти сьогодні?»_"
    )

def get_achievement_unlock_message(display_name: str, badge_title: str, description: str, xp_bonus: int) -> str:
    """Notification when an achievement is unlocked"""
    escaped_name = escape_markdown(display_name)
    escaped_badge = escape_markdown(badge_title)
    escaped_desc = escape_markdown(description)
    return (
        f"🏅 *НОВЕ ДОСЯГНЕННЯ РОЗБЛОКОВАНО!*\n"
        f"👤 *Учасник:* *{escaped_name}*\n"
        f"🏆 *Назва:* *{escaped_badge}*\n"
        f"📜 *Опис:* _{escaped_desc}_\n"
        f"⚡ *Бонус:* `+{xp_bonus} XP`"
    )

def get_level_up_message(display_name: str, level: int, title: str, description: str) -> str:
    """Notification when a user gains a new level"""
    escaped_name = escape_markdown(display_name)
    escaped_title = escape_markdown(title)
    escaped_desc = escape_markdown(description)
    return (
        f"⚡ *НОВИЙ РІВЕНЬ ДОСЯГНУТО!* ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Учасник:* *{escaped_name}*\n"
        f"🎖️ *Новий ранг:* *{escaped_title}* (Рівень `{level}`)\n"
        f"📜 *Стан розуму:* _{escaped_desc}_\n\n"
        f"🎁 *Нагорода за розвиток фокусу:* `+1 Заморозка стріку (❄️)`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Вітаємо! Твоя стійкість дає плоди."
    )
