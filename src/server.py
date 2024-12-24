import socket
import threading
import mysql.connector

# 服务器配置
HOST = 'localhost'
PORT = 12345

# 连接到数据库
db = mysql.connector.connect(
    host="localhost",
    user="Haerxile",
    password="200518",
    database="COMM"
)
cursor = db.cursor()

# 存储客户端连接
clients = {}
usernames = {}

def handle_client(conn, addr):
    print(f"新的连接来自 {addr}")
    try:
        while True:
            # 接收消息长度
            msg_length = conn.recv(4)
            if not msg_length:
                break
            msg_length = int.from_bytes(msg_length, byteorder='big')
            # 接收实际消息
            msg = conn.recv(msg_length).decode()
            print(f"收到消息: {msg} 来自 {addr}")
            
            # 解析消息（假设使用JSON格式）
            import json
            data = json.loads(msg)
            action = data.get("action")
            
            if action == "login":
                username = data.get("username")
                password = data.get("password")
                # 验证用户
                cursor.execute("SELECT idUserInfo, is_admin FROM UserInfo WHERE username = %s AND passwoord = %s", (username, password))
                user = cursor.fetchone()
                if user:
                    user_id, is_admin = user
                    usernames[user_id] = conn
                    response = {"status": "success", "user_id": user_id, "is_admin": is_admin}
                else:
                    response = {"status": "fail", "message": "用户名或密码错误"}
                send_message(conn, response)
            
            elif action == "send_message":
                sender_id = data.get("sender_id")
                chat_id = data.get("chat_id")
                content = data.get("content")
                # 插入消息到数据库
                cursor.execute("INSERT INTO ChatMessages (idBoardList, sender_id, content, timestamp) VALUES (%s, %s, %s, NOW())", (chat_id, sender_id, content))
                db.commit()
                # 转发消息给所有参与该聊天的用户
                cursor.execute("SELECT user_id FROM UserAnnounceDiagram WHERE announce_id = %s", (chat_id,))
                participants = cursor.fetchall()
                for participant in participants:
                    pid = participant[0]
                    if pid in usernames:
                        response = {
                            "action": "receive_message",
                            "sender_id": sender_id,
                            "content": content,
                            "timestamp": "NOW()"
                        }
                        send_message(usernames[pid], response)
            
            # 其他操作如注册、关注等可在此扩展

    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()
        # 清理用户
        for uid, connection in usernames.items():
            if connection == conn:
                del usernames[uid]
                break
        print(f"{addr} 连接断开")

def send_message(conn, message):
    import json
    msg = json.dumps(message).encode()
    msg_length = len(msg).to_bytes(4, byteorder='big')
    conn.sendall(msg_length + msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"服务器启动，监听 {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        server.close()
        cursor.close()
        db.close()

if __name__ == "__main__":
    start_server()

