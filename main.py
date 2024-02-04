from flask import Flask, render_template, request, redirect, url_for
import socket
import json
from datetime import datetime
import threading
import os

app = Flask(__name__)

# Шлях для зберігання файлу data.json
DATA_DIR = "storage"
JSON_FILE_PATH = os.path.join(DATA_DIR, "data.json")

# Перевірка існування каталогу та файлу data.json
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump({}, f)

# Функція для збереження даних в data.json
def save_to_json(data):
    with open(JSON_FILE_PATH, 'r+') as json_file:
        file_data = json.load(json_file)
        file_data.update(data)
        json_file.seek(0)
        json.dump(file_data, json_file, indent=2)
        json_file.truncate()

# Функція для обробки даних, отриманих через UDP
def handle_udp_data():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', 5000))
        print('Socket server listening on port 5000...')
        while True:
            data, _ = s.recvfrom(1024)
            data_dict = json.loads(data.decode())
            save_to_json(data_dict)

# Запускаємо сервер для обробки UDP-запитів у окремому потоці
udp_thread = threading.Thread(target=handle_udp_data)
udp_thread.start()

# Роутинг для головної сторінки
@app.route('/')
def index():
    return render_template('index.html')

# Роутинг для сторінки з формою
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']

        # Відправка даних на сервер через UDP
        send_to_socket(username, message_text)

        return redirect(url_for('index'))

    return render_template('message.html')

# Роутинг для обробки помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Функція для відправки даних на сервер через UDP
def send_to_socket(username, message_text):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        current_time: {
            "username": username,
            "message": message_text
        }
    }
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(data).encode(), ('localhost', 5000))

# Запуск веб-додатка
if __name__ == '__main__':
    app.run(port=3000)
