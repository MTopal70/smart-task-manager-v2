import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# .env laden
load_dotenv()

# API Key holen
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ WARNUNG: Kein GEMINI_API_KEY gefunden! ")

# Gemini konfigurieren
genai.configure(api_key=api_key)


def analyze_task_with_ai(text_input: str):
    """
    Nimmt eine Projektbeschreibung (z.B. "Urlaub planen")
    und liefert eine LISTE von Aufgaben zurück.
    """
    try:
        #model = genai.GenerativeModel("gemini-2.0-flash-exp")
        model = genai.GenerativeModel("gemini-flash-latest")

        # Der Prompt zwingt die KI, eine saubere Liste zu liefern
        prompt = f"""
        Du bist ein erfahrener Projektmanager.
        Zerlege das folgende Projekt in 3 bis 6 konkrete Einzelaufgaben (Tasks).

        Projekt: "{text_input}"

        Antworte AUSSCHLIESSLICH mit gültigem JSON in diesem Format (eine Liste von Objekten):
        [
            {{
                "title": "Titel der Aufgabe",
                "estimated_time": "Geschätzte Dauer (z.B. 2h)"
            }},
            ...
        ]
        Kein Markdown, kein Text davor oder danach. Nur das JSON-Array.
        """

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Markdown-Code-Blöcke entfernen, falls Gemini welche macht
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        # JSON parsen
        tasks_list = json.loads(raw_text)

        # Sicherheits-Check: Ist es wirklich eine Liste?
        if isinstance(tasks_list, list):
            print(f"✅ KI hat {len(tasks_list)} Aufgaben generiert.")
            return tasks_list
        else:
            print("⚠️ KI hat keine Liste zurückgegeben. Packe es in eine Liste.")
            return [tasks_list]  # Notfall-Lösung

    except Exception as e:
        print(f"❌ Fehler im KI-Service: {e}")
        # Fallback, damit nichts abstürzt
        return [{"title": "KI-Fehler: Bitte manuell prüfen", "estimated_time": "0h"}]