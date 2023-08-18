from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pypdf
import re
import os
import pandas as pd


def date_range():
    start_date = (datetime.now() - timedelta(weeks=1)).strftime("%d/%m/%Y")
    end_date = datetime.now().strftime("%d/%m/%Y")

    print(f"{start_date=} - {end_date=}")

    return start_date, end_date


def download_pdf(start_date: str, end_date: str):
    print("Fazendo download dos arquivos .pdf...")

    # Get the user's Desktop directory
    desktop = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

    # Define the directory where the PDF files will be downloaded
    pdf_folder = "cadernos_tst"

    # Full path to the PDF folder
    pdf_folder_path = os.path.join(desktop, pdf_folder)

    # Check if the directory exists, and create it if necessary
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)

    chrome_options = webdriver.ChromeOptions()

    # Set the default download directory to the specified folder
    prefs = {"download.default_directory": pdf_folder_path}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://dejt.jt.jus.br/dejt/f/n/diariocon")

    start_date_combo = driver.find_element(By.ID, "corpo:formulario:dataIni")
    start_date_combo.clear()
    start_date_combo.send_keys(start_date)

    end_date_combo = driver.find_element(By.ID, "corpo:formulario:dataFim")
    end_date_combo.clear()
    end_date_combo.send_keys(end_date)

    select_caderno_element = driver.find_element(By.ID, "corpo:formulario:tipoCaderno")
    select_caderno = Select(select_caderno_element)

    select_caderno.select_by_visible_text("Judiciário")

    select_orgao_element = driver.find_element(By.ID, "corpo:formulario:tribunal")
    select_orgao = Select(select_orgao_element)
    select_orgao.select_by_visible_text("TST")

    search_button = driver.find_element(By.ID, "corpo:formulario:botaoAcaoPesquisar")
    search_button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "plc-fieldset"))
    )

    download_buttons = driver.find_elements(
        By.XPATH, "//button[@class = 'bt af_commandButton']"
    )

    for button in download_buttons:
        button.click()

    driver.quit()

    return pdf_folder_path


def generate_excel(pdf_folder_path):
    print("Gerando excel...")
    all_data = []
    process_number_pattern = re.compile(r"Processo N[º°]?\s+(\S+)")

    for filename in os.listdir(pdf_folder_path):
        process_data = []
        print(f"{filename=}")
        if filename.endswith(".pdf"):
            # Extract the day, month, and year from the filename
            parts = filename.split("_")
            day, month, year = parts[-3], parts[-2], parts[-1].split(".")[0]
            date = f"{day}/{month}/{year}"
            print(f"{date=}")

            with open(os.path.join(pdf_folder_path, filename), "rb") as file:
                reader = pypdf.PdfReader(file)
                print(f"{reader}")
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    found_process_numbers = process_number_pattern.findall(text)

                    for process_number in found_process_numbers:
                        process_data.append({"Número do Processo": process_number})
                        all_data.append(
                            {"Data": date, "Número do Processo": process_number}
                        )

            df_per_day = pd.DataFrame(process_data)
            date = date.replace("/", "_")
            df_per_day.to_excel(
                os.path.join(pdf_folder_path, f"TST_{date}.xlsx"), index=False
            )

    df_all = pd.DataFrame(all_data)
    duplicates = df_all[df_all.duplicated("Número do Processo", keep=False)]
    duplicates.to_excel(os.path.join(pdf_folder_path, "Duplicatas.xlsx"), index=False)

    print(f"Arquivos gerados com sucesso em: {pdf_folder_path}")


if __name__ == "__main__":
    start_date, end_date = date_range()
    pdf_folder_path = download_pdf(start_date, end_date)
    excel_file = generate_excel(pdf_folder_path)
