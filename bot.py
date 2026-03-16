# ErisPulse 反馈机器人核心类
import asyncio
import time
from datetime import datetime
from ErisPulse import sdk


class FeedbackBot:
    def __init__(self, sdk):
        self.sdk = sdk
        self.storage = sdk.storage
        self.config = self._load_config()
        self.logger = sdk.logger.get_child("FeedbackBot")
    
    def _load_config(self):
        config = self.sdk.config.getConfig("FeedbackBot", {})
        
        default_config = {
            "storage_prefix": "feedback_",
            "admin": [],
            "categories": ["功能", "优化", "建议", "bug"],
            "target_groups": ["all"]
        }
        
        # 合并配置
        if "admin" not in config:
            config["admin"] = default_config["admin"]
        
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        self.sdk.config.setConfig("FeedbackBot", config)
        return config
    
    def is_admin(self, user_id):
        admins = self.config.get("admin", [])
        return user_id in admins
    
    async def _generate_feedback_id(self):
        key = f"{self.config['storage_prefix']}next_id"
        next_id = self.storage.get(key, 1)
        feedback_id = f"feedback_{next_id:06d}"
        self.storage.set(key, next_id + 1)
        return feedback_id
    
    async def submit_feedback(self, user_id, nickname, category, content, group_id):
        if category not in self.config["categories"]:
            categories = ", ".join(self.config["categories"])
            return f"无效的类别。请使用: {categories}"
        
        feedback_id = await self._generate_feedback_id()
        
        feedback_data = {
            "id": feedback_id,
            "user_id": user_id,
            "user_nickname": nickname,
            "category": category,
            "content": content,
            "status": "pending",
            "timestamp": int(time.time()),
            "group_id": group_id
        }
        
        self.storage.set(f"{self.config['storage_prefix']}{feedback_id}", feedback_data)
        self.logger.info(f"反馈已提交: {feedback_id} by {user_id}")
        
        return feedback_id
    
    async def update_feedback_status(self, feedback_id, new_status):
        feedback_data = self.storage.get(f"{self.config['storage_prefix']}{feedback_id}")
        if not feedback_data:
            return None
        
        feedback_data["status"] = new_status
        self.storage.set(f"{self.config['storage_prefix']}{feedback_id}", feedback_data)
        return feedback_data
    
    def get_feedback(self, feedback_id):
        return self.storage.get(f"{self.config['storage_prefix']}{feedback_id}")
    
    async def list_feedbacks(self, category=None, status=None, group_id=None, limit=20):
        all_keys = []
        for key in self.storage.keys():
            if key.startswith(self.config['storage_prefix']) and key != f"{self.config['storage_prefix']}next_id":
                all_keys.append(key)
        
        feedbacks = []
        for key in all_keys:
            data = self.storage.get(key)
            if data:
                feedbacks.append(data)
        
        # 筛选
        filtered = []
        for feedback in feedbacks:
            if category and feedback["category"] != category:
                continue
            
            if status and feedback["status"] != status:
                continue
            
            if group_id and feedback["group_id"] != group_id:
                continue
            
            filtered.append(feedback)
        
        # 按时间排序（最新的在前）
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered[:limit]