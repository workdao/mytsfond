#!/usr/bin/env python3
"""
Инструмент для получения данных о городах и организациях с сайта my.tsfond.ru
"""

import requests
import json
from typing import List, Dict, Any, Optional


BASE_URL = "https://my.tsfond.ru"
CITIES_API_ENDPOINT = "/city/get-cities-list"


def get_all_cities(
    sort: str = "latest",
    sort_status: str = "",
    search: str = "",
    limit_per_request: int = 50
) -> List[Dict[str, Any]]:
    """
    Получает все города с API сайта my.tsfond.ru
    
    Args:
        sort: Сортировка ('latest', 'oldest', 'title_asc', 'title_desc')
        sort_status: Фильтр по статусу ('', 'new', 'planned', 'started', 'ended', 'stopped', 'pause', 'friends')
        search: Поисковый запрос
        limit_per_request: Количество городов за один запрос
        
    Returns:
        Список словарей с данными о городах
    """
    all_cities = []
    offset = 0
    
    print(f"Начинаем загрузку городов...")
    print(f"Параметры: sort={sort}, sort_status={sort_status}, search='{search}'")
    
    while True:
        url = f"{BASE_URL}{CITIES_API_ENDPOINT}"
        params = {
            "offset": offset,
            "sort": sort,
            "sort_status": sort_status,
            "search": search
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                print(f"Ошибка API: {data.get('message', 'Неизвестная ошибка')}")
                break
            
            cities = data.get("data", {}).get("cities", [])
            count_all = data.get("data", {}).get("count_all", 0)
            
            if not cities:
                break
                
            all_cities.extend(cities)
            offset += len(cities)
            
            print(f"Загружено {len(all_cities)} из {count_all} городов")
            
            if len(all_cities) >= count_all:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            break
    
    return all_cities


def get_city_details(city_url: str) -> Optional[Dict[str, Any]]:
    """
    Получает детальную информацию о городе и его объектах
    
    Args:
        city_url: URL страницы города (например, '/arzamas')
        
    Returns:
        Словарь с детальной информацией о городе и объектах
    """
    url = f"{BASE_URL}{city_url}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Парсим HTML для получения данных об объектах
        # Это требует дополнительного анализа структуры страницы
        print(f"Получена страница города: {city_url}")
        return {"url": city_url, "status": "page_retrieved"}
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к странице города: {e}")
        return None


def format_city_info(city: Dict[str, Any]) -> str:
    """
    Форматирует информацию о городе для вывода
    
    Args:
        city: Словарь с данными о городе
        
    Returns:
        Форматированная строка с информацией о городе
    """
    title = city.get("title", "Без названия")
    year = city.get("year", "н/д")
    status = city.get("status", {})
    status_title = status.get("title", "н/д")
    status_type = status.get("type", "н/д")
    objects_count = city.get("count", {}).get("objects", 0)
    news_count = city.get("count", {}).get("news", 0)
    resources = city.get("resources", [])
    image = city.get("image")
    url = city.get("url")
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Город: {title}")
    output.append(f"URL: {BASE_URL}{url}")
    output.append(f"Год начала: {year}")
    output.append(f"Статус: {status_title} ({status_type})")
    output.append(f"Объектов: {objects_count}")
    output.append(f"Новостей: {news_count}")
    
    if image:
        output.append(f"Изображение: {BASE_URL}{image}")
    
    if resources:
        output.append("Ресурсы:")
        for res in resources:
            output.append(f"  - {res.get('title')}: {res.get('url')}")
    
    return "\n".join(output)


def export_to_json(cities: List[Dict[str, Any]], filename: str = "cities_data.json") -> None:
    """
    Экспортирует данные о городах в JSON файл
    
    Args:
        cities: Список словарей с данными о городах
        filename: Имя файла для экспорта
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)
    print(f"\nДанные экспортированы в файл: {filename}")


def export_to_csv(cities: List[Dict[str, Any]], filename: str = "cities_data.csv") -> None:
    """
    Экспортирует данные о городах в CSV файл
    
    Args:
        cities: Список словарей с данными о городах
        filename: Имя файла для экспорта
    """
    import csv
    
    if not cities:
        print("Нет данных для экспорта")
        return
    
    fieldnames = [
        "id", "title", "url", "year", "image", 
        "status_title", "status_type",
        "objects_count", "news_count",
        "resources"
    ]
    
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for city in cities:
            row = {
                "id": city.get("id"),
                "title": city.get("title"),
                "url": city.get("url"),
                "year": city.get("year"),
                "image": city.get("image"),
                "status_title": city.get("status", {}).get("title"),
                "status_type": city.get("status", {}).get("type"),
                "objects_count": city.get("count", {}).get("objects", 0),
                "news_count": city.get("count", {}).get("news", 0),
                "resources": json.dumps(city.get("resources", []), ensure_ascii=False)
            }
            writer.writerow(row)
    
    print(f"Данные экспортированы в файл: {filename}")


def print_summary(cities: List[Dict[str, Any]]) -> None:
    """
    Выводит сводную статистику по городам
    
    Args:
        cities: Список словарей с данными о городах
    """
    if not cities:
        print("Нет данных для анализа")
        return
    
    total_objects = sum(city.get("count", {}).get("objects", 0) for city in cities)
    total_news = sum(city.get("count", {}).get("news", 0) for city in cities)
    
    status_counts = {}
    for city in cities:
        status_type = city.get("status", {}).get("type", "unknown")
        status_counts[status_type] = status_counts.get(status_type, 0) + 1
    
    print("\n" + "="*60)
    print("СВОДНАЯ СТАТИСТИКА")
    print("="*60)
    print(f"Всего городов: {len(cities)}")
    print(f"Всего объектов: {total_objects}")
    print(f"Всего новостей: {total_news}")
    print("\nРаспределение по статусам:")
    for status_type, count in sorted(status_counts.items()):
        print(f"  {status_type}: {count}")


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Инструмент для получения данных о городах с my.tsfond.ru"
    )
    parser.add_argument(
        "--sort",
        choices=["latest", "oldest", "title_asc", "title_desc"],
        default="latest",
        help="Сортировка городов (по умолчанию: latest)"
    )
    parser.add_argument(
        "--status",
        choices=["", "new", "planned", "started", "ended", "stopped", "pause", "friends"],
        default="",
        help="Фильтр по статусу (по умолчанию: все)"
    )
    parser.add_argument(
        "--search",
        default="",
        help="Поисковый запрос по названию города"
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Экспорт данных в JSON файл"
    )
    parser.add_argument(
        "--output-csv",
        default=None,
        help="Экспорт данных в CSV файл"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Тихий режим (минимальный вывод)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Показать только сводную статистику"
    )
    
    args = parser.parse_args()
    
    # Получаем все города
    cities = get_all_cities(
        sort=args.sort,
        sort_status=args.status,
        search=args.search
    )
    
    if not cities:
        print("Не удалось получить данные о городах")
        return
    
    # Вывод информации
    if args.summary:
        print_summary(cities)
    elif not args.quiet:
        print_summary(cities)
        for city in cities:
            print(format_city_info(city))
    
    # Экспорт данных
    if args.output_json:
        export_to_json(cities, args.output_json)
    
    if args.output_csv:
        export_to_csv(cities, args.output_csv)


if __name__ == "__main__":
    main()
