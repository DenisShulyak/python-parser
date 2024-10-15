import json

import requests

from models import Section, Diagnosis, Block, Title, Item, Value


def get_section_json(section):
    return json.dumps(section.to_dict(), indent=4, ensure_ascii=False)

def saveToFile(json_data, filename=None):
    if not filename:
        filename = "data"
    with open(f"parsed_data/{filename}.json", "w", encoding="utf-8") as file:
        file.write(json_data)

def parseSpetiality(session,id=None, name=None, isPopular=False):
    section = Section(name)
    response_diagnoses = session.get(diagnoses_url + str(id)) if not isPopular else session.get('https://assist.fomin-clinic.ru/api/diagnoses/?popular=true')
    if response_diagnoses.status_code == 200:
        data_diagnoses = response_diagnoses.json()
        for diagnosis in data_diagnoses:
            diagnosis_id = diagnosis['id']
            diagnosis_code = diagnosis['icd_code']
            diagnosis_name = diagnosis['name']
            diagnosis_object = Diagnosis(diagnosis_name, diagnosis_code)
            diagnosis_url = "https://assist.fomin-clinic.ru/api/diagnoses/" + str(diagnosis_id) + "/conclusions/"
            response_diagnosis = session.get(diagnosis_url)
            if response_diagnosis.status_code == 200:
                data_diagnosis = response_diagnosis.json()
                guide = data_diagnosis['guide']
                for key in data_diagnosis.keys():
                    if key.endswith('_conclusions'):
                        key_name = key.replace('_conclusions', '')
                        ru_block_name = ''
                        if key_name == 'examination':
                            ru_block_name = 'Обследования'
                        if key_name == 'medication':
                            ru_block_name = 'Медикаментозное лечение'
                        no_recommended = None
                        recommended = None
                        try:
                            no_recommended = guide[key_name + 's_not_recommended']
                            recommended = guide[key_name + 's_recommended']
                        except:
                            no_recommended = None
                            recommended = None
                        conclusions = data_diagnosis[key_name + '_conclusions']
                        items = []
                        titles = []
                        for conclusion in conclusions:
                            conclusion_name = conclusion['name']
                            conclusion_comment = None
                            try:
                                conclusion_comment = conclusion['comment']
                            except:
                                conclusion_comment = None
                            try:
                                values = conclusion[key_name + 's']
                                title_values = []
                                for value in values:
                                    value_name = value['name']
                                    value_comment = None
                                    try:
                                        value_comment = value['comment']
                                    except:
                                        value_comment = None
                                    title_values.append(Value(value_name, value_comment))

                                titles.append(Title(conclusion_name, conclusion_comment, title_values))
                            except:
                                variants = conclusion['variants']
                                item_values = []
                                for variant in variants:
                                    variant_name = variant['name']
                                    variant_comment = None
                                    try:
                                        variant_comment = variant['comment']
                                    except:
                                        variant_comment = None
                                    item_values.append(Value(variant_name, variant_comment))
                                titles.append(Item(conclusion_name, conclusion_comment, item_values))

                        diagnosis_object.add_block(
                            Block(name=ru_block_name, recommendation=recommended, norecommendation=no_recommended,
                                  items=items, titles=titles))
                    # Если есть рекомендации, добавить
                try:
                    if data_diagnosis['recommendations']:
                        ru_block_name = 'Рекомендации'
                        no_recommended = guide['recommendations_not_recommended']
                        recommended = guide['recommendations_recommended']
                        titles = []
                        items = []
                        for conclusion in data_diagnosis['recommendations']:
                            conclusion_name = conclusion['name']
                            conclusion_comment = conclusion['comment']
                            titles.append(Title(conclusion_name, conclusion_comment))
                        diagnosis_object.add_block(
                            Block(name=ru_block_name, recommendation=recommended,
                                  norecommendation=no_recommended,
                                  items=items, titles=titles))
                except:
                    t = True

            section.add_diagnosis(diagnosis_object)
        json_data = get_section_json(section)
        saveToFile(json_data, name)
        print("Имопртирован: " + name)

auth_url = "https://assist.fomin-clinic.ru/api/auth/confirm_password/"

# Данные для авторизации
payload = {
    'phone_number': '79889928451',
    'password': '8451'
}

# Используем сессию для сохранения состояния
with requests.Session() as session:
    # Делаем POST-запрос для авторизации
    auth_response = session.post(auth_url, json=payload)

    # Проверяем успешность авторизации
    if auth_response.status_code == 200:
        print("Успешная авторизация!")

    # URL API
    url = "https://assist.fomin-clinic.ru/api/specialities/"
    diagnoses_url = "https://assist.fomin-clinic.ru/api/diagnoses/?speciality_id="

    # Делаем GET-запрос к API
    response = session.get(url)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Парсим JSON-ответ
        data = response.json()

        popular_name = 'Популярные диагнозы'
        print(f"ID: popular, Название: {popular_name}")
        parseSpetiality(session=session, name=popular_name, isPopular=True)
        # Проходим по каждому элементу списка
        for item in data:
            id = item['id']
            name = item['name']
            diagnoses_count = item['diagnoses_count']
            print(f"ID: {id}, Название: {name}, Количество диагнозов: {diagnoses_count}")
            parseSpetiality(session=session, id=id, name=name)

    else:
        print(f"Ошибка при запросе данных. Статус код: {response.status_code}")
