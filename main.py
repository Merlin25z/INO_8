import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_number(number):
    """Умножает число на 2 с задержкой 0.2 секунды."""
    time.sleep(0.2)  # Имитация задержки
    return number * 2


def load_numbers_from_file(filename):
    """Загружает список списков чисел из файла."""
    # Здесь предполагается, что файл содержит список списков чисел в формате Python
    with open(filename, 'r') as file:
        numbers = eval(file.read())
    return numbers


def main():
    # Загрузка данных из файла
    try:
        lists_of_numbers = load_numbers_from_file('test_list_numbers.txt')
    except FileNotFoundError:
        print("Файл test_list_numbers.txt не найден.")
        return
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return

    # Создаем пул потоков
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        list_indices = []  # Для отслеживания, к какому списку принадлежит каждое число

        # Отправляем все числа на обработку
        for list_idx, numbers in enumerate(lists_of_numbers):
            for number in numbers:
                future = executor.submit(process_number, number)
                futures.append(future)
                list_indices.append(list_idx)

        # Словарь для хранения результатов по спискам
        results = {i: [] for i in range(len(lists_of_numbers))}
        completed_lists = set()
        first_completed_sum = None

        # Обрабатываем результаты по мере их поступления
        for future in as_completed(futures):
            # Получаем индекс списка для этого числа
            future_idx = futures.index(future)
            list_idx = list_indices[future_idx]

            # Добавляем результат в соответствующий список
            result = future.result()
            results[list_idx].append(result)

            # Проверяем, завершен ли список
            if list_idx not in completed_lists and len(results[list_idx]) == len(lists_of_numbers[list_idx]):
                completed_lists.add(list_idx)
                current_sum = sum(results[list_idx])

                # Если это первый завершенный список, сохраняем его сумму
                if first_completed_sum is None:
                    first_completed_sum = current_sum

    # Выводим результат
    if first_completed_sum is not None:
        print(f"Сумма чисел в первом обработанном списке: {first_completed_sum}")
    else:
        print("Ни один список не был обработан полностью.")


if __name__ == "__main__":
    main()