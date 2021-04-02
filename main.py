import datetime as dt
import json

import requests
from bs4 import BeautifulSoup

from models.traineeship import Traineeship


def main(url, params, source, output_filename='output.json', prev_output_filename='output.json'):
    response = requests.get(url, params=params)
    if not response:
        return f'Не удалось получить доступ к сайту {url}'
    tags = {'IT, Интернет, связь, телеком': 'it',
            'Кадры, управление персоналом': 'hr',
            'Маркетинг, реклама, PR': 'marketing',
            'Дизайн': 'design',
            'Бухгалтерия, экономика и финансы': 'economics',
            'Право и юриспруденция': 'jurisprudence'}
    try:
        with open(prev_output_filename, encoding='utf-8') as json_file:
            models = json.loads(json_file.read())
        used_models = [mod.get('id') for mod in models]
    except FileNotFoundError:
        models, used_models = [], []
    while True:
        params['page'] = params.get('page', 0) + 1
        response = requests.get(url, params=params)
        if not response:
            print(f'Не удалось получить доступ к сайту {url}')
            continue
        if int(response.url.split('&')[-1].split('=')[1]) < params['page']:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_="TraineeshipList_item stu_block h_position_relative")
        for card in cards:
            try:
                position = card.find('h2', class_='TraineeshipList_item_post h_color_black').get_text()
            except AttributeError:
                position = None
            try:
                link = card.find('a', class_='h_color_black h_border_none').get('href')
            except AttributeError:
                continue
            try:
                id = int(link.rstrip('/').split('/')[-1].split('-')[-1])
                assert id not in used_models
            except (ValueError, AssertionError):
                continue
            tag_blocks = card.find_all('a', class_='sj_tag')
            try:
                city, specialization, company = map(lambda x: x.get_text(), tag_blocks[::-1])
            except AttributeError:
                city, specialization, company = None, None, None
            try:
                salary = card.find('div', class_='TraineeshipList_item_payment').get_text().strip()
                try:
                    salary = int(''.join(salary.split()))
                except ValueError:
                    pass
            except AttributeError:
                salary = None
            models.append(Traineeship(id=id, position=position, link=link, city=city,
                                      specialization=specialization, company=company, salary=salary,
                                      source=source, date=dt.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                      tag=tags.get(specialization)))
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps([mod.dict() if isinstance(mod, Traineeship) else mod for mod in models]))
        print(f'successfully wrote {output_filename}')


if __name__ == '__main__':
    url = 'https://students.superjob.ru/stazhirovki'
    params = {'actualOnly': 1, 'from_refresh': 1}
    source = 'students.superjob'
    callback = main(url, params, source)
    if callback:
        print(callback)
