import openai
from django.conf import settings
import pytesseract
from PIL import Image


def extract_text_from_image(image_path):
    # PIL Image object
    image = Image.open(image_path)
    # Extract text via pytesseract
    text = pytesseract.image_to_string(image)
    return text


openai.api_key = settings.OPENAI_API_KEY


def explain_medical_text(text):
    """
    Sends a prompt to OpenAI to get an explanation/summary 
    of the medical text in user-friendly language.
    """

    prompt = f"""
    You are a knowledgeable and empathetic medical assistant. 
    Your task is to explain the content of medical reports in a clear, concise, and non-technical way that can be easily understood by someone without a medical background. 

    Here is the medical report content:

    {text}

    Please provide:
    1. A summary of the key information in simple terms.
    2. The possible purpose or relevance of this report (if applicable).
    3. Any additional context or explanation that might help the reader understand it better.

    Be as detailed as needed, but keep the explanation easy to follow. Avoid technical jargon and use layman's terms wherever possible.
    """

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
        )
        # Extract the text from the response
        explanation = response.choices[0].text.strip()
        return explanation
    except Exception as e:
        print(e)
        return "Sorry, there was an error processing the request."


def translate_text_with_openai(text, target_language='es'):
    prompt = f"""
    Translate the following text to {target_language}:
    {text}
    """

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.0,
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(e)
        return "Error translating the text."
