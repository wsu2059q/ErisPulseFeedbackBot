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
            # 第一步：选择类别
            categories = self.bot.config["categories"]
            categories_menu = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])
            
            prompt_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">提交反馈</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请选择反馈类别：</div>
    <div style="color: #333; font-size: 13px; background: #f5f5f5; padding: 10px; border-radius: 6px;">
        {categories_menu}
    </div>
    <div style="color: #999; font-size: 12px; margin-top: 8px;">回复序号或类别名称（60秒内有效）</div>
</div>
"""
            await self.send_message(event, prompt_html)
            
            # 等待用户选择类别
            category_reply = await event.wait_reply(timeout=60)
            if not category_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消提交</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            category_input = category_reply.get_text().strip()
            
            # 解析类别选择
            category = None
            # 尝试数字选择
            try:
                index = int(category_input) - 1
                if 0 <= index < len(categories):
                    category = categories[index]
            except ValueError:
                # 尝试直接匹配类别名称
                if category_input in categories:
                    category = category_input
            
            if not category:
                error_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">无效的类别</div>
    <div style="color: #666; font-size: 13px;">请重新使用 /反馈 命令提交</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            # 第二步：输入内容
            content_prompt_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">已选择类别：{category}</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请输入反馈内容（500字以内）：</div>
    <div style="color: #999; font-size: 12px;">回复取消可终止提交（120秒内有效）</div>
</div>
"""
            await self.send_message(event, content_prompt_html)
            
            # 等待用户输入内容
            content_reply = await event.wait_reply(timeout=120)
            if not content_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消提交</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            content = content_reply.get_text().strip()
            
            # 检查是否取消
            if content.lower() in ["取消", "cancel", "exit"]:
                cancel_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">已取消提交</div>
</div>
"""
                await self.send_message(event, cancel_html)
                return
            
            # 验证内容长度
            if len(content) > 500:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">内容过长</div>
    <div style="color: #666; font-size: 13px;">反馈内容不能超过500字，请重新使用 /反馈 命令提交</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            if not content:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">内容为空</div>
    <div style="color: #666; font-size: 13px;">请输入反馈内容，请重新使用 /反馈 命令提交</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            # 提交反馈
            feedback_id = await self.bot.submit_feedback(
                event.get_user_id(),
                event.get_user_nickname() or "未知用户",
                category,
                content,
                event.get_group_id()
            )
            
            # 发送成功消息
            success_html = self.builder.build_success_html(feedback_id, category)
            await self.send_message(event, success_html)
        
        @command("反馈列表", help="查看反馈列表")
        async def feedback_list_command(event):
            # 第一步：选择类别筛选
            categories = self.bot.config["categories"]
            categories_list = "、".join(categories)
            
            category_prompt_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">查看反馈列表</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请选择类别筛选：</div>
    <div style="color: #333; font-size: 13px; background: #f5f5f5; padding: 10px; border-radius: 6px;">
        支持的类别: {categories_list}
    </div>
    <div style="color: #999; font-size: 12px; margin-top: 8px;">输入类别名称或直接回车跳过筛选（60秒内有效）</div>
</div>
"""
            await self.send_message(event, category_prompt_html)
            
            # 等待用户选择类别
            category_reply = await event.wait_reply(timeout=60)
            if not category_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消查询</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            category_input = category_reply.get_text().strip()
            
            # 解析类别（直接回车则为None）
            category = None
            if category_input and category_input in categories:
                category = category_input
            elif category_input:
                # 尝试数字选择
                try:
                    index = int(category_input) - 1
                    if 0 <= index < len(categories):
                        category = categories[index]
                except ValueError:
                    pass
            
            # 第二步：选择状态筛选
            status_menu = "1. 待处理\n2. 处理中\n3. 已完成"
            
            status_prompt_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">类别筛选: {category if category else '全部'}</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请选择状态筛选：</div>
    <div style="color: #333; font-size: 13px; background: #f5f5f5; padding: 10px; border-radius: 6px;">
        {status_menu}
    </div>
    <div style="color: #999; font-size: 12px; margin-top: 8px;">输入序号、状态名称或直接回车跳过筛选（60秒内有效）</div>
