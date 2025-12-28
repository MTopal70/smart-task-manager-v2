from app.services.ai_services import analyze_task_with_ai

text = "Nächste Woche unbedingt Mama anrufen wegen Geburtstag"
print(f"🤖 Frage Gemini: {text}")

ergebnis = analyze_task_with_ai(text)

print("\n📦 Ergebnis:")
print(ergebnis)
