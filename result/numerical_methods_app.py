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
        self.root.title("Численные методы: Интегрирование и Интерполяция(ЛР2, ЛР1)")
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
        self.theory_frame = ttk.Frame(self.notebook, padding="10")
        self.help_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.integration_frame, text="Интегрирование ЛР №2")
        self.notebook.add(self.interpolation_frame, text="Интерполяция ЛР №1")
        self.notebook.add(self.theory_frame, text="Теория по лр")
        self.notebook.add(self.help_frame, text="Справка о программе")

        self.setup_integration_tab()
        self.setup_interpolation_tab()
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
                self.theory_frame,
                self.help_frame,
            ):
                tab.configure(style="Light.TFrame")

            # Update button styles
            self.calculate_button.configure(style="Light.TButton")
            self.interpolate_button.configure(style="Light.TButton")
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
                self.theory_frame,
                self.help_frame,
            ):
                tab.configure(style="Dark.TFrame")

            self.calculate_button.configure(style="Dark.TButton")
            self.interpolate_button.configure(style="Dark.TButton")

        self.update_plot_style()

    def update_plot_style(self):
        if hasattr(self, "fig_integration"):
            self.fig_integration.set_facecolor(
                "#ffffff" if self.theme == "light" else "#1c1c1e"
            )
            for ax in self.fig_integration.get_axes():
                ax.set_facecolor("#ffffff" if self.theme == "light" else "#1c1c1e")
                ax.tick_params(colors="#000000" if self.theme == "light" else "#ffffff")
                ax.xaxis.label.set_color(
                    "#000000" if self.theme == "light" else "#ffffff"
                )
                ax.yaxis.label.set_color(
                    "#000000" if self.theme == "light" else "#ffffff"
                )
                ax.title.set_color("#000000" if self.theme == "light" else "#ffffff")

                ax.grid(
                    True,
                    color="#e5e5ea" if self.theme == "light" else "#2c2c2e",
                    linestyle="-",
                    linewidth=0.5,
                )

                for spine in ax.spines.values():
                    spine.set_color("#e5e5ea" if self.theme == "light" else "#2c2c2e")

            self.canvas_integration.draw()

        if hasattr(self, "fig_interpolation"):
            self.fig_interpolation.set_facecolor(
                "#ffffff" if self.theme == "light" else "#1c1c1e"
            )
            for ax in self.fig_interpolation.get_axes():
                ax.set_facecolor("#ffffff" if self.theme == "light" else "#1c1c1e")
                ax.tick_params(colors="#000000" if self.theme == "light" else "#ffffff")
                ax.xaxis.label.set_color(
                    "#000000" if self.theme == "light" else "#ffffff"
                )
                ax.yaxis.label.set_color(
                    "#000000" if self.theme == "light" else "#ffffff"
                )
                ax.title.set_color("#000000" if self.theme == "light" else "#ffffff")

                ax.grid(
                    True,
                    color="#e5e5ea" if self.theme == "light" else "#2c2c2e",
                    linestyle="-",
                    linewidth=0.5,
                )

                for spine in ax.spines.values():
                    spine.set_color("#e5e5ea" if self.theme == "light" else "#2c2c2e")

            self.canvas_interpolation.draw()

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
                if hasattr(self, "fig_integration"):
                    pdf.savefig(self.fig_integration)
                if hasattr(self, "fig_interpolation"):
                    pdf.savefig(self.fig_interpolation)

                fig_text = plt.figure(figsize=(8.27, 11.69))  # A4
                fig_text.clf()

                results_text = self.result_text.get(1.0, tk.END)
                if hasattr(self, "interpolation_result_text"):
                    results_text += "\n\n" + self.interpolation_result_text.get(
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
