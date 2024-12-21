import webbrowser
import atexit

import socket  # 用于创建网络通信的socket
import threading  # 用于创建和管理线程
import tkinter as tk  # 用于创建GUI
from tkinter import messagebox  # 用于显示消息框
import ctypes  # 用于调用Windows API函数
import shelve  # 用于创建简单的持久化数据库
import pickle  # 用于序列化和反序列化Python对象
import os  # 用于操作系统功能，如文件路径操作
import appdirs  # 用于获取应用程序数据目录的库
import time  # 用于时间相关的功能
import mysql.connector  # 用于连接MySQL数据库

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 全局变量用于存储socket客户端对象和连接状态
client = None


class LoginGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("登录")
        self.master.geometry("300x400")
        self.register_window = None
        
        # 用户名/邮箱标签和输入框
        self.username_label = tk.Label(self.master, text="用户名/邮箱:")
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=5)
        
        # 密码标签和输入框
        self.password_label = tk.Label(self.master, text="密码:")
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)
        
        # 登录按钮
        self.login_button = tk.Button(self.master, text="登录", command=self.login)
        self.login_button.pack(pady=10)
        
        # 注册按钮
        self.register_button = tk.Button(self.master, text="注册", command=self.register)
        self.register_button.pack(pady=10)
        
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.master)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
        
    def login(self):
        # 登录的逻辑
        username_or_email = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM UserInfo WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        user = cursor.fetchone()
        if user:
            if user[2] == password:  # Assuming the password is the third field in the UserInfo table
                self.show_temporary_message("登录成功", "登录成功")
                global is_login, user_id, user_name
                is_login = True
                user_id = user[0]
                user_name = user[1]         
                self.master.withdraw()
                board_window = ttk.Window()
                style = ttk.Style()
                style.theme_use('')
                board = BoardGUI(board_window, style)
            else:
                self.show_temporary_message("登录失败", "密码错误")
        else:
            self.show_temporary_message("登录失败", "用户不存在")
            self.register()
            
    def register(self):
        # 注册的逻辑
        register_window = tk.Toplevel(self.master)
        register_window.title("注册")
        register_window.geometry("300x600")
        self.register_window = register_window
        
        # 用户名标签和输入框
        username_label = tk.Label(register_window, text="用户名*:")
        username_label.pack(pady=10)
        username_entry = tk.Entry(register_window)
        username_entry.pack(pady=5)
        
        # 密码标签和输入框
        password_label = tk.Label(register_window, text="密码*:")
        password_label.pack(pady=10)
        password_entry = tk.Entry(register_window, show="*")
        password_entry.pack(pady=5)
        
        # 确认密码标签和输入框
        confirm_password_label = tk.Label(register_window, text="确认密码*:")
        confirm_password_label.pack(pady=10)
        confirm_password_entry = tk.Entry(register_window, show="*")
        confirm_password_entry.pack(pady=5)
        
        # 显示密码复选框
        show_password_var = tk.BooleanVar()
        show_password_check = tk.Checkbutton(register_window, text="显示密码", variable=show_password_var, command=lambda: self.toggle_password_visibility(password_entry, confirm_password_entry, show_password_var))
        show_password_check.pack(pady=5)
        
        # 邮箱标签和输入框
        email_label = tk.Label(register_window, text="邮箱:")
        email_label.pack(pady=10)
        email_entry = tk.Entry(register_window)
        email_entry.pack(pady=5)
        
        # 院系标签和输入框
        college_label = tk.Label(register_window, text="院系*:")
        college_label.pack(pady=10)
        college_entry = tk.Entry(register_window)
        college_entry.pack(pady=5)
        
        # 简介标签和输入框
        bio_label = tk.Label(register_window, text="简介:")
        bio_label.pack(pady=10)
        bio_entry = tk.Entry(register_window)
        bio_entry.pack(pady=5)
        
        # 注册按钮
        submit_button = tk.Button(register_window, text="提交", command=lambda: self.submit_registration(username_entry.get(), password_entry.get(), confirm_password_entry.get(), email_entry.get(), college_entry.get(), bio_entry.get()))
        submit_button.pack(pady=10)
        
    def toggle_password_visibility(self, password_entry, confirm_password_entry, show_password_var):
        if show_password_var.get():
            password_entry.config(show="")
            confirm_password_entry.config(show="")
        else:
            password_entry.config(show="*")
            confirm_password_entry.config(show="*")
        
    def submit_registration(self, username, password, confirm_password, email, college, bio):
        if not username or not password or not college:
            self.show_temporary_message("注册失败", "用户名、密码和院系不能为空")
            return
        if password != confirm_password:
            self.show_temporary_message("注册失败", "两次输入的密码不一致")
            return
        cursor.execute("SELECT * FROM UserInfo WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            self.show_temporary_message("注册失败", "用户名已存在")
            return
        else:
            cursor.execute("INSERT INTO UserInfo (username, passwoord, email, college, bio) VALUES (%s, %s, %s, %s, %s)", (username, password, email, college, bio))
            db.commit()
            self.show_temporary_message("注册成功", "注册成功，请登录")
            self.register_window.destroy()


class Announcement:
    def __init__(self, master, announcement_id, title, department, deadline, participants, initiator, announcement_type):
        self.frame = tk.Frame(master, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        
        # 标题
        self.title_label = tk.Label(self.frame, text=title, font=('微软雅黑', 14, 'bold'), anchor='w')
        self.title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        
        # 院系
        self.department_label = tk.Label(self.frame, text=department, font=('微软雅黑', 12), anchor='w')
        self.department_label.grid(row=1, column=1, sticky='w', pady=2)
        
        # 截止时间
        deadline_formatted = deadline.strftime('%Y-%m-%d %H:%M')
        self.deadline_label = tk.Label(self.frame, text=f"截止时间：{deadline_formatted}", font=('微软雅黑', 12), anchor='w', fg='black')
        self.deadline_label.grid(row=3, column=0, sticky='w', pady=2)
        
        # 参与人数
        self.participants_label = tk.Label(self.frame, text=f"参与人数: {participants}", font=('微软雅黑', 12), anchor='w')
        self.participants_label.grid(row=2, column=1, sticky='w', pady=2)
        
        # 发起人
        self.initiator_label = tk.Label(self.frame, text=f"by {initiator}", font=('微软雅黑', 12), anchor='w')
        self.initiator_label.grid(row=1, column=0, sticky='w', pady=2)
        
        # 公告类型
        self.announcement_type_label = tk.Label(self.frame, text=announcement_type, font=('微软雅黑', 12), anchor='w')
        self.announcement_type_label.grid(row=2, column=0, sticky='w', pady=2)
        
        # 详情按钮
        self.details_button = tk.Button(self.frame, text="查看详情", command=lambda: self.show_details(announcement_id=announcement_id, title=title))
        self.details_button.grid(row=3, column=1, pady=2, sticky='e')
        
        self.frame.grid(sticky='nsew')
        self.announcement_id = announcement_id
        
    def show_details(self, announcement_id, title):
        details_window = tk.Toplevel(self.frame)
        details_window.title("详情")
        details_window.geometry("600x400")
        
        details_label = tk.Label(details_window, text=f"公告标题: {title}", font=('微软雅黑', 12))
        details_label.pack(pady=20)
        
        # 从数据库中获取公告的具体内容
        cursor.execute("SELECT content FROM BoardList WHERE idBoardList = %s", (announcement_id,))
        content = cursor.fetchone()[0]
        
        content_label = tk.Label(details_window, text=f"公告内容: {content}", font=('微软雅黑', 12), wraplength=500, justify='left')
        content_label.pack(pady=10)
        
        # 判断是否已经加入群聊
        cursor.execute("SELECT * FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
        user_announcement = cursor.fetchone()
        
        if user_announcement:
            follow_button = tk.Button(details_window, text="取消关注", command=lambda: self.disfollow_announcement(user_id, announcement_id, details_window))
            follow_button.pack(pady=10)
            chatroom_frame = tk.Frame(details_window)
            chatroom_frame.pack(fill='both', expand=True)
            chatroom = ChatroomGUI(chat_id=announcement_id)
            chatroom.master = chatroom_frame
            chatroom.master.pack(fill='both', expand=True)
            chatroom.run()
        else:
            follow_button = tk.Button(details_window, text="关注该通知", command=lambda: self.follow_announcement(user_id, announcement_id, details_window))
            follow_button.pack(pady=10)
            
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.frame)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
            
    def follow_announcement(self, user_id, announcement_id, show_details_window):
        try:
            cursor.execute("INSERT INTO UserAnnounceDiagram (user_id, announce_id) VALUES (%s, %s)", (user_id, announcement_id))
            db.commit()
            self.show_temporary_message("关注成功", "关注成功")
            show_details_window.destroy()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("关注失败", f"关注失败: {err}")
            db.rollback()
            
    def disfollow_announcement(self, user_id, announcement_id, show_details_window):
        try:
            cursor.execute("DELETE FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
            db.commit()
            self.show_temporary_message("取消关注成功", "取消关注成功")
            show_details_window.destroy()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("取消关注失败", f"取消关注失败: {err}")
            db.rollback()
            

class BoardGUI:
    def __init__(self, master, style=None):
        self.master = master
        self.master.title("公告板")
        self.master.geometry("800x600")
        self.master.resizable(width=True, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 主题选择框
        theme_names = style.theme_names()
        theme_selection = ttk.Frame(self.master)
        theme_selection.pack(fill='x', pady=10)
        
        label = ttk.Label(theme_selection, text="主题:")
        label.pack(side='left', padx=5)
        
        theme_cbo = ttk.Combobox(
            master=theme_selection,
            text=style.theme.name,
            values=theme_names,
            state='readonly'
        )
        theme_cbo.pack(side='left', padx=5)
        theme_cbo.current(theme_names.index(style.theme.name))
        theme_cbo.bind("<<ComboboxSelected>>", lambda e: style.theme_use(theme_cbo.get()))
        
        # 刷新按钮
        self.refresh_button = tk.Button(theme_selection, text="刷新", command=self.show_all_announcements)
        self.refresh_button.pack(side='left', padx=5)
        
        # 发布公告按钮
        self.publish_button = tk.Button(theme_selection, text="发布公告", command=self.publish)
        self.publish_button.pack(side='left', padx=5)
        
        # 创建一个画布和滚动条
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定滚动事件
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        self.canvas.bind_all('<Button-4>', lambda event: self.canvas.yview_scroll(-1, "units"))  # For Linux
        self.canvas.bind_all('<Button-5>', lambda event: self.canvas.yview_scroll(1, "units"))  # For Linux
        
        # 标签页框架
        self.tab_frame = tk.Frame(self.master)
        self.tab_frame.pack(side='left', fill='y', pady=5)
        
        self.all_announcements_button = tk.Button(self.tab_frame, text="公告板", command=self.show_all_announcements)
        self.all_announcements_button.pack(side='top', expand=True, fill='x', pady=5, padx=20)
        
        self.my_announcements_button = tk.Button(self.tab_frame, text="我的", command=self.show_my_announcements)
        self.my_announcements_button.pack(side='top', expand=True, fill='x', pady=5, padx=20)
        
        self.current_tab = "all"
        self.highlight_current_tab()
        # 从数据库中获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 从 UserAnnounceDiagram 中更新 join_num
        for announcement in announcements_data:
            cursor.execute("SELECT COUNT(*) FROM UserAnnounceDiagram WHERE announce_id = %s", (announcement[0],))
            join_num = cursor.fetchone()[0]
            cursor.execute("UPDATE BoardList SET join_num = %s WHERE idBoardList = %s", (join_num, announcement[0]))
            db.commit()
        
        # 更新 join_num 后重新获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 创建公告对象列表
        self.announcements = []
        self.create_announcements(announcements_data)
        
    def create_announcements(self, announcements_data):
        def update_grid(event=None):
            width = self.master.winfo_width()
            columns = max(1, width // 400)  # 每列宽度约为400像素
            for i, announcement in enumerate(self.announcements):
                announcement.frame.grid(row=i // columns, column=i % columns, padx=10, pady=10, sticky='nsew')

        for announcement_data in announcements_data:
            announcement = Announcement(self.scrollable_frame, *announcement_data)
            self.announcements.append(announcement)

        self.master.bind('<Configure>', update_grid)
        update_grid()
    
    def refresh(self):
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        
        # 从数据库中获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 从 UserAnnounceDiagram 中更新 join_num
        for announcement in announcements_data:
            cursor.execute("SELECT COUNT(*) FROM UserAnnounceDiagram WHERE announce_id = %s", (announcement[0],))
            join_num = cursor.fetchone()[0]
            cursor.execute("UPDATE BoardList SET join_num = %s WHERE idBoardList = %s", (join_num, announcement[0]))
            db.commit()
        
        # 更新 join_num 后重新获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 创建新的公告对象列表
        self.create_announcements(announcements_data)
        
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.master)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
    
    def publish(self):
        # 发布公告的逻辑
        if not is_login:
            self.show_temporary_message("发布失败", "请先登录")
            return
        
        if not user_id:
            self.show_temporary_message("发布失败", "用户ID无效")
            return
        
        cursor.execute("SELECT is_admin FROM UserInfo WHERE idUserInfo = %s", (user_id,))
        is_admin = cursor.fetchone()[0]
        
        if not is_admin:
            self.show_temporary_message("发布失败", "只有管理员可以发布公告")
            return
        
        publish_window = tk.Toplevel(self.master)
        publish_window.title("发布公告")
        publish_window.geometry("400x800")
        
        # 标题标签和输入框
        title_label = tk.Label(publish_window, text="标题*:")
        title_label.pack(pady=10)
        title_entry = tk.Entry(publish_window)
        title_entry.pack(pady=5)
        
        # 院系标签和输入框
        college_label = tk.Label(publish_window, text="院系*:")
        college_label.pack(pady=10)
        college_entry = tk.Entry(publish_window)
        college_entry.pack(pady=5)
        
        # 截止时间标签和输入框
        deadline_label = tk.Label(publish_window, text="截止时间* (YYYY-MM-DD HH:MM:SS):")
        deadline_label.pack(pady=10)
        deadline_entry = tk.Entry(publish_window)
        deadline_entry.pack(pady=5)
        
        # 公告类型标签和输入框
        type_label = tk.Label(publish_window, text="公告类型*:")
        type_label.pack(pady=10)
        type_entry = tk.Entry(publish_window)
        type_entry.pack(pady=5)
        
        # 内容标签和输入框
        content_label = tk.Label(publish_window, text="内容*:")
        content_label.pack(pady=10)
        content_text = tk.Text(publish_window, height=10)
        content_text.pack(pady=5)
        
        # 提交按钮
        submit_button = tk.Button(publish_window, text="提交", command=lambda: self.submit_announcement(title_entry.get(), college_entry.get(), deadline_entry.get(), type_entry.get(), content_text.get("1.0", tk.END), publish_window))
        submit_button.pack(pady=10)
        
    def submit_announcement(self, title, college, deadline, announcement_type, content, publish_window):
        if not title or not college or not deadline or not announcement_type or not content.strip():
            self.show_temporary_message("发布失败", "所有字段均为必填项")
            return
        
        try:
            cursor.execute("INSERT INTO BoardList (headline, college, proposer_name, type, deadline, join_num, content) VALUES (%s, %s, %s, %s, %s, %s, %s)", (title, college, user_name, announcement_type, deadline, 0, content.strip()))
            db.commit()
            self.show_temporary_message("发布成功", "公告发布成功")
            publish_window.destroy()
            self.refresh()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("发布失败", f"发布失败: {err}")
            db.rollback()
    
    def on_closing(self):  
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.master.destroy()
            exit(0)
        else:
            pass
    
    def show_all_announcements(self):
        self.current_tab = "all"
        self.highlight_current_tab()
        self.refresh()
    
    def show_my_announcements(self):
        self.current_tab = "my"
        self.highlight_current_tab()
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        
        # 从数据库中获取我加入的公告数据
        cursor.execute("""
            SELECT b.idBoardList, b.headline, b.college, b.deadline, b.join_num, b.proposer_name, b.type 
            FROM BoardList b
            JOIN UserAnnounceDiagram uad ON b.idBoardList = uad.announce_id
            WHERE uad.user_id = %s
        """, (user_id,))
        announcements_data = cursor.fetchall()
        
        # 创建新的公告对象列表
        self.create_announcements(announcements_data)
    
    def highlight_current_tab(self):
        if self.current_tab == "all":
            self.all_announcements_button.config(relief="sunken", bg="lightblue")
            self.my_announcements_button.config(relief="raised", bg="SystemButtonFace")
        else:
            self.all_announcements_button.config(relief="raised", bg="SystemButtonFace")
            self.my_announcements_button.config(relief="sunken", bg="lightblue")

class ChatroomGUI:
    def __init__(self, chat_id=1):
        self.master = tk.Tk()
        self.master.title("聊天室")
        self.master.geometry("800x600")
        self.master.resizable(width=False, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        # 聊天记录框架
        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(fill='both', expand=True, pady=10)
        
        # 创建一个画布和滚动条
        self.canvas = tk.Canvas(self.chat_frame)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定滚动事件
        self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind_all('<Button-4>', self.on_mouse_wheel)  # For Linux
        self.canvas.bind_all('<Button-5>', self.on_mouse_wheel)  # For Linux

        # 消息输入框
        self.message_entry = tk.Text(self.master, font=('微软雅黑', 12), height=3, wrap='word')
        self.message_entry.pack(fill='x', pady=10)
        
        # 发送按钮
        self.send_button = tk.Button(self.master, text="发送", command=self.send_message)
        self.send_button.pack(side='right', padx=10, pady=10)
        
        # 绑定事件以自适应输入框高度
        self.message_entry.bind('<KeyRelease>', self.adjust_textbox_height)
            
        # 绑定回车键事件到 send_message 方法
        self.master.bind('<KeyPress-Return>', self.send_message_on_enter)
        
        # 初始化最旧的消息时间戳
        self.oldest_timestamp = time.time()
        self.chat_id = chat_id
        self.message_shown = []
    
    def adjust_textbox_height(self, event=None):
        lines = int(self.message_entry.index('end-1c').split('.')[0])
        self.message_entry.config(height=max(3, lines))
        
    def on_mouse_wheel(self, event):
        if event.delta > 0 and self.canvas.yview()[0] == 0.0:
            self.refresh_older_messages()
        else:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
    def display_message(self, message, sender_id, sender_name="我", timestamp=None):
        # 创建一个消息框架
        message_frame = tk.Frame(self.scrollable_frame, bd=2, relief=tk.SUNKEN, padx=5, pady=5, width=780)
        
        # 创建一个内部框架用于纵向排列发送者和时间
        info_frame = tk.Frame(message_frame)
        info_frame.pack(side='left', fill='y', padx=5)
        
        # 显示发送者
        sender_label = tk.Label(info_frame, text=sender_name, font=('微软雅黑', 10, 'bold'), anchor='w', fg='blue', cursor="hand2")
        sender_label.pack(fill='x')
        sender_label.bind("<Button-1>", lambda e: self.show_user_details(sender_id, sender_name))
        
        # 显示发送时间
        if timestamp:
            time_diff = time.time() - timestamp.timestamp()
            if time_diff < 60:
                time_str = "刚刚"
            elif time_diff < 3600:
                time_str = f"{int(time_diff // 60)}分钟前"
            elif time_diff < 86400:
                time_str = f"{int(time_diff // 3600)}小时前"
            else:
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = ""
        time_label = tk.Label(info_frame, text=time_str, font=('微软雅黑', 8), anchor='w')
        time_label.pack(fill='x')
        
        # 显示消息内容
        message_label = tk.Label(message_frame, text=message, font=('微软雅黑', 12), wraplength=700, justify='left')
        message_label.pack(side='left', fill='x', expand=True)
        
        if sender_id == user_id:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='e')
            message_frame.config(highlightbackground='blue', highlightthickness=2)
            info_frame.pack(side='right', fill='y', padx=5)
            message_label.config(justify='right')
            message_label.pack_configure(side='right')
        else:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='w')
            message_frame.config(highlightbackground='gray', highlightthickness=1)
            info_frame.pack(side='left', fill='y', padx=5)
            message_label.config(justify='left')
            message_label.pack_configure(side='left')
        
        # 滚动到最新消息
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
    def show_user_details(self, sender_id, sender_name):
        # 显示用户详情的逻辑
        cursor.execute("SELECT username, college, email, is_admin, bio FROM UserInfo WHERE idUserInfo = %s", (sender_id,))
        user_details = cursor.fetchone()
        
        if user_details:
            username, college, email, is_admin, bio = user_details
            
            user_details_window = tk.Toplevel(self.master)
            user_details_window.title("用户详情")
            user_details_window.geometry("400x300")
            
            # 创建一个框架用于放置用户信息
            details_frame = tk.Frame(user_details_window, bd=2, relief=tk.RIDGE, padx=10, pady=10)
            details_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # 用户名和管理员标签
            username_frame = tk.Frame(details_frame)
            username_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            username_title = tk.Label(username_frame, text=f"{username}", font=('微软雅黑', 14, 'bold'), fg='black')
            username_title.pack(side='left')
            if is_admin:
                admin_label = tk.Label(username_frame, text="管理员", font=('微软雅黑', 10), fg='red', bg='lightblue')
                admin_label.pack(side='left', padx=5)
            
            # 院系
            college_label = tk.Label(details_frame, text=f"{college}", font=('微软雅黑', 12), anchor='w')
            college_label.grid(row=1, column=0, sticky='w', pady=5)
            
            # 邮箱
            email_label = tk.Label(details_frame, text=f"{email}", font=('微软雅黑', 12), anchor='w')
            email_label.grid(row=1, column=1, sticky='w', pady=5)
            
            # 简介
            bio_label = tk.Label(details_frame, text=f"简介: {bio}", font=('微软雅黑', 12), wraplength=350, justify='left')
            bio_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)
        
    def send_message(self):
        # 发送消息的逻辑
        pass
    
    def send_message_on_enter(self, event):
        # 调用发送消息方法，忽略事件对象
        self.send_message()
    
    def run(self):
        self.load_recent_messages()
        self.master.mainloop()

    def load_recent_messages(self):
        # 获取最近一天的聊天记录
        cursor.execute("""
            SELECT sender_id, sender_name, content, timestamp 
            FROM ChatMessages 
            WHERE idBoardList = %s AND timestamp >= NOW() - INTERVAL 1 DAY 
            ORDER BY timestamp DESC
        """, (self.chat_id,))
        messages = cursor.fetchall()

        for message in reversed(messages):
            sender_id, sender_name, content, timestamp = message
            self.display_message(sender_id=sender_id, sender_name=sender_name, message=content, timestamp=timestamp)
            
        self.oldest_timestamp = messages[-1][3] if messages else time.time()
        print("已加载最近的消息")
        print("最旧的消息时间戳:", self.oldest_timestamp)
        self.message_shown.extend(messages)

    def refresh_older_messages(self):
        # 获取更早的聊天记录
        cursor.execute("""
            SELECT sender_id, sender_name, content, timestamp 
            FROM ChatMessages 
            WHERE idBoardList = %s AND timestamp < %s 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (self.chat_id, self.oldest_timestamp))
        messages = cursor.fetchall()
        self.message_shown.extend(messages)
        if messages:
            self.oldest_timestamp = messages[-1][3]
            current_scroll_position = self.canvas.yview()[0]
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            for message in reversed(self.message_shown):
                sender_id, sender_name, content, timestamp = message
                self.display_message(sender_id=sender_id, sender_name=sender_name, message=content, timestamp=timestamp)
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(current_scroll_position)
        
        print("已加载更早的消息")
        print("最旧的消息时间戳:", self.oldest_timestamp)
        return bool(messages)
    
# 主程序
if __name__ == "__main__":
    try:
        # 连接到数据库
        db = mysql.connector.connect(
            host="localhost",
            user="Haerxile",
            password="200518",
            database="COMM"
        )
        cursor = db.cursor()
        print("数据库连接成功！")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("数据库连接错误", f"无法连接到数据库: {err}")
        exit(1)
    
    # 插入测试数据

    test_data = [
        (1, "计算机科学讲座", "计算机学院", "Haerxile", "讲座", "2023-11-30 18:00:00", 50, "欢迎参加计算机科学讲座，了解最新的技术趋势和研究成果。"),
        (2, "英语角活动", "外国语学院", "Alice", "活动", "2023-12-01 15:00:00", 30, "加入我们的英语角活动，提升你的英语口语能力。"),
        (3, "数学竞赛报名", "数学学院", "Bob", "竞赛", "2023-12-05 23:59:59", 100, "数学竞赛报名开始了，展示你的数学才华，赢取丰厚奖品。"),
        (4, "物理实验室开放日", "物理学院", "Charlie", "开放日", "2023-12-10 10:00:00", 20, "物理实验室开放日，欢迎大家前来参观和体验最新的实验设备。"),
        (5, "化学实验安全培训", "化学学院", "David", "培训", "2023-12-15 14:00:00", 40, "化学实验安全培训，确保实验操作的安全性和规范性。"),
        (6, "生物科技创新大赛", "生物学院", "Eve", "竞赛", "2023-12-20 17:00:00", 60, "生物科技创新大赛，展示你的创新能力，赢取大奖。"),
        (7, "地理野外考察", "地理学院", "Frank", "考察", "2023-12-25 08:00:00", 25, "地理野外考察活动，亲身体验自然地理现象，提升实践能力。"),
        (8, "历史文化讲座", "历史学院", "Grace", "讲座", "2023-12-30 19:00:00", 35, "历史文化讲座，了解中华文明的悠久历史和文化底蕴。"),
        (9, "政治理论研讨会", "政治学院", "Heidi", "研讨会", "2024-01-05 16:00:00", 45, "政治理论研讨会，深入学习和探讨马克思主义理论和中国特色社会主义。"),
        (10, "心理健康讲座", "心理学院", "Ivan", "讲座", "2024-01-10 20:00:00", 55, "心理健康讲座，关注心理健康问题，提升心理素质。"),
        (11, "体育锻炼活动", "体育学院", "Judy", "活动", "2024-01-15 07:00:00", 65, "体育锻炼活动，锻炼身体，增强体质。"),
        (12, "音乐会演出", "音乐学院", "Mallory", "演出", "2024-01-20 21:00:00", 75, "音乐会演出，欣赏美妙的音乐，感受音乐的魅力。"),
        (13, "美术展览", "美术学院", "Niaj", "展览", "2024-01-25 13:00:00", 85, "美术展览，欣赏艺术作品，感受艺术的魅力。"),
        (14, "舞蹈表演", "舞蹈学院", "Olivia", "表演", "2024-01-30 22:00:00", 95, "舞蹈表演，富有激情和活力的舞蹈表演，绝对可以让你沉浸其中。"),
        (15, "戏剧演出", "戏剧学院", "Peggy", "演出", "2024-02-05 12:00:00", 105, "戏剧演出，精彩纷呈的戏剧表演，让你感受戏剧的魅力。"),
        (16, "电影放映", "电影学院", "Sybil", "放映", "2024-02-10 23:00:00", 115, "电影放映，欣赏经典电影，感受电影的魅力。")
    ]
    test_massage = [
        (1, 1, 1, "Haerxile", "大家好，欢迎参加计算机科学讲座！", "2023-11-01 10:00:00"),
        (2, 1, 2, "Alice", "很高兴能参加这个讲座，期待学习新知识。", "2023-11-01 10:05:00"),
        (3, 1, 3, "Bob", "计算机科学是一个非常有趣的领域。", "2023-11-01 10:10:00"),
        (4, 1, 4, "Charlie", "希望能在讲座中学到更多关于编程的知识。", "2023-11-01 10:15:00"),
        (5, 1, 5, "David", "我对人工智能特别感兴趣。", "2023-11-01 10:20:00"),
        (6, 1, 6, "Eve", "讲座的内容非常丰富，受益匪浅。", "2023-11-01 10:25:00"),
        (7, 1, 7, "Frank", "希望能有更多这样的讲座。", "2023-11-01 10:30:00"),
        (8, 1, 8, "Grace", "讲座的讲师非常专业。", "2023-11-01 10:35:00"),
        (9, 1, 9, "Heidi", "我对计算机网络有很多疑问，希望能在讲座中找到答案。", "2023-11-01 10:40:00"),
        (10, 1, 10, "Ivan", "讲座的互动环节非常有趣。", "2023-11-01 10:45:00"),
        (11, 1, 11, "Judy", "讲座的内容非常实用。", "2023-11-01 10:50:00"),
        (12, 1, 12, "Mallory", "希望能有更多关于编程语言的讲解。", "2023-11-01 10:55:00"),
        (13, 1, 13, "Niaj", "讲座的案例分析非常详细。", "2023-11-01 11:00:00"),
        (14, 1, 14, "Olivia", "讲座的PPT制作得非常精美。", "2023-11-01 11:05:00"),
        (15, 1, 15, "Peggy", "讲座的内容非常前沿。", "2023-11-01 11:10:00"),
        (16, 1, 16, "Sybil", "希望能有更多关于计算机安全的讲解。", "2023-11-01 11:15:00"),
        (17, 1, 1, "Haerxile", "讲座结束，感谢大家的参与！", "2024-12-22 0:20:00"),
        (18, 2, 1, "Haerxile", "大家好，欢迎参加英语角活动！", "2023-12-01 15:00:00"),
    ]
    test_user = [
        (1, "Haerxile", "123456", "工学院", "admin@outlook.com", 1, "I am a student of College of Engeering, and I love programming.", "./pic1.png"),
        (2, "Alice", "123456", "文学院", "alice@pku.edu.cn", 0, "我是文学院的学生，喜欢文学。", "./pic2.png"),
        (3, "Bob", "123456", "理学院", "bob@edu.cn", 0, "I am a student of College of Science, and I love math.", "./pic3.png"),
        (4, "Charlie", "123456", "法学院", "charlie@pku.edu.cn", 0, "我是法学院的学生，喜欢法律。", "./pic4.png"),
        (5, "David", "123456", "信息学院", "david@pku.edu.cn", 0, "我是信息学院的学生，喜欢计算机科学。", "./pic5.png"),
        (6, "Eve", "123456", "经济学院", "eve@pku.edu.cn", 0, "我是经济学院的学生，喜欢经济学。", "./pic6.png"),
        (7, "Frank", "123456", "管理学院", "frank@pku.edu.cn", 0, "我是管理学院的学生，喜欢管理学。", "./pic7.png"),
        (8, "Grace", "123456", "教育学院", "grace@pku.edu.cn", 0, "我是教育学院的学生，喜欢教育学。", "./pic8.png"),
        (9, "Heidi", "123456", "艺术学院", "heidi@pku.edu.cn", 0, "我是艺术学院的学生，喜欢艺术。", "./pic9.png"),
        (10, "Ivan", "123456", "体育学院", "ivan@pku.edu.cn", 0, "我是体育学院的学生，喜欢体育。", "./pic10.png"),
        (11, "Judy", "123456", "音乐学院", "judy@pku.edu.cn", 0, "我是音乐学院的学生，喜欢音乐。", "./pic11.png"),
        (12, "Mallory", "123456", "医学院", "mallory@pku.edu.cn", 0, "我是医学院的学生，喜欢医学。", "./pic12.png"),
        (13, "Niaj", "123456", "环境学院", "niaj@pku.edu.cn", 0, "我是环境学院的学生，喜欢环境科学。", "./pic13.png"),
        (14, "Olivia", "123456", "新闻学院", "olivia@pku.edu.cn", 0, "我是新闻学院的学生，喜欢新闻学。", "./pic14.png"),
        (15, "Peggy", "123456", "哲学院", "peggy@pku.edu.cn", 0, "我是哲学院的学生，喜欢哲学。", "./pic15.png"),
        (16, "Sybil", "123456", "心理学院", "sybil@pku.edu.cn", 0, "我是心理学院的学生，喜欢心理学。", "./pic16.png")
    ]
    test_Diagram = [(i, (i-1)//16+1, (i-1)%16+1) for i in range(1, 129)]

    # 插入数据前先清空表
    cursor.execute("DELETE FROM UserAnnounceDiagram")
    cursor.execute("DELETE FROM BoardList")
    cursor.execute("DELETE FROM ChatMessages")
    cursor.execute("DELETE FROM UserInfo")
    db.commit()

    # 插入测试数据
    for data in test_data:
        cursor.execute("INSERT INTO BoardList (idBoardList, headline, college, proposer_name, type, deadline, join_num, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data)
    for message in test_massage:
        cursor.execute("INSERT INTO ChatMessages (idChatMessages, idBoardList, sender_id, sender_name, content, timestamp) VALUES (%s, %s, %s, %s, %s, %s)", message)
    for user in test_user:
        cursor.execute("INSERT INTO UserInfo (idUserInfo, username, passwoord, college, email, is_admin, bio, profile_pictrue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", user)
    for diagram in test_Diagram:
        cursor.execute("INSERT INTO UserAnnounceDiagram (idUserAnnounceDiagram, user_id, announce_id) VALUES (%s, %s, %s)", diagram)
    db.commit()

    # 删除测试数据
    def delete_test_data():
        cursor.execute("DELETE FROM BoardList WHERE idBoardList IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)")
        cursor.execute("DELETE FROM ChatMessages WHERE idChatMessages IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)")
        cursor.execute("DELETE FROM UserInfo WHERE idUserInfo IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)")
        cursor.execute("DELETE FROM UserAnnounceDiagram WHERE idUserAnnounceDiagram IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)")
        db.commit()

    # 在程序结束时删除测试数据
    atexit.register(delete_test_data)
    
    print("数据插入成功！")
    
    # 创建主窗口，显示公告板，可更换主题
    is_login = False
    user_id = None
    user_name = None
    
    root = ttk.Window()
    style = ttk.Style()
    style.theme_use('')
    
    app = LoginGUI(root)
    root.mainloop()
    
    # 关闭数据库连接
    cursor.close()
    db.close()