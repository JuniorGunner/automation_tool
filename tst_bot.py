import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def date_range():

    start_date = (datetime.now() - timedelta(weeks=1)).strftime("%d/%m/%Y")
    end_date = datetime.now().strftime("%d/%m/%Y")

    print(f"{start_date=} - {end_date=}")

    return start_date, end_date


def download_pdf(start_date: str, end_date: str):
    driver = webdriver.Chrome('/etc/alternatives/google-chrome')  # set the path to chromedriver
    driver.get('https://dejt.jt.jus.br/dejt/f/n/diariocon')

    start_date_combo = driver.find_element_by_id('corpo:formulario:dataIni') 
    start_date_combo.clear()
    start_date_combo.send_keys(start_date)

    end_date_combo = driver.find_element_by_id('corpo:formulario:dataFim')
    end_date_combo.clear()
    end_date_combo.send_keys(end_date)

    print("dates setted")

    select_caderno = Select(driver.find_element_by_id('corpo:formulario:tipoCaderno'))
    select_caderno.select_by_value('Judiciário')

    print("caderno setted")

    select_orgao = Select(driver.find_element_by_id('corpo:formulario:tribunal'))
    select_orgao.select_by_value('TST')

    print("tribunal setted")

    search_button = driver.find_element_by_id('corpo:formulario:botaoAcaoPesquisar')
    search_button.click()

    print("Pesquisando...")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'result_table_id')))

    download_buttons = driver.find_elements_by_css_selector('.download-button-class')
    print("Downloading")

    for button in download_buttons:
        button.click()
        print("Downloading...")

    driver.quit()


def generate_excel(pdf_files: list):
    pass


if __name__ == '__main__':
    start_date, end_date = date_range()
    pdf_files = download_pdf(start_date, end_date)
    # excel_file = generate_excel(pdf_files)
