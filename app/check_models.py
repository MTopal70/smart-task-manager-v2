import google.generativeai as genai

# HIER DEINEN KEY REINKOPIEREN
MY_KEY = ""

genai.configure(api_key=MY_KEY)

print("Verfügbare Modelle:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)