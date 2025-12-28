import google.generativeai as genai

# HIER DEINEN KEY REINKOPIEREN
MY_KEY = "AIzaSyDKgx4Qg2lkx2G4en5Czc6yR6yZVhDiftI"

genai.configure(api_key=MY_KEY)

print("Verfügbare Modelle:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)