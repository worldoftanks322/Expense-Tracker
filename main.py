import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x700")

        # Загрузка расходов
        self.expenses = self.load_expenses()
        self.setup_ui()

    def setup_ui(self):
        # Поле ввода суммы
        ttk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=5)

        # Поле выбора категории
        ttk.Label(self.root, text="Категория:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Одежда", "Другое"]
        self.category_combo = ttk.Combobox(self.root, textvariable=self.category_var, values=categories, state="readonly")
        self.category_combo.grid(row=1, column=1, padx=10, pady=5)

        # Поле ввода даты
        ttk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопка добавления расхода
        self.add_btn = ttk.Button(self.root, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Фильтры
        ttk.Label(self.root, text="Фильтр по категории:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(self.root, textvariable=self.filter_category_var, values=["Все"] + categories)
        self.filter_category_combo.set("Все")
        self.filter_category_combo.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.filter_date_entry = ttk.Entry(self.root)
        self.filter_date_entry.grid(row=5, column=1, padx=10, pady=5)

        self.apply_filter_btn = ttk.Button(self.root, text="Применить фильтры", command=self.refresh_expense_table)
        self.apply_filter_btn.grid(row=6, column=0, columnspan=2, pady=5)


        # Подсчёт суммы за период
        ttk.Label(self.root, text="Период для подсчёта (ГГГГ-ММ-ДД - ГГГГ-ММ-ДД):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.period_from_entry = ttk.Entry(self.root, width=15)
        self.period_from_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        self.period_to_entry = ttk.Entry(self.root, width=15)
        self.period_to_entry.grid(row=7, column=1, padx=80, pady=5, sticky="w")

        self.calculate_btn = ttk.Button(self.root, text="Посчитать сумму за период", command=self.calculate_period_sum)
        self.calculate_btn.grid(row=8, column=0, columnspan=2, pady=5)

        self.sum_label = ttk.Label(self.root, text="Общая сумма за период: 0 руб.")
        self.sum_label.grid(row=9, column=0, columnspan=2, pady=5)

        # Таблица расходов
        ttk.Label(self.root, text="Записи о расходах:").grid(row=10, column=0, columnspan=2, pady=10)
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.expense_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)

        for col in columns:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=120)

        self.expense_tree.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Заполнение таблицы
        self.refresh_expense_table()

    def load_expenses(self):
        if os.path.exists("expenses.json"):
            with open("expenses.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []


    def save_expenses(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)


    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date_str = self.date_entry.get().strip()

        # Валидация суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            return

        # Валидация даты
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return

        # Проверка категории
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return

        # Добавление расхода
        expense = {
            "id": len(self.expenses) + 1,
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_expenses()
        self.refresh_expense_table()

        # Очистка полей ввода
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.date_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Расход добавлен")

    def refresh_expense_table(self):
        # Очистка таблицы
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)

        # Получение фильтров
        filter_category = self.filter_category_var.get()
        filter_date = self.filter_date_entry.get().strip()

        filtered_expenses = self.expenses

        # Фильтр по категории
        if filter_category != "Все":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == filter_category]

         # Фильтр по дате
        if filter_date:
            filtered_expenses = [e for e in filtered_expenses if e["date"] == filter_date]


        # Заполнение таблицы отфильтрованными записями
        for expense in filtered_expenses:
            self.expense_tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']} руб.",
                expense["category"],
                expense["date"]
            ))

    def calculate_period_sum(self):
        from_date_str = self.period_from_entry.get().strip()
        to_date_str = self.period_to_entry.get().strip()

        # Валидация дат периода
        try:
            if from_date_str:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            else:
                from_date = None

            if to_date_str:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            else:
                to_date = None
        except ValueError:
            messagebox.showerror("Ошибка", "Даты периода должны быть в формате ГГГГ-ММ-ДД")
            return

        total_sum = 0
        for expense in self.expenses:
            expense_date = datetime.strptime(expense["date"], "%Y-%m-%d").date()


            # Проверка, попадает ли дата расхода в период
            if from_date and expense_date < from_date:
                continue
            if to_date and expense_date > to_date:
                continue

            total_sum += expense["amount"]

        self.sum_label.config(text=f"Общая сумма за период: {total_sum} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
