# Institution Management System

A Django-based school management system with role-based dashboards for admins, teachers, students, and parents. Includes HR/payroll management and timetable scheduling.

## Live Demo

[tech-tawny-six.vercel.app](https://tech-tawny-six.vercel.app)

## Features

### Role-Based Dashboards
- **Admin Dashboard** - Full school overview: students, teachers, parents, classes, subjects, attendance stats, HR data
- **Admin Manager Dashboard** - Manage admin managers with limited admin access
- **Teacher Dashboard** - View assigned classes/subjects, mark attendance, manage homework, create exams, upload results, view timetable
- **Student Dashboard** - View attendance, results, homework, timetable
- **Parent Dashboard** - Track children's attendance, results, homework, timetable

### Academic Management
- Classes, subjects, and teacher-subject-class assignments
- Student attendance marking (per subject per day)
- Exam creation and result upload with pass/fail calculation
- Homework management with file attachments
- Weekly timetable management

### HR and Payroll
- Employee CRUD with search and filter
- Salary configuration and bulk monthly salary generation
- Salary slip generation and CSV export for bank transfers
- Monthly attendance summary tracking

### Other Features
- Separate login portals for each role
- Password reset via email
- School-level trial expiry system
- Multi-school support

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, Django |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite (dev), PostgreSQL (prod) |
| Deployment | Vercel |

## Project Structure

```
tech/
├── academics/          # Academic records (classes, students, exams, attendance, timetable)
├── accounts/           # User authentication and role management
├── hr/                 # HR and payroll management
├── dps_ravi/           # Main project configuration
├── api/                # Vercel serverless entry point
├── templates/          # HTML templates
├── fixtures/           # Database fixtures
├── manage.py
├── requirements.txt
└── vercel.json
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/arooba-shafique/tech.git
   cd tech
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # Linux/Mac
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
