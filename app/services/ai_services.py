# ai service

import google.generativeai as genai
from app.config import settings
import json

# 1.configure Gemini
genai.configure(api_key=settings.gemini_api_key)

def analyze_task_with_ai(text: str) -> dict:
    """
    Sends the Task_text to google Gemini API and returns the response
    """

    fallback_result = {
        "summary": text[:50],  # Titel kürzen
        "description": text,
        "priority": "Medium",
        "category": "General"
    }

    try:
        # we use the fast flash-model
        model = genai.GenerativeModel('gemini-flash-latest')

        # the prompt is the task text
        prompt = f"""
        Du bist ein intelligenter Task-Manager-Assistens.
        Analysiere den folgenden User-Input für eine neue Aufgabe: "{text}"
        
        Bitte extrahiere Informationen und antworte NUR mit einem validen JSON-Objekte.
        Kein Markdown, kein Text davor oder danach.
        
        Das JSON muss diese Felder haben:
        - "summary": Eine kurze, knackige Zusammenfassung des Tasks (als Titel).
        - "description": Eine etwas detailliertere Beschreibung (oder der Originaltext).
        - "priority": Entweder "High", "Medium" oder "Low". (Entscheide basierend auf Dringlichkeit).
        - "category": Eine passende Kategorie (z.B. "Work", "Personal", "Shopping", "Learning", "Health").
        
        Beispiel Input: "Morgen unbedingt Milch kaufen"
        Beispiel Output: {{"summary": "Milch kaufen", "description": "Morgen unbedingt Milch kaufen", "priority": "High", "category": "Shopping"}}
        """

        # sent the prompt
        response = model.generate_content(prompt)

        # DEBUG: Schauen wir mal, was Gemini antwortet (im Log sichtbar)
        print(f"DEBUG Gemini Response: {response.text}")

        # Bereinigen (Markdown entfernen)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()

        if not cleaned_text:
            print("Gemini hat leeren Text zurückgegeben!")
            return fallback_result

        # JSON parsen
        task_data = json.loads(cleaned_text)

        # Zusammenfügen (Fallback + echte Daten)
        final_result = {**fallback_result, **task_data}

        return final_result

    except Exception as e:
        print(f"AI Error: {e}")
        # WICHTIG: Im Fehlerfall geben wir IMMER die Fallback-Daten zurück, damit die App nicht abstürzt!
        return fallback_result






















