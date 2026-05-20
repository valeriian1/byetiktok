from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from database.models import User, DailyCheck, Achievement, FreezeUsage, Chat
from database.db import async_session
from services.gamification import get_level_info, process_gamification_streak, check_and_unlock_achievement

async def get_user(telegram_id: int) -> User | None:
    """Fetches a user from the database by Telegram ID"""
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def register_user(
    telegram_id: int, 
    username: str | None, 
    display_name: str,
    is_admin: bool = False
) -> tuple[User, bool]:
    """
    Registers a new user or updates their display name and username if already exists.
    Returns the User model and a boolean indicating if they are a new user.
    """
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        is_new = False
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                display_name=display_name,
                is_admin=is_admin,
                freezes_available=1, # Give 1 freeze at start
                join_date=datetime.utcnow()
            )
            session.add(user)
            is_new = True
        else:
            user.username = username
            user.display_name = display_name
            if is_admin:
                user.is_admin = True
                
        await session.commit()
        # Refresh user from DB to keep it bound to session if needed or just return it
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one(), is_new

async def register_chat(chat_id: int, chat_type: str, title: str | None) -> Chat:
    """Registers a Telegram group chat to receive daily polls"""
    async with async_session() as session:
        stmt = select(Chat).where(Chat.chat_id == chat_id)
        result = await session.execute(stmt)
        chat = result.scalar_one_or_none()
        
        if not chat:
            chat = Chat(
                chat_id=chat_id,
                chat_type=chat_type,
                title=title,
                is_active=True
            )
            session.add(chat)
        else:
            chat.is_active = True
            chat.title = title
            
        await session.commit()
        return chat

async def deactivate_chat(chat_id: int):
    """Deactivates a chat (e.g. when bot is removed from a group)"""
    async with async_session() as session:
        stmt = select(Chat).where(Chat.chat_id == chat_id)
        result = await session.execute(stmt)
        chat = result.scalar_one_or_none()
        if chat:
            chat.is_active = False
            await session.commit()

async def get_active_chats() -> list[Chat]:
    """Fetches all active chats registered for daily check-ins"""
    async with async_session() as session:
        stmt = select(Chat).where(Chat.is_active == True)
        result = await session.execute(stmt)
        return list(result.scalars().all())

