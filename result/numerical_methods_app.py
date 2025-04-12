import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import time
import sympy as sp
import os
import sys
from tkmacosx import ColorVar


class NumericalMethodsApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Численные методы: Интегрирование, Интерполяция, Дифференцирование, Уравнения"
        )
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        try:
            if sys.platform == "darwin":
                self.is_macos = True
            else:
                self.is_macos = False
        except ImportError:
            self.is_macos = False

        self.style = ttk.Style()
        self.create_styles()

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_menu()

        self.theory_content = self.load_text_file("theory.txt")
        self.help_content = self.load_text_file("help.txt")

        self.create_notebook()
        self.create_status_bar()

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self.theme = "light"

    def load_text_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            if filename == "theory.txt":
                return "# Теория численных методов\n\nФайл theory.txt не найден."
            else:
                return (
                    "# Справка по использованию программы\n\nФайл help.txt не найден."
                )

    def create_styles(self):
        self.style.theme_use("clam")
        light_bg = "#ffffff"
        light_primary = "#007aff"  # iOS blue
        light_secondary = "#f2f2f7"  # iOS light gray
        light_accent = "#34c759"  # iOS green
        light_text = "#000000"  # Black

        dark_bg = "#1c1c1e"  # iOS dark background
        dark_primary = "#0a84ff"  # iOS dark mode blue
        dark_secondary = "#2c2c2e"  # iOS dark gray
        dark_accent = "#30d158"  # iOS dark mode green
        dark_text = "#ffffff"  # White

        self.style.configure("Light.TFrame", background=light_bg)
        self.style.configure(
            "Light.TLabel",
            background=light_bg,
            foreground=light_text,
            font=("SF Pro", 10),
        )
        self.style.configure(
            "Light.TButton",
            background=light_primary,
            foreground=light_bg,
            font=("SF Pro", 10, "bold"),
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "Light.TButton",
            background=[("active", light_accent)],
            foreground=[("active", light_bg)],
        )
        self.style.configure(
            "Light.TNotebook", background=light_bg, tabmargins=[2, 5, 2, 0]
        )
        self.style.configure(
            "Light.TNotebook.Tab",
            background=light_secondary,
            foreground=light_text,
            font=("SF Pro", 10),
            padding=[15, 8],
            borderwidth=0,
        )
        self.style.map(
            "Light.TNotebook.Tab",
            background=[("selected", light_bg)],
            foreground=[("selected", light_primary)],
        )
        self.style.configure(
            "Light.Vertical.TScrollbar",
            background=light_secondary,
            troughcolor=light_bg,
            borderwidth=0,
            arrowsize=0,
        )

        self.style.configure("Dark.TFrame", background=dark_bg)
        self.style.configure(
            "Dark.TLabel", background=dark_bg, foreground=dark_text, font=("SF Pro", 10)
        )
        self.style.configure(
            "Dark.TButton",
            background=dark_primary,
            foreground=dark_text,
            font=("SF Pro", 10, "bold"),
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "Dark.TButton",
            background=[("active", dark_accent)],
            foreground=[("active", dark_text)],
        )
        self.style.configure(
            "Dark.TNotebook", background=dark_bg, tabmargins=[2, 5, 2, 0]
        )
        self.style.configure(
            "Dark.TNotebook.Tab",
            background=dark_secondary,
            foreground=dark_text,
            font=("SF Pro", 10),
            padding=[15, 8],
            borderwidth=0,
        )
        self.style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", dark_bg)],
            foreground=[("selected", dark_primary)],
        )
        self.style.configure(
            "Dark.Vertical.TScrollbar",
            background=dark_secondary,
            troughcolor=dark_bg,
            borderwidth=0,
            arrowsize=0,
        )

        self.style.configure("Title.TLabel", font=("SF Pro", 16, "bold"))
        self.style.configure("Subtitle.TLabel", font=("SF Pro", 12, "bold"))
        self.style.configure(
            "Rounded.TButton", padding=[15, 8], relief="flat", borderwidth=0
        )

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить результаты", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Смена темы", menu=view_menu)
        view_menu.add_command(
            label="Светлая тема", command=lambda: self.change_theme("light")
        )
        view_menu.add_command(
            label="Темная тема", command=lambda: self.change_theme("dark")
        )

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.integration_frame = ttk.Frame(self.notebook, padding="10")
        self.interpolation_frame = ttk.Frame(self.notebook, padding="10")
        self.differentiation_frame = ttk.Frame(
            self.notebook, padding="10"
        )  # New frame for Lab 3
        self.equations_frame = ttk.Frame(
            self.notebook, padding="10"
        )  # New frame for Lab 4
        self.theory_frame = ttk.Frame(self.notebook, padding="10")
        self.help_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.integration_frame, text="Интегрирование ЛР №2")
        self.notebook.add(self.interpolation_frame, text="Интерполяция ЛР №1")
        self.notebook.add(
            self.differentiation_frame, text="Дифференцирование ЛР №3"
        )  # New tab
        self.notebook.add(
            self.equations_frame, text="Нелинейные уравнения ЛР №4"
        )  # New tab
        self.notebook.add(self.theory_frame, text="Теория по лр")
        self.notebook.add(self.help_frame, text="Справка о программе")

        self.setup_integration_tab()
        self.setup_interpolation_tab()
        self.setup_differentiation_tab()  # Setup for Lab 3
        self.setup_equations_tab()  # Setup for Lab 4
        self.setup_theory_tab()
        self.setup_help_tab()

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.status_bar = ttk.Label(
            status_frame, textvariable=self.status_var, anchor=tk.W, padding=(10, 5)
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        version_label = ttk.Label(status_frame, text="v1.0.0", padding=(10, 5))
        version_label.pack(side=tk.RIGHT)

    def setup_integration_tab(self):
        container_frame = ttk.Frame(self.integration_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(
            container_frame, text="Входные данные", padding="15"
        )
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(input_frame, text="Функция f(x):", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.function_entry = ttk.Entry(input_frame, width=40, font=("SF Pro", 10))
        self.function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.function_entry.insert(0, "x**2")

        ttk.Label(
            input_frame,
            text="Доступные функции: sin, cos, tan, exp, sqrt, abs",
            font=("SF Pro", 8),
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        ttk.Label(input_frame, text="Нижний предел (a):", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.a_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.a_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.a_entry.insert(0, "0")

        ttk.Label(
            input_frame, text="Верхний предел (b):", style="Subtitle.TLabel"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.b_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.b_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.b_entry.insert(0, "1")

        ttk.Label(input_frame, text="Точность (eps):", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.eps_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.eps_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.eps_entry.insert(0, "1e-6")

        # Method selection (macOS style radio buttons)
        ttk.Label(input_frame, text="Методы:", style="Subtitle.TLabel").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )

        methods_frame = ttk.Frame(input_frame)
        methods_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

        self.method_var = tk.StringVar(value="all")
        methods = [
            ("Все методы", "all"),
            ("Метод трапеций", "trapezoidal"),
            ("Метод Симпсона", "simpson"),
            ("Метод Ньютона-Котеса", "newton_cotes"),
        ]

        for i, (text, value) in enumerate(methods):
            rb = ttk.Radiobutton(
                methods_frame, text=text, value=value, variable=self.method_var
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)

        self.calculate_button = ttk.Button(
            input_frame,
            text="Вычислить",
            command=self.calculate_integration,
            style="Rounded.TButton",
        )
        self.calculate_button.grid(
            row=6, column=0, columnspan=2, pady=(15, 0), sticky=(tk.W, tk.E)
        )

        output_frame = ttk.Frame(container_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.plot_frame = ttk.LabelFrame(output_frame, text="Графики", padding="10")
        self.plot_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        self.fig_integration = Figure(figsize=(10, 8), dpi=100)
        self.canvas_integration = FigureCanvasTkAgg(
            self.fig_integration, master=self.plot_frame
        )
        self.canvas_integration.draw()
        self.canvas_integration.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        results_frame = ttk.LabelFrame(
            output_frame, text="Результаты вычислений", padding="10"
        )
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=80, height=20, font=("SF Mono", 9)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.integration_frame.columnconfigure(0, weight=1)
        self.integration_frame.rowconfigure(0, weight=1)
        container_frame.columnconfigure(1, weight=3)
        container_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

    def setup_interpolation_tab(self):
        container_frame = ttk.Frame(self.interpolation_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(
            container_frame, text="Входные данные", padding="15"
        )
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(
            input_frame, text="Узловые точки (x, y):", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        points_frame = ttk.Frame(input_frame, borderwidth=1, relief="solid")
        points_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.points_text = scrolledtext.ScrolledText(
            points_frame,
            wrap=tk.WORD,
            width=30,
            height=10,
            font=("SF Mono", 9),
            borderwidth=0,
        )
        self.points_text.pack(fill=tk.BOTH, expand=True)
        self.points_text.insert(tk.END, "0 0\n1 1\n2 4\n3 9")

        ttk.Label(
            input_frame, text="Точка интерполяции (x*):", style="Subtitle.TLabel"
        ).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.x_star_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.x_star_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.x_star_entry.insert(0, "1.5")

        ttk.Label(input_frame, text="Методы:", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )

        interp_methods_frame = ttk.Frame(input_frame)
        interp_methods_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)

        self.interp_method_var = tk.StringVar(value="both")
        interp_methods = [
            ("Оба метода", "both"),
            ("Многочлен Лагранжа", "lagrange"),
            ("Многочлен Ньютона", "newton"),
        ]

        for i, (text, value) in enumerate(interp_methods):
            rb = ttk.Radiobutton(
                interp_methods_frame,
                text=text,
                value=value,
                variable=self.interp_method_var,
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)

        self.interpolate_button = ttk.Button(
            input_frame,
            text="Интерполировать",
            command=self.calculate_interpolation,
            style="Rounded.TButton",
        )
        self.interpolate_button.grid(row=6, column=0, pady=(15, 0), sticky=(tk.W, tk.E))

        output_frame = ttk.Frame(container_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.plot_frame_interpolation = ttk.LabelFrame(
            output_frame, text="Графики интерполяции", padding="10"
        )
        self.plot_frame_interpolation.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        self.fig_interpolation = Figure(figsize=(10, 8), dpi=100)
        self.canvas_interpolation = FigureCanvasTkAgg(
            self.fig_interpolation, master=self.plot_frame_interpolation
        )
        self.canvas_interpolation.draw()
        self.canvas_interpolation.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        results_frame = ttk.LabelFrame(
            output_frame, text="Результаты интерполяции", padding="10"
        )
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.interpolation_result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=80, height=20, font=("SF Mono", 9)
        )
        self.interpolation_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.interpolation_frame.columnconfigure(0, weight=1)
        self.interpolation_frame.rowconfigure(0, weight=1)
        container_frame.columnconfigure(1, weight=3)
        container_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

    def setup_differentiation_tab(self):
        """Setup the differentiation tab (Lab 3)"""
        container_frame = ttk.Frame(self.differentiation_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(
            container_frame, text="Входные данные", padding="15"
        )
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Input method selection
        ttk.Label(
            input_frame, text="Способ задания функции:", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        input_methods_frame = ttk.Frame(input_frame)
        input_methods_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        self.diff_input_method_var = tk.StringVar(value="analytic")
        input_methods = [
            ("Аналитически", "analytic"),
            ("Таблично", "tabular"),
        ]

        for i, (text, value) in enumerate(input_methods):
            rb = ttk.Radiobutton(
                input_methods_frame,
                text=text,
                value=value,
                variable=self.diff_input_method_var,
                command=self.toggle_diff_input_method,
            )
            rb.grid(row=0, column=i, sticky=tk.W, padx=10)

        # Analytic function input
        self.diff_analytic_frame = ttk.Frame(input_frame)
        self.diff_analytic_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )

        ttk.Label(
            self.diff_analytic_frame, text="Функция f(x):", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.diff_function_entry = ttk.Entry(
            self.diff_analytic_frame, width=40, font=("SF Pro", 10)
        )
        self.diff_function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.diff_function_entry.insert(0, "x**2")

        ttk.Label(
            self.diff_analytic_frame,
            text="Доступные функции: sin, cos, tan, exp, sqrt, abs",
            font=("SF Pro", 8),
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        ttk.Label(
            self.diff_analytic_frame, text="Точка x:", style="Subtitle.TLabel"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.diff_x_entry = ttk.Entry(
            self.diff_analytic_frame, width=20, font=("SF Pro", 10)
        )
        self.diff_x_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.diff_x_entry.insert(0, "1.0")

        # Tabular function input
        self.diff_tabular_frame = ttk.Frame(input_frame)
        self.diff_tabular_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        self.diff_tabular_frame.grid_remove()  # Initially hidden

        ttk.Label(
            self.diff_tabular_frame,
            text="Табличные данные (x, y):",
            style="Subtitle.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5), columnspan=2)

        points_frame = ttk.Frame(self.diff_tabular_frame, borderwidth=1, relief="solid")
        points_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10), columnspan=2
        )

        self.diff_points_text = scrolledtext.ScrolledText(
            points_frame,
            wrap=tk.WORD,
            width=30,
            height=10,
            font=("SF Mono", 9),
            borderwidth=0,
        )
        self.diff_points_text.pack(fill=tk.BOTH, expand=True)
        self.diff_points_text.insert(tk.END, "0 0\n0.5 0.25\n1 1\n1.5 2.25\n2 4")

        ttk.Label(
            self.diff_tabular_frame,
            text="Точка x для дифференцирования:",
            style="Subtitle.TLabel",
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.diff_tabular_x_entry = ttk.Entry(
            self.diff_tabular_frame, width=20, font=("SF Pro", 10)
        )
        self.diff_tabular_x_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.diff_tabular_x_entry.insert(0, "1.0")

        # Common settings
        ttk.Label(
            input_frame, text="Порядок производной:", style="Subtitle.TLabel"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)

        derivative_order_frame = ttk.Frame(input_frame)
        derivative_order_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        self.derivative_order_var = tk.StringVar(value="first")
        derivative_orders = [
            ("Первая производная", "first"),
            ("Вторая производная", "second"),
        ]

        for i, (text, value) in enumerate(derivative_orders):
            rb = ttk.Radiobutton(
                derivative_order_frame,
                text=text,
                value=value,
                variable=self.derivative_order_var,
            )
            rb.grid(row=0, column=i, sticky=tk.W, padx=10)

        ttk.Label(input_frame, text="Начальный шаг h:", style="Subtitle.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.diff_h_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.diff_h_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.diff_h_entry.insert(0, "0.1")

        ttk.Label(input_frame, text="Точность (eps):", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.diff_eps_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.diff_eps_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.diff_eps_entry.insert(0, "1e-6")

        self.differentiate_button = ttk.Button(
            input_frame,
            text="Вычислить производную",
            command=self.calculate_differentiation,
            style="Rounded.TButton",
        )
        self.differentiate_button.grid(
            row=5, column=0, columnspan=2, pady=(15, 0), sticky=(tk.W, tk.E)
        )

        # Output frame
        output_frame = ttk.Frame(container_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.plot_frame_differentiation = ttk.LabelFrame(
            output_frame, text="Графики дифференцирования", padding="10"
        )
        self.plot_frame_differentiation.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        self.fig_differentiation = Figure(figsize=(10, 8), dpi=100)
        self.canvas_differentiation = FigureCanvasTkAgg(
            self.fig_differentiation, master=self.plot_frame_differentiation
        )
        self.canvas_differentiation.draw()
        self.canvas_differentiation.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        results_frame = ttk.LabelFrame(
            output_frame, text="Результаты дифференцирования", padding="10"
        )
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.differentiation_result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=80, height=20, font=("SF Mono", 9)
        )
        self.differentiation_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.differentiation_frame.columnconfigure(0, weight=1)
        self.differentiation_frame.rowconfigure(0, weight=1)
        container_frame.columnconfigure(1, weight=3)
        container_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

    def setup_equations_tab(self):
        """Setup the nonlinear equations tab (Lab 4)"""
        container_frame = ttk.Frame(self.equations_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(
            container_frame, text="Входные данные", padding="15"
        )
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(
            input_frame, text="Уравнение f(x) = 0:", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.equation_entry = ttk.Entry(input_frame, width=40, font=("SF Pro", 10))
        self.equation_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.equation_entry.insert(0, "x**2 - 4")

        ttk.Label(
            input_frame,
            text="Доступные функции: sin, cos, tan, exp, log, ln, sqrt, abs",
            font=("SF Pro", 8),
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        ttk.Label(input_frame, text="Левая граница (a):", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.eq_a_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.eq_a_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.eq_a_entry.insert(0, "0")

        ttk.Label(
            input_frame, text="Правая граница (b):", style="Subtitle.TLabel"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.eq_b_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.eq_b_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.eq_b_entry.insert(0, "3")

        ttk.Label(input_frame, text="Точность (eps):", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.eq_eps_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.eq_eps_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.eq_eps_entry.insert(0, "1e-6")

        ttk.Label(
            input_frame,
            text="Начальное приближение (для методов Ньютона и секущих):",
            style="Subtitle.TLabel",
        ).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.eq_x0_entry = ttk.Entry(input_frame, width=20, font=("SF Pro", 10))
        self.eq_x0_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        self.eq_x0_entry.insert(0, "1.0")

        # Method selection
        ttk.Label(input_frame, text="Методы:", style="Subtitle.TLabel").grid(
            row=6, column=0, sticky=tk.W, pady=5
        )

        eq_methods_frame = ttk.Frame(input_frame)
        eq_methods_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)

        self.eq_method_var = tk.StringVar(value="all")
        eq_methods = [
            ("Все методы", "all"),
            ("Метод половинного деления", "bisection"),
            ("Метод хорд", "chord"),
            ("Метод Ньютона", "newton"),
            ("Метод секущих", "secant"),
            ("Гибридный метод Ньютона-половинного деления", "hybrid"),
        ]

        for i, (text, value) in enumerate(eq_methods):
            rb = ttk.Radiobutton(
                eq_methods_frame, text=text, value=value, variable=self.eq_method_var
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)

        self.solve_equation_button = ttk.Button(
            input_frame,
            text="Решить уравнение",
            command=self.solve_equation,
            style="Rounded.TButton",
        )
        self.solve_equation_button.grid(
            row=7, column=0, columnspan=2, pady=(15, 0), sticky=(tk.W, tk.E)
        )

        # Benchmark button
        self.benchmark_button = ttk.Button(
            input_frame,
            text="Сравнительный анализ методов",
            command=self.benchmark_equation_methods,
            style="Rounded.TButton",
        )
        self.benchmark_button.grid(
            row=8, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E)
        )

        output_frame = ttk.Frame(container_frame)
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.plot_frame_equation = ttk.LabelFrame(
            output_frame, text="Графики", padding="10"
        )
        self.plot_frame_equation.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        self.fig_equation = Figure(figsize=(10, 8), dpi=100)
        self.canvas_equation = FigureCanvasTkAgg(
            self.fig_equation, master=self.plot_frame_equation
        )
        self.canvas_equation.draw()
        self.canvas_equation.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        results_frame = ttk.LabelFrame(
            output_frame, text="Результаты решения уравнения", padding="10"
        )
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.equation_result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=80, height=20, font=("SF Mono", 9)
        )
        self.equation_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.equations_frame.columnconfigure(0, weight=1)
        self.equations_frame.rowconfigure(0, weight=1)
        container_frame.columnconfigure(1, weight=3)
        container_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

    def setup_theory_tab(self):
        theory_frame = ttk.Frame(self.theory_frame, padding="15")
        theory_frame.pack(fill=tk.BOTH, expand=True)

        text_container = ttk.Frame(theory_frame, borderwidth=1, relief="solid")
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        theory_text = scrolledtext.ScrolledText(
            text_container,
            wrap=tk.WORD,
            width=100,
            height=40,
            font=("SF Pro", 10),
            borderwidth=0,
        )
        theory_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        theory_text.insert(tk.END, self.theory_content)
        theory_text.configure(state="disabled")

    def setup_help_tab(self):
        help_frame = ttk.Frame(self.help_frame, padding="15")
        help_frame.pack(fill=tk.BOTH, expand=True)

        text_container = ttk.Frame(help_frame, borderwidth=1, relief="solid")
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        help_text = scrolledtext.ScrolledText(
            text_container,
            wrap=tk.WORD,
            width=100,
            height=40,
            font=("SF Pro", 10),
            borderwidth=0,
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_text.insert(tk.END, self.help_content)
        help_text.configure(state="disabled")

    def change_theme(self, theme):
        self.theme = theme
        if theme == "light":
            self.root.configure(bg="#ffffff")
            self.style.theme_use("clam")
            self.main_frame.configure(style="Light.TFrame")
            for child in self.root.winfo_children():
                try:
                    child.configure(style="Light.TFrame")
                except tk.TclError:
                    pass
            self.notebook.configure(style="Light.TNotebook")
            for tab in (
                self.integration_frame,
                self.interpolation_frame,
                self.differentiation_frame,
                self.equations_frame,
                self.theory_frame,
                self.help_frame,
            ):
                tab.configure(style="Light.TFrame")

            # Update button styles
            self.calculate_button.configure(style="Light.TButton")
            self.interpolate_button.configure(style="Light.TButton")
            self.differentiate_button.configure(style="Light.TButton")
            self.solve_equation_button.configure(style="Light.TButton")
            self.benchmark_button.configure(style="Light.TButton")
        else:
            self.root.configure(bg="#1c1c1e")
            self.style.theme_use("clam")
            self.main_frame.configure(style="Dark.TFrame")
            for child in self.root.winfo_children():
                try:
                    child.configure(style="Dark.TFrame")
                except tk.TclError:
                    pass
            self.notebook.configure(style="Dark.TNotebook")
            for tab in (
                self.integration_frame,
                self.interpolation_frame,
                self.differentiation_frame,
                self.equations_frame,
                self.theory_frame,
                self.help_frame,
            ):
                tab.configure(style="Dark.TFrame")

            self.calculate_button.configure(style="Dark.TButton")
            self.interpolate_button.configure(style="Dark.TButton")
            self.differentiate_button.configure(style="Dark.TButton")
            self.solve_equation_button.configure(style="Dark.TButton")
            self.benchmark_button.configure(style="Dark.TButton")

        self.update_plot_style()

    def update_plot_style(self):
        for fig_attr, canvas_attr in [
            ("fig_integration", "canvas_integration"),
            ("fig_interpolation", "canvas_interpolation"),
            ("fig_differentiation", "canvas_differentiation"),
            ("fig_equation", "canvas_equation"),
        ]:
            if hasattr(self, fig_attr):
                fig = getattr(self, fig_attr)
                canvas = getattr(self, canvas_attr)

                fig.set_facecolor("#ffffff" if self.theme == "light" else "#1c1c1e")
                for ax in fig.get_axes():
                    ax.set_facecolor("#ffffff" if self.theme == "light" else "#1c1c1e")
                    ax.tick_params(
                        colors="#000000" if self.theme == "light" else "#ffffff"
                    )
                    ax.xaxis.label.set_color(
                        "#000000" if self.theme == "light" else "#ffffff"
                    )
                    ax.yaxis.label.set_color(
                        "#000000" if self.theme == "light" else "#ffffff"
                    )
                    ax.title.set_color(
                        "#000000" if self.theme == "light" else "#ffffff"
                    )

                    ax.grid(
                        True,
                        color="#e5e5ea" if self.theme == "light" else "#2c2c2e",
                        linestyle="-",
                        linewidth=0.5,
                    )

                    for spine in ax.spines.values():
                        spine.set_color(
                            "#e5e5ea" if self.theme == "light" else "#2c2c2e"
                        )

                canvas.draw()

    def toggle_diff_input_method(self):
        """Toggle between analytic and tabular input methods for differentiation"""
        if self.diff_input_method_var.get() == "analytic":
            self.diff_analytic_frame.grid()
            self.diff_tabular_frame.grid_remove()
        else:
            self.diff_analytic_frame.grid_remove()
            self.diff_tabular_frame.grid()

    def f(self, x):
        function_str = self.function_entry.get().replace("ln(", "log(")
        local_dict = {
            "x": x,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log10,
            "ln": np.log,
            "log10": np.log10,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "pi": np.pi,
            "e": np.e,
        }
        return eval(function_str, {"__builtins__": {}}, local_dict)

    def f_diff(self, x):
        """Evaluate the function for differentiation"""
        function_str = self.diff_function_entry.get().replace("ln(", "log(")
        local_dict = {
            "x": x,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log10,
            "ln": np.log,
            "log10": np.log10,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "pi": np.pi,
            "e": np.e,
        }
        return eval(function_str, {"__builtins__": {}}, local_dict)

    def f_eq(self, x):
        """Evaluate the function for equation solving"""
        function_str = self.equation_entry.get().replace("ln(", "log(")
        local_dict = {
            "x": x,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log10,
            "ln": np.log,
            "log10": np.log10,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "pi": np.pi,
            "e": np.e,
        }
        return eval(function_str, {"__builtins__": {}}, local_dict)

    def df_eq(self, x):
        """Calculate the derivative of the equation function using central difference"""
        h = 1e-6
        return (self.f_eq(x + h) - self.f_eq(x - h)) / (2 * h)

    def trapezoidal_rule(self, a, b, n):
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = self.f(x)
        return h * (0.5 * y[0] + 0.5 * y[-1] + np.sum(y[1:-1])), x, y

    def simpson_rule(self, a, b, n):
        if n % 2 != 0:
            n += 1
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = self.f(x)
        return (
            h / 3 * (y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-1:2])),
            x,
            y,
        )

    def newton_cotes(self, a, b, n):
        if n % 3 != 0:
            n = 3 * (n // 3 + 1)
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = self.f(x)

        result = 0
        for i in range(0, n, 3):
            if i + 3 <= n:
                segment_result = (
                    3 * h / 8 * (y[i] + 3 * y[i + 1] + 3 * y[i + 2] + y[i + 3])
                )
                result += segment_result

        return result, x, y

    def runge_principle(self, I1, I2, p):
        return abs(I2 - I1) / (2**p - 1)

    def integrate(self, method, a, b, eps, initial_n):
        n = initial_n
        I1, x, y = method(a, b, n)
        iterations = 1

        steps = []
        steps.append((n, I1, x, y))

        while True:
            n *= 2
            I2, x, y = method(a, b, n)

            p = 4 if method in (self.simpson_rule, self.newton_cotes) else 2
            error = self.runge_principle(I1, I2, p)

            steps.append((n, I2, x, y))

            if error < eps or iterations > 15:
                return I2, n, error, steps

            I1 = I2
            iterations += 1

    def calculate_integration(self):
        try:
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            eps = float(self.eps_entry.get())
            initial_n = 4
            selected_method = self.method_var.get()

            if a >= b:
                raise ValueError("Верхний предел должен быть больше нижнего")

            if eps <= 0:
                raise ValueError("Точность должна быть положительным числом")

            self.result_text.delete(1.0, tk.END)

            self.result_text.insert(tk.END, "🔢 ЧИСЛЕННОЕ ИНТЕГРИРОВАНИЕ\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n\n")

            self.result_text.insert(tk.END, "📝 ВХОДНЫЕ ДАННЫЕ:\n")
            self.result_text.insert(tk.END, f"• Функция: {self.function_entry.get()}\n")
            self.result_text.insert(tk.END, f"• Интервал: [{a}, {b}]\n")
            self.result_text.insert(tk.END, f"• Требуемая точность: {eps}\n")
            self.result_text.insert(tk.END, "-" * 60 + "\n\n")

            self.status_var.set("Выполняются вычисления...")
            self.root.update()

            methods = []
            if selected_method == "all" or selected_method == "trapezoidal":
                methods.append(("Метод трапеций", self.trapezoidal_rule))
            if selected_method == "all" or selected_method == "simpson":
                methods.append(("Метод Симпсона", self.simpson_rule))
            if selected_method == "all" or selected_method == "newton_cotes":
                methods.append(("Метод Ньютона-Котеса", self.newton_cotes))

            results = []

            for method_name, method in methods:
                self.result_text.insert(tk.END, f"📊 {method_name.upper()}\n")
                self.result_text.insert(tk.END, "-" * 60 + "\n\n")

                self.result_text.insert(tk.END, "Шаг 1: Начальное разбиение\n")
                n = initial_n
                h = (b - a) / n
                x = np.linspace(a, b, n + 1)
                y = self.f(x)

                self.result_text.insert(tk.END, f"• Число отрезков: {n}\n")
                self.result_text.insert(
                    tk.END, f"• Шаг h = (b-a)/n = ({b}-{a})/{n} = {h:.8f}\n\n"
                )

                self.result_text.insert(
                    tk.END, "Шаг 2: Вычисление значений функции в узлах\n"
                )
                for i in range(n + 1):
                    self.result_text.insert(
                        tk.END, f"• x[{i}] = {x[i]:.6f}, f(x[{i}]) = {y[i]:.6f}\n"
                    )

                start_time = time.time()

                if method == self.trapezoidal_rule:
                    I1 = h * (0.5 * y[0] + 0.5 * y[-1] + np.sum(y[1:-1]))
                    self.result_text.insert(
                        tk.END, "\nВычисление по формуле метода трапеций:\n"
                    )
                    self.result_text.insert(
                        tk.END, f"I1 = h * (0.5 * f(a) + 0.5 * f(b) + сумма(f(x_i)))\n"
                    )
                    self.result_text.insert(
                        tk.END,
                        f"I1 = {h:.6f} * (0.5 * {y[0]:.6f} + 0.5 * {y[-1]:.6f} + {np.sum(y[1:-1]):.6f})\n",
                    )
                elif method == self.simpson_rule:
                    if n % 2 != 0:
                        n += 1
                        h = (b - a) / n
                        x = np.linspace(a, b, n + 1)
                        y = self.f(x)
                    I1 = (
                        h
                        / 3
                        * (y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-1:2]))
                    )
                    self.result_text.insert(
                        tk.END, "\nВычисление по формуле метода Симпсона:\n"
                    )
                    self.result_text.insert(
                        tk.END,
                        f"I1 = h/3 * (f(a) + f(b) + 4*сумма(f(x_нечет)) + 2*сумма(f(x_чет)))\n",
                    )
                    self.result_text.insert(
                        tk.END,
                        f"I1 = {h:.6f}/3 * ({y[0]:.6f} + {y[-1]:.6f} + 4*{np.sum(y[1:-1:2]):.6f} + 2*{np.sum(y[2:-1:2]):.6f})\n",
                    )
                else:
                    if n % 3 != 0:
                        n = 3 * (n // 3 + 1)
                        h = (b - a) / n
                        x = np.linspace(a, b, n + 1)
                        y = self.f(x)
                    I1 = 0
                    self.result_text.insert(
                        tk.END,
                        "\nВычисление по формуле метода Ньютона-Котеса (правило 3/8):\n",
                    )
                    for i in range(0, n, 3):
                        if i + 3 <= n:
                            segment_result = (
                                3
                                * h
                                / 8
                                * (y[i] + 3 * y[i + 1] + 3 * y[i + 2] + y[i + 3])
                            )
                            self.result_text.insert(
                                tk.END,
                                f"Сегмент [{x[i]:.6f}, {x[i+3]:.6f}]: 3*{h:.6f}/8 * ({y[i]:.6f} + 3*{y[i+1]:.6f} + 3*{y[i+2]:.6f} + {y[i+3]:.6f}) = {segment_result:.10f}\n",
                            )
                            I1 += segment_result

                self.result_text.insert(
                    tk.END, f"\nПервое приближение I1 = {I1:.10f}\n\n"
                )

                self.result_text.insert(
                    tk.END, "Шаг 3: Уточнение результата (метод Рунге)\n"
                )
                iteration = 1

                I2, final_n, error, steps = self.integrate(method, a, b, eps, n)

                for i, (n_i, I_i, x_i, y_i) in enumerate(steps[1:], 1):
                    h_i = (b - a) / n_i
                    p = 4 if method in (self.simpson_rule, self.newton_cotes) else 2
                    prev_I = steps[i - 1][1]
                    error_i = self.runge_principle(prev_I, I_i, p)

                    self.result_text.insert(tk.END, f"Итерация {i}:\n")
                    self.result_text.insert(tk.END, f"• Число отрезков: {n_i}\n")
                    self.result_text.insert(tk.END, f"• Шаг: {h_i:.10f}\n")

                    if method == self.trapezoidal_rule:
                        self.result_text.insert(
                            tk.END,
                            f"• I{i+1} = {h_i:.6f} * (0.5 * {y_i[0]:.6f} + 0.5 * {y_i[-1]:.6f} + {np.sum(y_i[1:-1]):.6f})\n",
                        )
                    elif method == self.simpson_rule:
                        self.result_text.insert(
                            tk.END,
                            f"• I{i+1} = {h_i:.6f}/3 * ({y_i[0]:.6f} + {y_i[-1]:.6f} + 4*{np.sum(y_i[1:-1:2]):.6f} + 2*{np.sum(y_i[2:-1:2]):.6f})\n",
                        )
                    else:
                        self.result_text.insert(
                            tk.END, f"• I{i+1} = сумма сегментов по правилу 3/8\n"
                        )

                    self.result_text.insert(
                        tk.END, f"• Значение интеграла: {I_i:.10f}\n"
                    )
                    self.result_text.insert(
                        tk.END, f"• Погрешность: {error_i:.10e}\n\n"
                    )

                execution_time = time.time() - start_time

                self.result_text.insert(tk.END, "🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:\n")
                self.result_text.insert(tk.END, f"• Значение интеграла: {I2:.10f}\n")
                self.result_text.insert(
                    tk.END, f"• Достигнутая точность: {error:.10e}\n"
                )
                self.result_text.insert(
                    tk.END, f"• Потребовалось итераций: {len(steps)-1}\n"
                )
                self.result_text.insert(
                    tk.END, f"• Финальное число отрезков: {final_n}\n"
                )
                self.result_text.insert(
                    tk.END, f"• Время выполнения: {execution_time:.6f} сек\n"
                )
                self.result_text.insert(tk.END, "=" * 60 + "\n\n")

                results.append((method_name, I2, final_n, error, execution_time, steps))

            self.plot_integration_results(a, b, results)

            self.status_var.set("Вычисления завершены")

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Произошла ошибка при вычислениях: {str(e)}"
            )
            self.status_var.set("Ошибка вычислений")

    def plot_integration_results(self, a, b, results):
        self.fig_integration.clear()

        ax1 = self.fig_integration.add_subplot(221)
        x = np.linspace(a, b, 1000)
        y = self.f(x)
        ax1.plot(x, y, "b-", linewidth=2, label=f"f(x) = {self.function_entry.get()}")
        ax1.fill_between(x, 0, y, alpha=0.3, color="blue")
        ax1.set_title("График функции")
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.legend()
        ax1.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        if any(name == "Метод трапеций" for name, _, _, _, _, _ in results):
            ax2 = self.fig_integration.add_subplot(222)
            trap_result = next((r for r in results if r[0] == "Метод трапеций"), None)
            if trap_result:
                n = min(20, trap_result[2])
                x_trap = np.linspace(a, b, n + 1)
                y_trap = self.f(x_trap)
                ax2.plot(x, y, "b-", linewidth=1, alpha=0.5)
                ax2.plot(x_trap, y_trap, "ro-", markersize=4)
                for i in range(n):
                    ax2.add_patch(
                        plt.Polygon(
                            [
                                [x_trap[i], 0],
                                [x_trap[i], y_trap[i]],
                                [x_trap[i + 1], y_trap[i + 1]],
                                [x_trap[i + 1], 0],
                            ],
                            fill=True,
                            alpha=0.2,
                            edgecolor="r",
                            facecolor="r",
                        )
                    )
                ax2.set_title("Метод трапеций")
                ax2.set_xlabel("x")
                ax2.set_ylabel("f(x)")
                ax2.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        if any(name == "Метод Симпсона" for name, _, _, _, _, _ in results):
            ax3 = self.fig_integration.add_subplot(223)
            simp_result = next((r for r in results if r[0] == "Метод Симпсона"), None)
            if simp_result:
                n = min(20, simp_result[2])
                if n % 2 != 0:
                    n += 1
                x_simp = np.linspace(a, b, n + 1)
                y_simp = self.f(x_simp)
                ax3.plot(x, y, "b-", linewidth=1, alpha=0.5)
                ax3.plot(x_simp, y_simp, "go-", markersize=4)
                for i in range(0, n, 2):
                    xx = np.linspace(x_simp[i], x_simp[i + 2], 100)
                    p = np.polyfit(
                        [x_simp[i], x_simp[i + 1], x_simp[i + 2]],
                        [y_simp[i], y_simp[i + 1], y_simp[i + 2]],
                        2,
                    )
                    yy = np.polyval(p, xx)
                    ax3.plot(xx, yy, "g-", linewidth=1, alpha=0.7)
                    ax3.fill_between(xx, 0, yy, alpha=0.2, color="green")
                ax3.set_title("Метод Симпсона")
                ax3.set_xlabel("x")
                ax3.set_ylabel("f(x)")
                ax3.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        ax4 = self.fig_integration.add_subplot(224)
        methods = [result[0] for result in results]
        values = [result[1] for result in results]
        errors = [result[3] for result in results]

        bar_width = 0.35
        x_pos = np.arange(len(methods))

        bars1 = ax4.bar(x_pos, values, bar_width, label="Значение")

        for bar in bars1:
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.01 * max(values),
                f"{height:.6f}",
                ha="center",
                va="bottom",
                rotation=0,
                fontsize=8,
            )

        ax4.set_title("Сравнение результатов")
        ax4.set_ylabel("Значение интеграла")
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(methods, rotation=45, ha="right")

        table_data = []
        for method, value, error in zip(methods, values, errors):
            table_data.append([method, f"{error:.2e}"])

        table = ax4.table(
            cellText=table_data,
            colLabels=["Метод", "Погрешность"],
            loc="bottom",
            cellLoc="center",
            bbox=[0, -0.5, 1, 0.3],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)

        ax4.grid(True, linestyle="-", linewidth=0.5, alpha=0.7, axis="y")

        self.fig_integration.tight_layout()
        self.canvas_integration.draw()

    def lagrange_polynomial(self, data, x):
        n = len(data)
        result = 0.0

        terms = []

        for i in range(n):
            term = data[i][1]
            L_i = 1.0

            term_parts = []
            for j in range(n):
                if i != j:
                    L_i *= (x - data[j][0]) / (data[i][0] - data[j][0])
                    term_parts.append(
                        f"(x - {data[j][0]:.4f}) / ({data[i][0]:.4f} - {data[j][0]:.4f})"
                    )

            term *= L_i
            terms.append(f"{data[i][1]:.4f} * {' * '.join(term_parts)}")
            result += term

        return result, terms

    def newton_polynomial(self, data, x):
        n = len(data)
        f = np.zeros((n, n))
        for i in range(n):
            f[i][0] = data[i][1]

        divided_diff = []

        for j in range(1, n):
            for i in range(n - j):
                f[i][j] = (f[i + 1][j - 1] - f[i][j - 1]) / (
                    data[i + j][0] - data[i][0]
                )
                divided_diff.append((i, j, f[i][j]))

        result = f[0][0]
        terms = [f"{f[0][0]:.4f}"]

        for j in range(1, n):
            term = f[0][j]
            term_str = f"{f[0][j]:.4f}"

            for i in range(j):
                term *= x - data[i][0]
                term_str += f" * (x - {data[i][0]:.4f})"

            terms.append(term_str)
            result += term

        return result, terms, divided_diff

    def calculate_interpolation(self):
        try:
            points_str = self.points_text.get("1.0", tk.END).strip().split("\n")
            data = [tuple(map(float, point.split())) for point in points_str]
            x_star = float(self.x_star_entry.get())
            selected_method = self.interp_method_var.get()

            self.interpolation_result_text.delete(1.0, tk.END)
            self.interpolation_result_text.insert(tk.END, "🔢 ИНТЕРПОЛЯЦИЯ\n")
            self.interpolation_result_text.insert(tk.END, "=" * 60 + "\n\n")

            self.interpolation_result_text.insert(tk.END, "📝 ВХОДНЫЕ ДАННЫЕ:\n")
            self.interpolation_result_text.insert(
                tk.END,
                f"• Узловые точки: {', '.join([f'({x:.2f}, {y:.2f})' for x, y in data])}\n",
            )
            self.interpolation_result_text.insert(
                tk.END, f"• Точка интерполяции x*: {x_star}\n"
            )
            self.interpolation_result_text.insert(tk.END, "-" * 60 + "\n\n")

            self.status_var.set("Выполняется интерполяция...")
            self.root.update()

            lagrange_result = None
            newton_result = None
            lagrange_terms = None
            newton_terms = None
            divided_diff = None

            if selected_method in ["both", "lagrange"]:
                self.interpolation_result_text.insert(tk.END, "📊 МНОГОЧЛЕН ЛАГРАНЖА\n")
                self.interpolation_result_text.insert(tk.END, "-" * 60 + "\n\n")

                self.interpolation_result_text.insert(
                    tk.END, "Шаг 1: Вычисление базисных полиномов\n"
                )
                for i in range(len(data)):
                    self.interpolation_result_text.insert(tk.END, f"L_{i}(x) = ")
                    terms = []
                    for j in range(len(data)):
                        if i != j:
                            terms.append(
                                f"(x - {data[j][0]:.4f}) / ({data[i][0]:.4f} - {data[j][0]:.4f})"
                            )
                    self.interpolation_result_text.insert(
                        tk.END, " * ".join(terms) + "\n"
                    )

                self.interpolation_result_text.insert(
                    tk.END, "\nШаг 2: Построение многочлена Лагранжа\n"
                )
                self.interpolation_result_text.insert(tk.END, "L(x) = ")
                terms = [f"{data[i][1]:.4f} * L_{i}(x)" for i in range(len(data))]
                self.interpolation_result_text.insert(
                    tk.END, " + ".join(terms) + "\n\n"
                )

                lagrange_result, lagrange_terms = self.lagrange_polynomial(data, x_star)
                self.interpolation_result_text.insert(
                    tk.END, f"Шаг 3: Вычисление значения в точке x* = {x_star}\n"
                )
                self.interpolation_result_text.insert(
                    tk.END, "L(x*) = " + " + ".join(lagrange_terms) + "\n"
                )
                self.interpolation_result_text.insert(
                    tk.END, f"L({x_star}) = {lagrange_result:.10f}\n\n"
                )

            if selected_method in ["both", "newton"]:
                self.interpolation_result_text.insert(tk.END, "📊 МНОГОЧЛЕН НЬЮТОНА\n")
                self.interpolation_result_text.insert(tk.END, "-" * 60 + "\n\n")

                self.interpolation_result_text.insert(
                    tk.END, "Шаг 1: Вычисление разделенных разностей\n"
                )
                newton_result, newton_terms, divided_diff = self.newton_polynomial(
                    data, x_star
                )

                self.interpolation_result_text.insert(
                    tk.END, "Таблица разделенных разностей:\n"
                )
                n = len(data)
                f = np.zeros((n, n))
                for i in range(n):
                    f[i][0] = data[i][1]

                header = "i | x_i | f[x_i]"
                for j in range(1, n):
                    header += f" | f[x_i,...,x_{i+j}]"
                self.interpolation_result_text.insert(tk.END, header + "\n")
                self.interpolation_result_text.insert(tk.END, "-" * len(header) + "\n")

                for i in range(n):
                    row = f"{i} | {data[i][0]:.4f} | {f[i][0]:.6f}"
                    for j in range(1, n):
                        if i < n - j:
                            row += f" | {f[i][j]:.6f}"
                        else:
                            row += " | -"
                    self.interpolation_result_text.insert(tk.END, row + "\n")

                self.interpolation_result_text.insert(
                    tk.END, "\nРазделенные разности первого порядка:\n"
                )
                for i, j, val in divided_diff:
                    if j == 1:
                        self.interpolation_result_text.insert(
                            tk.END,
                            f"f[x{i},x{i+1}] = (f[x{i+1}] - f[x{i}]) / (x{i+1} - x{i}) = ",
                        )
                        self.interpolation_result_text.insert(
                            tk.END,
                            f"({data[i+1][1]:.6f} - {data[i][1]:.6f}) / ({data[i+1][0]:.6f} - {data[i][0]:.6f}) = {val:.6f}\n",
                        )

                self.interpolation_result_text.insert(
                    tk.END, "\nРазделенные разности высших порядков:\n"
                )
                for i, j, val in divided_diff:
                    if j > 1:
                        self.interpolation_result_text.insert(
                            tk.END,
                            f"f[x{i},...,x{i+j}] = (f[x{i+1},...,x{i+j}] - f[x{i},...,x{i+j-1}]) / (x{i+j} - x{i}) = {val:.6f}\n",
                        )

                self.interpolation_result_text.insert(
                    tk.END, "\nШаг 2: Построение многочлена Ньютона\n"
                )
                self.interpolation_result_text.insert(
                    tk.END, "N(x) = " + " + ".join(newton_terms) + "\n\n"
                )

                self.interpolation_result_text.insert(
                    tk.END, f"Шаг 3: Вычисление значения в точке x* = {x_star}\n"
                )
                self.interpolation_result_text.insert(
                    tk.END, f"N({x_star}) = {newton_result:.10f}\n\n"
                )

            if selected_method == "both":
                self.interpolation_result_text.insert(
                    tk.END, "🎯 СРАВНЕНИЕ РЕЗУЛЬТАТОВ:\n"
                )
                self.interpolation_result_text.insert(tk.END, "-" * 60 + "\n")
                self.interpolation_result_text.insert(
                    tk.END,
                    f"• Многочлен Лагранжа: L({x_star}) = {lagrange_result:.10f}\n",
                )
                self.interpolation_result_text.insert(
                    tk.END, f"• Многочлен Ньютона: N({x_star}) = {newton_result:.10f}\n"
                )
                self.interpolation_result_text.insert(
                    tk.END,
                    f"• Разница |L(x*) - N(x*)|: {abs(lagrange_result - newton_result):.10e}\n",
                )

            self.plot_interpolation_results(
                data, x_star, lagrange_result, newton_result
            )

            self.status_var.set("Интерполяция завершена")

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Произошла ошибка при интерполяции: {str(e)}"
            )
            self.status_var.set("Ошибка интерполяции")

    def plot_interpolation_results(self, data, x_star, lagrange_result, newton_result):
        self.fig_interpolation.clear()

        ax1 = self.fig_interpolation.add_subplot(221)
        x = np.array([point[0] for point in data])
        y = np.array([point[1] for point in data])
        x_interp = np.linspace(min(x) - 0.5, max(x) + 0.5, 1000)

        y_lagrange = None
        y_newton = None

        if lagrange_result is not None:
            y_lagrange = np.array(
                [self.lagrange_polynomial(data, xi)[0] for xi in x_interp]
            )
            ax1.plot(
                x_interp, y_lagrange, "b-", linewidth=2, label="Многочлен Лагранжа"
            )
            ax1.plot(
                x_star,
                lagrange_result,
                "b*",
                markersize=10,
                label="Интерполяция (Лагранж)",
            )

        if newton_result is not None:
            y_newton = np.array(
                [self.newton_polynomial(data, xi)[0] for xi in x_interp]
            )
            ax1.plot(x_interp, y_newton, "g--", linewidth=2, label="Многочлен Ньютона")
            ax1.plot(
                x_star,
                newton_result,
                "g*",
                markersize=10,
                label="Интерполяция (Ньютон)",
            )

        ax1.plot(x, y, "ro", markersize=8, label="Узловые точки")
        ax1.set_title("Интерполяция")
        ax1.set_xlabel("x")
        ax1.set_ylabel("y")
        ax1.legend()
        ax1.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        if lagrange_result is not None and newton_result is not None:
            ax2 = self.fig_interpolation.add_subplot(222)
            error = np.abs(y_lagrange - y_newton)
            ax2.semilogy(x_interp, error, "r-", linewidth=2, label="|Лагранж - Ньютон|")
            ax2.set_title("Погрешность интерполяции")
            ax2.set_xlabel("x")
            ax2.set_ylabel("|L(x) - N(x)|")
            ax2.legend()
            ax2.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        if lagrange_result is not None:
            ax3 = self.fig_interpolation.add_subplot(223)
            for i in range(len(data)):
                y_basis = [1.0 if j == i else 0.0 for j in range(len(data))]
                basis_data = list(zip(x, y_basis))
                basis_poly = np.array(
                    [self.lagrange_polynomial(basis_data, xi)[0] for xi in x_interp]
                )
                ax3.plot(x_interp, basis_poly, label=f"L_{i}(x)")
            ax3.set_title("Базисные функции Лагранжа")
            ax3.set_xlabel("x")
            ax3.set_ylabel("L_i(x)")
            ax3.legend()
            ax3.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)

        if newton_result is not None:
            ax4 = self.fig_interpolation.add_subplot(224)
            n = len(data)
            divided_diff = np.zeros((n, n))
            for i in range(n):
                divided_diff[i][0] = data[i][1]
            for j in range(1, n):
                for i in range(n - j):
                    divided_diff[i][j] = (
                        divided_diff[i + 1][j - 1] - divided_diff[i][j - 1]
                    ) / (data[i + j][0] - data[i][0])

            im = ax4.imshow(divided_diff, cmap="viridis", aspect="auto")
            ax4.set_title("Таблица разделенных разностей")
            ax4.set_xlabel("Порядок разности")
            ax4.set_ylabel("Индекс начальной точки")
            self.fig_interpolation.colorbar(im, ax=ax4)

            ax4.set_xticks(np.arange(n))
            ax4.set_yticks(np.arange(n))
            ax4.set_xticklabels([f"{i}" for i in range(n)])
            ax4.set_yticklabels([f"{i}" for i in range(n)])

        self.fig_interpolation.tight_layout()
        self.canvas_interpolation.draw()

    def calculate_differentiation(self):
        """Calculate numerical differentiation (Lab 3)"""
        try:
            h = float(self.diff_h_entry.get())
            eps = float(self.diff_eps_entry.get())
            derivative_order = self.derivative_order_var.get()
            input_method = self.diff_input_method_var.get()

            if input_method == "analytic":
                x = float(self.diff_x_entry.get())
                function_str = self.diff_function_entry.get()
                x_sym = sp.Symbol("x")
                f_sym = sp.sympify(function_str.replace("^", "**"))
                if derivative_order == "first":
                    df_sym = sp.diff(f_sym, x_sym)
                    exact_derivative = float(df_sym.subs(x_sym, x))
                else:
                    df_sym = sp.diff(f_sym, x_sym, 2)
                    exact_derivative = float(df_sym.subs(x_sym, x))

                x_range = np.linspace(x - 2, x + 2, 1000)
                y_range = np.array([self.f_diff(xi) for xi in x_range])

                data = [
                    (x - 2 * h, self.f_diff(x - 2 * h)),
                    (x - h, self.f_diff(x - h)),
                    (x, self.f_diff(x)),
                    (x + h, self.f_diff(x + h)),
                    (x + 2 * h, self.f_diff(x + 2 * h)),
                ]
            else:
                points_str = (
                    self.diff_points_text.get("1.0", tk.END).strip().split("\n")
                )
                data = [tuple(map(float, point.split())) for point in points_str]
                data.sort(key=lambda point: point[0])

                x = float(self.diff_tabular_x_entry.get())

                if x < data[0][0] or x > data[-1][0]:
                    raise ValueError(
                        "Точка x должна быть в пределах диапазона табличных данных"
                    )

                x_data = np.array([point[0] for point in data])
                y_data = np.array([point[1] for point in data])

                poly = np.polyfit(x_data, y_data, len(data) - 1)
                poly_derivative = np.polyder(
                    poly, 1 if derivative_order == "first" else 2
                )
                exact_derivative = np.polyval(poly_derivative, x)

                x_range = np.linspace(min(x_data), max(x_data), 1000)
                y_range = np.polyval(poly, x_range)

                function_str = "Табличная функция"

            self.differentiation_result_text.delete(1.0, tk.END)
            self.differentiation_result_text.insert(
                tk.END, "🔢 ЧИСЛЕННОЕ ДИФФЕРЕНЦИРОВАНИЕ\n"
            )
            self.differentiation_result_text.insert(tk.END, "=" * 60 + "\n\n")

            self.differentiation_result_text.insert(tk.END, "📝 ВХОДНЫЕ ДАННЫЕ:\n")
            self.differentiation_result_text.insert(
                tk.END, f"• Функция: {function_str}\n"
            )
            self.differentiation_result_text.insert(tk.END, f"• Точка x: {x}\n")
            self.differentiation_result_text.insert(
                tk.END,
                f"• Порядок производной: {'Первый' if derivative_order == 'first' else 'Второй'}\n",
            )
            self.differentiation_result_text.insert(tk.END, f"• Начальный шаг h: {h}\n")
            self.differentiation_result_text.insert(
                tk.END, f"• Требуемая точность: {eps}\n"
            )
            self.differentiation_result_text.insert(tk.END, "-" * 60 + "\n\n")

            self.status_var.set("Выполняется дифференцирование...")
            self.root.update()

            self.differentiation_result_text.insert(
                tk.END, "Таблица значений функции:\n"
            )
            self.differentiation_result_text.insert(tk.END, "-" * 30 + "\n")
            self.differentiation_result_text.insert(tk.END, "    x    |    f(x)    \n")
            self.differentiation_result_text.insert(tk.END, "-" * 30 + "\n")

            for x_val, y_val in data:
                self.differentiation_result_text.insert(
                    tk.END, f" {x_val:8.4f} | {y_val:10.6f}\n"
                )

            self.differentiation_result_text.insert(tk.END, "\n")

            results = []

            if derivative_order == "first":
                formulas = [
                    (
                        "Левая разностная",
                        lambda x, h: (self.f_diff(x) - self.f_diff(x - h)) / h,
                    ),
                    (
                        "Правая разностная",
                        lambda x, h: (self.f_diff(x + h) - self.f_diff(x)) / h,
                    ),
                    (
                        "Центральная разностная",
                        lambda x, h: (self.f_diff(x + h) - self.f_diff(x - h))
                        / (2 * h),
                    ),
                    (
                        "Трехточечная",
                        lambda x, h: (
                            -3 * self.f_diff(x)
                            + 4 * self.f_diff(x + h)
                            - self.f_diff(x + 2 * h)
                        )
                        / (2 * h),
                    ),
                ]

                if input_method == "tabular":

                    def tabular_f(x_val):
                        for i, (xi, yi) in enumerate(data):
                            if abs(xi - x_val) < 1e-10:
                                return yi
                        return np.interp(
                            x_val, [p[0] for p in data], [p[1] for p in data]
                        )

                    formulas = [
                        (
                            "Левая разностная",
                            lambda x, h: (tabular_f(x) - tabular_f(x - h)) / h,
                        ),
                        (
                            "Правая разностная",
                            lambda x, h: (tabular_f(x + h) - tabular_f(x)) / h,
                        ),
                        (
                            "Центральная разностная",
                            lambda x, h: (tabular_f(x + h) - tabular_f(x - h))
                            / (2 * h),
                        ),
                        (
                            "Трехточечная",
                            lambda x, h: (
                                -3 * tabular_f(x)
                                + 4 * tabular_f(x + h)
                                - tabular_f(x + 2 * h)
                            )
                            / (2 * h),
                        ),
                    ]
            else:
                formulas = [
                    (
                        "Центральная разностная",
                        lambda x, h: (
                            self.f_diff(x + h) - 2 * self.f_diff(x) + self.f_diff(x - h)
                        )
                        / (h**2),
                    ),
                    (
                        "Пятиточечная",
                        lambda x, h: (
                            -self.f_diff(x + 2 * h)
                            + 16 * self.f_diff(x + h)
                            - 30 * self.f_diff(x)
                            + 16 * self.f_diff(x - h)
                            - self.f_diff(x - 2 * h)
                        )
                        / (12 * h**2),
                    ),
                ]

                if input_method == "tabular":

                    def tabular_f(x_val):
                        for i, (xi, yi) in enumerate(data):
                            if abs(xi - x_val) < 1e-10:
                                return yi
                        return np.interp(
                            x_val, [p[0] for p in data], [p[1] for p in data]
                        )

                    formulas = [
                        (
                            "Центральная разностная",
                            lambda x, h: (
                                tabular_f(x + h) - 2 * tabular_f(x) + tabular_f(x - h)
                            )
                            / (h**2),
                        ),
                        (
                            "Пятиточечная",
                            lambda x, h: (
                                -tabular_f(x + 2 * h)
                                + 16 * tabular_f(x + h)
                                - 30 * tabular_f(x)
                                + 16 * tabular_f(x - h)
                                - tabular_f(x - 2 * h)
                            )
                            / (12 * h**2),
                        ),
                    ]

            self.differentiation_result_text.insert(
                tk.END, "Вычисление производной с разными шагами:\n"
            )
            self.differentiation_result_text.insert(tk.END, "-" * 80 + "\n")
            self.differentiation_result_text.insert(
                tk.END,
                "Метод                  | Шаг h      | Значение производной | Погрешность\n",
            )
            self.differentiation_result_text.insert(tk.END, "-" * 80 + "\n")

            h_values = []
            errors = {formula[0]: [] for formula in formulas}
            derivative_values = {formula[0]: [] for formula in formulas}

            current_h = h
            for i in range(10):
                h_values.append(current_h)

                for name, formula in formulas:
                    try:
                        derivative = formula(x, current_h)
                        error = abs(derivative - exact_derivative)

                        self.differentiation_result_text.insert(
                            tk.END,
                            f"{name:22} | {current_h:10.8f} | {derivative:20.10f} | {error:10.8e}\n",
                        )

                        errors[name].append(error)
                        derivative_values[name].append(derivative)
                    except Exception as e:
                        self.differentiation_result_text.insert(
                            tk.END,
                            f"{name:22} | {current_h:10.8f} | {'Ошибка вычисления':20} | {'N/A':10}\n",
                        )
                        errors[name].append(np.nan)
                        derivative_values[name].append(np.nan)

                self.differentiation_result_text.insert(tk.END, "-" * 80 + "\n")
                current_h /= 2

            self.differentiation_result_text.insert(
                tk.END, "\nОпределение оптимального шага по принципу Рунге:\n"
            )

            best_h = {}
            best_derivative = {}
            best_error = {}

            for name, formula in formulas:
                min_error = float("inf")
                optimal_h = h
                optimal_derivative = None

                for i in range(len(h_values) - 1):
                    if np.isnan(errors[name][i]) or np.isnan(errors[name][i + 1]):
                        continue

                    p = 1 if "Левая" in name or "Правая" in name else 2
                    runge_error = abs(
                        derivative_values[name][i + 1] - derivative_values[name][i]
                    ) / (2**p - 1)

                    if runge_error < min_error:
                        min_error = runge_error
                        optimal_h = h_values[i + 1]
                        optimal_derivative = derivative_values[name][i + 1]

                best_h[name] = optimal_h
                best_derivative[name] = optimal_derivative
                best_error[name] = min_error

                self.differentiation_result_text.insert(
                    tk.END,
                    f"{name}: оптимальный шаг h = {optimal_h:.8f}, производная = {optimal_derivative:.10f}, погрешность = {min_error:.8e}\n",
                )

            self.differentiation_result_text.insert(
                tk.END, "\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:\n"
            )
            self.differentiation_result_text.insert(tk.END, "-" * 60 + "\n")

            if input_method == "analytic":
                self.differentiation_result_text.insert(
                    tk.END, f"• Точное значение производной: {exact_derivative:.10f}\n"
                )
            else:
                self.differentiation_result_text.insert(
                    tk.END,
                    f"• Интерполированное значение производной: {exact_derivative:.10f}\n",
                )

            for name in best_derivative:
                self.differentiation_result_text.insert(
                    tk.END,
                    f"• {name}: {best_derivative[name]:.10f} (h = {best_h[name]:.8f}, погрешность = {best_error[name]:.8e})\n",
                )

            self.plot_differentiation_results(
                x,
                x_range,
                y_range,
                derivative_order,
                h_values,
                errors,
                derivative_values,
                exact_derivative,
                best_h,
            )

            self.status_var.set("Дифференцирование завершено")

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Произошла ошибка при дифференцировании: {str(e)}"
            )
            self.status_var.set("Ошибка дифференцирования")

    def plot_differentiation_results(
        self,
        x,
        x_range,
        y_range,
        derivative_order,
        h_values,
        errors,
        derivative_values,
        exact_derivative,
        best_h,
    ):
        """Plot differentiation results"""
        self.fig_differentiation.clear()

        ax1 = self.fig_differentiation.add_subplot(221)
        ax1.plot(x_range, y_range, "b-", linewidth=2, label="f(x)")
        ax1.axvline(x=x, color="r", linestyle="--", label=f"x = {x}")
        ax1.set_title("График функции")
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.legend()
        ax1.grid(True)

        ax2 = self.fig_differentiation.add_subplot(222)
        for name in errors:
            valid_indices = ~np.isnan(np.array(errors[name]))
            if np.any(valid_indices):
                valid_h = np.array(h_values)[valid_indices]
                valid_errors = np.array(errors[name])[valid_indices]
                ax2.loglog(valid_h, valid_errors, "o-", label=name)

                if name in best_h:
                    optimal_idx = np.where(np.array(h_values) == best_h[name])[0]
                    if len(optimal_idx) > 0:
                        ax2.plot(
                            best_h[name],
                            errors[name][optimal_idx[0]],
                            "r*",
                            markersize=10,
                        )

        ax2.set_title("Зависимость погрешности от шага")
        ax2.set_xlabel("Шаг h")
        ax2.set_ylabel("Погрешность")
        ax2.legend()
        ax2.grid(True)

        ax3 = self.fig_differentiation.add_subplot(223)
        for name in derivative_values:
            valid_indices = ~np.isnan(np.array(derivative_values[name]))
            if np.any(valid_indices):
                valid_h = np.array(h_values)[valid_indices]
                valid_derivatives = np.array(derivative_values[name])[valid_indices]
                ax3.semilogx(valid_h, valid_derivatives, "o-", label=name)

        ax3.axhline(
            y=exact_derivative, color="k", linestyle="--", label="Точное значение"
        )

        ax3.set_title(
            f'Значения {"первой" if derivative_order == "first" else "второй"} производной'
        )
        ax3.set_xlabel("Шаг h")
        ax3.set_ylabel(f'f{"'" if derivative_order == "first" else "''"} (x)')
        ax3.legend()
        ax3.grid(True)

        ax4 = self.fig_differentiation.add_subplot(224)
        names = list(best_h.keys())
        values = [
            (
                derivative_values[name][h_values.index(best_h[name])]
                if name in best_h
                else np.nan
            )
            for name in names
        ]
        errors_at_best = [
            errors[name][h_values.index(best_h[name])] if name in best_h else np.nan
            for name in names
        ]

        x_pos = np.arange(len(names))
        ax4.bar(x_pos, values, align="center", alpha=0.7)
        ax4.axhline(
            y=exact_derivative, color="r", linestyle="--", label="Точное значение"
        )

        ax4.set_title("Сравнение методов (оптимальный шаг)")
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(names, rotation=45, ha="right")
        ax4.set_ylabel(f'f{"'" if derivative_order == "first" else "''"} (x)')

        for i, v in enumerate(values):
            if not np.isnan(v):
                ax4.text(
                    i,
                    v + 0.01 * max(values),
                    f"{errors_at_best[i]:.1e}",
                    ha="center",
                    va="bottom",
                    rotation=0,
                    fontsize=8,
                )

        self.fig_differentiation.tight_layout()
        self.canvas_differentiation.draw()

    def solve_equation(self):
        """Solve nonlinear equation using selected method(s)"""
        try:
            a = float(self.eq_a_entry.get())
            b = float(self.eq_b_entry.get())
            eps = float(self.eq_eps_entry.get())
            x0 = float(self.eq_x0_entry.get())
            selected_method = self.eq_method_var.get()

            # Validate input
            if a >= b:
                raise ValueError("Правая граница должна быть больше левой")

            if eps <= 0:
                raise ValueError("Точность должна быть положительным числом")

            fa = self.f_eq(a)
            fb = self.f_eq(b)

            if fa * fb > 0 and selected_method in [
                "all",
                "bisection",
                "chord",
                "hybrid",
            ]:
                messagebox.showwarning(
                    "Предупреждение",
                    "Функция имеет одинаковый знак на концах отрезка. Методы половинного деления, хорд и гибридный могут не сработать.",
                )

            self.equation_result_text.delete(1.0, tk.END)
            self.equation_result_text.insert(
                tk.END, "🔢 РЕШЕНИЕ НЕЛИНЕЙНОГО УРАВНЕНИЯ\n"
            )
            self.equation_result_text.insert(tk.END, "=" * 60 + "\n\n")

            self.equation_result_text.insert(tk.END, "📝 ВХОДНЫЕ ДАННЫЕ:\n")
            self.equation_result_text.insert(
                tk.END, f"• Уравнение: {self.equation_entry.get()} = 0\n"
            )
            self.equation_result_text.insert(tk.END, f"• Интервал: [{a}, {b}]\n")
            self.equation_result_text.insert(
                tk.END, f"• Начальное приближение x₀: {x0}\n"
            )
            self.equation_result_text.insert(tk.END, f"• Требуемая точность: {eps}\n")
            self.equation_result_text.insert(tk.END, "-" * 60 + "\n\n")

            self.status_var.set("Решение уравнения...")
            self.root.update()

            methods = []
            if selected_method == "all" or selected_method == "bisection":
                methods.append(("Метод половинного деления", self.bisection_method))
            if selected_method == "all" or selected_method == "chord":
                methods.append(("Метод хорд", self.chord_method))
            if selected_method == "all" or selected_method == "newton":
                methods.append(("Метод Ньютона", self.newton_method))
            if selected_method == "all" or selected_method == "secant":
                methods.append(("Метод секущих", self.secant_method))
            if selected_method == "all" or selected_method == "hybrid":
                methods.append(
                    ("Гибридный метод Ньютона-половинного деления", self.hybrid_method)
                )

            results = []

            for method_name, method in methods:
                self.equation_result_text.insert(tk.END, f"📊 {method_name.upper()}\n")
                self.equation_result_text.insert(tk.END, "-" * 60 + "\n\n")

                start_time = time.time()

                if method_name == "Метод Ньютона" or method_name == "Метод секущих":
                    root, iterations, convergence_data = method(a, b, eps, x0)
                else:
                    root, iterations, convergence_data = method(a, b, eps)

                execution_time = time.time() - start_time

                self.equation_result_text.insert(tk.END, "Итерации:\n")
                self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                if method_name == "Метод половинного деления":
                    self.equation_result_text.insert(
                        tk.END,
                        "  k  |     a     |     b     |     c     |    f(c)    |   |b-a|   \n",
                    )
                    self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                    for i, (a_i, b_i, c_i, fc_i, interval) in enumerate(
                        convergence_data
                    ):
                        self.equation_result_text.insert(
                            tk.END,
                            f" {i:3d} | {a_i:9.6f} | {b_i:9.6f} | {c_i:9.6f} | {fc_i:10.6e} | {interval:9.6e}\n",
                        )

                elif method_name == "Метод хорд":
                    self.equation_result_text.insert(
                        tk.END,
                        "  k  |     a     |     b     |     c     |    f(c)    |   |c-c_prev|   \n",
                    )
                    self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                    for i, (a_i, b_i, c_i, fc_i, delta) in enumerate(convergence_data):
                        self.equation_result_text.insert(
                            tk.END,
                            f" {i:3d} | {a_i:9.6f} | {b_i:9.6f} | {c_i:9.6f} | {fc_i:10.6e} | {delta if i > 0 else 'N/A':15}\n",
                        )

                elif method_name == "Метод Ньютона":
                    self.equation_result_text.insert(
                        tk.END,
                        "  k  |     x_k    |    f(x_k)   |   f'(x_k)   |   |x_k - x_{k-1}|   \n",
                    )
                    self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                    for i, (x_i, fx_i, dfx_i, delta) in enumerate(convergence_data):
                        self.equation_result_text.insert(
                            tk.END,
                            f" {i:3d} | {x_i:10.6f} | {fx_i:11.6e} | {dfx_i:11.6e} | {delta if i > 0 else 'N/A':17}\n",
                        )

                elif method_name == "Метод секущих":
                    self.equation_result_text.insert(
                        tk.END,
                        "  k  |    x_{k-1}   |     x_k     |    f(x_k)    |   |x_k - x_{k-1}|   \n",
                    )
                    self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                    for i, (x_prev, x_i, fx_i, delta) in enumerate(convergence_data):
                        self.equation_result_text.insert(
                            tk.END,
                            f" {i:3d} | {x_prev:12.6f} | {x_i:12.6f} | {fx_i:12.6e} | {delta if i > 0 else 'N/A':17}\n",
                        )

                elif method_name == "Гибридный метод Ньютона-половинного деления":
                    self.equation_result_text.insert(
                        tk.END,
                        "  k  |     a     |     b     |     x     |    f(x)    |   метод   |   |x_k - x_{k-1}|   \n",
                    )
                    self.equation_result_text.insert(tk.END, "-" * 100 + "\n")

                    for i, (a_i, b_i, x_i, fx_i, method_used, delta) in enumerate(
                        convergence_data
                    ):
                        self.equation_result_text.insert(
                            tk.END,
                            f" {i:3d} | {a_i:9.6f} | {b_i:9.6f} | {x_i:9.6f} | {fx_i:10.6e} | {method_used:9} | {delta if i > 0 else 'N/A':17}\n",
                        )

                # Summary
                self.equation_result_text.insert(tk.END, "\n🎯 РЕЗУЛЬТАТ:\n")
                self.equation_result_text.insert(
                    tk.END, f"• Корень уравнения: {root:.10f}\n"
                )
                self.equation_result_text.insert(
                    tk.END, f"• Значение функции: {self.f_eq(root):.10e}\n"
                )
                self.equation_result_text.insert(
                    tk.END, f"• Число итераций: {iterations}\n"
                )
                self.equation_result_text.insert(
                    tk.END, f"• Время выполнения: {execution_time:.6f} сек\n"
                )
                self.equation_result_text.insert(tk.END, "=" * 60 + "\n\n")

                results.append(
                    (method_name, root, iterations, execution_time, convergence_data)
                )

            self.plot_equation_results(a, b, results)

            self.status_var.set("Решение уравнения завершено")

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Произошла ошибка при решении уравнения: {str(e)}"
            )
            self.status_var.set("Ошибка решения уравнения")

    def bisection_method(self, a, b, eps):
        """Bisection method for solving nonlinear equations"""
        fa = self.f_eq(a)
        fb = self.f_eq(b)

        if fa * fb > 0:
            raise ValueError("Функция должна иметь разные знаки на концах отрезка")

        iterations = 0
        convergence_data = []

        while (b - a) > eps:
            c = (a + b) / 2
            fc = self.f_eq(c)

            convergence_data.append((a, b, c, fc, b - a))

            if abs(fc) < eps:
                break

            if fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc

            iterations += 1

            if iterations > 1000:
                break

        root = (a + b) / 2
        return root, iterations, convergence_data

    def chord_method(self, a, b, eps):
        """Chord method for solving nonlinear equations"""
        fa = self.f_eq(a)
        fb = self.f_eq(b)

        if fa * fb > 0:
            raise ValueError("Функция должна иметь разные знаки на концах отрезка")

        iterations = 0
        c_prev = a
        c = a - fa * (b - a) / (fb - fa)

        convergence_data = [(a, b, c, self.f_eq(c), None)]

        while abs(c - c_prev) > eps:
            fc = self.f_eq(c)

            if abs(fc) < eps:
                break

            if fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc

            c_prev = c
            c = a - fa * (b - a) / (fb - fa)

            convergence_data.append((a, b, c, self.f_eq(c), abs(c - c_prev)))

            iterations += 1

            if iterations > 1000:
                break

        return c, iterations, convergence_data

    def newton_method(self, a, b, eps, x0):
        """Newton's method for solving nonlinear equations"""
        if x0 < a or x0 > b:
            x0 = (a + b) / 2

        iterations = 0
        x = x0

        convergence_data = []

        while True:
            fx = self.f_eq(x)
            dfx = self.df_eq(x)

            if abs(dfx) < 1e-10:
                raise ValueError("Производная близка к нулю, метод Ньютона не сходится")

            x_new = x - fx / dfx

            if iterations > 0:
                delta = abs(x_new - x)
                convergence_data.append((x, fx, dfx, delta))
            else:
                convergence_data.append((x, fx, dfx, None))

            if abs(x_new - x) < eps or abs(fx) < eps:
                x = x_new
                break

            x = x_new
            iterations += 1

            if iterations > 1000:
                break

            if x < a or x > b:
                raise ValueError(f"Решение вышло за пределы отрезка [{a}, {b}]")

        return x, iterations, convergence_data

    def secant_method(self, a, b, eps, x0):
        """Secant method for solving nonlinear equations"""
        if x0 < a or x0 > b:
            x0 = (a + b) / 2

        iterations = 0
        x_prev = x0
        x = x0 + 0.1 * abs(x0)

        if x < a or x > b:
            x = x0 - 0.1 * abs(x0)

        convergence_data = [(x_prev, x, self.f_eq(x), None)]

        while True:
            fx_prev = self.f_eq(x_prev)
            fx = self.f_eq(x)

            if abs(fx - fx_prev) < 1e-10:
                raise ValueError(
                    "Разность значений функции близка к нулю, метод секущих не сходится"
                )

            x_new = x - fx * (x - x_prev) / (fx - fx_prev)

            delta = abs(x_new - x)
            convergence_data.append((x, x_new, self.f_eq(x_new), delta))

            if delta < eps or abs(fx) < eps:
                x = x_new
                break

            x_prev = x
            x = x_new
            iterations += 1

            if iterations > 1000:
                break

            if x < a or x > b:
                raise ValueError(f"Решение вышло за пределы отрезка [{a}, {b}]")

        return x, iterations, convergence_data

    def hybrid_method(self, a, b, eps):
        """Hybrid Newton-bisection method for solving nonlinear equations"""
        fa = self.f_eq(a)
        fb = self.f_eq(b)

        if fa * fb > 0:
            raise ValueError("Функция должна иметь разные знаки на концах отрезка")

        iterations = 0
        x = (a + b) / 2

        convergence_data = [(a, b, x, self.f_eq(x), "Бисекция", None)]

        while (b - a) > eps:
            fx = self.f_eq(x)

            if abs(fx) < eps:
                break

            dfx = self.df_eq(x)

            if abs(dfx) > 1e-10:
                x_newton = x - fx / dfx

                if a <= x_newton <= b and abs(x_newton - x) < 0.5 * (b - a):
                    x_prev = x
                    x = x_newton
                    method_used = "Ньютон"
                else:
                    c = (a + b) / 2
                    fc = self.f_eq(c)

                    if fa * fc < 0:
                        b = c
                        fb = fc
                    else:
                        a = c
                        fa = fc

                    x_prev = x
                    x = (a + b) / 2
                    method_used = "Бисекция"
            else:
                c = (a + b) / 2
                fc = self.f_eq(c)

                if fa * fc < 0:
                    b = c
                    fb = fc
                else:
                    a = c
                    fa = fc

                x_prev = x
                x = (a + b) / 2
                method_used = "Бисекция"

            if iterations > 0:
                delta = abs(x - x_prev)
                convergence_data.append((a, b, x, self.f_eq(x), method_used, delta))
            else:
                convergence_data.append((a, b, x, self.f_eq(x), method_used, None))

            iterations += 1

            if iterations > 1000:
                break

        return x, iterations, convergence_data

    def plot_equation_results(self, a, b, results):
        """Plot equation solving results"""
        self.fig_equation.clear()

        margin = 0.2 * (b - a)
        x_min = a - margin
        x_max = b + margin

        ax1 = self.fig_equation.add_subplot(221)
        x = np.linspace(x_min, x_max, 1000)
        y = np.array([self.f_eq(xi) for xi in x])

        ax1.plot(x, y, "b-", linewidth=2, label="f(x)")
        ax1.axhline(y=0, color="k", linestyle="-", alpha=0.3)
        ax1.axvline(x=a, color="r", linestyle="--", alpha=0.5, label=f"a = {a}")
        ax1.axvline(x=b, color="g", linestyle="--", alpha=0.5, label=f"b = {b}")

        for method_name, root, _, _, _ in results:
            ax1.plot(root, 0, "ro", markersize=6)
            ax1.annotate(
                f"{method_name}: x = {root:.6f}",
                xy=(root, 0),
                xytext=(root, self.f_eq(root) * 0.5),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
            )

        ax1.set_title("График функции")
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.legend()
        ax1.grid(True)

        ax2 = self.fig_equation.add_subplot(222)

        for method_name, _, _, _, convergence_data in results:
            if method_name == "Метод половинного деления":
                iterations = range(len(convergence_data))
                errors = [data[4] for data in convergence_data]  # |b-a|
                ax2.semilogy(iterations, errors, "o-", label=method_name)
            elif method_name == "Метод хорд":
                iterations = range(1, len(convergence_data))
                errors = [data[4] for data in convergence_data[1:]]  # |c-c_prev|
                ax2.semilogy(iterations, errors, "s-", label=method_name)
            elif method_name == "Метод Ньютона":
                iterations = range(1, len(convergence_data))
                errors = [data[3] for data in convergence_data[1:]]  # |x_k - x_{k-1}|
                ax2.semilogy(iterations, errors, "^-", label=method_name)
            elif method_name == "Метод секущих":
                iterations = range(1, len(convergence_data))
                errors = [data[3] for data in convergence_data[1:]]  # |x_k - x_{k-1}|
                ax2.semilogy(iterations, errors, "D-", label=method_name)
            elif method_name == "Гибридный метод Ньютона-половинного деления":
                iterations = range(1, len(convergence_data))
                errors = [data[5] for data in convergence_data[1:]]  # |x_k - x_{k-1}|
                ax2.semilogy(iterations, errors, "*-", label=method_name)

        ax2.set_title("Скорость сходимости")
        ax2.set_xlabel("Итерация")
        ax2.set_ylabel("Погрешность")
        ax2.legend()
        ax2.grid(True)

        ax3 = self.fig_equation.add_subplot(223)

        method_names = [result[0] for result in results]
        iterations_count = [result[2] for result in results]

        x_pos = np.arange(len(method_names))
        ax3.bar(x_pos, iterations_count, alpha=0.7)
        ax3.set_title("Число итераций")
        ax3.set_ylabel("Итерации")
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(method_names, rotation=45, ha="right")

        for i, v in enumerate(iterations_count):
            ax3.text(i, v + 0.1, str(v), ha="center")

        ax4 = self.fig_equation.add_subplot(224)

        execution_times = [result[3] for result in results]

        ax4.bar(x_pos, execution_times, alpha=0.7, color="green")
        ax4.set_title("Время выполнения")
        ax4.set_ylabel("Время (сек)")
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(method_names, rotation=45, ha="right")

        for i, v in enumerate(execution_times):
            ax4.text(i, v + 0.0001, f"{v:.6f}", ha="center")
        self.fig_equation.set_size_inches(12, 10)
        self.fig_equation.tight_layout(pad=1.5)
        self.canvas_equation.draw()

    def benchmark_equation_methods(self):
        """Benchmark equation solving methods with different precision levels"""
        try:
            a = float(self.eq_a_entry.get())
            b = float(self.eq_b_entry.get())
            x0 = float(self.eq_x0_entry.get())

            precision_levels = [1e-3, 1e-6, 1e-9, 1e-12]

            test_equations = [
                self.equation_entry.get(),
                "sin(x) - 0.5",
                "x**2 - ln(x) - 4",
                "x**2/5 + x/4 - ln(x)/4 - 1",
            ]

            self.equation_result_text.delete(1.0, tk.END)
            self.equation_result_text.insert(
                tk.END, "🔢 СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТОДОВ\n"
            )
            self.equation_result_text.insert(tk.END, "=" * 60 + "\n\n")

            self.status_var.set("Выполняется сравнительный анализ...")
            self.root.update()

            all_results = []

            for eq_idx, equation in enumerate(test_equations):
                self.equation_result_text.insert(
                    tk.END, f"📊 УРАВНЕНИЕ {eq_idx+1}: {equation} = 0\n"
                )
                self.equation_result_text.insert(tk.END, "-" * 60 + "\n\n")

                current_equation = self.equation_entry.get()

                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, equation)

                try:
                    fa = self.f_eq(a)
                    fb = self.f_eq(b)

                    if fa * fb > 0:
                        self.equation_result_text.insert(
                            tk.END,
                            f"⚠️ Функция имеет одинаковый знак на концах отрезка [{a}, {b}].\n"
                            f"Методы половинного деления, хорд и гибридный могут не сработать.\n\n",
                        )
                except Exception as e:
                    self.equation_result_text.insert(
                        tk.END, f"⚠️ Ошибка при вычислении функции: {str(e)}\n\n"
                    )
                    continue

                self.equation_result_text.insert(
                    tk.END, "Зависимость числа итераций от точности:\n"
                )
                self.equation_result_text.insert(tk.END, "-" * 80 + "\n")
                self.equation_result_text.insert(
                    tk.END,
                    "Метод                                | ε = 1e-3  | ε = 1e-6  | ε = 1e-9  | ε = 1e-12 \n",
                )
                self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                equation_results = {"equation": equation, "methods": {}}

                methods = [
                    ("Метод половинного деления", self.bisection_method),
                    ("Метод хорд", self.chord_method),
                    ("Метод Ньютона", self.newton_method),
                    ("Метод секущих", self.secant_method),
                    ("Гибридный метод", self.hybrid_method),
                ]

                for method_name, method in methods:
                    iterations_by_precision = []
                    times_by_precision = []

                    for eps in precision_levels:
                        try:
                            start_time = time.time()

                            if method_name in ["Метод Ньютона", "Метод секущих"]:
                                root, iterations, _ = method(a, b, eps, x0)
                            else:
                                root, iterations, _ = method(a, b, eps)

                            execution_time = time.time() - start_time

                            iterations_by_precision.append(iterations)
                            times_by_precision.append(execution_time)

                        except Exception as e:
                            iterations_by_precision.append("N/A")
                            times_by_precision.append("N/A")

                    self.equation_result_text.insert(
                        tk.END,
                        f"{method_name:38} | {iterations_by_precision[0] if iterations_by_precision[0] != 'N/A' else 'N/A':9} | "
                        f"{iterations_by_precision[1] if iterations_by_precision[1] != 'N/A' else 'N/A':9} | "
                        f"{iterations_by_precision[2] if iterations_by_precision[2] != 'N/A' else 'N/A':9} | "
                        f"{iterations_by_precision[3] if iterations_by_precision[3] != 'N/A' else 'N/A':9}\n",
                    )

                    equation_results["methods"][method_name] = {
                        "iterations": iterations_by_precision,
                        "times": times_by_precision,
                    }

                self.equation_result_text.insert(
                    tk.END, "\nЗависимость времени выполнения от точности (сек):\n"
                )
                self.equation_result_text.insert(tk.END, "-" * 80 + "\n")
                self.equation_result_text.insert(
                    tk.END,
                    "Метод                                | ε = 1e-3  | ε = 1e-6  | ε = 1e-9  | ε = 1e-12 \n",
                )
                self.equation_result_text.insert(tk.END, "-" * 80 + "\n")

                for method_name, method in methods:
                    times = equation_results["methods"][method_name]["times"]

                    self.equation_result_text.insert(
                        tk.END,
                        f"{method_name:38} | {times[0] if times[0] != 'N/A' else 'N/A':9.6f} | "
                        f"{times[1] if times[1] != 'N/A' else 'N/A':9.6f} | "
                        f"{times[2] if times[2] != 'N/A' else 'N/A':9.6f} | "
                        f"{times[3] if times[3] != 'N/A' else 'N/A':9.6f}\n",
                    )

                self.equation_result_text.insert(tk.END, "=" * 60 + "\n\n")

                all_results.append(equation_results)

                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, current_equation)

            self.plot_benchmark_results(all_results, precision_levels)

            self.status_var.set("Сравнительный анализ завершен")

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Произошла ошибка при выполнении сравнительного анализа: {str(e)}",
            )
            self.status_var.set("Ошибка сравнительного анализа")

    def plot_benchmark_results(self, all_results, precision_levels):
        """Plot benchmark results"""
        self.fig_equation.clear()

        for i, result in enumerate(all_results):
            ax = self.fig_equation.add_subplot(2, 2, i + 1)

            for method_name, data in result["methods"].items():
                iterations = data["iterations"]

                iterations_numeric = []
                for it in iterations:
                    if it == "N/A":
                        iterations_numeric.append(None)
                    else:
                        iterations_numeric.append(it)

                if any(it is not None for it in iterations_numeric):
                    valid_indices = [
                        i for i, it in enumerate(iterations_numeric) if it is not None
                    ]
                    valid_iterations = [iterations_numeric[i] for i in valid_indices]
                    valid_precision = [precision_levels[i] for i in valid_indices]

                    ax.loglog(
                        valid_precision, valid_iterations, "o-", label=method_name
                    )

            ax.set_title(f'Уравнение {i+1}: {result["equation"]}')
            ax.set_xlabel("Точность ε")
            ax.set_ylabel("Число итераций")
            ax.grid(True)
            ax.legend()

        self.fig_equation.tight_layout()
        self.canvas_equation.draw()

    def save_results(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Сохранить результаты",
            )

            if not file_path:
                return

            with PdfPages(file_path) as pdf:
                for fig_attr in [
                    "fig_integration",
                    "fig_interpolation",
                    "fig_differentiation",
                    "fig_equation",
                ]:
                    if hasattr(self, fig_attr):
                        pdf.savefig(getattr(self, fig_attr))

                fig_text = plt.figure(figsize=(8.27, 11.69))  # A4
                fig_text.clf()

                results_text = ""
                for text_attr in [
                    "result_text",
                    "interpolation_result_text",
                    "differentiation_result_text",
                    "equation_result_text",
                ]:
                    if hasattr(self, text_attr):
                        results_text += "\n\n" + getattr(self, text_attr).get(
                            1.0, tk.END
                        )

                chars_per_page = 3000
                text_pages = [
                    results_text[i : i + chars_per_page]
                    for i in range(0, len(results_text), chars_per_page)
                ]

                for page_text in text_pages:
                    fig = plt.figure(figsize=(8.27, 11.69))
                    fig.text(
                        0.1,
                        0.95,
                        page_text,
                        transform=fig.transFigure,
                        size=10,
                        family="monospace",
                        va="top",
                        ha="left",
                        wrap=True,
                    )
                    pdf.savefig(fig)
                    plt.close(fig)

            messagebox.showinfo(
                "Сохранение", f"Результаты успешно сохранены в файл:\n{file_path}"
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при сохранении результатов: {str(e)}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = NumericalMethodsApp(root)
    root.mainloop()
