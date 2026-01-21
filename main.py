#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os

from config import PLANNED_WORK, ALLOWANCE, save_config, load_config
from database import Database


class CarLoggerApp:
    def __init__(self):
        self.db = Database()
        self.root = tk.Tk()
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("🚗 Автомобильный сервисный журнал")
        self.root.geometry("800x600")
        
        # Устанавливаем белый фон для всего окна
        self.root.configure(bg="white")
        
        # Центрируем окно
        self.center_window(800, 600)
        
        # Создаем меню
        self.create_menu()
        
        # Приветственное сообщение
        welcome_label = tk.Label(
            self.root,
            text="Добро пожаловать в систему учета сервисных работ!",
            font=("Arial", 14, "bold"),
            pady=20,
            bg="white"
        )
        welcome_label.pack()
        
        # Основные кнопки
        buttons_frame = tk.Frame(self.root, bg="white")
        buttons_frame.pack(pady=30)
        
        # ДОБАВЛЕНО: кнопка "Настроить ТО"
        buttons = [
            ("🔍 Проверить состояние", self.check_status),
            ("➕ Добавить запись", self.add_record),
            ("📋 История обслуживания", self.view_history),
            ("🔧 Плановые ТО", self.view_services),
            ("⚙️ Настроить ТО", self.configure_services),  # НОВАЯ КНОПКА
            ("❌ Выход", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=("Arial", 12),
                bg="#1976D2",
                fg="white",
                width=25,
                pady=10,
                command=command
            )
            btn.pack(pady=5)
        
        # Информация о версии
        version_label = tk.Label(
            self.root,
            text="Версия 1.0",
            font=("Arial", 8),
            fg="gray",
            bg="white"
        )
        version_label.pack(side="bottom", pady=10)
    
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Настройки"
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Автомобильный сервисный журнал\nВерсия 1.1\n\nУчет и контроль обслуживания автомобиля\n\n© 2024"
        )
    
    def check_status(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Проверка состояния")
        dialog.geometry("950x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Устанавливаем белый фон для диалога
        dialog.configure(bg="white")
        
        # Центрируем диалог
        self.center_dialog(dialog, 950, 700)
        
        # Заголовок
        tk.Label(dialog, text="Проверка состояния автомобиля", 
                font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Основной контейнер с прокруткой
        main_container = tk.Frame(dialog, bg="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Поле ввода
        input_frame = tk.Frame(main_container, bg="white")
        input_frame.pack(fill="x", pady=10)
        
        tk.Label(input_frame, text="Введите текущий пробег автомобиля (км):", 
                font=("Arial", 11),
                bg="white").pack(anchor="w")
        
        mileage_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=mileage_var, 
                        font=("Arial", 12), width=20)
        entry.pack(fill="x", pady=5)
        entry.focus()
        
        # Фрейм для результата
        result_frame = tk.Frame(main_container, bg="white")
        result_frame.pack(fill="both", expand=True, pady=10)
        
        def perform_check():
            try:
                mileage = int(mileage_var.get())
                if mileage < 0:
                    raise ValueError("Пробег не может быть отрицательным")
                
                # Очищаем предыдущие результаты
                for widget in result_frame.winfo_children():
                    widget.destroy()
                
                # Проверяем состояние
                services = self.db.check_services(mileage)
                
                if not services:
                    success_frame = tk.Frame(result_frame, bg="#E8F5E9")
                    success_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    tk.Label(success_frame,
                            text="✅ ВСЕ СИСТЕМЫ В НОРМЕ",
                            font=("Arial", 14, "bold"),
                            fg="#2E7D32",
                            bg="#E8F5E9",
                            pady=20
                    ).pack()
                    
                    tk.Label(success_frame,
                            text="Сервисное обслуживание не требуется.",
                            font=("Arial", 12),
                            fg="#388E3C",
                            bg="#E8F5E9",
                            pady=10
                    ).pack()
                    
                    tk.Label(success_frame,
                            text=f"Текущий пробег: {mileage:,} км",
                            font=("Arial", 11),
                            fg="#666666",
                            bg="#E8F5E9"
                    ).pack()
                    
                else:
                    # Создаем контейнер для Treeview
                    container = tk.Frame(result_frame, bg="white")
                    container.pack(fill='both', expand=True)
                    
                    # Заголовок результата
                    tk.Label(container,
                            text=f"⚠️ ТРЕБУЕТСЯ ОБСЛУЖИВАНИЕ (пробег: {mileage:,} км)",
                            font=("Arial", 13, "bold"),
                            fg="#D32F2F",
                            bg="white",
                            pady=5
                    ).pack(anchor="w")
                    
                    # Создаем Treeview
                    tree_frame = tk.Frame(container, bg="white")
                    tree_frame.pack(fill='both', expand=True, pady=10)
                    
                    # Настраиваем стиль Treeview
                    style = ttk.Style()
                    style.configure("Status.Treeview", 
                                   font=("Arial", 11),
                                   rowheight=35,
                                   background="#FFFFFF",
                                   fieldbackground="#FFFFFF")
                    style.configure("Status.Treeview.Heading", 
                                   font=("Arial", 12, "bold"),
                                   background="#FF9800",
                                   foreground="white")
                    
                    # Создаем Treeview с цветовым кодированием
                    tree = ttk.Treeview(tree_frame, 
                                       columns=('work', 'last_service', 'next_service', 'status'),
                                       show='headings',
                                       style="Status.Treeview",
                                       height=8)
                    
                    # Настраиваем столбцы
                    tree.heading('work', text='Работа', anchor='w')
                    tree.heading('last_service', text='Последнее ТО (км)', anchor='center')
                    tree.heading('next_service', text='Следующее ТО (км)', anchor='center')
                    tree.heading('status', text='Статус', anchor='center')
                    
                    tree.column('work', width=380, anchor='w')
                    tree.column('last_service', width=150, anchor='center')
                    tree.column('next_service', width=150, anchor='center')
                    tree.column('status', width=120, anchor='center')
                    
                    # Добавляем данные
                    for work_desc, last_mileage, next_service, status in services:
                        tree.insert('', 'end', values=(
                            work_desc,
                            f"{last_mileage:,}",
                            f"{next_service:,}",
                            status
                        ))
                    
                    # Добавляем теги для цветового оформления
                    tree.tag_configure('urgent', background='#FFEBEE', foreground='#C62828')
                    tree.tag_configure('soon', background='#FFF3E0', foreground='#EF6C00')
                    
                    # Применяем теги к строкам
                    for i, item in enumerate(tree.get_children()):
                        values = tree.item(item)['values']
                        status = values[3]
                        if status == "СРОЧНО!":
                            tree.item(item, tags=('urgent',))
                        else:
                            tree.item(item, tags=('soon',))
                    
                    # Добавляем скроллбар
                    vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
                    tree.configure(yscrollcommand=vsb.set)
                    
                    tree.grid(row=0, column=0, sticky='nsew')
                    vsb.grid(row=0, column=1, sticky='ns')
                    
                    tree_frame.grid_rowconfigure(0, weight=1)
                    tree_frame.grid_columnconfigure(0, weight=1)
                    
                    # Легенда
                    legend_frame = tk.Frame(container, bg="white")
                    legend_frame.pack(fill='x', pady=10)
                    
                    tk.Label(legend_frame, text="Легенда:", 
                            font=("Arial", 10, "bold"),
                            bg="white").pack(side='left', padx=5)
                    
                    urgent_sample = tk.Label(legend_frame, text="█", 
                                           bg="#FFEBEE", fg="#C62828", font=("Arial", 10))
                    urgent_sample.pack(side='left', padx=(10, 2))
                    tk.Label(legend_frame, text="Требуется срочно", 
                            font=("Arial", 9),
                            bg="white").pack(side='left', padx=(0, 15))
                    
                    soon_sample = tk.Label(legend_frame, text="█", 
                                         bg="#FFF3E0", fg="#EF6C00", font=("Arial", 10))
                    soon_sample.pack(side='left', padx=(10, 2))
                    tk.Label(legend_frame, text="Скоро потребуется", 
                            font=("Arial", 9),
                            bg="white").pack(side='left')
                    
                    # Статистика
                    urgent_count = sum(1 for _, _, _, status in services if status == "СРОЧНО!")
                    soon_count = sum(1 for _, _, _, status in services if status == "Скоро потребуется")
                    
                    stats_frame = tk.Frame(container, bg="white")
                    stats_frame.pack(fill='x', pady=5)
                    
                    tk.Label(stats_frame,
                            text=f"Всего работ: {len(services)} | Срочных: {urgent_count} | Скоро: {soon_count}",
                            font=("Arial", 10, "bold"),
                            fg="#1976D2",
                            bg="white"
                    ).pack()
            
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный пробег (положительное число)")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        
        # Кнопки в отдельном фрейме внизу
        button_frame = tk.Frame(dialog, bg="white")
        button_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Button(
            button_frame,
            text="🔍 Проверить",
            command=perform_check,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Закрыть",
            command=dialog.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side="left", padx=5)
        
        # Делаем кнопки растягиваемыми
        button_frame.pack_propagate(False)
        button_frame.configure(height=50)
    
    def add_record(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить запись")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Белый фон для диалога
        dialog.configure(bg="white")
        
        self.center_dialog(dialog, 500, 500)
        
        # Заголовок
        tk.Label(dialog, text="Добавление записи", 
                font=("Arial", 14, "bold"),
                bg="white").pack(pady=10)
        
        # Основной фрейм с прокруткой
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Поля формы
        tk.Label(main_frame, text="Пробег (км):", bg="white").pack(anchor="w")
        mileage_entry = tk.Entry(main_frame, font=("Arial", 12))
        mileage_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(main_frame, text="Дата (ГГГГ-ММ-ДД):", bg="white").pack(anchor="w")
        date_entry = tk.Entry(main_frame, font=("Arial", 12))
        date_entry.pack(fill="x", pady=(0, 10))
        date_entry.insert(0, str(datetime.date.today()))
        
        tk.Label(main_frame, text="Тип обслуживания:", bg="white").pack(anchor="w")
        type_var = tk.StringVar(value="плановое ТО")
        type_menu = ttk.Combobox(main_frame, textvariable=type_var,
                                values=["плановое ТО", "внеплановый ремонт"],
                                state="readonly")
        type_menu.pack(fill="x", pady=(0, 10))
        
        # Фрейм для выбора описания работ
        desc_frame = tk.Frame(main_frame, bg="white")
        desc_frame.pack(fill="x", pady=(0, 20))
        
        # Создаем все элементы один раз, но будем их показывать/скрывать
        planned_label = tk.Label(desc_frame, text="Выберите работу:", anchor="w", bg="white")
        manual_label = tk.Label(desc_frame, text="Введите описание вручную:", anchor="w", bg="white")
        
        # Выпадающий список для плановых ТО
        planned_work_var = tk.StringVar()
        planned_work_combo = ttk.Combobox(desc_frame, textvariable=planned_work_var,
                                         values=[work for work, _ in PLANNED_WORK],
                                         state="readonly",
                                         font=("Arial", 11))
        
        # Текстовое поле для ручного ввода
        manual_desc_text = tk.Text(desc_frame, height=4, font=("Arial", 10))
        
        # Функция для переключения между выпадающим списком и текстовым полем
        def toggle_description_input(*args):
            # Очищаем фрейм от всех элементов
            for widget in desc_frame.winfo_children():
                widget.pack_forget()
            
            if type_var.get() == "плановое ТО":
                # Показываем выпадающий список
                planned_label.pack(anchor="w")
                planned_work_combo.pack(fill="x", pady=(0, 10))
            else:
                # Показываем текстовое поле
                manual_label.pack(anchor="w")
                manual_desc_text.pack(fill="x", pady=(0, 10))
        
        # Связываем изменение типа обслуживания с функцией переключения
        type_var.trace("w", toggle_description_input)
        
        # Инициализируем состояние
        toggle_description_input()
        
        def save():
            try:
                mileage = int(mileage_entry.get())
                if mileage < 0:
                    raise ValueError("Пробег не может быть отрицательным")
                
                date = date_entry.get()
                # Проверяем дату
                try:
                    datetime.date.fromisoformat(date)
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты")
                    return
                
                type_ = type_var.get()
                
                # Получаем описание в зависимости от типа
                if type_ == "плановое ТО":
                    description = planned_work_var.get()
                    if not description:
                        messagebox.showerror("Ошибка", "Выберите работу из списка")
                        return
                else:
                    description = manual_desc_text.get("1.0", "end-1c").strip()
                    if not description:
                        messagebox.showerror("Ошибка", "Введите описание работ")
                        return
                
                # Сохраняем в БД
                record_id = self.db.add_record(mileage, date, type_, description)
                
                # Форматируем пробег с разделителями тысяч
                formatted_mileage = f"{mileage:,} км".replace(",", " ")
                
                messagebox.showinfo(
                    "Успех",
                    f"Пробег: {formatted_mileage}\n"
                    f"Дата: {date}\n"
                    f"Тип: {type_}\n"
                    f"Описание: {description}"
                )
                dialog.destroy()
            
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        
        # Кнопки
        button_frame = tk.Frame(dialog, bg="white")
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Сохранить",
            command=save,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Отмена",
            command=dialog.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 11),
            padx=20
        ).pack(side="left", padx=5)
    
    def view_history(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("История обслуживания")
        dialog.geometry("950x650")
        dialog.transient(self.root)
        
        dialog.configure(bg="white")
        self.center_dialog(dialog, 950, 650)
        
        tk.Label(dialog, text="История обслуживания", 
                font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            records = self.db.get_all_records()
            
            if not records:
                tk.Label(main_frame, text="История пуста", 
                        font=("Arial", 14), pady=20, bg="white").pack()
                
                tk.Button(main_frame,
                        text="Закрыть",
                        command=dialog.destroy,
                        bg="#f44336",
                        fg="white",
                        font=("Arial", 11),
                        padx=20,
                        pady=5).pack(pady=10)
                return
            
            # Контейнер для Treeview
            container = tk.Frame(main_frame, bg="white")
            container.pack(fill='both', expand=True)
            
            # Настраиваем стиль
            style = ttk.Style()
            style.configure("Treeview", 
                        font=("Arial", 11),
                        rowheight=30)
            style.configure("Treeview.Heading", 
                        font=("Arial", 12, "bold"),
                        background="#4CAF50",
                        foreground="white")
            
            # Создаем Treeview с дополнительной колонкой для действий
            tree = ttk.Treeview(container, 
                            columns=('mileage', 'date', 'type', 'description', 'actions'),
                            show='headings',
                            height=15)
            
            # Настраиваем столбцы
            tree.heading('mileage', text='Пробег (км)', anchor='center')
            tree.heading('date', text='Дата', anchor='center')
            tree.heading('type', text='Тип', anchor='center')
            tree.heading('description', text='Описание работ', anchor='w')
            tree.heading('actions', text='Действия', anchor='center')
            
            tree.column('mileage', width=100, anchor='center')
            tree.column('date', width=100, anchor='center')
            tree.column('type', width=120, anchor='center')
            tree.column('description', width=400, anchor='w')
            tree.column('actions', width=80, anchor='center')
            
            # Добавляем данные (без ID!)
            for record in records:
                # record содержит: (id, mileage, date, type, description)
                # Мы пропускаем первый элемент (id) и добавляем остальные
                tree.insert('', 'end', 
                        values=(record[1], record[2], record[3], record[4], "❌ Удалить"),
                        tags=(str(record[0]),))  # Сохраняем ID в теге!
            
            # Добавляем цвета для строк
            tree.tag_configure('even', background='#F5F5F5')
            tree.tag_configure('odd', background='#FFFFFF')
            
            for i, item in enumerate(tree.get_children()):
                tag = 'even' if i % 2 == 0 else 'odd'
                # Добавляем оба тега: четность и ID
                current_tags = list(tree.item(item, 'tags'))
                current_tags.append(tag)
                tree.item(item, tags=tuple(current_tags))
            
            # Функция обработки кликов по Treeview
            def on_treeview_click(event):
                region = tree.identify("region", event.x, event.y)
                if region == "cell":
                    column = tree.identify_column(event.x)
                    if column == "#5":  # Колонка "actions" (теперь пятая, а не шестая)
                        item = tree.identify_row(event.y)
                        if item:
                            # Получаем ID из тега (первый элемент тега - это ID)
                            tags = tree.item(item, 'tags')
                            if tags and len(tags) > 0:
                                # Ищем тег, который является числом (ID)
                                for tag in tags:
                                    if tag and tag.isdigit():
                                        record_id = int(tag)
                                        break
                                else:
                                    messagebox.showerror("Ошибка", "Не удалось найти ID записи")
                                    return
                            
                            # Получаем значения строки для показа в сообщении
                            values = tree.item(item, 'values')
                            # values содержит: (mileage, date, type, description, "❌ Удалить")
                            description = values[3]  # Описание работы
                            mileage = values[0]      # Пробег
                            date = values[1]         # Дата
                            type_ = values[2]        # Тип
                            
                            response = messagebox.askyesno(
                                "Подтверждение удаления",
                                f"Удалить запись: '{description}'?\n\n"
                                f"• Пробег: {mileage} км\n"
                                f"• Дата: {date}\n"
                                f"• Тип: {type_}"
                            )
                            
                            if response:
                                if self.db.delete_record(record_id):
                                    tree.delete(item)
                                    messagebox.showinfo("Успех", f"Запись '{description}' удалена")
                                else:
                                    messagebox.showerror("Ошибка", "Не удалось удалить запись")
            
            # Привязываем обработчик кликов
            tree.bind("<Button-1>", on_treeview_click)
            
            # Добавляем скроллбар
            vsb = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            
            # Информационная подсказка
            info_frame = tk.Frame(main_frame, bg="white")
            info_frame.pack(fill='x', pady=5)
            
            tk.Label(info_frame,
                    text="ℹ️ Для удаления записи нажмите на '❌ Удалить' в колонке 'Действия'",
                    font=("Arial", 9),
                    fg="#1976D2",
                    bg="white").pack()
            
            # Кнопка закрытия
            tk.Button(main_frame,
                    text="Закрыть",
                    command=dialog.destroy,
                    bg="#f44336",
                    fg="white",
                    font=("Arial", 11),
                    padx=20,
                    pady=5).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
    
    def view_services(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Процедуры планового ТО")
        dialog.geometry("800x650")
        dialog.transient(self.root)
        
        # Белый фон для диалога
        dialog.configure(bg="white")
        
        self.center_dialog(dialog, 800, 650)
        
        # Основной контейнер
        main_container = tk.Frame(dialog, bg="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container, text="Процедуры планового технического обслуживания", 
                font=("Arial", 14, "bold"),
                bg="white").pack(pady=10)
        
        # Информация
        tk.Label(main_container, 
                text="Полный перечень регулярных технических процедур с рекомендованными интервалами пробега",
                font=("Arial", 11),
                bg="white").pack(pady=5)
        
        # Создаем контейнер для Treeview
        tree_container = tk.Frame(main_container, bg="white")
        tree_container.pack(fill='both', expand=True, pady=10)
        
        # Настраиваем стиль Treeview
        style = ttk.Style()
        style.configure("Services.Treeview", 
                       font=("Arial", 11),
                       rowheight=30,
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF")
        style.configure("Services.Treeview.Heading", 
                       font=("Arial", 12, "bold"),
                       background="#1976D2",
                       foreground="white")
        
        # Создаем Treeview
        tree = ttk.Treeview(tree_container, 
                           columns=('code', 'procedure', 'interval'),
                           show='headings',
                           style="Services.Treeview",
                           height=12)
        
        # Настраиваем столбцы
        tree.heading('code', text='Код', anchor='center')
        tree.heading('procedure', text='Процедура', anchor='w')
        tree.heading('interval', text='Интервал (км)', anchor='center')
        
        tree.column('code', width=80, anchor='center')
        tree.column('procedure', width=500, anchor='w')
        tree.column('interval', width=150, anchor='center')
        
        # Добавляем данные
        for code, (work, interval) in enumerate(PLANNED_WORK):
            tree.insert('', 'end', values=(code, work, f"{interval:,}"))
        
        # Добавляем цвета для строк
        tree.tag_configure('even', background='#F5F5F5')
        tree.tag_configure('odd', background='#FFFFFF')
        
        for i, item in enumerate(tree.get_children()):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.item(item, tags=(tag,))
        
        # Добавляем вертикальный скроллбар
        vsb = ttk.Scrollbar(tree_container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Размещаем элементы
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Настраиваем растягивание
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(dialog, bg="white", height=50)
        button_frame.pack(side="bottom", fill="x", pady=10, padx=20)
        button_frame.pack_propagate(False)
        
        # Кнопка закрытия
        tk.Button(
            button_frame,
            text="Закрыть",
            command=dialog.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8
        ).pack(expand=True)
    
    def configure_services(self):
        """Настройка списка планового ТО"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Настройка планового ТО")
        dialog.geometry("1100x800")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Устанавливаем белый фон
        dialog.configure(bg="white")
        self.center_dialog(dialog, 1100, 800)
        
        # Сохраняем оригинальные данные для сравнения
        original_work = PLANNED_WORK[:]  # Копия списка
        original_allowance = ALLOWANCE
        
        # Контейнер с прокруткой
        main_container = tk.Frame(dialog, bg="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_container,
                text="Настройка процедур планового ТО",
                font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Инструкция
        tk.Label(main_container,
                text="Редактируйте список процедур и интервалы обслуживания:",
                font=("Arial", 11),
                bg="white").pack(pady=5)
        
        # Фрейм для списка процедур с двойной прокруткой
        list_frame = tk.Frame(main_container, bg="white")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Создаем Canvas с прокруткой
        canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        # Конфигурация скроллинга
        def configure_scroll_region(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Добавляем скролл колесиком мыши (для всех систем)
        def on_mousewheel(event):
            if event.num == 4 or event.delta == 120:  # Вверх
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta == -120:  # Вниз
                canvas.yview_scroll(1, "units")
        
        # Привязываем события для разных систем
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/Mac
        canvas.bind_all("<Button-4>", on_mousewheel)    # Linux
        canvas.bind_all("<Button-5>", on_mousewheel)    # Linux
        
        # Размещаем элементы
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Переменные для хранения данных
        entries = []
        
        # Функция для добавления новой строки
        def add_row(work="", interval=10000):
            row_frame = tk.Frame(scrollable_frame, bg="white")
            row_frame.pack(fill="x", pady=2, padx=5)
            
            # Поле для названия работы
            work_var = tk.StringVar(value=work)
            work_entry = tk.Entry(row_frame, textvariable=work_var, 
                                font=("Arial", 11), width=90)
            work_entry.pack(side="left", padx=(0, 15))
            
            # Поле для интервала
            interval_var = tk.StringVar(value=str(interval))
            interval_entry = tk.Entry(row_frame, textvariable=interval_var,
                                    font=("Arial", 11), width=12)
            interval_entry.pack(side="left", padx=(0, 5))
            
            tk.Label(row_frame, text="км", bg="white", font=("Arial", 11)).pack(side="left")
            
            # Кнопка удаления
            delete_btn = tk.Button(row_frame, text="❌",
                                font=("Arial", 9),
                                bg="#f44336",
                                fg="white",
                                width=3,
                                command=lambda: delete_row(row_frame, work_var, interval_var))
            delete_btn.pack(side="left", padx=(15, 0))
            
            entries.append((work_var, interval_var, row_frame))
        
        # Функция удаления строки
        def delete_row(row_frame, work_var, interval_var):
            row_frame.destroy()
            if (work_var, interval_var, row_frame) in entries:
                entries.remove((work_var, interval_var, row_frame))
        
        # Добавляем существующие процедуры
        for work, interval in PLANNED_WORK:
            add_row(work, interval)
        
        # Настройка допуска
        allowance_frame = tk.Frame(main_container, bg="white")
        allowance_frame.pack(fill="x", pady=(20, 10))
        
        tk.Label(allowance_frame, text="Допуск для предупреждения:", 
                font=("Arial", 11), bg="white").pack(side="left", padx=(0, 10))
        
        allowance_var = tk.StringVar(value=str(ALLOWANCE))
        allowance_entry = tk.Entry(allowance_frame, textvariable=allowance_var,
                                font=("Arial", 11), width=8)
        allowance_entry.pack(side="left", padx=(0, 5))
        
        tk.Label(allowance_frame, text="% (предупреждение за сколько % до срока ТО)", 
                font=("Arial", 9), bg="white", fg="gray").pack(side="left")
        
        
        # Функция закрытия окна (БЕЗ ПРОВЕРКИ)
        def close_window():
            """Закрывает окно без проверки изменений"""
            # Просто спрашиваем, точно ли закрыть
            response = messagebox.askyesno(
                "Закрыть окно",
                "Вы уверены, что хотите закрыть окно настройки ТО?"
            )
            
            if response:
                # Отвязываем события мыши
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
                dialog.destroy()
            
            # Обработка закрытия окна через крестик
            dialog.protocol("WM_DELETE_WINDOW", close_window)
            
            # Функция для отвязки событий при закрытии окна
            def unbind_events():
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            
            # Привязываем событие закрытия окна к отвязке
            dialog.bind("<Destroy>", lambda e: unbind_events())
            
        # Фрейм для кнопок управления
        controls_frame = tk.Frame(main_container, bg="white")
        controls_frame.pack(fill="x", pady=10)
        
        # Кнопка добавления новой процедуры
        tk.Button(controls_frame,
                text="➕ Добавить процедуру",
                font=("Arial", 10, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda: add_row()).pack(side="left", padx=5)
        
        # Фрейм для кнопок сохранения/закрытия
        save_frame = tk.Frame(dialog, bg="white", height=60)
        save_frame.pack(side="bottom", fill="x", pady=10, padx=20)
        save_frame.pack_propagate(False)
        
        # Функция сохранения (возвращает True при успешном сохранении)
        def save_configuration():
            try:
                new_planned_work = []
                
                for work_var, interval_var, _ in entries:
                    work = work_var.get().strip()
                    if not work:
                        continue  # Пропускаем пустые строки
                    
                    try:
                        interval = int(interval_var.get())
                        if interval <= 0:
                            raise ValueError("Интервал должен быть положительным числом")
                    except ValueError:
                        messagebox.showerror("Ошибка", 
                                        f"Некорректный интервал для: {work}")
                        return False
                    
                    new_planned_work.append((work, interval))
                
                if not new_planned_work:
                    messagebox.showerror("Ошибка", "Список процедур не может быть пустым")
                    return False
                
                # Получаем допуск
                try:
                    allowance = float(allowance_var.get())
                    if not 1 <= allowance <= 99:
                        raise ValueError("Допуск должен быть между 1 и 99%")
                except ValueError:
                    messagebox.showerror("Ошибка", 
                                    "Некорректное значение допуска (должно быть от 1 до 99%)")
                    return False
                
                # Сохраняем в конфигурацию
                from config import save_config
                if save_config(new_planned_work, allowance):
                    # Обновляем глобальные переменные для текущей сессии
                    global PLANNED_WORK, ALLOWANCE
                    PLANNED_WORK[:] = new_planned_work
                    ALLOWANCE = allowance
                    
                    messagebox.showinfo("Успех", 
                                    "Конфигурация успешно сохранена!")
                    return True
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить конфигурацию")
                    return False
            
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
                return False

        # Кнопки - все слева, закрыть первая
        tk.Button(save_frame,
                text="❌ Закрыть",
                font=("Arial", 11),
                bg="#f44336",
                fg="white",
                padx=30,
                pady=8,
                command=close_window).pack(side="right", padx=10)

        tk.Button(save_frame,
                text="💾 Сохранить",
                font=("Arial", 11, "bold"),
                bg="#4CAF50",
                fg="white",
                padx=30,
                pady=8,
                command=save_configuration).pack(side="left", padx=10)

        tk.Button(save_frame,
                text="💾 Сохранить и закрыть",
                font=("Arial", 11),
                bg="#2196F3",
                fg="white",
                padx=20,
                pady=8,
                command=lambda: save_configuration() and dialog.destroy()).pack(side="left", padx=10)
        
    
    def center_dialog(self, dialog, width, height):
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        self.root.mainloop()
        self.db.close()


def main():
    try:
        app = CarLoggerApp()
        print("Приложение запущено успешно!")
        app.run()
        print("Приложение завершено.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()