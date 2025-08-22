from playwright.sync_api import sync_playwright
import requests
import json

def main():
    with sync_playwright() as p:
        # Avvia browser reale
        my_path="C:\Program Files\Google\Chrome\Application\chrome.exe"
        browser = p.chromium.launch(headless=False,executable_path=my_path)  # headless=True se non vuoi vedere la finestra
        context = browser.new_context()
        page = context.new_page()

        # Vai al sito
        page.goto("https://leghe.fantacalcio.it/bacheca-leghe-pubbliche")

        print("🔑 Fai login manualmente nella finestra del browser...")
        input("➡️ Premi INVIO quando hai completato il login...")

        # Estrai cookie
        cookies = context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        print(cookie_str)

        # Ora puoi fare la tua chiamata
        url = "https://leghe.fantacalcio.it/servizi/v1_leghe/leghepubbliche?page=1&limit=5"

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "origin": "https://leghe.fantacalcio.it",
            "referer": "https://leghe.fantacalcio.it/bacheca-leghe-pubbliche",
            "cookie": cookie_str,
        }
        
        print(cookie_str)
        payload = {}
        response = requests.put(url, headers=headers, json=payload)

        print("Status:", response.status_code)
        print("Risposta:", response.text)

        browser.close()

if __name__ == "__main__":
    main()
