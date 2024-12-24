import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import mysql.connector
import time
import atexit

# 其他导入保持不变

# 全局变量用于存储socket客户端对象和连接状态
client_socket = None
receive_thread = None
connected = False

# 用户登录信息
current_user_id = None
current_username = None

def connect_to_server():
    global client_socket, connected
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))  # 服务器地址和端口
        connected = True
        print("成功连接到服务器")
        # 启动接收线程
        receive_thread = threading.Thread(target=receive_messages, daemon=True)
        receive_thread.start()
    except Exception as e:
        print(f"无法连接到服务器: {e}")
        messagebox.showerror("连接错误", f"无法连接到服务器: {e}")

def receive_messages():
    global connected
    try:
        while connected:
            # 接收消息长度
            msg_length_data = client_socket.recv(4)
            if not msg_length_data:
                break
            msg_length = int.from_bytes(msg_length_data, byteorder='big')
            # 接收实际消息
            msg_data = client_socket.recv(msg_length).decode()
            message = json.loads(msg_data)
            handle_server_message(message)
    except Exception as e:
        print(f"接收消息错误: {e}")
    finally:
        client_socket.close()
        connected = False
        print("与服务器的连接已关闭")

def handle_server_message(message):
    action = message.get("action")
    if action == "receive_message":
        sender_id = message.get("sender_id")
        content = message.get("content")
        timestamp = message.get("timestamp")
        # 更新聊天窗口
        # 假设有一个全局 ChatroomGUI 实例
        if app.board.chatroom:
            app.board.chatroom.display_message(content=content, sender_id=sender_id, timestamp=timestamp)
    elif action == "login":
        status = message.get("status")
        if status == "success":
            global current_user_id, current_username
            current_user_id = message.get("user_id")
            is_admin = message.get("is_admin")
            current_username = app.login_gui.username_entry.get()
            app.login_success()
        else:
            error_msg = message.get("message")
            app.login_gui.show_temporary_message("登录失败", error_msg)
    # 处理其他类型的消息

def send_message_to_server(message):
    try:
        msg = json.dumps(message).encode()
        msg_length = len(msg).to_bytes(4, byteorder='big')
        client_socket.sendall(msg_length + msg)
    except Exception as e:
        print(f"发送消息错误: {e}")
        messagebox.showerror("发送错误", f"发送消息失败: {e}")

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
        temp_window.after(3000, temp_window.destroy)
        
    def login(self):
        # 登录的逻辑
        username_or_email = self.username_entry.get()
        password = self.password_entry.get()
        
        if not connected:
            self.show_temporary_message("连接错误", "无法连接到服务器")
            return
        
        # 发送登录请求到服务器
        login_request = {
            "action": "login",
            "username": username_or_email,
            "password": password
        }
        send_message_to_server(login_request)
        
    def register(self):
        # 注册的逻辑保持不变
        # 这里可以选择通过服务器处理注册，而不是直接操作数据库
        pass
    
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
        
        self.announcements = []
        self.chatroom = None  # 添加一个属性用于存储当前聊天室
        # 初始显示所有公告
        self.show_all_announcements()
        
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
        
        # 从服务器获取公告数据
        # 这里需要实现从服务器请求公告数据的逻辑
        # 暂时使用本地数据库
        # 你可以将公告数据也通过网络发送
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
        
        # 从服务器获取我加入的公告数据
        cursor.execute("""
            SELECT b.idBoardList, b.headline, b.college, b.deadline, b.join_num, b.proposer_name, b.type 
            FROM BoardList b
            JOIN UserAnnounceDiagram uad ON b.idBoardList = uad.announce_id
            WHERE uad.user_id = %s
        """, (current_user_id,))
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
    
    def publish(self):
        # 发布公告的逻辑保持不变
        pass

class ChatroomGUI:
    def __init__(self, master, chat_id=1):
        self.master = master
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
            # 假设 timestamp 是字符串
            time_diff = time.time() - time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
            if time_diff < 60:
                time_str = "刚刚"
            elif time_diff < 3600:
                time_str = f"{int(time_diff // 60)}分钟前"
            elif time_diff < 86400:
                time_str = f"{int(time_diff // 3600)}小时前"
            else:
                time_str = timestamp
        else:
            time_str = ""
        time_label = tk.Label(info_frame, text=time_str, font=('微软雅黑', 8), anchor='w')
        time_label.pack(fill='x')
        
        # 显示消息内容
        message_label = tk.Label(message_frame, text=message, font=('微软雅黑', 12), wraplength=700, justify='left')
        message_label.pack(side='left', fill='x', expand=True)
        
        if sender_id == current_user_id:
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
        content = self.message_entry.get("1.0", tk.END).strip()
        if content and connected and current_user_id:
            message = {
                "action": "send_message",
                "sender_id": current_user_id,
                "chat_id": self.chat_id,
                "content": content
            }
            send_message_to_server(message)
            self.display_message(content=content, sender_id=current_user_id, sender_name=current_username, timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))
            self.message_entry.delete("1.0", tk.END)
        elif not connected:
            self.show_temporary_message("发送失败", "未连接到服务器")
    
    def send_message_on_enter(self, event):
        # 调用发送消息方法，忽略事件对象
        self.send_message()
    
    def run(self):
        self.load_recent_messages()
        self.master.mainloop()
    
    def load_recent_messages(self):
        # 从服务器加载消息
        # 需要实现从服务器请求消息的逻辑
        pass
    
    def refresh_older_messages(self):
        # 从服务器加载更早的消息
        pass

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.login_gui = LoginGUI(root)
        self.board = None  # 初始化公告板为空
    
    def login_success(self):
        self.login_gui.master.withdraw()
        self.board = BoardGUI(ttk.Window())
        self.board.master.mainloop()

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
    
    # 初始化数据库数据（保持不变）
    # ...

    # 在程序结束时删除测试数据
    # 保持不变
    
    # 连接到服务器
    connect_to_server()
    
    # 创建主窗口，显示登录界面
    root = ttk.Window()
    style = ttk.Style()
    style.theme_use('')
    
    app = LoginApp(root)
    root.mainloop()
    
    # 关闭数据库连接
    cursor.close()
    db.close()
