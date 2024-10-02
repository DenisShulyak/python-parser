from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


from parser_functions import login_button, get_element_by_xpath, start_parser, get_a_tags, saveToFile, load_browser

speciality_link_index = 0  # С какой специальности начать
diagnosis_link_index = 0  # С какого диагноза начать
isStart = True
parsingAttempts = 3
counter = 0
browser = load_browser()
# Шаг 4: Парсим нужные данные после успешного входа
speciality_links = get_a_tags(browser, 'Specialitystyled')

while speciality_link_index < len(speciality_links):
    try:
        start_parser(browser, speciality_links, speciality_link_index, diagnosis_link_index)
        speciality_link_index += 1
        browser.quit()
        browser = load_browser()
    except Exception as e:
        print(f"Ошибка парсинга специальнсти. Индекс: {speciality_link_index}", e)
        #  Если нужны повторные попытки парсинга категории
        # if counter < parsingAttempts:
        #     counter += 1
        # else:
        #     counter = 0
        #     speciality_link_index += 1
        #     browser.get(baseUrl)
        speciality_link_index += 1
        browser.quit()
        browser = load_browser()

# Закрываем браузер
browser.quit()

