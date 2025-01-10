import re
import requests
import openai
from django.conf import settings
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
openai.api_key = settings.OPENAI_API_KEY

def extract_text_from_image(image_path):
    # PIL Image object
    image = Image.open(image_path)
    # Extract text via pytesseract
    text = pytesseract.image_to_string(image)
    return text


def explain_medical_text(text):
    """
    Sends a prompt to Gemini Pro to get an explanation/summary 
    of the medical text in user-friendly language.
    """

    # Define the API endpoint and key
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    # Replace with your actual Gemini API key
    api_key = "AIzaSyAgMEXRLnWiyCMm4lTGh_aoQKGNVp34Jag"

    # Construct the headers
    headers = {
        "Content-Type": "application/json",
    }

    # Define the payload
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
                        Your task is to explain the content of medical reports in a clear, concise, and non-technical way that can be easily understood by someone without a medical background.

                        Here is the medical report content:

                        {text}

                        Please provide:

                        Summary of Key Information: Clearly explain the main points of the report in simple and easy-to-follow language. Use a narrative format rather than bullet points.
                        Possible Purpose or Relevance: Discuss why this report might be important or what it is addressing in a paragraph format.
                        Additional Context or Explanation: Provide any helpful details or background information to ensure the reader fully understands the content, written as a cohesive narrative.
                        
                        Be as detailed as needed while maintaining simplicity and clarity. Avoid technical jargon and ensure the explanation flows naturally.
                        """
            }]
        }]
    }

    try:
        # Make the POST request
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params={"key": api_key}  # API key as a query parameter
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']

        explanation_html = format_response_as_html(raw_text)
        return explanation_html

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}


def format_response_as_html(raw_text):
    """
    Converts the raw response text into HTML by replacing markdown-like syntax with HTML tags.
    """
    # Convert section headings (**Title**) into <h2> tags
    html = re.sub(r"\*\*Summary of Key Information:\*\*",
                  r"<h2>Summary of Key Information:</h2>", raw_text)
    html = re.sub(r"\*\*Possible Purpose or Relevance:\*\*",
                  r"<h2>Possible Purpose or Relevance:</h2>", html)
    html = re.sub(r"\*\*Additional Context or Explanation:\*\*",
                  r"<h2>Additional Context or Explanation:</h2>", html)

    # Convert bold text (**Text**) into <strong> tags
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

    # Handle italic text (*Text*) into <em> tags
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # Convert bullet points (*) into <li> tags inside a <ul>
    # Wrap individual points in <li>
    html = re.sub(r"\n\* (.+)", r"<li>\1</li>", html)
    html = re.sub(r"(<li>.+?</li>)", r"<ul>\1</ul>",
                  html, count=1)  # Wrap first set in <ul>

    # Ensure all lists are properly closed
    html = html.replace("</li><ul>", "</li></ul><ul>")

    # Return the processed HTML
    return html.strip()



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