async def add_daily_check(
    telegram_id: int, 
    check_date: date, 
    status: str
) -> tuple[User, str | None, list[Achievement]]:
    """
    Submits a daily check-in ('clean' or 'relapsed') for a user.
    Handles streak, XP, level, and achievement updates safely in one transaction.
    """
    async with async_session() as session:
        # Check for existing check today
        stmt = select(DailyCheck).where(
            and_(
                DailyCheck.telegram_id == telegram_id,
                DailyCheck.check_date == check_date
            )
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Ти вже надіслав свій звіт сьогодні!")
            
        # Get user
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError("Користувача не знайдено. Будь ласка, напиши /start спочатку.")
            
        # Record old gamification info
        old_xp = user.xp_points
        old_level, _, _ = get_level_info(old_xp)
        
        # Insert Daily Check
        new_check = DailyCheck(
            telegram_id=telegram_id,
            check_date=check_date,
            status=status,
            checked_at=datetime.utcnow()
        )
        session.add(new_check)
        
        unlocked_achievements = []
        
        if status == 'clean':
            user.current_streak += 1
            user.total_clean_days += 1
            if user.current_streak > user.best_streak:
                user.best_streak = user.current_streak
            # +10 XP for daily check-in
            user.xp_points += 10
            
            # Check for streak achievements
            new_achs = await process_gamification_streak(user, session)
            unlocked_achievements.extend(new_achs)
            
        elif status == 'relapsed':
            user.current_streak = 0
            user.total_failures += 1
            
            # Check for first relapse achievement
            ach = await check_and_unlock_achievement(user, "first_relapse", session)
            if ach:
                unlocked_achievements.append(ach)
                
        # Calculate level up
        new_xp = user.xp_points
        new_level, level_title, _ = get_level_info(new_xp)
        
        level_up_title = None
        if new_level > old_level:
            user.level = new_level
            level_up_title = level_title
            
        await session.commit()
        
        # Re-fetch user in session-completed state
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        return user_res.scalar_one(), level_up_title, unlocked_achievements

async def use_freeze(telegram_id: int, check_date: date) -> tuple[User, list[Achievement]]:
    """
    Consumes a freeze token for today, keeping the current streak active.
    Fails if no freezes are available or if today is already logged.
    """
    async with async_session() as session:
        # Check if already has a record for today
        stmt = select(DailyCheck).where(
            and_(
                DailyCheck.telegram_id == telegram_id,
                DailyCheck.check_date == check_date
            )
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            if existing.status == 'clean':
                raise ValueError("Ти вже відмітився сьогодні як чистий! Заморозка не потрібна.")
            elif existing.status == 'freeze':
                raise ValueError("Ти вже заморозив сьогоднішній день.")
            else:
                raise ValueError("На жаль, ти вже відмітив зрив сьогодні. Заморозити день вже не можна.")
                
        # Get user
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError("Користувача не знайдено. Будь ласка, напиши /start спочатку.")
            
        if user.freezes_available <= 0:
            raise ValueError("У тебе немає доступних заморозок. Заморозки даються за нові рівні та досягнення.")
            
        # Consume freeze
        user.freezes_available -= 1
        
        # Add daily check as freeze
        new_check = DailyCheck(
            telegram_id=telegram_id,
            check_date=check_date,
            status='freeze',
            checked_at=datetime.utcnow()
        )
        session.add(new_check)
        
        # Add record to FreezeUsage
        new_usage = FreezeUsage(
            telegram_id=telegram_id,
            used_date=check_date,
            created_at=datetime.utcnow()
        )
        session.add(new_usage)
        
        # Check and unlock freeze achievement
        unlocked_achievements = []
        ach = await check_and_unlock_achievement(user, "freeze_master", session)
        if ach:
            unlocked_achievements.append(ach)
            
        await session.commit()
        
        # Re-fetch user
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        return user_res.scalar_one(), unlocked_achievements

async def get_leaderboard(sort_by: str = "best_streak") -> list[User]:
    """
    Returns top 10 users sorted by:
    - 'best_streak': longest streak of all time
    - 'current_streak': current active streak
    - 'xp': total experience points
    """
    async with async_session() as session:
        if sort_by == "current_streak":
            order_col = desc(User.current_streak)
        elif sort_by == "xp":
            order_col = desc(User.xp_points)
        else:
            order_col = desc(User.best_streak)
            
        stmt = select(User).order_by(order_col).limit(10)
        result = await session.execute(stmt)
        return list(result.scalars().all())

async def get_user_stats(telegram_id: int) -> dict | None:
    """Calculates comprehensive statistics for a user"""
    async with async_session() as session:
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if not user:
            return None
            
        # Get count of clean and relapse checks
        clean_stmt = select(func.count(DailyCheck.id)).where(
            and_(DailyCheck.telegram_id == telegram_id, DailyCheck.status == 'clean')
        )
        relapse_stmt = select(func.count(DailyCheck.id)).where(
            and_(DailyCheck.telegram_id == telegram_id, DailyCheck.status == 'relapsed')
        )
        freeze_stmt = select(func.count(DailyCheck.id)).where(
            and_(DailyCheck.telegram_id == telegram_id, DailyCheck.status == 'freeze')
        )
        
        clean_cnt = (await session.execute(clean_stmt)).scalar() or 0
        relapse_cnt = (await session.execute(relapse_stmt)).scalar() or 0
        freeze_cnt = (await session.execute(freeze_stmt)).scalar() or 0
        
        total_active_days = clean_cnt + relapse_cnt
        success_percentage = int((clean_cnt / total_active_days * 100)) if total_active_days > 0 else 0
        
        # Get user's level metadata
        level, level_title, _ = get_level_info(user.xp_points)
        
        # Fetch unlocked badges
        badge_stmt = select(Achievement).where(Achievement.telegram_id == telegram_id)
        badge_res = await session.execute(badge_stmt)
        badges = [b.title for b in badge_res.scalars().all()]
        
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "display_name": user.display_name,
            "current_streak": user.current_streak,
            "best_streak": user.best_streak,
            "total_failures": user.total_failures,
            "total_clean_days": user.total_clean_days,
            "freezes_available": user.freezes_available,
            "xp": user.xp_points,
            "level": level,
            "level_title": level_title,
            "success_percentage": success_percentage,
            "badges": badges,
            "clean_count": clean_cnt,
            "relapse_count": relapse_cnt,
            "freeze_count": freeze_cnt
        }

async def check_user_checkin_status(telegram_id: int, check_date: date) -> str | None:
    """Returns the check-in status of a user for a specific date, or None if not checked in"""
    async with async_session() as session:
        stmt = select(DailyCheck.status).where(
            and_(
                DailyCheck.telegram_id == telegram_id,
                DailyCheck.check_date == check_date
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

# --- ADMIN ACTIONS ---

async def reset_user_stats(telegram_id: int) -> User | None:
    """Admin function: resets a user's stats completely"""
    async with async_session() as session:
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        
        if user:
            user.current_streak = 0
            user.best_streak = 0
            user.total_failures = 0
            user.total_clean_days = 0
            user.xp_points = 0
            user.level = 1
            user.freezes_available = 1
            
            # Delete their checks and achievements
            delete_checks = select(DailyCheck).where(DailyCheck.telegram_id == telegram_id)
            checks_res = await session.execute(delete_checks)
            for c in checks_res.scalars().all():
                await session.delete(c)
                
            delete_achievements = select(Achievement).where(Achievement.telegram_id == telegram_id)
            ach_res = await session.execute(delete_achievements)
            for a in ach_res.scalars().all():
                await session.delete(a)
                
            delete_freezes = select(FreezeUsage).where(FreezeUsage.telegram_id == telegram_id)
            freeze_res = await session.execute(delete_freezes)
            for f in freeze_res.scalars().all():
                await session.delete(f)
                
            await session.commit()
            
            # Re-fetch
            user_stmt = select(User).where(User.telegram_id == telegram_id)
            user_res = await session.execute(user_stmt)
            return user_res.scalar_one()
        return None

async def force_award_freeze(telegram_id: int, count: int = 1) -> User | None:
    """Admin function: grants additional freeze days to a user"""
    async with async_session() as session:
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if user:
            user.freezes_available += count
            await session.commit()
            return user
        return None
