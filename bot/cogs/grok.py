from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API"))

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents="hi",
)

print(response.text)