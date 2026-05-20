from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, Achievement

# Levels Configuration
LEVEL_THRESHOLDS = [
    (1, 0, "Mind Beginner 🧠", "Початок усвідомленого шляху. Твоя увага все ще вразлива, але перший крок зроблено."),
    (2, 100, "Focus Keeper 🛡️", "Твій фокус міцнішає. Короткі відео більше не керують твоїм ранком."),
    (3, 300, "Attention Guardian 👁️", "Вартовий уваги. Твій мозок почав помічати красу реального світу."),
    (4, 600, "Dopamine Master ⚡", "Володар дофаміну. Ти бачиш дешеві гачки алгоритмів наскрізь."),
    (5, 1000, "Scroll Destroyer 🔥", "Руйнівник нескінченної стрічки. Ти повністю повернув контроль над розумом.")
]

# Badge/Achievement Definitions
ACHIEVEMENTS_BOOK = {
    "first_step": {
        "title": "Перший крок 🌱",
        "description": "Початок детоксу. 1 день без коротких відео.",
        "xp_bonus": 15
    },
    "streak_3": {
        "title": "Свідомий Вікенд 🕊️",
        "description": "3 дні без скролінгу. Мозок починає очищуватись.",
        "xp_bonus": 30
    },
    "streak_7": {
        "title": "Тиждень Ясності 👁️",
        "description": "7 днів без doomscrolling. Мозок починає дякувати тобі.",
        "xp_bonus": 70
    },
    "streak_14": {
        "title": "Два Тижні Реальності 🌍",
        "description": "14 днів свободи. Справжнє життя набагато цікавіше.",
        "xp_bonus": 150
    },
    "streak_30": {
        "title": "Дофаміновий Перезапуск ⚡",
        "description": "30 днів без TikTok. Ти буквально повертаєш собі увагу.",
        "xp_bonus": 300
    },
    "streak_50": {
        "title": "Майстер Концентрації 🧘‍♂️",
        "description": "50 днів чистоти. Твоя воля стала міцною як сталь.",
        "xp_bonus": 500
    },
    "streak_100": {
        "title": "Абсолютний Дзен 🌌",
        "description": "100 днів без коротких відео. Алгоритми офіційно програли.",
        "xp_bonus": 1000
    },
    "first_relapse": {
        "title": "Урок, а не Поразка 🍂",
        "description": "Перший зрив. Зроби висновки і повертайся сильнішим.",
        "xp_bonus": 5
    },
    "freeze_master": {
        "title": "Кріогенний Сон ❄️",
        "description": "Вперше активовано заморозку стріку.",
        "xp_bonus": 10
    }
}

def get_level_info(xp_points: int) -> tuple[int, str, str]:
    """
    Returns (level, title, description) based on XP points.
    For levels above 5, dynamically calculates standard progression.
    """
    # Check fixed levels
    for lvl, threshold, name, desc in reversed(LEVEL_THRESHOLDS):
        if xp_points >= threshold:
            # If level is 5, check if they deserve even higher procedural levels
            if lvl == 5:
                extra_xp = xp_points - 1000
                extra_levels = extra_xp // 500
                final_lvl = 5 + extra_levels
                if final_lvl > 5:
                    return final_lvl, f"Scroll Destroyer V{final_lvl} 🔥", "Абсолютний володар уваги, що перейшов межі людських можливостей."
            return lvl, name, desc
    return 1, LEVEL_THRESHOLDS[0][2], LEVEL_THRESHOLDS[0][3]

async def check_and_unlock_achievement(
    user: User, 
    badge_id: str, 
    session: AsyncSession
) -> Achievement | None:
    """
    Helper to check if achievement is already unlocked. If not, unlocks it,
    adds XP, updates user levels and returns the unlocked Achievement model.
    """
    if badge_id not in ACHIEVEMENTS_BOOK:
        return None
        
    # Check if already unlocked
    stmt = select(Achievement).where(
        Achievement.telegram_id == user.telegram_id,
        Achievement.badge_id == badge_id
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return None
        
    # Unlock achievement
    badge = ACHIEVEMENTS_BOOK[badge_id]
    achievement = Achievement(
        telegram_id=user.telegram_id,
        badge_id=badge_id,
        title=badge["title"],
        description=badge["description"],
        unlocked_at=datetime.utcnow()
    )
    session.add(achievement)
    
    # Award XP
    user.xp_points += badge["xp_bonus"]
    
    return achievement

async def process_gamification_streak(
    user: User, 
    session: AsyncSession
) -> list[Achievement]:
    """
    Evaluates streak achievements based on the user's current or best streak.
    Returns a list of newly unlocked achievements.
    """
    unlocked = []
    
    # Check 1 day
    if user.total_clean_days >= 1:
        ach = await check_and_unlock_achievement(user, "first_step", session)
        if ach: unlocked.append(ach)
        
    # Check streak milestones
    streak_milestones = {
        3: "streak_3",
        7: "streak_7",
        14: "streak_14",
        30: "streak_30",
        50: "streak_50",
        100: "streak_100"
    }
    
    for streak_val, badge_id in streak_milestones.items():
        if user.current_streak >= streak_val:
            ach = await check_and_unlock_achievement(user, badge_id, session)
            if ach: unlocked.append(ach)
            
    return unlocked
