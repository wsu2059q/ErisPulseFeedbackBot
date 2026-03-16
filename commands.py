from ErisPulse.Core.Event import command


class FeedbackCommands:
    
    def __init__(self, bot, builder):
        self.bot = bot
        self.builder = builder
    
    async def send_message(self, event, message):
        platform = event.get_platform()
        supported_methods = self.bot.sdk.adapter.list_sends(platform)
        
        if "Html" in supported_methods:
            await event.reply(message, method="Html")
        elif "Markdown" in supported_methods:
            md_message = message.replace("<b>", "**").replace("</b>", "**")
            md_message = md_message.replace("<i>", "*").replace("</i>", "*")
            md_message = md_message.replace("<br>", "\n")
            md_message = md_message.replace("<div>", "\n").replace("</div>", "\n")
            md_message = md_message.replace("<strong>", "**").replace("</strong>", "**")
            md_message = md_message.replace("<code>", "`").replace("</code>", "`")
            await event.reply(md_message, method="Markdown")
        else:
            # 纯文本模式
            text = message.replace("<br>", "\n").replace("<div>", "\n").replace("</div>", "\n")
            text = text.replace("<b>", "").replace("</b>", "")
            text = text.replace("<strong>", "").replace("</strong>", "")
            text = text.replace("<i>", "").replace("</i>", "")
            text = text.replace("<code>", "").replace("</code>", "")
            text = text.replace("<ul>", "").replace("</ul>", "")
            text = text.replace("<li>", "• ").replace("</li>", "")
            text = text.replace("<span", "").replace("</span>", "")
            # 移除所有HTML标签
            import re
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\n+', '\n', text).strip()
            await event.reply(text, method="Text")
    
    async def register_commands(self):
        
        @command("反馈", help="提交反馈（功能、优化、建议、bug）")
        async def feedback_command(event):
            args = event.get_command_args()
            
            if len(args) < 2:
                categories = "、".join(self.bot.config["categories"])
                help_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #e65100; font-size: 14px; font-weight: bold; margin-bottom: 8px;">用法错误</div>
    <div style="color: #666; font-size: 13px;">
        用法: /反馈 <类别> <内容>
    </div>
    <div style="color: #666; font-size: 13px; margin-top: 8px;">
        支持的类别: {categories}
    </div>
</div>
"""
                await self.send_message(event, help_html)
                return
            
            category = args[0]
            content = " ".join(args[1:])
            
            if len(content) > 500:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">内容过长</div>
    <div style="color: #666; font-size: 13px;">反馈内容不能超过500字</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            feedback_id = await self.bot.submit_feedback(
                event.get_user_id(),
                event.get_user_nickname() or "未知用户",
                category,
                content,
                event.get_group_id()
            )
            
            success_html = self.builder.build_success_html(feedback_id, category)
            await self.send_message(event, success_html)
        
        @command("反馈列表", help="查看反馈列表")
        async def feedback_list_command(event):
            args = event.get_command_args()
            category = args[0] if len(args) > 0 else None
            status = args[1] if len(args) > 1 else None
            
            feedbacks = await self.bot.list_feedbacks(category, status, event.get_group_id())
            list_html = self.builder.build_feedback_list_html(feedbacks, category, status)
            await self.send_message(event, list_html)
        
        @command("反馈状态", help="修改反馈状态（提交者或管理员）")
        async def feedback_status_command(event):
            args = event.get_command_args()
            
            if len(args) < 2:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #e65100; font-size: 14px; font-weight: bold; margin-bottom: 8px;">用法错误</div>
    <div style="color: #666; font-size: 13px;">
        用法: /反馈状态 <编号> <状态>
    </div>
    <div style="color: #666; font-size: 13px; margin-top: 8px;">
        支持的状态: pending, processing, completed
    </div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            feedback_id = args[0]
            new_status = args[1]
            
            if new_status not in ["pending", "processing", "completed"]:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">无效的状态</div>
    <div style="color: #666; font-size: 13px;">支持的状态: pending, processing, completed</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            feedback_data = self.bot.get_feedback(feedback_id)
            if not feedback_data:
                error_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">找不到反馈</div>
    <div style="color: #666; font-size: 13px;">反馈编号 {feedback_id} 不存在</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            if not (event.get_user_id() == feedback_data["user_id"] or self.bot.is_admin(event.get_user_id())):
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">权限不足</div>
    <div style="color: #666; font-size: 13px;">仅提交者或管理员可修改</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            # 构建确认消息
            status_text = {
                "pending": "待处理",
                "processing": "处理中",
                "completed": "已完成"
            }
            confirm_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认操作</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">
        确认将反馈 {feedback_id} 的状态改为 {status_text.get(new_status, new_status)} 吗？
    </div>
    <div style="color: #999; font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>
"""
            await self.send_message(event, confirm_html)
            
            reply = await event.wait_reply(timeout=30)
            if reply and reply.get_text().lower() in ["是", "yes", "y"]:
                old_status = feedback_data["status"]
                await self.bot.update_feedback_status(feedback_id, new_status)
                update_html = self.builder.build_status_update_html(feedback_id, old_status, new_status)
                await self.send_message(event, update_html)
            else:
                cancel_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">操作已取消</div>
</div>
"""
                await self.send_message(event, cancel_html)
        
        @command("反馈帮助", help="查看反馈系统帮助")
        async def feedback_help_command(event):
            help_html = self.builder.build_help_html()
            await self.send_message(event, help_html)