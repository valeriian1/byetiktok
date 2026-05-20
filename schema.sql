-- =====================================================================
-- SQL Database Schema for "No TikTok / No Reels Challenge" Bot
-- Database engine: SQLite 3
-- =====================================================================

PRAGMA foreign_keys = ON;

-- 1. Table for tracking group members and users
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    display_name TEXT NOT NULL,
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_failures INTEGER DEFAULT 0,
    total_clean_days INTEGER DEFAULT 0,
    join_date DATETIME NOT NULL,
    xp_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    freezes_available INTEGER DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0
);

-- 2. Table for daily check-in reports (clean, relapsed, or frozen days)
CREATE TABLE IF NOT EXISTS daily_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    check_date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('clean', 'relapsed', 'freeze')),
    checked_at DATETIME NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

-- 3. Table for unlocked badges/achievements
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    badge_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    unlocked_at DATETIME NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

-- 4. Log for history of freeze token usage
CREATE TABLE IF NOT EXISTS freeze_usages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    used_date DATE NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

-- 5. Table to track chats (groups) where the bot is registered
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    chat_type TEXT NOT NULL,
    title TEXT,
    added_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

-- Indices for performance tuning
CREATE INDEX IF NOT EXISTS idx_daily_checks_date ON daily_checks (check_date);
CREATE INDEX IF NOT EXISTS idx_daily_checks_user ON daily_checks (telegram_id);
CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements (telegram_id);
