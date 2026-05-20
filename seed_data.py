import asyncio
from datetime import datetime, timedelta
from database.db import init_db, async_session
from database.models import User, Achievement, Chat

async def seed():
    """Seeds the SQLite database with rich mock data for testing"""
    print("⏳ Initializing database models...")
    await init_db()
    
    print("🌱 Injecting mock test data...")
    async with async_session() as session:
        # 1. Create Mock Users
        users = [
            User(
                telegram_id=111111111,
                username="philosopher_diogenes",
                display_name="Діоген Синопський 🍯",
                current_streak=35,
                best_streak=35,
                total_clean_days=35,
                total_failures=0,
                join_date=datetime.utcnow() - timedelta(days=40),
                xp_points=650,
                level=4,
                freezes_available=0,
                is_admin=False
            ),
            User(
                telegram_id=222222222,
                username="stoic_seneca",
                display_name="Сенека Молодший 🕯️",
                current_streak=0,
                best_streak=8,
                total_clean_days=18,
                total_failures=2,
                join_date=datetime.utcnow() - timedelta(days=25),
                xp_points=210,
                level=2,
                freezes_available=1,
                is_admin=False
            ),
            User(
                telegram_id=333333333,
                username="emperor_marcus",
                display_name="Маркус Аврелій 🏛️",
                current_streak=15,
                best_streak=15,
                total_clean_days=15,
                total_failures=0,
                join_date=datetime.utcnow() - timedelta(days=20),
                xp_points=350,
                level=3,
                freezes_available=3,
                is_admin=True # Marcus Aurelius is registered as admin
            )
        ]
        
        for u in users:
            session.add(u)
            
        # 2. Create historical Achievements
        achievements = [
            # Diogenes Achievements
            Achievement(telegram_id=111111111, badge_id="first_step", title="Перший крок 🌱", description="Початок детоксу. 1 день без коротких відео.", unlocked_at=datetime.utcnow() - timedelta(days=35)),
            Achievement(telegram_id=111111111, badge_id="streak_3", title="Свідомий Вікенд 🕊️", description="3 дні без скролінгу. Мозок починає очищуватись.", unlocked_at=datetime.utcnow() - timedelta(days=33)),
            Achievement(telegram_id=111111111, badge_id="streak_7", title="Тиждень Ясності 👁️", description="7 днів без doomscrolling. Мозок починає дякувати тобі.", unlocked_at=datetime.utcnow() - timedelta(days=29)),
            Achievement(telegram_id=111111111, badge_id="streak_14", title="Два Тижні Реальності 🌍", description="14 днів свободи. Справжнє життя набагато цікавіше.", unlocked_at=datetime.utcnow() - timedelta(days=22)),
            Achievement(telegram_id=111111111, badge_id="streak_30", title="Дофаміновий Перезапуск ⚡", description="30 днів без TikTok. Ти буквально повертаєш собі увагу.", unlocked_at=datetime.utcnow() - timedelta(days=6)),
            
            # Seneca Achievements
            Achievement(telegram_id=222222222, badge_id="first_step", title="Перший крок 🌱", description="Початок детоксу. 1 день без коротких відео.", unlocked_at=datetime.utcnow() - timedelta(days=24)),
            Achievement(telegram_id=222222222, badge_id="streak_3", title="Свідомий Вікенд 🕊️", description="3 дні без скролінгу. Мозок починає очищуватись.", unlocked_at=datetime.utcnow() - timedelta(days=22)),
            Achievement(telegram_id=222222222, badge_id="streak_7", title="Тиждень Ясності 👁️", description="7 днів без doomscrolling. Мозок починає дякувати тобі.", unlocked_at=datetime.utcnow() - timedelta(days=18)),
            Achievement(telegram_id=222222222, badge_id="first_relapse", title="Урок, а не Поразка 🍂", description="Перший зрив. Зроби висновки і повертайся сильнішим.", unlocked_at=datetime.utcnow() - timedelta(days=16)),
            
            # Marcus Achievements
            Achievement(telegram_id=333333333, badge_id="first_step", title="Перший крок 🌱", description="Початок детоксу. 1 день без коротких відео.", unlocked_at=datetime.utcnow() - timedelta(days=15)),
            Achievement(telegram_id=333333333, badge_id="streak_3", title="Свідомий Вікенд 🕊️", description="3 дні без скролінгу. Мозок починає очищуватись.", unlocked_at=datetime.utcnow() - timedelta(days=13)),
            Achievement(telegram_id=333333333, badge_id="streak_7", title="Тиждень Ясності 👁️", description="7 днів без doomscrolling. Мозок починає дякувати тобі.", unlocked_at=datetime.utcnow() - timedelta(days=9)),
            Achievement(telegram_id=333333333, badge_id="streak_14", title="Два Тижні Реальності 🌍", description="14 днів свободи. Справжнє життя набагато цікавіше.", unlocked_at=datetime.utcnow() - timedelta(days=2))
        ]
        
        for a in achievements:
            session.add(a)
            
        # 3. Create Group Chats
        chats = [
            Chat(chat_id=-100123456789, chat_type="supergroup", title="🕯️ Академія Уваги (Друзі)", added_at=datetime.utcnow() - timedelta(days=30), is_active=True),
            Chat(chat_id=-100987654321, chat_type="group", title="🏛️ Клуб Стоїків", added_at=datetime.utcnow() - timedelta(days=10), is_active=True)
        ]
        
        for c in chats:
            session.add(c)
            
        await session.commit()
    print("🚀 Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
