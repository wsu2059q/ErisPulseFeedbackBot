from datetime import datetime


class FeedbackBuilder:
    def __init__(self, feedback_bot):
        self.bot = feedback_bot
        self.categories = feedback_bot.config["categories"]
    
    def build_single_feedback_html(self, feedback):
        time_str = datetime.fromtimestamp(feedback["timestamp"]).strftime("%Y-%m-%d %H:%M")
        
        # 状态颜色
        status_colors = {
            "pending": "#fff3e0",
            "processing": "#e3f2fd",
            "completed": "#e8f5e9"
        }
        
        status = feedback["status"]
        status_bg = status_colors.get(status, "#f5f5f5")
        status_text = {
            "pending": "待处理",
            "processing": "处理中",
            "completed": "已完成"
        }.get(status, status)
        
        # 类别颜色
        category_colors = {
            "功能": "#e1bee7",
            "优化": "#ffccbc",
            "建议": "#b3e5fc",
            "bug": "#ffcdd2"
        }
        category_bg = category_colors.get(feedback["category"], "#f5f5f5")
        
        html = f"""
<div style="padding: 10px; background: #ffffff; border-radius: 8px; margin-bottom: 10px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div>
            <strong>{feedback['user_nickname']}</strong>
            <small style="font-size: 12px; color: #888; margin-left: 8px;">ID: {feedback['user_id']}</small>
            <small style="font-size: 12px; color: #888; margin-left: 8px;">{time_str}</small>
        </div>
        <div style="display: flex; gap: 6px;">
            <div style="padding: 4px 8px; background-color: {category_bg}; color: #333; font-size: 12px; border-radius: 4px;">
                {feedback['category']}
            </div>
            <div style="padding: 4px 8px; background-color: {status_bg}; color: #333; font-size: 12px; border-radius: 4px;">
                {status_text}
            </div>
        </div>
    </div>
    
    <div style="padding: 10px; background: #f1f1f1; color: #000000; border-radius: 6px;">
        <div style="font-size: 12px; color: #666; margin-bottom: 6px;">#{feedback['id']}</div>
        <div style="color: #333; line-height: 1.6; font-size: 14px;">
            {feedback['content']}
        </div>
    </div>
</div>
"""
        return html
    
    def build_feedback_list_html(self, feedbacks, category_filter=None, status_filter=None):
        """构建反馈列表的 HTML 消息"""
        if not feedbacks:
            return self._build_empty_list_html()
        
        # 构建筛选信息
        filter_parts = []
        if category_filter:
            filter_parts.append(f"类别: {category_filter}")
        if status_filter:
            status_text = {
                "pending": "待处理",
                "processing": "处理中",
                "completed": "已完成"
            }.get(status_filter, status_filter)
            filter_parts.append(f"状态: {status_text}")
        
        filter_html = ""
        if filter_parts:
            filter_html = f"""
<div style="padding: 8px 12px; background: #e3f2fd; color: #1565c0; border-radius: 8px; margin-bottom: 10px; font-size: 13px;">
    {" | ".join(filter_parts)}
</div>
"""
        
        # 构建统计信息
        stats = {
            "total": len(feedbacks),
            "pending": sum(1 for f in feedbacks if f["status"] == "pending"),
            "processing": sum(1 for f in feedbacks if f["status"] == "processing"),
            "completed": sum(1 for f in feedbacks if f["status"] == "completed")
        }
        
        stats_html = f"""
<div style="display: flex; gap: 10px; margin-bottom: 12px;">
    <div style="flex: 1; padding: 8px; background: #f5f5f5; border-radius: 6px; text-align: center;">
        <div style="font-size: 18px; font-weight: bold; color: #333;">{stats['total']}</div>
        <div style="font-size: 11px; color: #666;">总计</div>
    </div>
    <div style="flex: 1; padding: 8px; background: #fff3e0; border-radius: 6px; text-align: center;">
        <div style="font-size: 18px; font-weight: bold; color: #e65100;">{stats['pending']}</div>
        <div style="font-size: 11px; color: #bf360c;">待处理</div>
    </div>
    <div style="flex: 1; padding: 8px; background: #e3f2fd; border-radius: 6px; text-align: center;">
        <div style="font-size: 18px; font-weight: bold; color: #1565c0;">{stats['processing']}</div>
        <div style="font-size: 11px; color: #0d47a1;">处理中</div>
    </div>
    <div style="flex: 1; padding: 8px; background: #e8f5e9; border-radius: 6px; text-align: center;">
        <div style="font-size: 18px; font-weight: bold; color: #2e7d32;">{stats['completed']}</div>
        <div style="font-size: 11px; color: #1b5e20;">已完成</div>
    </div>
</div>
"""
        
        # 构建反馈列表
        feedbacks_html = ""
        for feedback in feedbacks:
            feedbacks_html += self.build_single_feedback_html(feedback)
        
        return filter_html + stats_html + feedbacks_html
    
    def _build_empty_list_html(self):
        """构建空列表的 HTML"""
        return """
<div style="padding: 30px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #333; font-size: 16px; font-weight: bold; margin-bottom: 8px;">暂无反馈</div>
    <div style="color: #666; font-size: 14px;">还没有任何反馈提交</div>
</div>
"""
    
    def build_help_html(self):
        """构建帮助信息的 HTML"""
        categories_html = "、".join(self.categories)
        
        return f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">提交反馈</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈 <类别> <内容>
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">查看列表</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈列表 [类别] [状态]
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">修改状态</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈状态 <编号> <状态>
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">支持的类别</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            {categories_html}
        </div>
    </div>
    
    <div>
        <strong style="color: #333; font-size: 14px;">支持的状态</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            <span style="background: #fff3e0; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">pending</span>
            <span style="background: #e3f2fd; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">processing</span>
            <span style="background: #e8f5e9; padding: 2px 6px; border-radius: 4px;">completed</span>
        </div>
    </div>
</div>
"""
    
    def build_success_html(self, feedback_id, category):
        """构建提交成功的 HTML"""
        return f"""
<div style="padding: 16px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 18px; font-weight: bold; margin-bottom: 12px;">反馈已提交成功</div>
    <div style="color: #666; font-size: 14px; margin-bottom: 8px;">
        编号: {feedback_id}<br>
        类别: {category}<br>
        状态: 待处理
    </div>
</div>
"""
    
    def build_status_update_html(self, feedback_id, old_status, new_status):
        """构建状态更新的 HTML"""
        status_text = {
            "pending": "待处理",
            "processing": "处理中",
            "completed": "已完成"
        }
        
        return f"""
<div style="padding: 16px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈状态已更新</div>
    <div style="color: #666; font-size: 14px; margin-bottom: 8px;">
        反馈编号: {feedback_id}
    </div>
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 12px;">
        <span style="background: #f5f5f5; padding: 4px 10px; border-radius: 4px; font-size: 13px;">{status_text.get(old_status, old_status)}</span>
        <span style="font-size: 16px; color: #999;">→</span>
        <span style="background: #e8f5e9; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: bold;">{status_text.get(new_status, new_status)}</span>
    </div>
</div>
"""