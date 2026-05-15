import base64
import time
import os
import shutil
import re
import glob
import concurrent.futures
import img2pdf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import to_be_processed
def crea_pdf_da_immagini(cartella_input, nome_pdf, thread_id):
    """Raccoglie le immagini scaricate e le unisce in un unico PDF usando img2pdf."""
    print(f"[Thread {thread_id} | {cartella_input}] Avvio creazione PDF tramite img2pdf...")
    
    # Cerca tutte le immagini PNG nella cartella
    percorso_ricerca = os.path.join(cartella_input, "documento_pagina_*.png")
    file_immagini = glob.glob(percorso_ricerca)
    
    if not file_immagini:
        print(f"[Thread {thread_id} | {cartella_input}] Nessuna immagine trovata per creare il PDF.")
        return

    # Ordina i file numericamente
    try:
        file_immagini.sort(key=lambda x: int(re.search(r'pagina_(\d+)', x).group(1)))
    except Exception as e:
        print(f"[Thread {thread_id}] Errore durante l'ordinamento dei file: {e}")
        return

    # Salva il file PDF
    percorso_pdf = os.path.join(os.path.dirname(cartella_input), nome_pdf)
    
    try:
        # img2pdf fa tutto il lavoro sporco in modo molto più efficiente
        with open(percorso_pdf, "wb") as f:
            f.write(img2pdf.convert(file_immagini))
            
        print(f"[Thread {thread_id} | {cartella_input}] PDF creato con successo: {nome_pdf}")
        
        # OPZIONALE: Scommenta le due righe sotto per eliminare le PNG dopo aver creato il PDF
        # for file in file_immagini:
        #     os.remove(file)
            
    except Exception as e:
        print(f"[Thread {thread_id}] ERRORE CRITICO durante la creazione del PDF con img2pdf: {e}")

def scarica_registro(url, output_folder, numero_pagine_da_salvare, thread_id):
    """Funzione eseguita dal singolo thread per scaricare un registro."""
    
    os.makedirs(output_folder, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-site-isolation-trials")
    # chrome_options.add_argument("--headless=new") # Esecuzione in background (consigliata)
    
    temp_profile = rf"C:\temp-chrome-profile-thread-{thread_id}"
    chrome_options.add_argument(f"--user-data-dir={temp_profile}") 

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

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
            
            time.sleep(2) 
            
            canvas_base64 = driver.execute_script(
                "return arguments[0].toDataURL('image/png');", canvas
            )
            
            base64_data = canvas_base64.split(",")[1]
            
            nome_file = os.path.join(output_folder, f"documento_pagina_{i+1}.png")
            with open(nome_file, "wb") as fh:
                fh.write(base64.b64decode(base64_data))
            
            try:
                pulsante_next = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selettore_avanti))
                )
                driver.execute_script("arguments[0].click();", pulsante_next)
                time.sleep(1)
            except Exception:
                print(f"[Thread {thread_id} | {output_folder}] Pulsante 'Avanti' non trovato. Fine del registro.")
                break

        # A download finito, invoca la funzione per creare il PDF
        # Il PDF prenderà il nome della cartella (es. "1939_Registro.pdf")
        nome_cartella_finale = os.path.basename(os.path.normpath(output_folder))
        nome_pdf = f"{nome_cartella_finale}_Registro.pdf"
        crea_pdf_da_immagini(output_folder, nome_pdf, thread_id)

    except Exception as e:
        print(f"[Thread {thread_id} | {output_folder}] Si è verificato un errore: {e}")
    finally:
        print(f"[Thread {thread_id} | {output_folder}] Operazione conclusa. Chiusura driver.")
        driver.quit()
        
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
    #   Esempio di struttura per ogni registro:
    # {
    #   "url": "https://antenati.cultura.gov.it/ark:/12657/an_ua37813016/wbxPPJ4",
    #   "output_folder": "registri_antenati/Morti_Cuneo/1904",
    #   "pagine": 384
    # },
    

    
    ### INSERIRE QUI I REGISTRI CHE VUOI SCARICARE ###
    #                                                #
    registri_da_scaricare = to_be_processed.Morti_cuneo
    #                                                #
    ###--------------------------------------------###



    # Quanti browser vuoi aprire in contemporanea?
    # ATTENZIONE: Non esagerare con i thread simultanei. Troppe richieste in parallelo
    # saturano la RAM/CPU e possono causare il blocco del tuo IP da parte del server remoto.
    MAX_THREADS = 7

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