</div>
"""
            await self.send_message(event, status_prompt_html)
            
            # 等待用户选择状态
            status_reply = await event.wait_reply(timeout=60)
            if not status_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消查询</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            status_input = status_reply.get_text().strip()
            
            # 解析状态（直接回车则为None）
            status = None
            status_map = {
                "1": "pending",
                "待处理": "pending",
                "2": "processing",
                "处理中": "processing",
                "3": "completed",
                "已完成": "completed"
            }
            
            if status_input:
                status = status_map.get(status_input)
            
            # 第三步：查询并显示列表
            feedbacks = await self.bot.list_feedbacks(category, status, event.get_group_id())
            list_html = self.builder.build_feedback_list_html(feedbacks, category, status)
            await self.send_message(event, list_html)
        
        @command("反馈状态", help="修改反馈状态（提交者或管理员）")
        async def feedback_status_command(event):
            # 第一步：输入反馈编号
            id_prompt_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">修改反馈状态</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请输入要修改的反馈编号：</div>
    <div style="color: #999; font-size: 12px;">例如: feedback_000001（60秒内有效）</div>
</div>
"""
            await self.send_message(event, id_prompt_html)
            
            # 等待用户输入反馈编号
            id_reply = await event.wait_reply(timeout=60)
            if not id_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消操作</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            feedback_id = id_reply.get_text().strip()
            
            # 验证反馈是否存在
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
            
            # 验证权限
            if not (event.get_user_id() == feedback_data["user_id"] or self.bot.is_admin(event.get_user_id())):
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">权限不足</div>
    <div style="color: #666; font-size: 13px;">仅提交者或管理员可修改</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            # 显示当前反馈信息
            current_status = feedback_data["status"]
            status_text_map = {
                "pending": "待处理",
                "processing": "处理中",
                "completed": "已完成"
            }
            current_status_text = status_text_map.get(current_status, current_status)
            
            feedback_info_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">反馈信息</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 4px;">编号: {feedback_id}</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 4px;">当前状态: {current_status_text}</div>
</div>
"""
            await self.send_message(event, feedback_info_html)
            
            # 第二步：选择新状态
            status_menu = "1. 待处理\n2. 处理中\n3. 已完成"
            
            status_prompt_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">请选择新状态：</div>
    <div style="color: #333; font-size: 13px; background: #f5f5f5; padding: 10px; border-radius: 6px;">
        {status_menu}
    </div>
    <div style="color: #999; font-size: 12px; margin-top: 8px;">输入序号或状态名称（60秒内有效）</div>
</div>
"""
            await self.send_message(event, status_prompt_html)
            
            # 等待用户选择状态
            status_reply = await event.wait_reply(timeout=60)
            if not status_reply:
                timeout_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">操作超时，已取消操作</div>
</div>
"""
                await self.send_message(event, timeout_html)
                return
            
            status_input = status_reply.get_text().strip()
            
            # 解析状态选择
            status_map = {
                "1": "pending",
                "待处理": "pending",
                "2": "processing",
                "处理中": "processing",
                "3": "completed",
                "已完成": "completed"
            }
            
            new_status = status_map.get(status_input)
            if not new_status or new_status not in ["pending", "processing", "completed"]:
                error_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">无效的状态</div>
    <div style="color: #666; font-size: 13px;">请重新使用 /反馈状态 命令操作</div>
</div>
"""
                await self.send_message(event, error_html)
                return
            
            # 如果状态没有改变
            if new_status == current_status:
                info_html = """
<div style="padding: 12px; background: #ffffff; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">状态未发生变化</div>
</div>
"""
                await self.send_message(event, info_html)
                return
            
            # 第三步：确认操作
            new_status_text = status_text_map.get(new_status, new_status)
            confirm_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认操作</div>
    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">
        确认将反馈 {feedback_id} 的状态从 {current_status_text} 改为 {new_status_text} 吗？
    </div>
    <div style="color: #999; font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>
"""
            await self.send_message(event, confirm_html)
            
            # 等待确认
            confirm_reply = await event.wait_reply(timeout=30)
            if confirm_reply and confirm_reply.get_text().lower() in ["是", "yes", "y"]:
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
            categories_html = "、".join(self.bot.config["categories"])
            
            help_html = f"""
<div style="padding: 12px; background: #ffffff; border-radius: 8px;">
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">提交反馈</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈
        </div>
        <div style="color: #999; font-size: 12px; margin-top: 4px;">
            按提示选择类别并输入内容
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">查看列表</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈列表
        </div>
        <div style="color: #999; font-size: 12px; margin-top: 4px;">
            按提示选择类别和状态筛选条件
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="color: #333; font-size: 14px;">修改状态</strong>
        <div style="color: #666; font-size: 13px; margin-top: 4px;">
            用法: /反馈状态
        </div>
        <div style="color: #999; font-size: 12px; margin-top: 4px;">
            按提示输入反馈编号并选择新状态
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
            <span style="background: #fff3e0; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">待处理</span>
            <span style="background: #e3f2fd; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">处理中</span>
            <span style="background: #e8f5e9; padding: 2px 6px; border-radius: 4px;">已完成</span>
        </div>
    </div>
</div>
"""
            await self.send_message(event, help_html)
