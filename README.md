# 🏥 First KHCC Interventional Oncology Conference Website 🧪

![Conference Logo](static/images/logo.png)

## 🌟 Overview

This is the official website for the First KHCC Interventional Oncology Conference 2025, a pioneering event gathering leading experts in the field to explore innovative approaches to cancer treatment. The conference will take place on April 18-19, 2025, at the Four Seasons Hotel in Amman.

## ✨ Features

- 🏠 **Homepage** with conference overview and highlights
- 👥 **Speakers page** showcasing distinguished presenters with photos and bios
- 📅 **Schedule page** with detailed program information
- 📝 **Registration system** for attendees with different pricing tiers
- 🤖 **GPT-4o Integration** for automatically extracting speaker information from PDFs, Word documents and other file formats

## 🛠️ Technologies Used

- Django 5.0+
- Bootstrap 5
- Python 3.10+
- OpenAI GPT-4o for document processing
- SQLite (development) / PostgreSQL (production)
- Pillow for image processing

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/khcc-conference.git
cd khcc-conference
```

2. **Set up a virtual environment**

```bash
# Using venv
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
# Add your OpenAI API key to enable GPT-4o processing of speaker files
OPENAI_API_KEY=your_api_key_here
```

5. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Process speaker data** (optional)

```bash
python process_speakers.py
```

7. **Create a superuser**

```bash
python manage.py createsuperuser
```

8. **Run the development server**

```bash
python manage.py runserver
```

9. **Visit the website at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

## 📋 Project Structure

```
khcc_conference/              # Main project folder
├── conference/               # Main app
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── forms.py              # Forms
│   ├── urls.py               # URL routing
│   └── admin.py              # Admin configuration
├── templates/                # HTML templates
│   └── conference/           # App templates
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User-uploaded content
│   └── speakers/             # Speaker photos
├── khcc_conference/          # Project settings
├── process_speakers.py       # Script to process speaker data
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## 🔧 Management Commands

- **Run the server**: `python manage.py runserver`
- **Create migrations**: `python manage.py makemigrations`
- **Apply migrations**: `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`

## 🧩 Admin Interface

Access the admin interface at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to:

- 👥 Manage speakers (add, edit, delete)
- 📅 Configure conference sessions and schedule items
- 📊 View and manage registrations

## 🔒 Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string (for production)
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- Your Name - Initial work

## 🙏 Acknowledgments

- King Hussein Cancer Center for supporting this initiative
- All the distinguished speakers participating in the conference
- Bootstrap team for the amazing UI components 