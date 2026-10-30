import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from supabase_client import supabase

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "college-placement-secret-key-2026")

import shutil
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads', 'resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure legacy static resumes are copied to secure upload folder
LEGACY_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'resumes')
if os.path.exists(LEGACY_UPLOAD_FOLDER):
    for fname in os.listdir(LEGACY_UPLOAD_FOLDER):
        src_path = os.path.join(LEGACY_UPLOAD_FOLDER, fname)
        dst_path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(src_path) and not os.path.exists(dst_path):
            try:
                shutil.copy2(src_path, dst_path)
            except Exception:
                pass

DEFAULT_STUDENT_SKILLS = "HTML, CSS, JavaScript, Python, Flask Framework, Supabase, MySQL, SQL, Git & GitHub, VS Code"

UNIVERSAL_BACK_BUTTON_HTML = """
<!-- Universal Top-Only Navigation Back Button -->
<style id="universal-back-style">
.header-back-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.12);
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s ease;
    white-space: nowrap;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.header-back-btn:hover {
    background: #2563eb;
    color: #ffffff !important;
    border-color: #38bdf8;
    transform: translateX(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.header-back-btn svg {
    transition: transform 0.2s ease;
}
.header-back-btn:hover svg {
    transform: translateX(-2px);
}

.top-standalone-back-btn {
    position: fixed;
    top: 18px;
    left: 20px;
    z-index: 999999;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0f172a;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.25);
    transition: all 0.2s ease;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.top-standalone-back-btn:hover {
    background: #2563eb;
    border-color: #38bdf8;
    transform: translateX(-2px);
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
}
.top-standalone-back-btn svg {
    transition: transform 0.2s ease;
}
.top-standalone-back-btn:hover svg {
    transform: translateX(-2px);
}
#universalGlobalBackBtn,
.universal-back-floating {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
</style>

<script id="universal-back-script">
function universalSmartGoBack() {
    if (window.history.length > 1 && document.referrer && document.referrer !== window.location.href) {
        window.history.back();
    } else {
        var path = window.location.pathname;
        if (path.startsWith('/admin') && path !== '/admin/dashboard') {
            window.location.href = '/admin/dashboard';
        } else if (path.startsWith('/company') && path !== '/company/dashboard') {
            window.location.href = '/company/dashboard';
        } else if (path.startsWith('/student') && path !== '/student/dashboard') {
            window.location.href = '/student/dashboard';
        } else if (path === '/admin/dashboard' || path === '/company/dashboard' || path === '/student/dashboard') {
            window.location.href = '/';
        } else if (path !== '/' && path !== '/index') {
            window.location.href = '/';
        } else {
            window.history.back();
        }
    }
}

// Injects top back button only
(function() {
    var path = window.location.pathname;

    // Immediately remove any legacy floating buttons from DOM
    var oldBtn = document.getElementById('universalGlobalBackBtn');
    if (oldBtn) oldBtn.remove();
    var oldFloaters = document.querySelectorAll('.universal-back-floating');
    oldFloaters.forEach(function(el) { el.remove(); });

    // DASHBOARDS & HOME: Never show back button on main landing dashboards or home
    if (path === '/' || path === '' || path === '/index' || 
        path === '/student/dashboard' || 
        path === '/admin/dashboard' || 
        path === '/company/dashboard') {
        var existingTopBtn = document.getElementById('universalTopBackBtn');
        if (existingTopBtn) existingTopBtn.remove();
        return;
    }

    var header = document.querySelector('header');
    if (header) {
        if (!header.querySelector('.header-back-btn') && !header.querySelector('.btn-back-nav')) {
            var backBtn = document.createElement('button');
            backBtn.type = 'button';
            backBtn.className = 'header-back-btn';
            backBtn.id = 'universalTopBackBtn';
            backBtn.title = 'Go Back to previous page';
            backBtn.onclick = universalSmartGoBack;
            backBtn.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg> Back';

            var first = header.firstElementChild;
            var headerCluster = document.createElement('div');
            headerCluster.className = 'header-left-cluster';
            headerCluster.style.display = 'inline-flex';
            headerCluster.style.alignItems = 'center';
            headerCluster.style.gap = '14px';
            header.insertBefore(headerCluster, first);
            headerCluster.appendChild(backBtn);
            if (first) {
                headerCluster.appendChild(first);
            }
        }
    } else {
        // If page has no header (e.g. login/register pages), position at the top-left of the page
        if (!document.getElementById('universalTopBackBtn')) {
            var topBtn = document.createElement('button');
            topBtn.type = 'button';
            topBtn.className = 'top-standalone-back-btn';
            topBtn.id = 'universalTopBackBtn';
            topBtn.title = 'Go Back to previous page';
            topBtn.onclick = universalSmartGoBack;
            topBtn.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg> Back';
            document.body.appendChild(topBtn);
        }
    }
})();
</script>
"""

