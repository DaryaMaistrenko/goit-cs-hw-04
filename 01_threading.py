import os
import threading
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

def threaded_search(files, keywords):
    """Багатопотоковий пошук по файлах."""
    threads = []
    results = defaultdict(list)
    lock = threading.Lock()

    def search_task(files_subset):
        local_result = defaultdict(list)
        for file in files_subset:
            result = search_keywords_in_file(file, keywords)
            for k, v in result.items():
                local_result[k].extend(v)
        with lock:
            for k, v in local_result.items():
                results[k].extend(v)

    num_threads = min(4, len(files))  # Максимум 4 потоки
    chunk_size = len(files) // num_threads if num_threads > 0 else 1
    for i in range(num_threads):
        start = i * chunk_size
        end = len(files) if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=search_task, args=(files[start:end],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results

if __name__ == "__main__":
    keywords = ["error", "warning", "critical"]
    files = [f for f in os.listdir(".") if f.endswith(".txt")]

    if not files:
        print("Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results = threaded_search(files, keywords)
        end_time = time()

        print(f"Багатопотоковий пошук завершено за {end_time - start_time:.2f} секунд.")
        for keyword, matched_files in results.items():
            print(f"Ключове слово '{keyword}' знайдено у файлах: {matched_files}")