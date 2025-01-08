# Medical Report Analyzer SaaS

A Django-based SaaS platform that allows users to upload medical reports as images, extracts text using OCR, and provides simplified explanations using OpenAI's GPT models. The platform also supports translating medical explanations into different languages.

---

## Features

- **Image Upload**: Users can upload medical reports in image format.
- **Text Extraction**: Extracts text from uploaded images using OCR (Tesseract).
- **Medical Explanation**: Generates simplified, user-friendly explanations of the report contents using OpenAI.
- **Translation**: Translates explanations into different languages.
- **User Authentication**: Secures uploads and reports with user accounts.

---

## Technology Stack

- **Backend**: Django, Python
- **Frontend**: HTML, CSS (optional Bootstrap/Tailwind for styling)
- **AI Integration**: OpenAI API
- **OCR**: Tesseract (via `pytesseract`)
- **Database**: SQLite (default) or PostgreSQL (for production)
- **Storage**: Local or AWS S3 (for media files)

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<USERNAME>/<REPOSITORY_NAME>.git
cd <REPOSITORY_NAME>
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```


