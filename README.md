# Institution Management System

A Django-based school management system with role-based dashboards for admins, teachers, students, and parents.

## Features

### Role-Based Dashboards
- **Admin Dashboard** - Manage admins, teachers, students, and school settings
- **Teacher Dashboard** - View classes, manage student records
- **Student Dashboard** - View academic info and attendance
- **Parent Dashboard** - Track child's progress and attendance

### Other Features
- Secure login for each role
- Password reset functionality
- Academic records management
- Account management

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Deployment:** PythonAnywhere

## Project Structure

```
Project/
├── academics/          # Academic records app
├── accounts/           # User accounts & authentication
├── dps_ravi/           # Main project settings
├── fixtures/           # Database fixtures
├── templates/          # HTML templates
├── manage.py
├── requirements.txt
└── Procfile
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/arooba-shafique/Project.git
   cd Project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Live Demo

[arooba.pythonanywhere.com](https://arooba.pythonanywhere.com/)
