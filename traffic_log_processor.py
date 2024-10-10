import re

import mysql.connector
from datetime import datetime

# Настройки подключения к базе данных
DB_NAME = "traffic_accounting"
DB_USER = "root"
DB_PASSWORD = " "
DB_HOST = "localhost"
DB_PORT = "3306"

# Путь к файлу логов
LOG_FILE_PATH = "/var/log/iptables.log"

# Размер батча для вставки
BATCH_SIZE = 5000  # Настроить по мере необходимости


# Регулярное выражение для парсинга строк логов
log_regex = re.compile(r"""
    (?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+        # Дата и время
    \S+\s+kernel:\s+IPTables-Forward-(?P<direction>In|Out):\s+  # Направление (In/Out)
    IN=\S+\s+OUT=\S+\s+
    MAC=\S+\s+
    SRC=(?P<src_ip>\d+\.\d+\.\d+\.\d+)\s+            # Источник IP
    DST=(?P<dst_ip>\d+\.\d+\.\d+\.\d+)\s+            # Назначение IP
    LEN=(?P<packet_length>\d+)\s+                    # Длина пакета
""", re.VERBOSE)

# Функция для подключения к базе данных
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        print("Успешное подключение к базе данных.")
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для парсинга строк логов
def parse_log_line(log_line):
    match = log_regex.search(log_line)
    if match:
        log_data = match.groupdict()
        current_year = datetime.now().year  # Получаем текущий год
        log_data['timestamp'] = datetime.strptime(f"{current_year} {log_data['timestamp']}", '%Y %b %d %H:%M:%S')
        return log_data
    return None

# Функция для пакетной записи логов в базу данных
def save_batch_to_db(batch):
    conn = connect_to_db()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            for log in batch:
                print(f"Обрабатывается лог: {log}")  # Логируем каждый лог
                # Проверка на наличие IP в таблице users
                cursor.execute("SELECT id FROM users WHERE src_ip = %s", (log['src_ip'],))
                user_id = cursor.fetchone()

                # Если IP нет, добавляем его в users
                if not user_id:
                    cursor.execute("INSERT INTO users (src_ip) VALUES (%s)", (log['src_ip'],))
                    conn.commit()  # Зафиксировать вставку
                    user_id = cursor.lastrowid  # Получить последний ID
                else:
                    user_id = user_id[0]

                # Добавляем лог в таблицу traffic_logs
                cursor.execute("""
                    INSERT INTO traffic_logs (src_ip, dst_ip, ts, packet_length)
                    VALUES (%s, %s, %s, %s)
                """, (log['src_ip'], log['dst_ip'], log['timestamp'], log['packet_length']))

            # Фиксация транзакции после записи всех логов из батча
            conn.commit()
            print(f"Успешно сохранено {len(batch)} логов в базе данных.")
    except Exception as e:
        print(f"Ошибка при записи в базу данных: {e}")
    finally:
        conn.close()

# Функция для обработки файла логов с батчами
def process_log_file():
    logs_batch = []
    remaining_logs = []  # Список для хранения оставшихся логов
    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            for log_line in log_file:
                log_data = parse_log_line(log_line)
                if log_data:
                    logs_batch.append(log_data)
                else:
                    remaining_logs.append(log_line)  # Сохраняем строки, которые не удалось распарсить

                # Если размер батча достиг BATCH_SIZE, сохраняем батч
                if len(logs_batch) >= BATCH_SIZE:
                    save_batch_to_db(logs_batch)
                    logs_batch.clear()  # Очищаем батч после вставки

            # Сохранение оставшихся логов, если они не были сохранены
            if logs_batch:
                save_batch_to_db(logs_batch)

    except FileNotFoundError:
        print(f"Файл {LOG_FILE_PATH} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла логов: {e}")

    # Запись оставшихся логов обратно в файл
    write_remaining_logs(remaining_logs)

# Функция для записи оставшихся логов обратно в файл
def write_remaining_logs(remaining_logs):
    with open(LOG_FILE_PATH, 'w') as log_file:
        for log in remaining_logs:
            log_file.write(log)
    print(f"Оставшиеся логи записаны обратно в файл: {LOG_FILE_PATH}")

# Основная функция
if __name__ == "__main__":
    process_log_file()
