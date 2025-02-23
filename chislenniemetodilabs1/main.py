import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Ввод данных с клавиатуры или из файла
def input_data():
    print("Выберите способ ввода данных:")
    print("1. Ввод с клавиатуры")
    print("2. Ввод из файла")
    choice = input("Введите номер варианта (1 или 2): ")

    if choice == '1':
        n = int(input("Введите количество узловых точек: "))
        data = []
        for i in range(n):
            xi = float(input(f"Введите значение x{i+1}: "))
            yi = float(input(f"Введите значение y{i+1}: "))
            data.append((xi, yi))
    elif choice == '2':
        file_name = input("Введите имя файла: ")
        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()
                data = [(float(line.split()[0]), float(line.split()[1])) for line in lines]
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return None
    else:
        print("Неверный выбор!")
        return None

    return np.array(data)

# Построение интерполяционного многочлена Лагранжа
def lagrange_polynomial(data, x_star):
    n = len(data)
    result = 0.0

    log = "Вычисление многочлена Лагранжа:\n"
    for i in range(n):
        L_i = 1.0
        for j in range(n):
            if i != j:
                term = (x_star - data[j][0]) / (data[i][0] - data[j][0])
                L_i *= term
                log += f"L_{i}({x_star}) *= ({x_star} - {data[j][0]}) / ({data[i][0]} - {data[j][0]})\n"

        term_value = L_i * data[i][1]
        result += term_value
        log += f"Добавляем к результату: {L_i} * {data[i][1]} = {term_value}\n"

    log += f"\nЗначение многочлена Лагранжа в точке {x_star}: {result}\n"
    return result, log

# Построение интерполяционного многочлена Ньютона
def newton_polynomial(data, x_star):
    n = len(data)
    divided_diffs = [[y for _, y in data]]

    # Вычисление разделенных разностей
    log = "Вычисление разделенных разностей:\n"
    for i in range(1, n):
        current_diffs = []
        for j in range(n - i):
            diff = (divided_diffs[i-1][j+1] - divided_diffs[i-1][j]) / (data[j+i][0] - data[j][0])
            current_diffs.append(diff)
            log += f"f[{', '.join(map(str, [data[k][0] for k in range(j, j+i+1)]))}] = " \
                   f"({divided_diffs[i-1][j+1]} - {divided_diffs[i-1][j]}) / ({data[j+i][0]} - {data[j][0]}) = {diff}\n"
        divided_diffs.append(current_diffs)

    # Построение многочлена Ньютона
    result = divided_diffs[0][0]
    log += "\nВычисление многочлена Ньютона:\n"
    for i in range(1, n):
        product = 1.0
        for j in range(i):
            product *= (x_star - data[j][0])
            log += f"Произведение *= ({x_star} - {data[j][0]})\n"
        term = divided_diffs[i][0] * product
        result += term
        log += f"Добавляем к результату: {divided_diffs[i][0]} * {product} = {term}\n"

    log += f"\nЗначение многочлена Ньютона в точке {x_star}: {result}\n"
    return result, log

# Визуализация графиков
def plot_graphs(data, x_star, lagrange_result, newton_result):
    x_values = np.linspace(min(data[:, 0]) - 1, max(data[:, 0]) + 1, 500)
    y_lagrange = np.array([lagrange_polynomial(data, x)[0] for x in x_values])
    y_newton = np.array([newton_polynomial(data, x)[0] for x in x_values])

    fig, ax = plt.subplots(figsize=(12, 6))  # Создаем объект Figure и Axes

    # График исходных данных
    ax.scatter(data[:, 0], data[:, 1], color='red', label='Узлы интерполяции', zorder=5)

    # График многочлена Лагранжа
    ax.plot(x_values, y_lagrange, label='Многочлен Лагранжа', color='blue', linewidth=2)

    # График многочлена Ньютона
    ax.plot(x_values, y_newton, label='Многочлен Ньютона', color='green', linestyle='--', linewidth=2)

    # Отметка точки x*
    ax.scatter([x_star], [lagrange_result], color='purple', label=f'x*={x_star}', zorder=5)
    ax.scatter([x_star], [newton_result], color='orange', label=f'x*={x_star}', zorder=5)

    ax.set_title('Интерполяционные многочлены', fontsize=16)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    return fig  # Возвращаем объект Figure

# Сохранение результатов в PDF
def save_to_pdf(data, x_star, lagrange_result, newton_result, lagrange_log, newton_log):
    pdf_pages = PdfPages('results.pdf')

    # Создание графика
    fig = plot_graphs(data, x_star, lagrange_result, newton_result)  # Получаем объект Figure
    pdf_pages.savefig(fig)  # Сохраняем график в PDF
    plt.close(fig)  # Закрываем фигуру после сохранения

    # Добавление текстовых данных
    text_fig = plt.figure(figsize=(8.27, 11.69))  # Размер A4
    text_ax = text_fig.add_subplot(111)
    text_ax.axis('off')

    text = (
        "=== Многочлен Лагранжа ===\n"
        f"{lagrange_log}\n"
        "\n=== Многочлен Ньютона ===\n"
        f"{newton_log}\n"
        "\n=== Сравнение результатов ===\n"
        f"Значение многочлена Лагранжа в точке {x_star}: {lagrange_result}\n"
        f"Значение многочлена Ньютона в точке {x_star}: {newton_result}\n"
        f"Разница между результатами: {abs(lagrange_result - newton_result)}\n"
    )

    text_ax.text(0.5, 0.5, text, fontsize=10, ha='center', va='center', wrap=True)
    pdf_pages.savefig(text_fig)  # Сохраняем текст в PDF
    plt.close(text_fig)  # Закрываем фигуру после сохранения

    pdf_pages.close()  # Закрываем PDF-файл

# Сохранение результатов в HTML
def save_to_html(data, x_star, lagrange_result, newton_result, lagrange_log, newton_log):
    # Создание графика
    plot_graphs(data, x_star, lagrange_result, newton_result).savefig('plot.png')

    # Создание HTML-файла
    html_content = f"""
    <html>
    <head>
        <title>Интерполяционные многочлены</title>
    </head>
    <body>
        <h1>График интерполяционных многочленов</h1>
        <img src="plot.png" alt="График интерполяционных многочленов">

        <h2>Многочлен Лагранжа</h2>
        <pre>{lagrange_log}</pre>

        <h2>Многочлен Ньютона</h2>
        <pre>{newton_log}</pre>

        <h2>Сравнение результатов</h2>
        <p>Значение многочлена Лагранжа в точке {x_star}: {lagrange_result}</p>
        <p>Значение многочлена Ньютона в точке {x_star}: {newton_result}</p>
        <p>Разница между результатами: {abs(lagrange_result - newton_result)}</p>
    </body>
    </html>
    """

    with open('results.html', 'w') as file:
        file.write(html_content)

# Основная программа
if __name__ == "__main__":
    # Ввод данных
    data = input_data()
    if data is None:
        exit()

    x_star = float(input("Введите точку x*, в которой нужно вычислить значение функции: "))

    # Построение многочлена Лагранжа
    lagrange_result, lagrange_log = lagrange_polynomial(data, x_star)

    # Построение многочлена Ньютона
    newton_result, newton_log = newton_polynomial(data, x_star)

    # Сохранение результатов в PDF
    save_to_pdf(data, x_star, lagrange_result, newton_result, lagrange_log, newton_log)

    # Сохранение результатов в HTML
    save_to_html(data, x_star, lagrange_result, newton_result, lagrange_log, newton_log)

    print("Результаты сохранены в файлах results.pdf и results.html")
