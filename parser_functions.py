import json
from telnetlib import EC
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from models import Title, Item, Section, Diagnosis, Block

# Шаг 1: Ожидание и нажатие кнопки "Войти" для перехода к вводу телефона
def login_button(browser):
    try:
        login_button = WebDriverWait(browser, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//*[text()="Войти"]'))  # Поиск по тексту кнопки
        )
        login_button.click()
    except Exception as e:
        print("Ошибка при нажатии кнопки 'Войти':", e)
        browser.quit()


def get_a_tags(browser, class_name_contains):
    return WebDriverWait(browser, 2).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "' + class_name_contains + '")]'))
    )


def get_elements_by_xpath(browser, xpath, element=None):
    try:
        if element is not None:
            return element.find_elements(By.XPATH, xpath)
        else:
            return WebDriverWait(browser, 2).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
    except Exception:
        return []


def get_element_by_xpath(browser, xpath, element=None):
    try:
        if element is not None:
            return element.find_element(By.XPATH, xpath)
        else:
            return WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
    except Exception:
        return None

def find_diagnosis_group_name(browser, diagnos_block):
    try:
        return get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisGroupstyled__Name")]', diagnos_block)
    except NoSuchElementException:
        return None


def find_sub_block_btn(browser, item):
    try:
        return get_element_by_xpath(browser, './/button', item)
    except NoSuchElementException:
        return None


def back_button_click(browser):
    back_button = get_a_tags(browser, "BackButtonstyled__Root")[0]
    back_button.click()


def get_section_json(section):
    return json.dumps(section.to_dict(), indent=4, ensure_ascii=False)


def get_sections_json(sections):
    return json.dumps([section.to_dict() for section in sections], indent=4, ensure_ascii=False)


def saveToFile(json_data, filename=None):
    if not filename:
        filename = "data"
    with open(f"parsed_data/{filename}.json", "w", encoding="utf-8") as file:
        file.write(json_data)


def get_items_by_element(browser, element, title=None):
    diagnosis_block_items = get_elements_by_xpath(browser, './/div[contains(@class, "DiagnosisItemstyled__Root")]', element)
    items = []
    if title:
        for item in diagnosis_block_items:
            name_element = get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisItemstyled__Name")]', item)
            items.append(name_element.text)
        return Title(title, items)

    name_element = get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisItemstyled__Name")]', element)
    item_btn = find_sub_block_btn(browser, element)
    if item_btn:
        browser.execute_script("arguments[0].scrollIntoView(true);", item_btn)
        item_btn.click()
        sub_items = get_elements_by_xpath(browser, './/div[contains(@class, "DiagnosisItemVariantstyled__Root")]')
        sub_items_list = []
        for sub_item in sub_items:
            sub_name_element = get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisItemVariantstyled__Name")]', sub_item)
            sub_items_list.append(sub_name_element.text)
        browser.execute_script("arguments[0].scrollIntoView(true);", item_btn)
        item_btn.click()
        return Item(name_element.text, sub_items_list)
    return Item(name_element.text)


def start_parser(browser, speciality_links, speciality_link_index=0, diagnosis_link_index=0):
    speciality_link = get_a_tags(browser, 'Specialitystyled')[speciality_link_index]
    speciality_description = get_element_by_xpath(browser, './/div[contains(@class, "Specialitystyled__Description")]', speciality_link)
    # Создание медицинской секции
    section = Section(name=speciality_description.text)

    # Переход на страницу диагноза
    speciality_link.click()

    diagnosies_links = get_a_tags(browser, 'Diagnosisstyled__Root')

    print(f"{section.name} ({speciality_link_index + 1}/{len(speciality_links)})")

    for diagnosis_link in diagnosies_links:
        try:

            diagnosis_link = get_a_tags(browser, 'Diagnosisstyled__Root')[diagnosis_link_index]
            diagnos_description = get_element_by_xpath(browser, './/div[contains(@class, "Diagnosisstyled__Description")]',
                                                       diagnosis_link)
            diagnosis_code = get_element_by_xpath(browser, './/div[contains(@class, "Diagnosisstyled__Code")]')
            # Создание диагноза и добавление в секцию
            diagnosis = Diagnosis(diagnos_description.text, diagnosis_code.text)
            print(f"        {diagnosis.name} ({diagnosis_link_index + 1}/{len(diagnosies_links)})")

            diagnosis_link.click()
            # Достать блоки
            diagnosis_blocks = get_elements_by_xpath(browser, './/div[contains(@class, "DiagnosisSectionstyled__Root")]')
            attempts = 10
            count = 0
            while len(diagnosis_blocks) == 0 and count < attempts:
                diagnosis_blocks = get_elements_by_xpath(browser, './/div[contains(@class, "DiagnosisSectionstyled__Root")]')
                count += 1
            print(f"            Блоки ({len(diagnosis_blocks)})")
            for diagnosis_block in diagnosis_blocks:
                diagnosis_block_name = get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisSectionstyled__Name")]', diagnosis_block)
                diagnosis_block_content = get_element_by_xpath(browser, './/div[contains(@class, "DiagnosisSectionstyled__Content")]', diagnosis_block)
                diagnosis_block_sections = get_elements_by_xpath(browser, './div', diagnosis_block_content)

                items = []
                titles = []
                if diagnosis_block_sections:
                    for diagnosis_block_section in diagnosis_block_sections:
                        diagnosis_block_group_name = find_diagnosis_group_name(browser, diagnosis_block_section)
                        diagnosis_block_group_name_text = diagnosis_block_group_name.text if diagnosis_block_group_name else None
                        if (diagnosis_block_group_name_text):
                            titles.append(
                                get_items_by_element(browser, diagnosis_block_section, diagnosis_block_group_name_text))
                        else:
                            items.append(get_items_by_element(browser, diagnosis_block_section))

                comment_button = get_element_by_xpath(browser, '//div[contains(@class, "CommentButtonstyled__Root")]')
                recommendation = None
                norecommendation = None
                if comment_button:
                    comment_button.click()

                    comments = get_elements_by_xpath(browser, '//div[contains(@class, "CommentItemstyled__Root")]')
                    if len(comments) == 1:
                        recommendation = comments[0].get_attribute('outerHTML')
                    if len(comments) == 2:
                        recommendation = comments[0].get_attribute('outerHTML')
                        norecommendation = comments[1].get_attribute('outerHTML')

                    close_comment_button = get_element_by_xpath(browser, '//div[contains(@class, "CommentSectionstyled__Button")]')
                    close_comment_button.click()

                diagnosis.add_block(
                    Block(name=diagnosis_block_name.text, recommendation=recommendation, norecommendation=norecommendation, items=items, titles=titles))
                print(f"             ✓{diagnosis_block_name.text} ({len(items)} - {len(titles)})")
            section.add_diagnosis(diagnosis)
            json_data = get_section_json(section)
            saveToFile(json_data, section.name)
            back_button_click(browser)
            diagnosis_link_index += 1
        except Exception:
            print(f"Ошибка парсинга диагноза. Индекс: {diagnosis_link_index}")
            diagnosis_link_index += 1

    back_button_click(browser)
    speciality_link_index += 1