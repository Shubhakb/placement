# 🎓 College Placement Management System (CPMS)

An interactive, full-stack campus recruitment and placement management platform built with Python (Flask) and Supabase (PostgreSQL).

## 🚀 Key Features

* **Student Portal & Dashboard**: Profile completion, dynamic CGPA eligibility validation, job bookmarks, and real-time application tracking.
* **Placement Drives Directory**: Multi-parameter search & filtering (keywords, location, package CTC, CGPA criteria, active status).
* **Corporate Recruiter Portal**: Job posting creation, applicant review, interview schedule management, and candidate selection.
* **Administrative Control Center**: Centralized roster management, live placement metrics, and corporate partner onboarding.
* **Modern Rich Design System**: Plus Jakarta Sans typography, vibrant interactive color themes, animated floating shapes, glassmorphism, and live status pulses.

## 🛠️ Tech Stack

* **Backend**: Python 3, Flask, Supabase Python Client
* **Database**: PostgreSQL (Supabase)
* **Frontend**: HTML5, Vanilla CSS3, Bootstrap Icons, Plus Jakarta Sans
* **Network Transport**: Resilient HTTP/1.1 transport with auto-reconnecting keepalives

## 💻 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shubhakb/placement.git
   cd placement
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask supabase python-dotenv httpx
   ```

4. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SECRET_KEY=your_secret_key
   ```

5. **Run the Application:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.
