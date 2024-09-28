import json

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from models import Section, Diagnosis, Block, Item, Title
from parser_functions import login_button, get_element_by_xpath, start_parser, get_a_tags

chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в headless режиме
chrome_options.add_argument("--disable-gpu")  # Отключение использования GPU
# chrome_options.add_argument("--no-sandbox")  # Без песочницы
chrome_options.add_argument("--window-size=1920,1080")  # Эмуляция окна браузера с разрешением 1920x1080
chrome_options.add_argument("--start-maximized")  # Полноэкранный режим

baseUrl = 'https://assist.fomin-clinic.ru/'

time_sec = 0.7

sections = []

# Убедитесь, что у вас скачан ChromeDriver и добавлен в PATH
browser = webdriver.Chrome(options=chrome_options)

# Открываем сайт
browser.get(baseUrl)  # Замените на нужный вам URL

# Шаг 1: Нажать кнопку войти

login_button(browser)

# Шаг 2: Ввод номера телефона
try:
    phone_input = get_element_by_xpath(browser, '//*[@placeholder="(000) 000 00 00"]')
    phone_input.send_keys('9889928451')

    confirm_phone_button = get_element_by_xpath(browser, '//*[text()="Ввести пароль (если установлен)"]')
    # Нажимаем на кнопку для подтверждения номера телефона (если нужно)
    confirm_phone_button.click()
except Exception as e:
    print("Ошибка при вводе номера телефона:", e)
    browser.quit()

# Шаг 3: Ввод пароля
try:
    password_input = WebDriverWait(browser, 2).until(
        EC.presence_of_element_located((By.NAME, 'password'))
    )
    password_input.send_keys('8451')
    # Нажимаем кнопку "Войти" для подтверждения пароля
    confirm_password_button = get_element_by_xpath(browser, '(//*[text()="Войти"])[2]')
    confirm_password_button.click()
except Exception as e:
    print("Ошибка при вводе пароля:", e)
    browser.quit()

speciality_link_index = 0  # С какой специальности начать
diagnosis_link_index = 0  # С какого диагноза начать
isStart = True
parsingAttempts = 3
counter = 0
# Шаг 4: Парсим нужные данные после успешного входа
speciality_links = get_a_tags(browser, 'Specialitystyled')

while speciality_link_index < len(speciality_links):
    try:
        start_parser(browser, speciality_links, speciality_link_index, diagnosis_link_index)
        speciality_link_index += 1
    except Exception:
        print(f"Ошибка парсинга специальнсти. Индекс: {speciality_link_index}")
        if counter < parsingAttempts:
            counter += 1
        else:
            counter = 0
            speciality_link_index += 1
            browser.get(baseUrl)

# Закрываем браузер
browser.quit()

