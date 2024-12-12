import os
import multiprocessing
from collections import defaultdict
from time import time

def search_keywords_in_file(filename, keywords):
    """Пошук ключових слів у конкретному файлі."""
    result = defaultdict(list)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read().lower()
            for word in keywords:
                if word.lower() in text:
                    result[word].append(filename)
    except Exception as e:
        print(f"Помилка при читанні файлу {filename}: {e}")
    return result

def process_task(files, keywords, queue):
    """Завдання для окремого процесу."""
    local_result = defaultdict(list)
    for file in files:
        result = search_keywords_in_file(file, keywords)
        for k, v in result.items():
            local_result[k].extend(v)
    queue.put(local_result)

def multiprocessing_search(files, keywords):
    """Багатопроцесорний пошук по файлах."""
    processes = []
    queue = multiprocessing.Queue()
    results = defaultdict(list)

    num_processes = min(4, len(files))  # Максимум 4 процеси
    chunk_size = len(files) // num_processes if num_processes > 0 else 1
    for i in range(num_processes):
        start = i * chunk_size
        end = len(files) if i == num_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(target=process_task, args=(files[start:end], keywords, queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    while not queue.empty():
        result = queue.get()
        for k, v in result.items():
            results[k].extend(v)

    return results

if __name__ == "__main__":
    keywords = ["error", "warning", "critical"]
    files = [f for f in os.listdir(".") if f.endswith(".txt")]

    if not files:
        print("Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results = multiprocessing_search(files, keywords)
        end_time = time()

        print(f"Багатопроцесорний пошук завершено за {end_time - start_time:.2f} секунд.")
        for keyword, matched_files in results.items():
            print(f"Ключове слово '{keyword}' знайдено у файлах: {matched_files}")
