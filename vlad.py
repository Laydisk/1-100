import tkinter as tk
import random
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

def establish_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',
            database='guess_number_db',
            user='root',
            password='55555'
        )
        if connection.is_connected():
            return connection
    except Error as exc:
        print(f"Ошибка: {exc}")
        return None

def setup_user_table():
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

def setup_results_table():
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                result INT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

def add_user(user, passwd):
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password) VALUES (%s, %s)
            """, (user, passwd))
            connection.commit()
            messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован!")
        except Error as exc:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрировать пользователя: {exc}")
        finally:
            cursor.close()
            connection.close()

def validate_user(user, passwd):
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s AND password = %s
        """, (user, passwd))
        user_record = cursor.fetchone()
        cursor.close()
        connection.close()

        if user_record:
            messagebox.showinfo("Успех", "Авторизация завершена успешно!")
            global current_user_id
            current_user_id = user_record[0]  # Сохранение ID пользователя в глобальную переменную
            main_window.destroy()
            launch_game()
        else:
            messagebox.showerror("Ошибка", "Неверные логин или пароль.")

def save_game_result(user_id, result):
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO game_results (user_id, result) VALUES (%s, %s)
            """, (user_id, result))
            connection.commit()
            print("Результат игры сохранен.")
        except Error as exc:
            print(f"Ошибка при сохранении результата: {exc}")
        finally:
            cursor.close()
            connection.close()

def registration():
    username = entry_username.get()
    password = entry_password.get()
    if username and password:
        add_user(username, password)
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")

def login_action():
    username = entry_username.get()
    password = entry_password.get()
    validate_user(username, password)

def launch_game():
    def start_game():
        target_number = random.randint(1, 100)
        attempts = 0

        def verify_guess():
            nonlocal attempts
            guess = int(entry_guess.get())
            attempts += 1
            if guess < target_number:
                messagebox.showinfo("Результат", "Ваше число слишком низкое!")
            elif guess > target_number:
                messagebox.showinfo("Результат", "Ваше число слишком высокое!")
            else:
                messagebox.showinfo("Поздравляем!", "Вы угадали число!")
                # Сохранение результата
                save_game_result(current_user_id, attempts)
                game_window.destroy()

        game_window = tk.Tk()
        game_window.title("Угадай число")
        game_window.geometry("300x200")

        tk.Label(game_window, text="Попробуйте угадать число от 1 до 100:").pack()
        entry_guess = tk.Entry(game_window)
        entry_guess.pack()

        button_check = tk.Button(game_window, text="Проверить", command=verify_guess)
        button_check.pack()

        game_window.mainloop()

    start_game()

if __name__ == "__main__":
    setup_user_table()  # Создание таблицы пользователей при запуске
    setup_results_table()
    main_window = tk.Tk()
    main_window.title("Авторизация")
    main_window.geometry("250x200")
    
    x = (main_window.winfo_screenwidth() - main_window.winfo_reqwidth()) / 2
    y = (main_window.winfo_screenheight() - main_window.winfo_reqheight()) / 2
    main_window.wm_geometry("+%d+%d" % (x, y))

    tk.Label(main_window, text="Введите логин:").pack()
    entry_username = tk.Entry(main_window)
    entry_username.pack()

    tk.Label(main_window, text="Введите пароль:").pack()
    entry_password = tk.Entry(main_window, show='*')
    entry_password.pack()

    button_login = tk.Button(main_window, text="Войти", command=login_action)  # кнопка входа
    button_login.pack()

    button_register = tk.Button(main_window, text="Зарегистрироваться", command=registration)  # кнопка регистрации
    button_register.pack()

    current_user_id = None  # Глобальная переменная для хранения ID текущего пользователя
    main_window.mainloop()