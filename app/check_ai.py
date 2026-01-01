import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Versuchen, .env zu laden
loaded = load_dotenv()
print(f"📂 .env geladen: {loaded}")

# 2. Key prüfen
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ FEHLER: Kein API Key in den Umgebungsvariablen gefunden!")
else:
    print(f"✅ API Key gefunden: {api_key[:5]}...*******")

    # 3. Modelle abfragen
    try:
        genai.configure(api_key=api_key)
        print("🔍 Frage Google nach verfügbaren Modellen...")
        models = genai.list_models()
        found_any = False
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                print(f"   - Verfügbar: {m.name}")
                found_any = True

        if not found_any:
            print("⚠️ Keine Modelle für 'generateContent' gefunden.")
    except Exception as e:
        print(f"❌ Verbindungstest fehlgeschlagen: {e}")