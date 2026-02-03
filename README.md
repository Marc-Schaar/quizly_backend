# ![Coderr Logo](assets/icons/logo_quizly.svg) Quizly Backend API

This is a RESTful API backend for the **Quizly** platform, built with **Django** and **Django REST Framework (DRF)**.  
Quizly transforms YouTube videos into interactive quizzes using AI-powered content analysis and automatically generates quizzes with **10 questions per video**.

The API handles video processing, quiz generation, user management, and provides all endpoints required for seamless frontend integration.

## Features
- YouTube video analysis
- AI-powered quiz generation
- Automatic creation of quizzes with 10 questions
- User registration and token-based authentication
- Quiz, question, and result management
- RESTful API for frontend consumption
- Permissions ensuring only authorized users can access or modify data
- Data validation, error handling, and serialization
- Scalable and extensible backend architecture

## Requirements
- Python 3.10+
- Django
- Django REST Framework

## Setup & Installation

Clone the repository:

```bash
git clone https://github.com/Marc-Schaar/quizly_backend.git
cd quizly_backend
```

Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate  # macOS/Linux
# .\env\Scripts\activate # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

Run the development server:
```bash
python manage.py runserver
```

## Usage
API base URL: http://127.0.0.1:8000/api/

## Authentication
Token-based authentication is used.
Obtain a token via the login endpoint and include it in the request header:

```bash
Authorization: Token <your_token>
```

## Project Highlights
- Clear separation of concerns (business logic, API, data layer)
- Backend-first design with frontend integration in mind
- Easily extendable for additional quiz formats or AI models
- Production-ready API structure following best practices

## About the Project
Quizly demonstrates practical backend development skills with Django & DRF, focusing on real-world use cases such as AI integration, data modeling, authentication, and API design.
The project was built as a portfolio project to showcase backend architecture, clean code, and scalable API development.





