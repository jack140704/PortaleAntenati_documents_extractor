import base64
import time
import os
import shutil
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scarica_registro(url, output_folder, numero_pagine_da_salvare, thread_id):
    """Funzione eseguita dal singolo thread per scaricare un registro."""
    
    # 1. Crea la cartella per i salvataggi
    os.makedirs(output_folder, exist_ok=True)

    # 2. Configura le opzioni di Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-site-isolation-trials")
    
    # OPZIONALE: Scommenta la riga sotto per eseguire Chrome in background senza aprire le finestre a schermo.
    # Molto utile quando si usano molti thread.
    # chrome_options.add_argument("--headless=new")
    
    # IMPORTANTE: Crea una cartella del profilo univoca per questo thread
    temp_profile = rf"C:\temp-chrome-profile-thread-{thread_id}"
    chrome_options.add_argument(f"--user-data-dir={temp_profile}") 

    # 3. Inizializza il browser per questo specifico thread
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Accetta i cookie (se presenti)
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "cookie_action_close_header"))
            )
            cookie_btn.click()
        except:
            pass
        
        selettore_avanti = ".mirador-next-canvas-button"
        
        for i in range(numero_pagine_da_salvare):
            print(f"[Thread {thread_id} | {output_folder}] Elaborazione pagina {i+1}/{numero_pagine_da_salvare}...")
            
            canvas_xpath = "//canvas[@aria-label='Digitized view']"
            canvas = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, canvas_xpath))
            )
            
            # Attendiamo per la messa a fuoco
            time.sleep(3) 
            
            # Estrai i pixel dal canvas
            canvas_base64 = driver.execute_script(
                "return arguments[0].toDataURL('image/png');", canvas
            )
            
            base64_data = canvas_base64.split(",")[1]
            
            nome_file = os.path.join(output_folder, f"documento_pagina_{i+1}.png")
            with open(nome_file, "wb") as fh:
                fh.write(base64.b64decode(base64_data))
            
            # Trova e clicca 'Avanti'
            try:
                pulsante_next = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selettore_avanti))
                )
                driver.execute_script("arguments[0].click();", pulsante_next)
                time.sleep(1)
            except Exception:
                print(f"[Thread {thread_id} | {output_folder}] Pulsante 'Avanti' non trovato. Fine del registro.")
                break

    except Exception as e:
        print(f"[Thread {thread_id} | {output_folder}] Si è verificato un errore: {e}")
    finally:
        print(f"[Thread {thread_id} | {output_folder}] Operazione conclusa. Chiusura driver.")
        driver.quit()
        
        # Pulizia della cartella temporanea del profilo per non intasare l'hard disk
        try:
            if os.path.exists(temp_profile):
                shutil.rmtree(temp_profile, ignore_errors=True)
        except:
            pass

# ==========================================
# ESECUZIONE MULTI-THREAD
# ==========================================
if __name__ == "__main__":
    # Definisci qui tutti i registri che vuoi scaricare
    registri_da_scaricare = [
        # Matrimonio Carlo
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825806/wkNmm4e",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1912",
            "pagine": 76
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825791/LyJBpkq",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1911",
            "pagine": 70
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825776/wj6v26K",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1910",
            "pagine": 60
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825761/wrMG11O",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1909",
            "pagine": 59
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825745/0A6zJl8",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1908",
            "pagine": 64
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825730/w1ogr76",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1907",
            "pagine": 76
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825715/5VAnxmP",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1906",
            "pagine": 60
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825700/w1og2nD",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1905",
            "pagine": 86
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825685/5VAnN9d",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1904",
            "pagine": 66
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825669/wEdNbpX",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1903",
            "pagine": 56
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37825654/LNKMgY7",
            "output_folder": "registri_antenati/Matrimonio_Carlo/1902",
            "pagine": 70
        },
        # Morte Carlo
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827407/03aV9GY",
            "output_folder": "registri_antenati/Morte_Carlo/1936",
            "pagine": 68
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827398/LmZBEWM",
            "output_folder": "registri_antenati/Morte_Carlo/1935",
            "pagine": 82
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827379/wrMBQlO",
            "output_folder": "registri_antenati/Morte_Carlo/1934",
            "pagine": 82
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827365/0J7YW32",
            "output_folder": "registri_antenati/Morte_Carlo/1933",
            "pagine": 80
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827351/5xmB7jg",
            "output_folder": "registri_antenati/Morte_Carlo/1932",
            "pagine": 66
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827337/04Y3a2a",
            "output_folder": "registri_antenati/Morte_Carlo/1931",
            "pagine": 74
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827323/04Y3azQ",
            "output_folder": "registri_antenati/Morte_Carlo/1930",
            "pagine": 84
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827310/wbxOA6A",
            "output_folder": "registri_antenati/Morte_Carlo/1929",
            "pagine": 72
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827295/5dqBnRE",
            "output_folder": "registri_antenati/Morte_Carlo/1928",
            "pagine": 68
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827282/5VAOGJ1",
            "output_folder": "registri_antenati/Morte_Carlo/1927",
            "pagine": 70
        },
        {
            "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37827268/wEdrE9d",
            "output_folder": "registri_antenati/Morte_Carlo/1926",
            "pagine": 82
        },

        
        # Aggiungi un nuovo dizionario {...} per ogni link aggiuntivo
    ]

    # Quanti browser vuoi aprire in contemporanea?
    # ATTENZIONE: Non esagerare con i thread simultanei. Troppe richieste in parallelo
    # saturano la RAM/CPU e possono causare il blocco del tuo IP da parte del server remoto.
    MAX_THREADS = 5

    print(f"Avvio del sistema con {MAX_THREADS} worker simultanei...")
    
    # ThreadPoolExecutor gestirà le esecuzioni parallele in automatico
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for index, task in enumerate(registri_da_scaricare):
            # Sottomettiamo la funzione e i relativi parametri al gestore dei thread
            future = executor.submit(
                scarica_registro, 
                url=task["url"], 
                output_folder=task["output_folder"], 
                numero_pagine_da_salvare=task["pagine"], 
                thread_id=index + 1
            )
            futures.append(future)
            
        # Il main attenderà qui finché tutti i thread non hanno terminato
        for future in concurrent.futures.as_completed(futures):
            future.result() # Permette di intercettare eventuali eccezioni
            
    print("\n--- Tutti i download sono stati completati con successo! ---")