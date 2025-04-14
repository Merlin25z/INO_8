import zipfile
import multiprocessing
from multiprocessing import Pool
import os
import logging
from tqdm import tqdm
import re

# Настройка логирования
logging.basicConfig(
    filename='processing_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(message)s'
)


def extract_final_number(zip_file, file_path):
    """Извлекает конечное число из файла в архиве"""
    try:
        with zip_file.open(file_path) as f:
            content = f.read().decode('utf-8').strip()
            # Ищем последнее число в содержимом
            numbers = re.findall(r'\d+', content)
            if numbers:
                return int(numbers[-1])
        return 0
    except:
        return 0


def process_file(first_archive_path, file_name):
    """Обрабатывает файл и возвращает число или 0 при ошибке."""
    try:
        # 1. Чтение пути из первого архива
        with zipfile.ZipFile(first_archive_path, 'r') as first_archive:
            with first_archive.open(file_name) as file:
                next_path = file.read().decode('utf-8').strip()

                # Очищаем путь от префикса 'recursive_challenge'
                next_path = next_path.replace('recursive_challenge', '').strip('/\\')

                # Если путь содержит только имя файла без расширения, добавляем .txt
                if '.' not in next_path:
                    next_path += '.txt'

        # 2. Чтение из второго архива
        second_archive_path = 'recursive_challenge_8_8.zip'
        with zipfile.ZipFile(second_archive_path, 'r') as second_archive:
            # Ищем файл по частичному совпадению
            for possible_path in second_archive.namelist():
                # Нормализуем пути для сравнения
                normalized_possible = possible_path.lower().replace('\\', '/')
                normalized_next = next_path.lower().replace('\\', '/')

                if normalized_next in normalized_possible:
                    return extract_final_number(second_archive, possible_path)

            raise FileNotFoundError(f"Файл '{next_path}' не найден во втором архиве")

    except Exception as e:
        logging.error(f"Ошибка в файле {file_name}: {str(e)}")
        return 0


def main():
    first_archive_path = 'path_8_8.zip'
    if not os.path.exists(first_archive_path):
        print(f"Ошибка: архив {first_archive_path} не найден.")
        return

    try:
        with zipfile.ZipFile(first_archive_path, 'r') as first_archive:
            file_list = [name for name in first_archive.namelist()
                         if name.endswith('.txt') and not name.startswith('__')]
    except zipfile.BadZipFile:
        print("Ошибка: архив поврежден.")
        return

    print(f"Найдено {len(file_list)} файлов для обработки...")

    # Подготовка аргументов для multiprocessing
    file_infos = [(first_archive_path, file_name) for file_name in file_list]

    # Обработка с прогресс-баром
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        results = []
        with tqdm(total=len(file_infos), desc="Обработка файлов") as pbar:
            for result in pool.starmap(process_file, file_infos):
                results.append(result)
                pbar.update(1)

    total_sum = sum(results)
    print(f"\nОбщая сумма чисел: {total_sum}")
    #print(f"Ошибки записаны в файл: processing_errors.log")


if __name__ == "__main__":
    main()