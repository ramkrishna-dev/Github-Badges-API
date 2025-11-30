import aiosqlite
from typing import Dict, List
from .config import settings

DB_PATH = "analytics.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS badge_renders (
                id INTEGER PRIMARY KEY,
                type TEXT,
                identifier TEXT,
                metric TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def track_badge_render(badge_type: str, identifier: str, metric: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO badge_renders (type, identifier, metric) VALUES (?, ?, ?)",
            (badge_type, identifier, metric)
        )
        await db.commit()

async def get_analytics() -> Dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM badge_renders")
        total_renders = await cursor.fetchone()

        cursor = await db.execute("SELECT metric, COUNT(*) as count FROM badge_renders GROUP BY metric ORDER BY count DESC LIMIT 10")
        popular = await cursor.fetchall()

        return {
            "total_renders": total_renders[0] if total_renders else 0,
            "popular_metrics": [{"metric": row[0], "count": row[1]} for row in popular]
        }