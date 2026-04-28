import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    try:
        response = model.generate_content(
            "Give me a JSON with a single key 'test' and value 'hello'",
            generation_config={"response_mime_type": "application/json"}
        )
        print("Success:", response.text)
    except Exception as e:
        print("Error:", e)
else:
    print("No API KEY")
