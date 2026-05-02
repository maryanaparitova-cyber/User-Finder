import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Путь к файлу избранных пользователей
FAVORITES_FILE = "izbr.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей с обработкой ошибок
        self.favorites = self.load_favorites()

        # Интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Поле ввода
        tk.Label(self.root, text="Введите имя пользователя GitHub:").pack(pady=5)
        self.search_entry = tk.Entry(self.root, width=50)
        self.search_entry.pack(pady=5)

        # Кнопка поиска
        search_button = tk.Button(self.root, text="Найти", command=self.search_user)
        search_button.pack(pady=5)

        # Список результатов
        tk.Label(self.root, text="Результаты поиска:").pack(pady=5)
        self.results_listbox = tk.Listbox(self.root, height=10, width=70)
        self.results_listbox.pack(pady=10)

        # Кнопки управления избранным
        add_favorite_button = tk.Button(
            self.root,
            text="Добавить в избранное",
            command=self.add_to_favorites
        )
        add_favorite_button.pack(pady=2)

        remove_favorite_button = tk.Button(
            self.root,
            text="Удалить из избранного",
            command=self.remove_from_favorites
        )
        remove_favorite_button.pack(pady=2)

        # Список избранных
        tk.Label(self.root, text="Избранные пользователи:").pack(pady=5)
        self.favorites_listbox = tk.Listbox(self.root, height=5, width=70)
        self.favorites_listbox.pack(pady=10)
        self.update_favorites_display()

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")

            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", "Пользователь не найден (код: 404)")
            elif response.status_code == 403:
                messagebox.showerror(
                    "Ошибка",
                    "Превышен лимит запросов к API GitHub (код: 403). Попробуйте позже или используйте токен аутентификации."
                )
            else:
                messagebox.showerror(
                    "Ошибка",
            f"Произошла ошибка при запросе к API (код: {response.status_code})"
                )
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к интернету. Проверьте соединение.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def display_user(self, user_data):
        self.results_listbox.delete(0, tk.END)
        info = f"{user_data['login']} - {user_data.get('name', 'Нет имени')} - {user_data.get('public_repos', 0)} репозиториев"
        self.results_listbox.insert(tk.END, info)

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        user_info = self.results_listbox.get(selection[0])
        username = user_info.split(" - ")[0]

        if username not in self.favorites:
            self.favorites.append(username)
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"{username} добавлен в избранное!")
        else:
            messagebox.showwarning("Предупреждение", f"{username} уже в избранном!")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка избранного!")
            return

        username = self.favorites_listbox.get(selection[0])
        self.favorites.remove(username)
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", f"{username} удалён из избранного!")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                return json.loads(content)
            else:
                # Файл существует, но пустой — инициализируем пустым массивом
                return []
            except json.JSONDecodeError:
                # Если файл содержит некорректный JSON, сбрасываем его
                print(f"Предупреждение: файл {FAVORITES_FILE} содержит некорректный JSON. Создаём новый.")
                return []
        else:
            # Файл не существует — создаём пустой список
            return []

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def update_favorites_display(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
