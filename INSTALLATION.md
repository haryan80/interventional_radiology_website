# 🚀 First KHCC Interventional Oncology Conference Website - Installation Guide

## 📋 Prerequisites

- Python 3.10 or higher
- pip package manager

## 🔧 Setup Steps

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Create necessary directories

Ensure these directories exist for proper operation:

```bash
mkdir -p static/images static/css static/js media/speakers
```

### 3️⃣ Set up environment variables

Make sure to set up your OpenAI API key in the `.env` file to enable GPT-4o for processing speaker files:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=your_api_key_here
```

### 4️⃣ Make migrations

Generate migration files for the database models:

```bash
python manage.py makemigrations
```

### 5️⃣ Apply migrations

Apply the migrations to create the database tables:

```bash
python manage.py migrate
```

### 6️⃣ Process speaker data

Run the script to process speaker data from the website_material directory:

```bash
python process_speakers.py
```

This script will:
- Extract speaker information from the provided files using GPT-4o
- Parse PDFs, Word documents, and other file formats to extract bios, titles, and institutions
- Create speaker entries in the database
- Copy speaker photos to the media directory
- Create a sample conference schedule

> Note: The GPT-4o integration requires a valid OpenAI API key in your `.env` file. Without this key, the script will still run but with limited functionality.

### 7️⃣ Create a superuser (admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8️⃣ Run the development server

```bash
python manage.py runserver
```

The website will be available at http://127.0.0.1:8000/

## 🛠️ Admin Interface

Access the admin interface at http://127.0.0.1:8000/admin/ using your superuser credentials to:

- Add and edit speakers
- Manage the conference schedule
- View registrations

## 📱 Website Sections

- **Homepage**: http://127.0.0.1:8000/
- **Speakers**: http://127.0.0.1:8000/speakers/
- **Schedule**: http://127.0.0.1:8000/schedule/
- **Registration**: http://127.0.0.1:8000/registration/

## ⚙️ Troubleshooting

### Database issues

If you encounter database errors, try:

```bash
python manage.py migrate --run-syncdb
```

### Media files not displaying

Ensure the MEDIA_ROOT and MEDIA_URL settings are correct in settings.py and media directories have appropriate permissions.

### Static files missing

Collect static files with:

```bash
python manage.py collectstatic
```

### OpenAI API issues

If you encounter issues with the OpenAI API:

1. Check that your API key is valid and has sufficient credits
2. Ensure you have internet connectivity when running the script
3. For large PDF files, there might be token limit issues - try breaking down the files into smaller chunks if needed 