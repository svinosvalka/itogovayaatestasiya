import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime


class RandomQuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("850x650")
        self.root.resizable(True, True)

        # Хранилище данных
        self.quotes = []
        self.history = []
        self.quotes_file = "quotes_data.json"
        self.history_file = "history.json"

        # Загрузка данных
        self.load_quotes()
        self.load_history()

        # Настройка интерфейса
        self.setup_ui()
        self.update_history_list()
        self.update_author_filter()
        self.update_topic_filter()

    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Область отображения цитаты
        quote_frame = ttk.LabelFrame(main_frame, text="Текущая цитата", padding="10")
        quote_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.quote_text = tk.Text(quote_frame, height=4, width=65, wrap=tk.WORD, font=("Arial", 12))
        self.quote_text.grid(row=0, column=0, columnspan=2, pady=5)

        self.quote_author_label = ttk.Label(quote_frame, text="Автор: ", font=("Arial", 10, "italic"))
        self.quote_author_label.grid(row=1, column=0, sticky=tk.W)

        self.quote_topic_label = ttk.Label(quote_frame, text="Тема: ", font=("Arial", 10))
        self.quote_topic_label.grid(row=1, column=1, sticky=tk.W)

        # Кнопка генерации
        self.generate_btn = ttk.Button(quote_frame, text="🎲 Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Фильтры
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтры", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Фильтр по автору
        ttk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.author_filter_var = tk.StringVar(value="Все")
        self.author_filter_combo = ttk.Combobox(filter_frame, textvariable=self.author_filter_var, width=35)
        self.author_filter_combo.grid(row=0, column=1, padx=5)
        self.author_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Фильтр по теме
        ttk.Label(filter_frame, text="Фильтр по теме:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.topic_filter_var = tk.StringVar(value="Все")
        self.topic_filter_combo = ttk.Combobox(filter_frame, textvariable=self.topic_filter_var, width=35)
        self.topic_filter_combo.grid(row=1, column=1, padx=5)
        self.topic_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Добавление новой цитаты
        add_frame = ttk.LabelFrame(main_frame, text="➕ Добавить новую цитату", padding="10")
        add_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.new_quote_text = tk.Text(add_frame, height=3, width=55, wrap=tk.WORD)
        self.new_quote_text.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.new_author_entry = ttk.Entry(add_frame, width=45)
        self.new_author_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.new_topic_entry = ttk.Entry(add_frame, width=45)
        self.new_topic_entry.grid(row=2, column=1, padx=5, pady=5)

        add_btn = ttk.Button(add_frame, text="✅ Добавить цитату", command=self.add_quote)
        add_btn.grid(row=3, column=1, pady=10, sticky=tk.E)

        # История цитат
        history_frame = ttk.LabelFrame(main_frame, text="📜 История сгенерированных цитат", padding="10")
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Скроллбар для истории
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, height=8, yscrollcommand=scrollbar.set)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="🗑️ Очистить историю", command=self.clear_history)
        clear_btn.pack(pady=5)

        # Настройка весов сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def load_quotes(self):
        """Загрузка цитат из JSON файла"""
        if os.path.exists(self.quotes_file):
            try:
                with open(self.quotes_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.quotes = data.get('quotes', [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки цитат: {e}")
                self.quotes = []

        # Цитаты по умолчанию, если файл пуст или не существует
        if not self.quotes:
            self.quotes = [
                {"text": "Единственная граница для нашего завтра - это наши сегодняшние сомнения.",
                 "author": "Франклин Д. Рузвельт", "topic": "Мотивация"},
                {"text": "Делай что можешь, с тем что имеешь, там где ты есть.", "author": "Теодор Рузвельт",
                 "topic": "Действие"},
                {"text": "Счастье зависит от нас самих.", "author": "Аристотель", "topic": "Счастье"},
                {"text": "Будь тем изменением, которое хочешь видеть в мире.", "author": "Махатма Ганди",
                 "topic": "Перемены"},
                {"text": "Живи так, будто завтра умрёшь. Учись так, будто будешь жить вечно.",
                 "author": "Махатма Ганди", "topic": "Жизнь"},
                {"text": "Будущее принадлежит тем, кто верит в красоту своей мечты.", "author": "Элеонора Рузвельт",
                 "topic": "Мечты"},
                {"text": "Оставайтесь голодными, оставайтесь безрассудными.", "author": "Стив Джобс",
                 "topic": "Мотивация"},
                {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "topic": "Творчество"},
                {"text": "Лучшее время посадить дерево было 20 лет назад. Следующее лучшее время - сейчас.",
                 "author": "Китайская пословица", "topic": "Действие"},
                {"text": "Неважно, как медленно ты идёшь, главное - не останавливаться.", "author": "Конфуций",
                 "topic": "Настойчивость"},
                {"text": "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма.",
                 "author": "Уинстон Черчилль", "topic": "Успех"},
                {"text": "Вставать и падать - часть жизни. А вот оставаться лежать - выбор.", "author": "Неизвестный",
                 "topic": "Мотивация"}
            ]
            self.save_quotes()

    def save_quotes(self):
        """Сохранение цитат в JSON файл"""
        try:
            with open(self.quotes_file, 'w', encoding='utf-8') as file:
                json.dump({"quotes": self.quotes}, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения цитат: {e}")

    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.history = data.get('history', [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки истории: {e}")
                self.history = []

    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as file:
                json.dump({"history": self.history}, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения истории: {e}")

    def generate_quote(self):
        """Генерация случайной цитаты с учётом фильтров"""
        filtered_quotes = self.get_filtered_quotes()

        if not filtered_quotes:
            messagebox.showwarning("Нет цитат", "Нет цитат, соответствующих выбранным фильтрам!")
            return

        quote = random.choice(filtered_quotes)

        # Отображение цитаты
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(1.0, quote['text'])
        self.quote_author_label.config(text=f"Автор: {quote['author']}")
        self.quote_topic_label.config(text=f"Тема: {quote['topic']}")

        # Добавление в историю
        history_entry = {
            "text": quote['text'],
            "author": quote['author'],
            "topic": quote['topic'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, history_entry)
        self.save_history()
        self.update_history_list()

    def get_filtered_quotes(self):
        """Получение цитат, отфильтрованных по автору и теме"""
        filtered = self.quotes
        author_filter = self.author_filter_var.get()
        topic_filter = self.topic_filter_var.get()

        if author_filter != "Все":
            filtered = [q for q in filtered if q['author'] == author_filter]

        if topic_filter != "Все":
            filtered = [q for q in filtered if q['topic'] == topic_filter]

        return filtered

    def update_history_list(self):
        """Обновление списка истории"""
        self.history_listbox.delete(0, tk.END)
        for entry in self.history:
            display_text = f"[{entry['timestamp']}] \"{entry['text'][:55]}...\" — {entry['author']}"
            self.history_listbox.insert(tk.END, display_text)

    def update_author_filter(self):
        """Обновление выпадающего списка авторов"""
        authors = sorted(set(q['author'] for q in self.quotes))
        self.author_filter_combo['values'] = ['Все'] + authors
        if self.author_filter_var.get() not in self.author_filter_combo['values']:
            self.author_filter_var.set('Все')

    def update_topic_filter(self):
        """Обновление выпадающего списка тем"""
        topics = sorted(set(q['topic'] for q in self.quotes))
        self.topic_filter_combo['values'] = ['Все'] + topics
        if self.topic_filter_var.get() not in self.topic_filter_combo['values']:
            self.topic_filter_var.set('Все')

    def on_filter_change(self, event=None):
        """Обработка изменения фильтров"""
        self.update_author_filter()
        self.update_topic_filter()

    def add_quote(self):
        """Добавление новой цитаты в коллекцию"""
        text = self.new_quote_text.get(1.0, tk.END).strip()
        author = self.new_author_entry.get().strip()
        topic = self.new_topic_entry.get().strip()

        # Проверка корректности ввода
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return

        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return

        if not topic:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return

        # Добавление новой цитаты
        new_quote = {
            "text": text,
            "author": author,
            "topic": topic
        }

        self.quotes.append(new_quote)
        self.save_quotes()

        # Очистка полей ввода
        self.new_quote_text.delete(1.0, tk.END)
        self.new_author_entry.delete(0, tk.END)
        self.new_topic_entry.delete(0, tk.END)

        # Обновление фильтров
        self.update_author_filter()
        self.update_topic_filter()

        messagebox.showinfo("Успех", "Цитата успешно добавлена!")

    def clear_history(self):
        """Очистка истории цитат"""
        self.history = []
        self.save_history()
        self.update_history_list()
        messagebox.showinfo("История очищена", "История цитат успешно очищена!")


def main():
    root = tk.Tk()
    app = RandomQuoteGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()