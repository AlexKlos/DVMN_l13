import os

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable


def get_hh_vacancies(programming_language: str) -> list:
    area_index = 1
    searching_period = 30
    vacabcies_per_page = 100
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    pages = 1
    page = 0
    while page < pages:
        params = {
            'text': f'Программист {programming_language}',
            'area': area_index,
            'period': searching_period,
            'only_with_salary': 'True',
            'currency': 'RUR',
            'per_page': vacabcies_per_page,
            'page': page
        }
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        hh_data = response.json()
        pages = hh_data['pages']
        vacancies.extend(hh_data['items'])

        page += 1
    return vacancies


def predict_hh_rub_salary(vacancie: dict) -> int:
    salary_from = vacancie['salary']['from']
    salary_to = vacancie['salary']['to']
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    elif not salary_from:
        return int(salary_to * 0.8)
    elif not salary_to:
        return int(salary_from * 1.2)


def get_hh_average_salary(vacancies: list) -> int:
    salary_amount = 0
    for vacancie in vacancies:
        salary_amount += predict_hh_rub_salary(vacancie)
    
    if len(vacancies):
        average_salary = salary_amount / len(vacancies)

    return int(average_salary)


def get_hh_salary_statistic(programming_languages: list) -> dict:
    salary_statistic = {}
    for programming_language in programming_languages:
        vacancies = get_hh_vacancies(programming_language)
        salary_statistic[programming_language] = {
            'vacancies_found': len(vacancies), 
            'vacancies_processed': len(vacancies),
            'average_salary': get_hh_average_salary(vacancies)
        }

    return salary_statistic


def get_sj_vacancies(programming_language: str, superjob_api_key: str) -> list:
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies = []
    more = True
    while more:
        headers = {
            'X-Api-App-Id': superjob_api_key
        }
        params = {
            'count': 100,
            'keyword': f'Программист {programming_language} Москва'
        }
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        sj_data = response.json()
        more = sj_data['more']
        vacancies.extend(sj_data['objects'])

    return vacancies


def predict_sj_rub_salary(vacancie: dict) -> int:
    payment_from = vacancie['payment_from']
    payment_to = vacancie['payment_to']
    if payment_from and payment_to:
        return int((payment_from + payment_to) / 2)
    elif payment_from:
        return int(payment_from * 1.2)
    elif payment_to:
        return int(payment_to * 0.8)
    

def get_sj_average_salary(vacancies: list) -> tuple[int, int]:
    salary_amount = 0
    salary_count = 0
    for vacancie in vacancies:
        salary = predict_sj_rub_salary(vacancie)
        if salary:
            salary_amount += salary
            salary_count += 1
    
    if salary_amount:
        average_salary = salary_amount / salary_count

    return int(average_salary), salary_count


def get_sj_salary_statistic(programming_languages: list, superjob_api_key: str) -> dict:
    salary_statistic = {}
    for programming_language in programming_languages:
        vacancies = get_sj_vacancies(programming_language, superjob_api_key)
        average_salary, salary_count = get_sj_average_salary(vacancies)
        salary_statistic[programming_language] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': salary_count,
            'average_salary': average_salary
        }

    return salary_statistic


def print_table(salary_statistic: dict, table_title: str):
    table_data = [
        ['Язык программирования', 
         'Вакансий найдено', 
         'Вакансий обработано', 
         'Средняя зарплата']
    ]
    for programming_language, salary_stat in salary_statistic.items():
        table_data.append([
            programming_language, 
            salary_stat['vacancies_found'], 
            salary_stat['vacancies_processed'], 
            salary_stat['average_salary']
        ])

    table = AsciiTable(table_data)
    table.title = table_title

    print(table.table)


def main():
    load_dotenv()
    superjob_api_key = os.environ['SUPERJOB_API_KEY']
    programming_languages = [
        'Python',
        'C++',
        'Java',
        'C',
        'C#',
        'JavaScript',
        'Go',
        'SQL',
        'Visual Basic',
        'Fortran'
    ]

    hh_salary_statistic = get_hh_salary_statistic(programming_languages)
    print_table(hh_salary_statistic, 'HeadHunter Moscow')

    sj_salary_statistic = get_sj_salary_statistic(programming_languages, superjob_api_key)
    print_table(sj_salary_statistic, 'SuperJob Moscow')


if __name__ == '__main__':
    main()