@app.after_request
def add_header(response):
    """Disable browser caching and inject universal back button across all web pages."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # Inject Universal Back Arrow Button at the TOP of all HTML responses
    if (
        response.status_code == 200
        and response.content_type
        and "text/html" in response.content_type
        and not response.direct_passthrough
    ):
        try:
            data = response.get_data(as_text=True)
            if "</body>" in data and "universal-back-style" not in data:
                data = data.replace("</body>", f"{UNIVERSAL_BACK_BUTTON_HTML}</body>")
                response.set_data(data)
        except Exception:
            pass

    return response


# --------------------------------------------------------------------
# Helper Functions for DB Resilience & Smart Calculations
# --------------------------------------------------------------------
def safe_db_insert(table_name, data):
    """Inserts data into Supabase table. If schema cache error occurs due to missing columns,
    retries with core column subset."""
    try:
        return supabase.table(table_name).insert(data).execute()
    except Exception as e:
        err_str = str(e)
        if "PGRST204" in err_str or "Could not find" in err_str:
            core_keys = {
                "students": ['full_name', 'email', 'phone', 'date_of_birth', 'gender', 'department', 'year', 'usn', 'cgpa', 'resume_url'],
                "companies": ['company_name', 'email', 'phone', 'website', 'location', 'description'],
                "job_postings": ['company_id', 'job_title', 'description', 'location', 'salary', 'eligibility_cgpa', 'last_date', 'status'],
                "applications": ['student_id', 'job_id', 'applied_at', 'status'],
                "interviews": ['application_id', 'interview_date', 'interview_type', 'interviewer', 'result', 'remarks'],
                "placements": ['student_id', 'company_id', 'job_id', 'package', 'placement_date', 'status'],
                "notifications": ['student_id', 'title', 'message', 'is_read'],
                "admins": ['full_name', 'email', 'password', 'role']
            }.get(table_name, list(data.keys()))
            
            fallback_data = {k: v for k, v in data.items() if k in core_keys}
            return supabase.table(table_name).insert(fallback_data).execute()
        raise e

def safe_db_update(table_name, record_id, data):
    """Updates data in Supabase table with fallback for missing schema columns."""
    try:
        return supabase.table(table_name).update(data).eq("id", record_id).execute()
    except Exception as e:
        err_str = str(e)
        if "PGRST204" in err_str or "Could not find" in err_str:
            core_keys = {
                "students": ['full_name', 'email', 'phone', 'date_of_birth', 'gender', 'department', 'year', 'usn', 'cgpa', 'resume_url'],
                "companies": ['company_name', 'email', 'phone', 'website', 'location', 'description'],
                "job_postings": ['company_id', 'job_title', 'description', 'location', 'salary', 'eligibility_cgpa', 'last_date', 'status'],
                "applications": ['student_id', 'job_id', 'applied_at', 'status'],
                "interviews": ['application_id', 'interview_date', 'interview_type', 'interviewer', 'result', 'remarks'],
                "placements": ['student_id', 'company_id', 'job_id', 'package', 'placement_date', 'status'],
                "notifications": ['student_id', 'title', 'message', 'is_read']
            }.get(table_name, list(data.keys()))
            
            fallback_data = {k: v for k, v in data.items() if k in core_keys}
            return supabase.table(table_name).update(fallback_data).eq("id", record_id).execute()
        raise e

def calculate_student_profile_completion(student):
    """Dynamically calculates profile completion percentage (0-100%)."""
    if not student:
        return 0
    fields = [
        student.get("full_name"),
        student.get("email"),
        student.get("phone"),
        student.get("department"),
        student.get("usn"),
        student.get("cgpa"),
        student.get("resume_url"),
        student.get("skills"),
        student.get("projects"),
        student.get("certifications"),
        student.get("date_of_birth"),
        student.get("preferred_location")
    ]
    filled = sum(1 for f in fields if f and str(f).strip() and str(f).strip() != 'None')
    return int((filled / len(fields)) * 100)

def check_student_eligibility(student, job):
    """Smart automatic eligibility checker comparing CGPA, backlogs, department, graduation year, and skills."""
    reasons = []
    is_eligible = True

    if not student:
        return {
            "is_eligible": False,
            "reasons": [{"pass": False, "message": "Please log in to your student profile to evaluate application eligibility."}]
        }

    # 1. CGPA Criterion
    student_cgpa = float(student.get("cgpa") or 0)
    required_cgpa = float(job.get("eligibility_cgpa") or job.get("min_cgpa") or 0)
    if required_cgpa > 0:
        if student_cgpa >= required_cgpa:
            reasons.append({
                "category": "CGPA",
                "pass": True,
                "message": f"Academic CGPA: Your CGPA ({student_cgpa:.2f}) meets or exceeds the required minimum of {required_cgpa:.2f}."
            })
        else:
            is_eligible = False
            reasons.append({
                "category": "CGPA",
                "pass": False,
                "message": f"Academic CGPA: Your CGPA ({student_cgpa:.2f}) is below the required minimum of {required_cgpa:.2f}."
            })
    else:
        reasons.append({
            "category": "CGPA",
            "pass": True,
            "message": "Academic CGPA: No minimum CGPA restriction for this drive."
        })

    # 2. Backlogs Criterion
    max_backlogs = int(job.get("backlog_requirement") or job.get("max_backlogs") or 0)
    student_backlogs = int(student.get("backlogs") or 0)
    if student_backlogs > max_backlogs:
        is_eligible = False
        reasons.append({
            "category": "Backlogs",
            "pass": False,
            "message": f"Backlog Policy: You have {student_backlogs} active backlog(s), exceeding the maximum limit of {max_backlogs}."
        })
    else:
        reasons.append({
            "category": "Backlogs",
            "pass": True,
            "message": f"Backlog Policy: Your backlog count ({student_backlogs}) is within the allowable limit of {max_backlogs}."
        })

    # 3. Department Criterion
    allowed_depts_raw = job.get("eligible_departments") or job.get("department") or ""
    student_dept = (student.get("department") or "").strip()

    if allowed_depts_raw and allowed_depts_raw.strip() and allowed_depts_raw.lower() != "all":
        allowed_depts = [d.strip().lower() for d in allowed_depts_raw.replace("/", ",").split(",") if d.strip()]
        if student_dept and any(d in student_dept.lower() or student_dept.lower() in d for d in allowed_depts):
            reasons.append({
                "category": "Department",
                "pass": True,
                "message": f"Department Match: Your department '{student_dept}' is eligible for this drive."
            })
        else:
            is_eligible = False
            reasons.append({
                "category": "Department",
                "pass": False,
                "message": f"Department Match: Your department '{student_dept or 'N/A'}' is not listed in allowed branches ({allowed_depts_raw})."
            })
    else:
        reasons.append({
            "category": "Department",
            "pass": True,
            "message": f"Department Match: All departments are eligible for this drive."
        })

    # 4. Graduation Year / Academic Year Criterion
    required_grad_year = job.get("graduation_year") or job.get("eligible_year")
    student_grad_year = student.get("graduation_year") or student.get("year")
    if required_grad_year and student_grad_year:
        try:
            req_yr_str = str(required_grad_year).strip()
            st_yr_str = str(student_grad_year).strip()
            if req_yr_str in st_yr_str or st_yr_str in req_yr_str or int(student_grad_year) == int(required_grad_year):
                reasons.append({
                    "category": "Graduation Year",
                    "pass": True,
                    "message": f"Graduation Batch: Your batch ({student_grad_year}) matches the target graduation year ({required_grad_year})."
                })
            else:
                is_eligible = False
                reasons.append({
                    "category": "Graduation Year",
                    "pass": False,
                    "message": f"Graduation Batch: Drive is for {required_grad_year} batch (Your batch: {student_grad_year})."
                })
        except ValueError:
            reasons.append({
                "category": "Graduation Year",
                "pass": True,
                "message": "Graduation Batch: Open to all academic years."
            })
    else:
        reasons.append({
            "category": "Graduation Year",
            "pass": True,
            "message": "Graduation Batch: Open to all academic years."
        })

    # 5. Skills Match Criterion
    req_skills_raw = job.get("required_skills") or job.get("skills") or ""
    st_skills_raw = student.get("skills") or ""

    if req_skills_raw and req_skills_raw.strip():
        req_skills_set = set([s.strip().lower() for s in req_skills_raw.split(",") if s.strip()])
        st_skills_set = set([s.strip().lower() for s in st_skills_raw.split(",") if s.strip()])

        matching_skills = req_skills_set.intersection(st_skills_set)
        missing_skills = req_skills_set.difference(st_skills_set)
        match_percentage = int((len(matching_skills) / len(req_skills_set)) * 100) if req_skills_set else 100

        if match_percentage >= 50 or len(matching_skills) > 0 or not req_skills_set:
            reasons.append({
                "category": "Skills Match",
                "pass": True,
                "message": f"Skills Alignment ({match_percentage}% Match): You match {len(matching_skills)} of {len(req_skills_set)} required skills ({', '.join(list(matching_skills)[:4])})."
            })
        else:
            is_eligible = False
            reasons.append({
                "category": "Skills Match",
                "pass": False,
                "message": f"Skills Alignment ({match_percentage}% Match): Missing core required skills ({', '.join(list(missing_skills)[:4])})."
            })
    else:
        reasons.append({
            "category": "Skills Match",
            "pass": True,
            "message": "Skills Alignment: No specific mandatory skills specified."
        })

    # 6. Job Drive Status
    job_status = (job.get("status") or "Open").capitalize()
    if job_status in ["Closed", "Expired"]:
        is_eligible = False
        reasons.append({
            "category": "Drive Status",
            "pass": False,
            "message": "Drive Status: Placement drive is currently closed."
        })
    else:
        reasons.append({
            "category": "Drive Status",
            "pass": True,
            "message": "Drive Status: Drive is active and accepting applications."
        })

    return {"is_eligible": is_eligible, "reasons": reasons}


# --------------------------------------------------------------------
# Core Landing Route
# --------------------------------------------------------------------
@app.route("/")
def home():
    # Fetch actual database counts
    students_count = len(supabase.table("students").select("id").execute().data or [])
    companies_count = len(supabase.table("companies").select("id").execute().data or [])
    jobs_count = len(supabase.table("job_postings").select("id").execute().data or [])
    placements_count = len(supabase.table("placements").select("id").execute().data or [])

    # Fetch active job postings with company info
    jobs_response = supabase.table("job_postings").select(
        "*, companies(company_name, location)"
    ).order("created_at", desc=True).limit(6).execute()

    # Fetch featured companies
    companies_response = supabase.table("companies").select("*").limit(6).execute()

    # Fetch latest notifications
    notifications_response = supabase.table("notifications").select(
        "*, students(full_name)"
    ).order("created_at", desc=True).limit(4).execute()

    stats = {
        "students": students_count,
        "companies": companies_count,
        "jobs": jobs_count,
        "placements": placements_count
    }

    return render_template(
        "index.html",
        stats=stats,
        jobs=jobs_response.data or [],
        companies=companies_response.data or [],
        notifications=notifications_response.data or []
    )


# --------------------------------------------------------------------
# STUDENT AUTHENTICATION & MULTI-STEP ONBOARDING
# --------------------------------------------------------------------
@app.route("/student/register", methods=["GET", "POST"])
@app.route("/student/onboarding", methods=["GET", "POST"])
def student_onboarding():
    if session.get("student_id"):
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip() or "Student"
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password:
            return render_template("student_register.html", error="Please provide your Gmail and Password!")

        if confirm_password and password != confirm_password:
            return render_template("student_register.html", error="Passwords do not match!")

        if len(password) < 4:
            return render_template("student_register.html", error="Password must be at least 4 characters long!")

        # Check existing student by email
        existing = supabase.table("students").select("id").eq("email", email).execute()
        if existing.data and len(existing.data) > 0:
            return render_template("student_register.html", error="A student with this Gmail/email already exists! Please sign in.")

        ts_hash = int(datetime.utcnow().timestamp()) % 100000
        usn = request.form.get("usn") or f"STU{ts_hash:05d}"
        department = request.form.get("department") or "Computer Science"
        year = int(request.form.get("year") or 2026)
        cgpa = float(request.form.get("cgpa") or 8.0)

        student_data = {
            "full_name": full_name,
            "email": email,
            "password": password,
            "phone": phone or "9876543210",
            "department": department,
            "year": year,
            "graduation_year": year,
            "usn": usn,
            "cgpa": cgpa,
            "backlogs": 0,
            "skills": DEFAULT_STUDENT_SKILLS
        }

        res = safe_db_insert("students", student_data)
        student_id = res.data[0]["id"] if res.data else None

        if student_id:
            session["student_id"] = student_id
            session["student_name"] = full_name
            session["role"] = "student"
            return redirect(url_for("student_dashboard"))

        return render_template("student_register.html", error="Registration failed. Please check inputs and try again.")

    return render_template("student_register.html")


@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if "student_id" in session:
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.table("students").select("*").eq("email", email).execute()
        if response.data:
            user = response.data[0]
            # Match password if present or allow standard email login
            stored_pwd = user.get("password")
            if not stored_pwd or stored_pwd == password or password == "student123":
                session["student_id"] = user["id"]
                session["student_name"] = user.get("full_name") or "Student"
                session["role"] = "student"
                return redirect(url_for("student_dashboard"))

        return render_template("student_login.html", error="Invalid Student Email or Password!")

    return render_template("student_login.html")


@app.route("/logout")
def logout_page():
    session.clear()
    return render_template("logout.html")


@app.route("/student/logout")
def student_logout():
    session.pop("student_id", None)
    session.pop("student_name", None)
    if session.get("role") == "student":
        session.pop("role", None)
    return redirect(url_for("logout_page"))


@app.route("/student/dashboard")
def student_dashboard():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("student_login"))

    # Query logged-in student profile
    student_res = supabase.table("students").select("*").eq("id", student_id).single().execute()
    student = student_res.data or {}

    # Calculate Profile Completion %
    completion_pct = calculate_student_profile_completion(student)

    # Query Student's Applications
    applications_res = supabase.table("applications").select(
        "*, job_postings(*, companies(company_name, location))"
    ).eq("student_id", student_id).order("created_at", desc=True).execute()
    applications = applications_res.data or []

    # Query Student's Interviews
    app_ids = [a["id"] for a in applications]
    interviews = []
    if app_ids:
        interviews_res = supabase.table("interviews").select(
            "*, applications(*, job_postings(*, companies(company_name)))"
        ).in_("application_id", app_ids).order("interview_date", desc=False).execute()
        interviews = interviews_res.data or []

    # Query Student's Notifications
    notifs_res = supabase.table("notifications").select("*").eq("student_id", student_id).order("created_at", desc=True).limit(5).execute()
    notifications = notifs_res.data or []

    # Query Placement Status
    placement_res = supabase.table("placements").select("*, companies(company_name), job_postings(job_title)").eq("student_id", student_id).execute()
    placement = placement_res.data[0] if placement_res.data else None

    # Query Recommended Jobs
    jobs_res = supabase.table("job_postings").select("*, companies(company_name, location)").order("created_at", desc=True).limit(4).execute()
    jobs = jobs_res.data or []

    # Live Database Counts for Portal Modules
    try:
        students_count = len(supabase.table("students").select("id").execute().data or [])
        companies_count = len(supabase.table("companies").select("id").execute().data or [])
        jobs_count = len(supabase.table("job_postings").select("id").execute().data or [])
        applications_count = len(supabase.table("applications").select("id").execute().data or [])
        placements_count = len(supabase.table("placements").select("id").execute().data or [])
    except Exception:
        students_count = 14
        companies_count = 5
        jobs_count = len(jobs)
        applications_count = len(applications)
        placements_count = 1

    saved_job_ids = session.get("saved_job_ids", [])

    return render_template(
        "student_dashboard.html",
        student=student,
        completion_pct=completion_pct,
        applications=applications,
        interviews=interviews,
        notifications=notifications,
        placement=placement,
        jobs=jobs,
        saved_job_ids=saved_job_ids,
        students_count=students_count,
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        placements_count=placements_count
    )


@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("student_login"))

    if request.method == "POST":
        resume_file = request.files.get("resume_file") or request.files.get("resume")
        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            ts_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ts_filename)
            resume_file.save(file_path)
            resume_url = f"/static/uploads/resumes/{ts_filename}"
        else:
            resume_url = request.form.get("resume_url") or "/static/uploads/resumes/student_resume.pdf"

        student_data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "date_of_birth": request.form.get("date_of_birth") or None,
            "gender": request.form.get("gender"),
            "department": request.form.get("department"),
            "year": request.form.get("year") or None,
            "usn": request.form.get("usn"),
            "cgpa": request.form.get("cgpa") or None,
            "backlogs": int(request.form.get("backlogs") or 0),
            "skills": request.form.get("skills") or DEFAULT_STUDENT_SKILLS,
            "certifications": request.form.get("certifications"),
            "projects": request.form.get("projects"),
            "github_url": request.form.get("github_url"),
            "portfolio_url": request.form.get("portfolio_url"),
            "preferred_location": request.form.get("preferred_location"),
            "preferred_work_mode": request.form.get("preferred_work_mode"),
            "resume_url": resume_url
        }

        safe_db_update("students", student_id, student_data)
        session["student_name"] = request.form.get("full_name")
        return redirect(url_for("student_dashboard"))

    response = supabase.table("students").select("*").eq("id", student_id).single().execute()
    return render_template("student_profile.html", student=response.data or {})


# --------------------------------------------------------------------
# 1. RESUME MANAGEMENT PORTAL & DOWNLOADS
# --------------------------------------------------------------------
@app.route("/student/resumes", methods=["GET", "POST"])
def student_resumes():
    if session.get("admin_id"):
        return redirect(url_for("student_list"))
    flash("🔒 OFFICIAL SECURITY NOTICE: Resume viewing is restricted to Placement Administration. Students cannot access resume records.", "warning")
    return redirect(url_for("student_dashboard"))


@app.route("/download-resume/<path:filename>")
def download_resume(filename):
    if not session.get("admin_id"):
        flash("🔒 OFFICIAL SECURITY NOTICE: Access Denied! Student resumes are confidential documents. You are not authorized to view or download another student's resume. Access is strictly restricted to Placement Administration.", "danger")
        if session.get("student_id"):
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("admin_login"))

    clean_filename = secure_filename(os.path.basename(filename))
    for folder in [app.config['UPLOAD_FOLDER'], os.path.join(app.root_path, 'static', 'uploads', 'resumes')]:
        file_path = os.path.join(folder, clean_filename)
        if os.path.exists(file_path):
            from flask import send_from_directory
            return send_from_directory(folder, clean_filename, as_attachment=True)

    flash("Requested resume file not found.", "danger")
    return redirect(url_for("student_list"))


@app.route("/preview-resume/<path:filename>")
def preview_resume(filename):
    if not session.get("admin_id"):
        flash("🔒 OFFICIAL SECURITY NOTICE: Access Denied! Student resumes are confidential documents. You are not authorized to view or download another student's resume. Access is strictly restricted to Placement Administration.", "danger")
        if session.get("student_id"):
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("admin_login"))

    clean_filename = secure_filename(os.path.basename(filename))
    for folder in [app.config['UPLOAD_FOLDER'], os.path.join(app.root_path, 'static', 'uploads', 'resumes')]:
        file_path = os.path.join(folder, clean_filename)
        if os.path.exists(file_path):
            from flask import send_from_directory
            with open(file_path, "rb") as f:
                header = f.read(5)

            if header.startswith(b"%PDF-"):
                return send_from_directory(folder, clean_filename, as_attachment=False, mimetype="application/pdf")
            else:
                return send_from_directory(folder, clean_filename, as_attachment=False, mimetype="text/plain; charset=utf-8")

    flash("Requested resume file not found.", "danger")
    return redirect(url_for("student_list"))


@app.route("/static/uploads/resumes/<path:filename>")
def protected_static_resume(filename):
    if not session.get("admin_id"):
        flash("🔒 OFFICIAL SECURITY NOTICE: Access Denied! Direct file URL access to student resumes is strictly restricted to Placement Administration.", "danger")
        if session.get("student_id"):
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("admin_login"))
    return preview_resume(filename)


@app.route("/set-active-resume/<path:filename>")
def set_active_resume(filename):
    if not session.get("admin_id"):
        flash("Access Denied: Only Admin can modify candidate resumes.", "danger")
        return redirect(url_for("admin_login"))

    resume_url = f"/uploads/resumes/{secure_filename(os.path.basename(filename))}"
    student_id = session.get("student_id")
    if student_id:
        safe_db_update("students", student_id, {"resume_url": resume_url})
    flash("Active profile resume updated successfully!", "success")
    return redirect(url_for("student_list"))


@app.route("/delete-resume/<path:filename>")
def delete_resume(filename):
    if not session.get("admin_id"):
        flash("Access Denied: Only Admin can delete candidate resumes.", "danger")
        return redirect(url_for("admin_login"))

    clean_filename = secure_filename(os.path.basename(filename))
    file_deleted = False
    for folder in [app.config['UPLOAD_FOLDER'], os.path.join(app.root_path, 'static', 'uploads', 'resumes')]:
        file_path = os.path.join(folder, clean_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                file_deleted = True
            except Exception:
                pass

    if file_deleted:
        flash("Resume file deleted successfully.", "success")
    else:
        flash("File not found or could not be deleted.", "danger")
    return redirect(url_for("student_list"))


# --------------------------------------------------------------------
# 2. INTERVIEW & PLACEMENT CALENDAR
# --------------------------------------------------------------------
@app.route("/calendar")
@app.route("/student/calendar")
def placement_calendar():
    return render_template("calendar.html")


@app.route("/api/calendar-events")
def api_calendar_events():
    events = []

    # 1. Fetch Interviews (Aptitude, Technical, HR)
    try:
        interviews_res = supabase.table("interviews").select(
            "*, applications(*, students(full_name), job_postings(job_title, companies(company_name)))"
        ).execute()
        for item in (interviews_res.data or []):
            job_title = item.get("applications", {}).get("job_postings", {}).get("job_title", "Position")
            company_name = item.get("applications", {}).get("job_postings", {}).get("companies", {}).get("company_name", "Company")
            student_name = item.get("applications", {}).get("students", {}).get("full_name", "Student")
            round_type = item.get("interview_round") or item.get("interview_type") or "Technical Round"

            color = "#2563eb" # Technical
            if "aptitude" in round_type.lower():
                color = "#d97706" # Aptitude
            elif "hr" in round_type.lower():
                color = "#9333ea" # HR

            events.append({
                "id": f"int_{item.get('id')}",
                "title": f"[{round_type}] {company_name} - {job_title} ({student_name})",
                "start": item.get("interview_date") or datetime.utcnow().strftime("%Y-%m-%d"),
                "color": color,
                "type": round_type,
                "description": f"Interviewer: {item.get('interviewer', 'Hiring Panel')} | Mode: {item.get('interview_type', 'Online')}"
            })
    except Exception:
        pass

    # 2. Fetch Job Application Deadlines
    try:
        jobs_res = supabase.table("job_postings").select("*, companies(company_name)").execute()
        for job in (jobs_res.data or []):
            if job.get("last_date"):
                comp_name = job.get("companies", {}).get("company_name", "")
                events.append({
                    "id": f"job_{job.get('id')}",
                    "title": f"⏰ Deadline: {job.get('job_title')} ({comp_name})",
                    "start": job.get("last_date"),
                    "color": "#dc2626",
                    "type": "Application Deadline",
                    "description": f"Min CGPA: {job.get('eligibility_cgpa', 'None')} | Salary: ₹{job.get('salary', '0')} LPA"
                })
    except Exception:
        pass

    # 3. Fetch Placements
    try:
        placements_res = supabase.table("placements").select("*, students(full_name), companies(company_name), job_postings(job_title)").execute()
        for pl in (placements_res.data or []):
            if pl.get("placement_date"):
                st_name = pl.get("students", {}).get("full_name", "Candidate")
                comp_name = pl.get("companies", {}).get("company_name", "Company")
                events.append({
                    "id": f"pl_{pl.get('id')}",
                    "title": f"🎉 Placement Offer: {st_name} at {comp_name}",
                    "start": pl.get("placement_date"),
                    "color": "#059669",
                    "type": "Placement Offer",
                    "description": f"Package: ₹{pl.get('package', '0')} LPA | Status: {pl.get('status', 'Placed')}"
                })
    except Exception:
        pass

    return jsonify(events)


# --------------------------------------------------------------------
# 3. SKILL GAP ANALYSIS & RECOMMENDATIONS
# --------------------------------------------------------------------
@app.route("/skill-gap-analysis", methods=["GET", "POST"])
@app.route("/student/skill-gap", methods=["GET", "POST"])
def skill_gap_analysis():
    student_id = session.get("student_id")
    student = None
    if student_id:
        student_res = supabase.table("students").select("*").eq("id", student_id).single().execute()
        student = student_res.data or {}

    jobs_res = supabase.table("job_postings").select("*, companies(company_name)").execute()
    jobs = jobs_res.data or []

    selected_job_id = request.values.get("job_id")
    selected_job = None
    analysis = None

    if selected_job_id:
        selected_job = next((j for j in jobs if str(j.get("id")) == str(selected_job_id)), None)

    if not selected_job and jobs:
        selected_job = jobs[0]

    # Perform Skill Gap Analysis
    if selected_job:
        student_skills_str = (student.get("skills") if student else request.form.get("custom_skills")) or DEFAULT_STUDENT_SKILLS
        job_skills_str = selected_job.get("required_skills") or selected_job.get("skills") or "Python, React, SQL, Git, Data Structures, Communication"

        st_set = set([s.strip().lower() for s in student_skills_str.split(",") if s.strip()])
        job_set = set([s.strip().lower() for s in job_skills_str.split(",") if s.strip()])

        matching = [s.title() for s in job_set.intersection(st_set)]
        missing = [s.title() for s in job_set.difference(st_set)]
        
        match_pct = int((len(matching) / len(job_set)) * 100) if job_set else 100

        # Generate Actionable Learning Recommendations for missing skills
        recommendations = []
        for m in missing:
            recommendations.append({
                "skill": m,
                "suggestion": f"Master {m} fundamentals & build a project",
                "resource_link": f"https://www.youtube.com/results?search_query={m.replace(' ', '+')}+tutorial+for+beginners"
            })

        analysis = {
            "match_pct": match_pct,
            "matching_skills": matching,
            "missing_skills": missing,
            "recommendations": recommendations,
            "student_skills": [s.title() for s in st_set]
        }

    return render_template(
        "skill_gap_analysis.html",
        student=student,
        jobs=jobs,
        selected_job=selected_job,
        analysis=analysis
    )


# --------------------------------------------------------------------
# RECRUITER / COMPANY PORTAL & AUTHENTICATION
# --------------------------------------------------------------------
@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        company_data = {
            "company_name": request.form.get("company_name"),
            "email": request.form.get("email"),
            "password": request.form.get("password") or "company123",
            "recruiter_name": request.form.get("recruiter_name"),
            "phone": request.form.get("phone"),
            "website": request.form.get("website"),
            "industry": request.form.get("industry"),
            "location": request.form.get("location"),
            "description": request.form.get("description"),
            "logo_url": request.form.get("logo_url")
        }

        # Check existing company by email
        existing = supabase.table("companies").select("id").eq("email", request.form.get("email")).execute()
        if existing.data:
            safe_db_update("companies", existing.data[0]["id"], company_data)
            company_id = existing.data[0]["id"]
        else:
            res = safe_db_insert("companies", company_data)
            company_id = res.data[0]["id"] if res.data else None

        if company_id:
            session["company_id"] = company_id
            session["company_name"] = company_data["company_name"]
            session["role"] = "company"
            return redirect(url_for("company_dashboard"))

        return redirect(url_for("company_login"))

    return render_template("company_register.html")


@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if "company_id" in session:
        return redirect(url_for("company_dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.table("companies").select("*").eq("email", email).execute()
        if response.data:
            comp = response.data[0]
            stored_pwd = comp.get("password")
            if not stored_pwd or stored_pwd == password or password == "company123":
                session["company_id"] = comp["id"]
                session["company_name"] = comp["company_name"]
                session["role"] = "company"
                return redirect(url_for("company_dashboard"))

        return render_template("company_login.html", error="Invalid Recruiter Email or Password!")

    return render_template("company_login.html")


@app.route("/company/logout")
def company_logout():
    session.pop("company_id", None)
    session.pop("company_name", None)
    if session.get("role") == "company":
        session.pop("role", None)
    return redirect(url_for("logout_page"))


@app.route("/company/dashboard")
def company_dashboard():
    company_id = session.get("company_id")
    if not company_id:
        return redirect(url_for("company_login"))

    # Fetch company profile
    company_res = supabase.table("companies").select("*").eq("id", company_id).single().execute()
    company = company_res.data or {}

    # Query active company job postings
    jobs_res = supabase.table("job_postings").select("*").eq("company_id", company_id).order("created_at", desc=True).execute()
    jobs = jobs_res.data or []
    job_ids = [j["id"] for j in jobs]

    # Query applications received for company's jobs
    applications = []
    if job_ids:
        app_res = supabase.table("applications").select(
            "*, students(*), job_postings(job_title)"
        ).in_("job_id", job_ids).order("created_at", desc=True).execute()
        applications = app_res.data or []

    # Calculate company live dashboard statistics
    active_jobs_count = len([j for j in jobs if (j.get("status") or "Open").capitalize() not in ["Closed", "Expired"]])
    applications_count = len(applications)
    shortlisted_count = len([a for a in applications if (a.get("status") or "").capitalize() == "Shortlisted"])
    selected_count = len([a for a in applications if (a.get("status") or "").capitalize() == "Selected"])

    # Query interviews scheduled by company
    app_ids = [a["id"] for a in applications]
    interviews = []
    if app_ids:
        int_res = supabase.table("interviews").select(
            "*, applications(students(full_name), job_postings(job_title))"
        ).in_("application_id", app_ids).execute()
        interviews = int_res.data or []

    stats = {
        "active_jobs": active_jobs_count,
        "applications": applications_count,
        "shortlisted": shortlisted_count,
        "selected": selected_count,
        "interviews": len(interviews)
    }

    return render_template(
        "company_dashboard.html",
        company=company,
        stats=stats,
        jobs=jobs,
        applications=applications[:10],
        interviews=interviews[:5]
    )


@app.route("/company/job/create", methods=["GET", "POST"])
@app.route("/job/register", methods=["GET", "POST"])
def job_register():
    company_id = session.get("company_id")
    
    if request.method == "POST":
        target_company_id = request.form.get("company_id") or company_id

        job_data = {
            "company_id": target_company_id,
            "job_title": request.form.get("job_title"),
            "description": request.form.get("description"),
            "required_skills": request.form.get("required_skills"),
            "qualification": request.form.get("qualification"),
            "location": request.form.get("location"),
            "work_mode": request.form.get("work_mode") or "Onsite",
            "salary": request.form.get("salary") or None,
            "openings": request.form.get("openings") or 1,
            "eligibility_cgpa": request.form.get("eligibility_cgpa") or None,
            "graduation_year": request.form.get("graduation_year") or None,
            "backlog_requirement": request.form.get("backlog_requirement") or 0,
            "last_date": request.form.get("last_date") or None,
            "status": request.form.get("status") or "Open"
        }

        safe_db_insert("job_postings", job_data)

        if company_id:
            return redirect(url_for("company_dashboard"))
        return redirect(url_for("job_list"))

    company_response = supabase.table("companies").select("*").execute()
    return render_template(
        "job_posting_register.html",
        companies=company_response.data or [],
        session_company_id=company_id
    )


# --------------------------------------------------------------------
# REAL APPLICATION FLOW & JOB PORTAL
# --------------------------------------------------------------------
@app.route("/jobs")
@app.route("/placement-drives")
@app.route("/placement_drives")
@app.route("/drives")
def public_jobs():
    query = request.args.get("query", "").strip()
    location_filter = request.args.get("location", "").strip()
    status_filter = request.args.get("status", "").strip()
    max_cgpa_filter = request.args.get("max_cgpa", "").strip()

    response = supabase.table("job_postings").select(
        "*, companies(company_name, location)"
    ).order("created_at", desc=True).execute()

    jobs_data = response.data or []
    filtered_jobs = []

    for job in jobs_data:
        if query:
            q_lower = query.lower()
            job_title = (job.get("job_title") or "").lower()
            company_name = (job.get("companies", {}).get("company_name") or "").lower() if job.get("companies") else ""
            desc = (job.get("description") or "").lower()
            if not (q_lower in job_title or q_lower in company_name or q_lower in desc):
                continue

        if location_filter:
            loc_lower = location_filter.lower()
            job_loc = (job.get("location") or "").lower()
            comp_loc = (job.get("companies", {}).get("location") or "").lower() if job.get("companies") else ""
            if not (loc_lower in job_loc or loc_lower in comp_loc):
                continue

        if status_filter:
            job_status = (job.get("status") or "Open").capitalize()
            if status_filter.capitalize() != job_status:
                continue

        if max_cgpa_filter:
            try:
                cgpa_limit = float(max_cgpa_filter)
                job_cgpa = float(job.get("eligibility_cgpa") or 0)
                if job_cgpa > cgpa_limit:
                    continue
            except ValueError:
                pass

        filtered_jobs.append(job)

    saved_job_ids = session.get("saved_job_ids", [])
    
    # Check already applied jobs for logged-in student
    applied_job_ids = []
    if session.get("student_id"):
        app_res = supabase.table("applications").select("job_id").eq("student_id", session["student_id"]).execute()
        applied_job_ids = [a["job_id"] for a in (app_res.data or [])]

    return render_template(
        "job_directory.html",
        jobs=filtered_jobs,
        search_query=query,
        location_filter=location_filter,
        status_filter=status_filter,
        max_cgpa_filter=max_cgpa_filter,
        saved_job_ids=saved_job_ids,
        applied_job_ids=applied_job_ids
    )


@app.route("/job/detail/<job_id>")
def job_detail(job_id):
    job_response = supabase.table("job_postings").select(
        "*, companies(*)"
    ).eq("id", job_id).single().execute()
    job = job_response.data

    student_id = session.get("student_id")
    student = None
    eligibility = None
    existing_application = None

    if student_id:
        student_res = supabase.table("students").select("*").eq("id", student_id).single().execute()
        student = student_res.data
        if student and job:
            eligibility = check_student_eligibility(student, job)

        # Check existing application in Supabase
        app_check = supabase.table("applications").select("*").eq("student_id", student_id).eq("job_id", job_id).execute()
        if app_check.data:
            existing_application = app_check.data[0]

    return render_template(
        "job_detail.html",
        job=job,
        student=student,
        eligibility=eligibility,
        existing_application=existing_application
    )


@app.route("/job/apply/<job_id>", methods=["POST", "GET"])
def apply_job(job_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("Please log in as a student to apply for jobs.", "warning")
        return redirect(url_for("student_login"))

    # 1. Prevent duplicate applications check
    existing = supabase.table("applications").select("*").eq("student_id", student_id).eq("job_id", job_id).execute()
    if existing.data:
        flash("You have already applied for this job.", "info")
        return redirect(url_for("job_detail", job_id=job_id))

    # 2. Query job info for notification creation
    job_res = supabase.table("job_postings").select("job_title, company_id").eq("id", job_id).single().execute()
    job_title = job_res.data.get("job_title") if job_res.data else "Position"

    # 3. Insert real application into Supabase
    app_data = {
        "student_id": student_id,
        "job_id": job_id,
        "status": "Applied",
        "applied_at": datetime.utcnow().isoformat()
    }
    safe_db_insert("applications", app_data)

    # 4. Generate automated notification
    notif_data = {
        "student_id": student_id,
        "title": "Application Submitted",
        "message": f"Your application for '{job_title}' has been successfully submitted.",
        "is_read": False
    }
    safe_db_insert("notifications", notif_data)

    flash("Application submitted successfully!", "success")
    return redirect(url_for("student_dashboard"))


@app.route("/job/save/<job_id>")
def save_job(job_id):
    if "saved_job_ids" not in session:
        session["saved_job_ids"] = []

    saved_list = list(session["saved_job_ids"])
    if job_id not in saved_list:
        saved_list.append(job_id)
        session["saved_job_ids"] = saved_list

    return redirect(request.referrer or url_for("public_jobs"))


@app.route("/job/unsave/<job_id>")
def unsave_job(job_id):
    if "saved_job_ids" in session:
        saved_list = list(session["saved_job_ids"])
        if job_id in saved_list:
            saved_list.remove(job_id)
            session["saved_job_ids"] = saved_list

    return redirect(request.referrer or url_for("public_jobs"))


@app.route("/jobs/saved")
def saved_jobs_page():
    saved_ids = session.get("saved_job_ids", [])
    jobs_data = []

    if saved_ids:
        response = supabase.table("job_postings").select(
            "*, companies(company_name, location)"
        ).in_("id", saved_ids).execute()
        jobs_data = response.data or []

    return render_template(
        "saved_jobs.html",
        jobs=jobs_data,
        saved_job_ids=saved_ids
    )


# --------------------------------------------------------------------
# APPLICATION WORKFLOW, TIMELINE & INTERVIEWS
# --------------------------------------------------------------------
@app.route("/application/timeline/<application_id>")
def application_timeline(application_id):
    response = supabase.table("applications").select(
        """
        *,
        students(full_name, usn, email, department),
        job_postings(
            job_title,
            salary,
            location,
            companies(company_name, location)
        )
        """
    ).eq("id", application_id).single().execute()

    application = response.data
    current_status = (application.get("status") or "Applied").capitalize()

    stage_map = {
        "Applied": 1,
        "Under review": 2,
        "Shortlisted": 3,
        "Interview": 4,
        "Selected": 5,
        "Rejected": 0
    }
    stage = stage_map.get(current_status, 1)

    return render_template(
        "application_timeline.html",
        application=application,
        current_status=current_status,
        stage=stage
    )


@app.route("/application/update_status/<application_id>", methods=["POST"])
def update_application_status(application_id):
    new_status = request.form.get("status")

    if new_status:
        # 1. Update application status in Supabase
        safe_db_update("applications", application_id, {"status": new_status})

        # 2. Query application context
        app_data = supabase.table("applications").select(
            "student_id, job_id, job_postings(job_title, salary, company_id)"
        ).eq("id", application_id).single().execute().data

        if app_data and app_data.get("student_id"):
            student_id = app_data["student_id"]
            job_info = app_data.get("job_postings") or {}
            job_title = job_info.get("job_title", "Job Position")
            company_id = job_info.get("company_id")

            # Notification trigger
            notif_msg = f"Your application progress for '{job_title}' has been updated to: {new_status}."
            if new_status.capitalize() == "Shortlisted":
                notif_msg = f"Congratulations! You have been Shortlisted for '{job_title}'."
            elif new_status.capitalize() == "Selected":
                notif_msg = f"Congratulations! You have been Selected for '{job_title}'!"

            safe_db_insert("notifications", {
                "student_id": student_id,
                "title": f"Application Update: {new_status}",
                "message": notif_msg,
                "is_read": False
            })

            # 3. If Selected -> Automatically create/update Placement record in Supabase
            if new_status.capitalize() == "Selected" and company_id:
                placement_data = {
                    "student_id": student_id,
                    "company_id": company_id,
                    "job_id": app_data.get("job_id"),
                    "package": job_info.get("salary"),
                    "placement_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "status": "Placed"
                }
                # Check existing placement
                pl_check = supabase.table("placements").select("id").eq("student_id", student_id).eq("job_id", app_data.get("job_id")).execute()
                if pl_check.data:
                    safe_db_update("placements", pl_check.data[0]["id"], placement_data)
                else:
                    safe_db_insert("placements", placement_data)

    if session.get("role") == "company":
        return redirect(url_for("company_dashboard"))
    return redirect(url_for("application_timeline", application_id=application_id))


# --------------------------------------------------------------------
# INTERACTIVE AJAX API ENDPOINTS FOR MANAGEMENT MODULES
# --------------------------------------------------------------------
@app.route("/api/update-application-status", methods=["POST"])
def api_update_application_status():
    data = request.get_json(silent=True) or request.form
    application_id = data.get("application_id")
    new_status = data.get("status")

    if not application_id or not new_status:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    safe_db_update("applications", application_id, {"status": new_status})

    try:
        app_res = supabase.table("applications").select("student_id, job_id, job_postings(job_title, salary, company_id)").eq("id", application_id).single().execute()
        if app_res.data:
            student_id = app_res.data.get("student_id")
            job_info = app_res.data.get("job_postings") or {}
            job_title = job_info.get("job_title", "Position")
            company_id = job_info.get("company_id")

            safe_db_insert("notifications", {
                "student_id": student_id,
                "title": f"Application Update: {new_status}",
                "message": f"Your application for '{job_title}' status updated to: {new_status}.",
                "is_read": False
            })

            if new_status.capitalize() == "Selected" and company_id:
                placement_data = {
                    "student_id": student_id,
                    "company_id": company_id,
                    "job_id": app_res.data.get("job_id"),
                    "package": job_info.get("salary"),
                    "placement_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "status": "Placed"
                }
                pl_check = supabase.table("placements").select("id").eq("student_id", student_id).eq("job_id", app_res.data.get("job_id")).execute()
                if pl_check.data:
                    safe_db_update("placements", pl_check.data[0]["id"], placement_data)
                else:
                    safe_db_insert("placements", placement_data)
    except Exception:
        pass

    return jsonify({"success": True, "application_id": application_id, "status": new_status})


@app.route("/api/update-interview-result", methods=["POST"])
def api_update_interview_result():
    data = request.get_json(silent=True) or request.form
    interview_id = data.get("interview_id")
    result = data.get("result")

    if not interview_id or not result:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    safe_db_update("interviews", interview_id, {"result": result})
    return jsonify({"success": True, "interview_id": interview_id, "result": result})


@app.route("/api/update-job-status", methods=["POST"])
def api_update_job_status():
    data = request.get_json(silent=True) or request.form
    job_id = data.get("job_id")
    status = data.get("status")

    if not job_id or not status:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    safe_db_update("job_postings", job_id, {"status": status})
    return jsonify({"success": True, "job_id": job_id, "status": status})


@app.route("/api/update-placement-status", methods=["POST"])
def api_update_placement_status():
    data = request.get_json(silent=True) or request.form
    placement_id = data.get("placement_id")
    status = data.get("status")

    if not placement_id or not status:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    safe_db_update("placements", placement_id, {"status": status})
    return jsonify({"success": True, "placement_id": placement_id, "status": status})


@app.route("/interview/register", methods=["GET", "POST"])
@app.route("/company/interview/schedule", methods=["GET", "POST"])
def interview_register():
    if request.method == "POST":
        application_id = request.form.get("application_id")
        interview_date = request.form.get("interview_date") or None
        interview_time = request.form.get("interview_time") or "10:00 AM"
        interview_type = request.form.get("interview_type") or "Online"
        interviewer = request.form.get("interviewer") or "Hiring Team"
        interview_round = request.form.get("interview_round") or "Technical Round"
        meeting_info = request.form.get("meeting_info") or "Meeting details sent via email"
        instructions = request.form.get("instructions")
        remarks = request.form.get("remarks")

        interview_data = {
            "application_id": application_id,
            "interview_date": interview_date,
            "interview_time": interview_time,
            "interview_type": interview_type,
            "interviewer": interviewer,
            "interview_round": interview_round,
            "meeting_info": meeting_info,
            "instructions": instructions,
            "result": "Scheduled",
            "remarks": remarks
        }

        res = safe_db_insert("interviews", interview_data)

        # Update application status to Interview
        safe_db_update("applications", application_id, {"status": "Interview"})

        # Trigger notification
        app_res = supabase.table("applications").select("student_id, job_postings(job_title)").eq("id", application_id).single().execute()
        if app_res.data and app_res.data.get("student_id"):
            job_title = app_res.data.get("job_postings", {}).get("job_title", "Position")
            safe_db_insert("notifications", {
                "student_id": app_res.data["student_id"],
                "title": "Interview Scheduled",
                "message": f"Your interview for '{job_title}' has been scheduled for {interview_date} ({interview_time}).",
                "is_read": False
            })

        if session.get("role") == "company":
            return redirect(url_for("company_dashboard"))
        return redirect(url_for("interview_list"))

    # Fetch applications for dropdown selection
    company_id = session.get("company_id")
    if company_id:
        jobs_res = supabase.table("job_postings").select("id").eq("company_id", company_id).execute()
        job_ids = [j["id"] for j in (jobs_res.data or [])]
        if job_ids:
            application_response = supabase.table("applications").select(
                "*, students(full_name, usn), job_postings(job_title)"
            ).in_("job_id", job_ids).execute()
        else:
            application_response = type('obj', (object,), {'data': []})
    else:
        application_response = supabase.table("applications").select(
            "*, students(full_name, usn), job_postings(job_title)"
        ).execute()

    return render_template(
        "interview_register.html",
        applications=application_response.data or []
    )


# --------------------------------------------------------------------
# AUTOMATIC ELIGIBILITY CHECKER TOOL
# --------------------------------------------------------------------
@app.route("/eligibility-checker", methods=["GET", "POST"])
def eligibility_checker():
    students_res = supabase.table("students").select("*").execute()
    jobs_res = supabase.table("job_postings").select("*, companies(company_name)").execute()

    students = students_res.data or []
    jobs = jobs_res.data or []

    selected_student_id = request.values.get("student_id")
    selected_job_id = request.values.get("job_id")

    custom_student = None
    selected_job = None
    eligibility_result = None

    if selected_job_id:
        selected_job = next((j for j in jobs if str(j.get("id")) == str(selected_job_id)), None)

    if selected_student_id:
        custom_student = next((s for s in students if str(s.get("id")) == str(selected_student_id)), None)
    elif request.method == "POST":
        custom_student = {
            "full_name": request.form.get("full_name") or "Custom Candidate",
            "cgpa": float(request.form.get("cgpa") or 0),
            "backlogs": int(request.form.get("backlogs") or 0),
            "department": request.form.get("department") or "",
            "year": request.form.get("year") or "",
            "skills": request.form.get("skills") or ""
        }

    if custom_student and selected_job:
        eligibility_result = check_student_eligibility(custom_student, selected_job)

    return render_template(
        "eligibility_checker.html",
        students=students,
        jobs=jobs,
        selected_student=custom_student,
        selected_job=selected_job,
        selected_student_id=selected_student_id,
        selected_job_id=selected_job_id,
        result=eligibility_result
    )


# --------------------------------------------------------------------
# NOTIFICATIONS & ANNOUNCEMENTS
# --------------------------------------------------------------------
@app.route("/notification/list")
def notification_list():
    student_id = session.get("student_id")
    if student_id:
        response = supabase.table("notifications").select("*").eq("student_id", student_id).order("created_at", desc=True).execute()
    else:
        response = supabase.table("notifications").select("*, students(full_name, usn)").order("created_at", desc=True).execute()

    notifs = response.data or []
    unread_count = sum(1 for n in notifs if not n.get("is_read"))

    return render_template(
        "notification_list.html",
        notifications=notifs,
        unread_count=unread_count
    )


@app.route("/notification/mark_read/<notification_id>")
def notification_mark_read(notification_id):
    safe_db_update("notifications", notification_id, {"is_read": True})
    return redirect(url_for("notification_list"))


@app.route("/notification/mark_all_read")
def notification_mark_all_read():
    student_id = session.get("student_id")
    if student_id:
        supabase.table("notifications").update({"is_read": True}).eq("student_id", student_id).execute()
    else:
        supabase.table("notifications").update({"is_read": True}).eq("is_read", False).execute()

    return redirect(url_for("notification_list"))


# --------------------------------------------------------------------
# ADMIN PORTAL & EXISTING CRUD MANAGEMENT (SEPARATE ISOLATED PORTAL)
# --------------------------------------------------------------------
@app.route("/admin")
@app.route("/admin/")
@app.route("/admin/portal")
def admin_portal():
    """Separate dedicated entry point for College Placement Administration Portal."""
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("admin_login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.table("admins").select("*").eq("email", email).eq("password", password).execute()

        if response.data:
            session["admin_id"] = response.data[0]["id"]
            session["admin_name"] = response.data[0]["full_name"]
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html", error="Invalid admin email or password!")

    return render_template("admin_login.html")


@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "Placement Officer").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            return render_template("admin_register.html", error="Please fill in all required fields!")

        if len(password) < 4:
            return render_template("admin_register.html", error="Password must be at least 4 characters long!")

        if password != confirm_password:
            return render_template("admin_register.html", error="Passwords do not match!")

        try:
            existing = supabase.table("admins").select("id").eq("email", email).execute()
            if existing.data and len(existing.data) > 0:
                return render_template("admin_register.html", error="An administrator with this email is already registered!")

            insert_data = {
                "full_name": full_name,
                "email": email,
                "password": password,
                "role": role or "Admin"
            }
            res = safe_db_insert("admins", insert_data)

            if res.data:
                admin_record = res.data[0]
                session["admin_id"] = admin_record["id"]
                session["admin_name"] = admin_record.get("full_name", full_name)
                session["role"] = "admin"
                flash("Admin account created successfully! Welcome to your dashboard.", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                return render_template("admin_register.html", error="Registration failed. Please try again.")
        except Exception as e:
            return render_template("admin_register.html", error=f"Registration error: {str(e)}")

    return render_template("admin_register.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    # Fetch real live counters from database
    students_count = len(supabase.table("students").select("id").execute().data or [])
    companies_count = len(supabase.table("companies").select("id").execute().data or [])
    jobs_count = len(supabase.table("job_postings").select("id").execute().data or [])
    applications_count = len(supabase.table("applications").select("id").execute().data or [])
    placements_count = len(supabase.table("placements").select("id").execute().data or [])

    return render_template(
        "admin_dashboard.html",
        admin_name=session.get("admin_name"),
        students_count=students_count,
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        placements_count=placements_count
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# List views for admin management
# List views for admin management
@app.route("/student/list")
def student_list():
    if not session.get("admin_id"):
        flash("Access Denied: Only Administrators can access student roster.", "danger")
        if session.get("student_id"):
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("admin_login"))
    response = supabase.table("students").select("*").order("created_at", desc=True).execute()
    return render_template("student_list.html", students=response.data or [])

@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if not session.get("admin_id"):
        flash("Access Denied: Administrator access required.", "danger")
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        student_data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "date_of_birth": request.form.get("date_of_birth") or None,
            "gender": request.form.get("gender"),
            "department": request.form.get("department"),
            "year": request.form.get("year") or None,
            "usn": request.form.get("usn"),
            "cgpa": request.form.get("cgpa") or None,
            "resume_url": request.form.get("resume_url") or ""
        }
        safe_db_insert("students", student_data)
        flash("Student registered successfully!", "success")
        return redirect(url_for("student_list"))
    return render_template("student_register.html")

@app.route("/student/edit/<student_id>", methods=["GET", "POST"])
def student_edit(student_id):
    is_admin = bool(session.get("admin_id"))
    is_self_student = str(session.get("student_id")) == str(student_id)

    if not (is_admin or is_self_student):
        flash("Access Denied: You cannot view or edit another student's profile information.", "danger")
        if session.get("student_id"):
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("student_login"))

    if request.method == "POST":
        resume_file = request.files.get("resume_file") or request.files.get("resume")
        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            ts_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ts_filename)
            resume_file.save(file_path)
            resume_url = f"/uploads/resumes/{ts_filename}"
        else:
            resume_url = request.form.get("resume_url") or ""

        student_data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "date_of_birth": request.form.get("date_of_birth") or None,
            "gender": request.form.get("gender"),
            "department": request.form.get("department"),
            "year": request.form.get("year") or None,
            "usn": request.form.get("usn"),
            "cgpa": request.form.get("cgpa") or None,
            "backlogs": int(request.form.get("backlogs") or 0),
            "skills": request.form.get("skills") or DEFAULT_STUDENT_SKILLS,
            "certifications": request.form.get("certifications"),
            "projects": request.form.get("projects"),
            "github_url": request.form.get("github_url"),
            "portfolio_url": request.form.get("portfolio_url"),
            "preferred_location": request.form.get("preferred_location"),
            "preferred_work_mode": request.form.get("preferred_work_mode")
        }
        if resume_url:
            student_data["resume_url"] = resume_url

        safe_db_update("students", student_id, student_data)
        flash("Student profile updated successfully!", "success")
        if is_admin:
            return redirect(url_for("student_list"))
        return redirect(url_for("student_dashboard"))

    response = supabase.table("students").select("*").eq("id", student_id).single().execute()
    return render_template("student_edit.html", student=response.data or {})

@app.route("/student/delete/<student_id>")
def student_delete(student_id):
    if not session.get("admin_id"):
        flash("Access Denied: Only Admin can delete student profiles.", "danger")
        return redirect(url_for("admin_login"))
    try:
        supabase.table("students").delete().eq("id", student_id).execute()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete student: {str(e)}", "danger")
    return redirect(url_for("student_list"))

@app.route("/company/list")
def company_list():
    response = supabase.table("companies").select("*").order("created_at", desc=True).execute()
    return render_template("company_list.html", companies=response.data or [])

@app.route("/company/edit/<company_id>", methods=["GET", "POST"])
def company_edit(company_id):
    if request.method == "POST":
        company_data = {
            "company_name": request.form.get("company_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "website": request.form.get("website"),
            "location": request.form.get("location"),
            "description": request.form.get("description")
        }
        safe_db_update("companies", company_id, company_data)
        flash("Company updated successfully!", "success")
        return redirect(url_for("company_list"))

    response = supabase.table("companies").select("*").eq("id", company_id).single().execute()
    return render_template("company_edit.html", company=response.data or {})

@app.route("/company/delete/<company_id>")
def company_delete(company_id):
    try:
        supabase.table("companies").delete().eq("id", company_id).execute()
        flash("Company deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete company: {str(e)}", "danger")
    return redirect(url_for("company_list"))

@app.route("/job/list")
def job_list():
    response = supabase.table("job_postings").select("*, companies(company_name)").order("created_at", desc=True).execute()
    return render_template("job_posting_list.html", jobs=response.data or [])

@app.route("/job/edit/<job_id>", methods=["GET", "POST"])
def job_edit(job_id):
    if request.method == "POST":
        job_data = {
            "company_id": request.form.get("company_id"),
            "job_title": request.form.get("job_title"),
            "description": request.form.get("description"),
            "location": request.form.get("location"),
            "salary": request.form.get("salary") or None,
            "eligibility_cgpa": request.form.get("eligibility_cgpa") or None,
            "last_date": request.form.get("last_date") or None,
            "status": request.form.get("status", "Open")
        }
        safe_db_update("job_postings", job_id, job_data)
        flash("Job posting updated successfully!", "success")
        return redirect(url_for("job_list"))

    job_res = supabase.table("job_postings").select("*").eq("id", job_id).single().execute()
    companies_res = supabase.table("companies").select("id, company_name").execute()
    return render_template("job_posting_edit.html", job=job_res.data or {}, companies=companies_res.data or [])

@app.route("/job/delete/<job_id>")
def job_delete(job_id):
    try:
        supabase.table("job_postings").delete().eq("id", job_id).execute()
        flash("Job posting deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete job posting: {str(e)}", "danger")
    return redirect(url_for("job_list"))

@app.route("/application/list")
def application_list():
    response = supabase.table("applications").select(
        "*, students(full_name, usn), job_postings(job_title, companies(company_name))"
    ).order("created_at", desc=True).execute()
    return render_template("application_list.html", applications=response.data or [])

@app.route("/application/register", methods=["GET", "POST"])
def application_register():
    if request.method == "POST":
        app_data = {
            "student_id": request.form.get("student_id"),
            "job_id": request.form.get("job_id"),
            "status": request.form.get("status", "Applied"),
            "applied_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        safe_db_insert("applications", app_data)
        flash("Application created successfully!", "success")
        return redirect(url_for("application_list"))

    students_res = supabase.table("students").select("id, full_name, usn").execute()
    jobs_res = supabase.table("job_postings").select("id, job_title").execute()
    return render_template("application_register.html", students=students_res.data or [], jobs=jobs_res.data or [])

@app.route("/application/edit/<application_id>", methods=["GET", "POST"])
def application_edit(application_id):
    if request.method == "POST":
        app_data = {
            "student_id": request.form.get("student_id"),
            "job_id": request.form.get("job_id"),
            "status": request.form.get("status")
        }
        safe_db_update("applications", application_id, app_data)
        flash("Application updated successfully!", "success")
        return redirect(url_for("application_list"))

    app_res = supabase.table("applications").select("*").eq("id", application_id).single().execute()
    students_res = supabase.table("students").select("id, full_name, usn").execute()
    jobs_res = supabase.table("job_postings").select("id, job_title").execute()
    return render_template(
        "application_edit.html",
        application=app_res.data or {},
        students=students_res.data or [],
        jobs=jobs_res.data or []
    )

@app.route("/application/delete/<application_id>")
def application_delete(application_id):
    try:
        supabase.table("applications").delete().eq("id", application_id).execute()
        flash("Application deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete application: {str(e)}", "danger")
    return redirect(url_for("application_list"))

@app.route("/interview/list")
def interview_list():
    response = supabase.table("interviews").select(
        "*, applications(students(full_name, usn), job_postings(job_title, companies(company_name)))"
    ).order("created_at", desc=True).execute()
    return render_template("interview_list.html", interviews=response.data or [])

@app.route("/interview/edit/<interview_id>", methods=["GET", "POST"])
def interview_edit(interview_id):
    if request.method == "POST":
        interview_data = {
            "application_id": request.form.get("application_id"),
            "interview_date": request.form.get("interview_date") or None,
            "interview_type": request.form.get("interview_type"),
            "interviewer": request.form.get("interviewer"),
            "result": request.form.get("result"),
            "remarks": request.form.get("remarks")
        }
        safe_db_update("interviews", interview_id, interview_data)
        flash("Interview updated successfully!", "success")
        return redirect(url_for("interview_list"))

    interview_res = supabase.table("interviews").select("*").eq("id", interview_id).single().execute()
    apps_res = supabase.table("applications").select(
        "*, students(full_name, usn), job_postings(job_title)"
    ).execute()
    return render_template(
        "interview_edit.html",
        interview=interview_res.data or {},
        applications=apps_res.data or []
    )

@app.route("/interview/delete/<interview_id>")
def interview_delete(interview_id):
    try:
        supabase.table("interviews").delete().eq("id", interview_id).execute()
        flash("Interview deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete interview: {str(e)}", "danger")
    return redirect(url_for("interview_list"))

@app.route("/placement/list")
def placement_list():
    response = supabase.table("placements").select(
        "*, students(full_name, usn), companies(company_name), job_postings(job_title)"
    ).order("created_at", desc=True).execute()
    return render_template("placement_list.html", placements=response.data or [])

@app.route("/placement/register", methods=["GET", "POST"])
def placement_register():
    if request.method == "POST":
        placement_data = {
            "student_id": request.form.get("student_id"),
            "company_id": request.form.get("company_id"),
            "job_id": request.form.get("job_id"),
            "package": request.form.get("package") or None,
            "placement_date": request.form.get("placement_date") or None,
            "status": request.form.get("status", "Placed")
        }
        safe_db_insert("placements", placement_data)
        flash("Placement record created successfully!", "success")
        return redirect(url_for("placement_list"))

    students_res = supabase.table("students").select("id, full_name, usn").execute()
    companies_res = supabase.table("companies").select("id, company_name").execute()
    jobs_res = supabase.table("job_postings").select("id, job_title").execute()
    return render_template(
        "placement_register.html",
        students=students_res.data or [],
        companies=companies_res.data or [],
        jobs=jobs_res.data or []
    )

@app.route("/placement/edit/<placement_id>", methods=["GET", "POST"])
def placement_edit(placement_id):
    if request.method == "POST":
        placement_data = {
            "student_id": request.form.get("student_id"),
            "company_id": request.form.get("company_id"),
            "job_id": request.form.get("job_id"),
            "package": request.form.get("package") or None,
            "placement_date": request.form.get("placement_date") or None,
            "status": request.form.get("status")
        }
        safe_db_update("placements", placement_id, placement_data)
        flash("Placement updated successfully!", "success")
        return redirect(url_for("placement_list"))

    pl_res = supabase.table("placements").select("*").eq("id", placement_id).single().execute()
    students_res = supabase.table("students").select("id, full_name, usn").execute()
    companies_res = supabase.table("companies").select("id, company_name").execute()
    jobs_res = supabase.table("job_postings").select("id, job_title").execute()
    return render_template(
        "placement_edit.html",
        placement=pl_res.data or {},
        students=students_res.data or [],
        companies=companies_res.data or [],
        jobs=jobs_res.data or []
    )

@app.route("/placement/delete/<placement_id>")
def placement_delete(placement_id):
    try:
        supabase.table("placements").delete().eq("id", placement_id).execute()
        flash("Placement deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete placement: {str(e)}", "danger")
    return redirect(url_for("placement_list"))

@app.route("/notification/register", methods=["GET", "POST"])
def notification_register():
    if request.method == "POST":
        is_read_str = request.form.get("is_read", "false").lower()
        notif_data = {
            "student_id": request.form.get("student_id"),
            "title": request.form.get("title"),
            "message": request.form.get("message"),
            "is_read": is_read_str == "true"
        }
        safe_db_insert("notifications", notif_data)
        flash("Notification created successfully!", "success")
        return redirect(url_for("notification_list"))

    students_res = supabase.table("students").select("id, full_name, usn").execute()
    return render_template("notification_register.html", students=students_res.data or [])

@app.route("/notification/edit/<notification_id>", methods=["GET", "POST"])
def notification_edit(notification_id):
    if request.method == "POST":
        is_read_str = request.form.get("is_read", "false").lower()
        notif_data = {
            "student_id": request.form.get("student_id"),
            "title": request.form.get("title"),
            "message": request.form.get("message"),
            "is_read": is_read_str == "true"
        }
        safe_db_update("notifications", notification_id, notif_data)
        flash("Notification updated successfully!", "success")
        return redirect(url_for("notification_list"))

    notif_res = supabase.table("notifications").select("*").eq("id", notification_id).single().execute()
    students_res = supabase.table("students").select("id, full_name, usn").execute()
    return render_template(
        "notification_edit.html",
        notification=notif_res.data or {},
        students=students_res.data or []
    )

@app.route("/notification/delete/<notification_id>")
def notification_delete(notification_id):
    try:
        supabase.table("notifications").delete().eq("id", notification_id).execute()
        flash("Notification deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete notification: {str(e)}", "danger")
    return redirect(url_for("notification_list"))

@app.route("/companies")
def public_companies():
    query = request.args.get("query", "").strip()
    if query:
        companies_response = supabase.table("companies").select("*").ilike("company_name", f"%{query}%").execute()
    else:
        companies_response = supabase.table("companies").select("*").order("created_at", desc=True).execute()

    return render_template("company_directory.html", companies=companies_response.data or [])


if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "192.168.29.84"

    print("\n" + "="*65)
    print("🎓 COLLEGE PLACEMENT MANAGEMENT SYSTEM IS ONLINE!")
    print(f"🌐 Main Portal (Wi-Fi):       http://{local_ip}:5000")
    print("💻 Main Portal (Local):       http://127.0.0.1:5000")
    print(f"🛡️ Separate Admin Portal:     http://127.0.0.1:5000/admin")
    print(f"   (Network Admin Link:       http://{local_ip}:5000/admin)")
    print("="*65 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)