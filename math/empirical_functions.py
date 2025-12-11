import numpy as np
from scipy.optimize import curve_fit

def linear(x, a, b):
    """Линейная функция: y = ax + b"""
    return a * x + b

def quadratic(x, a, b, c):
    """Квадратичная функция: y = ax² + bx + c"""
    return a * x**2 + b * x + c

def power(x, a, b):
    """Степенная функция: y = ax^b"""
    return a * x**b

def exponential(x, a, b):
    """Экспоненциальная функция: y = ae^(bx)"""
    return a * np.exp(b * x)

def logarithmic(x, a, b):
    """Логарифмическая функция: y = a + b*ln(x)"""
    # Добавляем небольшую константу чтобы избежать ln(0)
    x_safe = np.where(x > 0, x, 1e-10)
    return a + b * np.log(x_safe)

def get_all_models():
    """Возвращает список всех моделей для подбора"""
    return [
        (linear, "Линейная", 2, "y = {a:.6f}x + {b:.6f}"),
        (quadratic, "Квадратичная", 3, "y = {a:.6f}x² + {b:.6f}x + {c:.6f}"),
        (power, "Степенная", 2, "y = {a:.6f}x^{b:.6f}"),
        (exponential, "Экспоненциальная", 2, "y = {a:.6f}e^({b:.6f}x)"),
        (logarithmic, "Логарифмическая", 2, "y = {a:.6f} + {b:.6f}·ln(x)")
    ]

def fit_models(x, y):
    """
    Подбирает все модели и возвращает результаты
    """
    models = get_all_models()
    results = []
    
    for func, name, num_params, equation_template in models:
        try:
            # Проверяем данные для специфических функций
            if func == logarithmic and np.any(x <= 0):
                continue  # Пропускаем логарифмическую если есть неположительные x
                
            # Особые начальные приближения для некоторых функций
            if func == power:
                p0 = [1, 1]
            elif func == exponential:
                p0 = [1, 0.5]
            elif func == logarithmic:
                p0 = [1, 1]
            else:
                p0 = None
            
            popt, pcov = curve_fit(func, x, y, p0=p0, maxfev=5000)
            y_pred = func(x, *popt)
            
            # Вычисляем различные метрики ошибок
            sum_squared_errors = np.sum((y - y_pred)**2)
            mean_squared_error = sum_squared_errors / len(y)
            rmse = np.sqrt(mean_squared_error)
            mean_abs_error = np.mean(np.abs(y - y_pred))
            
            # Коэффициент детерминации R²
            y_mean = np.mean(y)
            ss_total = np.sum((y - y_mean)**2)
            ss_residual = np.sum((y - y_pred)**2)
            r_squared = 1 - (ss_residual / ss_total)
            
            # Форматируем уравнение
            param_names = ['a', 'b', 'c'][:len(popt)]
            param_dict = dict(zip(param_names, popt))
            equation = equation_template.format(**param_dict)
            
            result = {
                'function': func,
                'name': name,
                'parameters': popt,
                'equation': equation,
                'sum_squared_errors': sum_squared_errors,
                'rmse': rmse,
                'mean_abs_error': mean_abs_error,
                'r_squared': r_squared,
                'y_pred': y_pred
            }
            
            results.append(result)
            
        except Exception as e:
            # Пропускаем модели которые не удалось подобрать
            continue
    
    # Сортируем по сумме квадратов ошибок (лучшие первыми)
    results.sort(key=lambda x: x['sum_squared_errors'])
    
    return results

def get_best_model(results):
    """Возвращает лучшую модель из результатов"""
    if results:
        return results[0]
    return None

def format_model_result(result):
    """Форматирует результат модели в читаемый вид"""
    text = f"{result['name']} функция:\n"
    text += f"Уравнение: {result['equation']}\n"
    text += f"R² = {result['r_squared']:.6f} ({result['r_squared']*100:.2f}%)\n"
    text += f"Сумма квадратов ошибок = {result['sum_squared_errors']:.6f}\n"
    text += f"Среднеквадратичная ошибка = {result['rmse']:.6f}\n"
    text += f"Средняя абсолютная ошибка = {result['mean_abs_error']:.6f}\n"
    
    # Оценка качества по R²
    r2 = result['r_squared']
    if r2 > 0.95:
        quality = "Отличное"
    elif r2 > 0.85:
        quality = "Очень хорошее"
    elif r2 > 0.7:
        quality = "Хорошее"
    elif r2 > 0.5:
        quality = "Удовлетворительное"
    else:
        quality = "Плохое"
    
    text += f"Качество подгонки: {quality}\n"
    text += "-" * 50 + "\n"
    
    return text
