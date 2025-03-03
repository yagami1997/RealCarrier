"""
缓存管理模块 - 负责存储和检索查询结果缓存
"""

import os
import json
import time
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from lnptool.config import CONFIG_DIR, get_config

# 缓存常量
CACHE_DIR = CONFIG_DIR / "cache"
DB_FILE = CACHE_DIR / "lookup_cache.db"

logger = logging.getLogger(__name__)


class Cache:
    """查询结果缓存管理"""
    
    def __init__(self):
        """初始化缓存管理器"""
        self._ensure_cache_dir()
        self._init_db()
    
    def _ensure_cache_dir(self) -> None:
        """确保缓存目录存在"""
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True, mode=0o700)
            logger.info(f"Created cache directory: {CACHE_DIR}")
    
    def _init_db(self) -> None:
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            # 创建查询结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS lookup_results (
                phone_number TEXT PRIMARY KEY,
                result TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON lookup_results(timestamp)')
            
            conn.commit()
            conn.close()
            logger.debug("Cache database initialized")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize cache database: {e}")
    
    def get(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取查询结果
        
        Args:
            phone_number: 电话号码
            
        Returns:
            Optional[Dict[str, Any]]: 缓存的查询结果，如果未找到或已过期则返回None
        """
        config = get_config()
        cache_ttl = config.get("api_cache_ttl", 86400)  # 默认缓存1天
        
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            # 获取缓存结果
            cursor.execute(
                'SELECT result, timestamp FROM lookup_results WHERE phone_number = ?',
                (phone_number,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                result_json, timestamp = row
                current_time = time.time()
                
                # 检查缓存是否过期
                if current_time - timestamp <= cache_ttl:
                    try:
                        return json.loads(result_json)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode cached result for {phone_number}")
                else:
                    logger.debug(f"Cache for {phone_number} has expired")
            
            return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, phone_number: str, result: Dict[str, Any]) -> bool:
        """
        将查询结果存入缓存
        
        Args:
            phone_number: 电话号码
            result: 查询结果
            
        Returns:
            bool: 存储成功返回True，否则返回False
        """
        try:
            result_json = json.dumps(result)
            timestamp = time.time()
            
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            # 插入或替换缓存结果
            cursor.execute(
                'INSERT OR REPLACE INTO lookup_results (phone_number, result, timestamp) VALUES (?, ?, ?)',
                (phone_number, result_json, timestamp)
            )
            
            conn.commit()
            conn.close()
            logger.debug(f"Cached result for {phone_number}")
            return True
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Failed to cache result for {phone_number}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清除所有缓存
        
        Returns:
            bool: 清除成功返回True，否则返回False
        """
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM lookup_results')
            
            conn.commit()
            conn.close()
            logger.info("Cache cleared")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def clear_expired(self) -> int:
        """
        清除过期缓存
        
        Returns:
            int: 清除的缓存条目数
        """
        config = get_config()
        cache_ttl = config.get("api_cache_ttl", 86400)
        expiry_time = time.time() - cache_ttl
        
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM lookup_results WHERE timestamp < ?', (expiry_time,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} expired cache entries")
            return deleted_count
        except sqlite3.Error as e:
            logger.error(f"Failed to clear expired cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            # 获取总条目数
            cursor.execute('SELECT COUNT(*) FROM lookup_results')
            total_count = cursor.fetchone()[0]
            
            # 获取最早和最新的缓存时间
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM lookup_results')
            min_time, max_time = cursor.fetchone()
            
            # 计算过期条目数
            config = get_config()
            cache_ttl = config.get("api_cache_ttl", 86400)
            expiry_time = time.time() - cache_ttl
            cursor.execute('SELECT COUNT(*) FROM lookup_results WHERE timestamp < ?', (expiry_time,))
            expired_count = cursor.fetchone()[0]
            
            # 计算缓存大小
            cursor.execute('SELECT SUM(LENGTH(result)) FROM lookup_results')
            size_bytes = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_entries": total_count,
                "expired_entries": expired_count,
                "valid_entries": total_count - expired_count,
                "oldest_entry_time": min_time,
                "newest_entry_time": max_time,
                "cache_size_bytes": size_bytes,
                "cache_ttl_seconds": cache_ttl
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "error": str(e),
                "total_entries": 0,
                "expired_entries": 0,
                "valid_entries": 0
            }
    
    def get_recent_lookups(self, limit: int = 10) -> List[Tuple[str, float]]:
        """
        获取最近的查询记录
        
        Args:
            limit: 返回的记录数限制
            
        Returns:
            List[Tuple[str, float]]: 最近查询的电话号码和时间戳列表
        """
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT phone_number, timestamp FROM lookup_results ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except sqlite3.Error as e:
            logger.error(f"Failed to get recent lookups: {e}")
            return []
