import os
from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash, send_from_directory, Response
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime, time
from fpdf import FPDF
import qrcode
import csv
from collections import Counter

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "evidence_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'change_this_to_anything_for_security'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Session configuration for proper cookie handling
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * 24  # 24 hours

student_names = [
    # Paste your full list of student names here
    "SHERIN MAYBEL", "SHIJO", "SHRISHTICA", "SHRUTHI", "SIBI RICHARD", "SIBI SUDHAN",
    "SIVA", "SIVA ADITHYA NARAYANA", "SIVACHANDRAN", "SREE RAJ", "SRI SANJANA", "SRIMAGAL",
    "SRUTHIKA", "STEVE ALLAN PAUL", "STEVE FRANCIS JESA", "SUCHARITAA", "SUGASRI", "SUGUMAR",
    "SURENDRAN", "SURYA", "SUSHIL DAVID", "SUVIKSHA", "SVETHA", "SWATHI", "SWETHA", "TAMILARASI",
    "TAMIZH SELVAN", "TAYYIBAH", "TEJESHVAR", "TEJESWINI", "THAMINA FARZANA", "THARANI", "THARIKA",
    "THARUN KUMAR", "THILLAI RAJAN", "THIVAGAR", "UDAYA", "UMABHARATHI", "VARSHITHA", "VARUN",
    "VARUNIKA", "VATHSALYA", "VIBUSHAN", "VICKRAMVEL", "VIDHIYA", "VIGNESH", "VIGNESHWARAN",
    "VIJAY REDDY", "VISHAL KUMAR", "VISHALINI", "VISHWA RUBA", "VISHWAROOPAN", "VISWAPRIYAN",
    "VIVEDHA", "YASHASWINI", "YASHWANTH", "YOGESH KANNAN", "YOGESHWAR", "YUVA KUMARAN",
    "YUVARAJ", "YUVASHRI"
]

absence_reasons = ["Sick", "Permission", "Unknown", "Travel", "Other"]

attendance_data = {}  # {date: {student: {status, timestamp, reason, evidence}}}
correction_requests = []  # List of dicts: {student, date, requested_status, reason, evidence, status, comments, response_comments}

# Users dict with admin and teacher, plus a login for each student.
users = {
    "admin": {"password": "adminpass", "role": "admin"},
    "teacher": {"password": "teacherpass", "role": "teacher"},
}
for n in student_names:
    uname = n.lower().replace(" ", "_")
    users[uname] = {"password": "studentpass", "role": "student"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def today_str():
    return datetime.now().strftime('%Y-%m-%d')

@app.route("/login", methods=["GET", "POST"])
def login():
    qrcode_img = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            flash("Username and password are required", "danger")
            return render_template("login.html", qrcode_img=qrcode_img)
        
        user = users.get(username)
        if user and user["password"] == password:
            session.clear()
            session.permanent = True
            session["username"] = username
            session["role"] = user["role"]
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "danger")
    if "username" in session and session.get("role") == "student":
        from base64 import b64encode
        q = qrcode.make(session["username"])
        buf = BytesIO()
        q.save(buf, format="PNG")
        buf.seek(0)
        qrcode_img = b64encode(buf.read()).decode()
    return render_template("login.html", qrcode_img=qrcode_img)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", role=session.get("role"))

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "username" not in session:
        return redirect(url_for("login"))
    date = today_str()
    if date not in attendance_data:
        attendance_data[date] = {}
    day_attendance = attendance_data[date]
    late_time = datetime.now().time() > time(10, 30)
    role = session.get("role")
    if len(day_attendance) < len(student_names) and late_time and role == "teacher":
        flash("Reminder: Attendance for today is not completely filled!", "warning")
    
    if request.method == "POST":
        if role == "teacher" and request.form.get("qr_student"):
            qr_student = request.form.get("qr_student")
            for n in student_names:
                if qr_student == n.lower().replace(" ", "_") and n not in day_attendance:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    day_attendance[n] = {
                        "status": "Present",
                        "timestamp": now,
                        "reason": None,
                        "evidence": None
                    }
                    flash(f"{n} marked present from QR!", "success")
            return redirect(url_for("attendance"))
        
        student = request.form.get("student")
        status = request.form.get("status")
        reason = request.form.get("reason") if status == "Absent" else None
        evidence = None
        if status == "Absent" and "evidence" in request.files and request.files["evidence"].filename:
            file = request.files["evidence"]
            if allowed_file(file.filename):
                fname = f"{date}_{student}_{secure_filename(file.filename)}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                file.save(file_path)
                evidence = fname
            else:
                flash("Invalid file format.", "danger")
                return redirect(url_for("attendance"))
        if student and status and student not in day_attendance:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            day_attendance[student] = {"status": status, "timestamp": now, "reason": reason, "evidence": evidence}
        return redirect(url_for("attendance"))

    return render_template("attendance.html", student_names=student_names, attendance_status=day_attendance, date=date, role=role, absence_reasons=absence_reasons)

@app.route("/view_evidence/<date>/<student>")
def view_evidence(date, student):
    att = attendance_data.get(date, {}).get(student, {})
    fname = att.get("evidence")
    if fname:
        return send_from_directory(app.config['UPLOAD_FOLDER'], fname, as_attachment=True)
    return "No evidence uploaded.", 404

@app.route("/attendance_log_view", methods=["GET"])
def attendance_log_view():
    if "username" not in session:
        return redirect(url_for("login"))
    view_date = request.args.get("date") or today_str()
    log_dates = sorted(attendance_data.keys(), reverse=True)
    attendance_status = attendance_data.get(view_date, {})
    absent_counts = {}
    for day, log in attendance_data.items():
        for student, d in log.items():
            if d.get("status") == "Absent":
                absent_counts[student] = absent_counts.get(student, 0) + 1
    alerts = [f"{student} is absent for {count} times!" for student, count in absent_counts.items() if count >= 3]
    return render_template("attendance_log.html", student_names=student_names, attendance_status=attendance_status, view_date=view_date, log_dates=log_dates, alerts=alerts, role=session.get("role"), absence_reasons=absence_reasons)

@app.route("/attendance_log_pdf")
def attendance_log_pdf():
    if "username" not in session or session.get("role") != "teacher":
        flash("Only teachers can download logs.", "danger")
        return redirect(url_for('attendance_log_view'))
    date = request.args.get("date") or today_str()
    day_attendance = attendance_data.get(date, {})
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Attendance Log: {date}", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align="R")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(12, 10, "No", border=1, align="C")
    pdf.cell(60, 10, "Student", border=1, align="C")
    pdf.cell(22, 10, "Status", border=1, align="C")
    pdf.cell(27, 10, "Reason", border=1, align="C")
    pdf.cell(40, 10, "Marked At", border=1, align="C")
    pdf.cell(20, 10, "Evidence", border=1, align="C", ln=1)
    pdf.set_font("Arial", "", 10)
    for i, student in enumerate(student_names, 1):
        d = day_attendance.get(student, {})
        pdf.cell(12, 10, str(i), border=1, align="C")
        pdf.cell(60, 10, student, border=1)
        pdf.cell(22, 10, d.get("status", "Not marked"), border=1, align="C")
        pdf.cell(27, 10, d.get("reason") if d.get("status") == "Absent" else "-", border=1, align="C")
        pdf.cell(40, 10, d.get("timestamp", "-"), border=1, align="C")
        pdf.cell(20, 10, "Yes" if d.get("evidence") else "-", border=1, align="C", ln=1)
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    pdf_output = BytesIO(pdf_bytes)
    filename = f"attendance_{date}.pdf"
    return send_file(pdf_output, download_name=filename, as_attachment=True, mimetype='application/pdf')

@app.route("/attendance_log_csv")
def attendance_log_csv():
    if "username" not in session or session.get("role") != "teacher":
        flash("Only teachers can download logs.", "danger")
        return redirect(url_for('attendance_log_view'))
    date = request.args.get("date") or today_str()
    day_attendance = attendance_data.get(date, {})
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(["No", "Student", "Status", "Reason", "Marked At", "Evidence"])
    for i, student in enumerate(student_names, 1):
        d = day_attendance.get(student, {})
        writer.writerow([
            i,
            student,
            d.get("status", "Not marked"),
            d.get("reason") if d.get("status") == "Absent" else "-",
            d.get("timestamp", "-"),
            "Yes" if d.get("evidence") else "-"
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=attendance_{date}.csv"}
    )

@app.route("/attendance_analytics")
def attendance_analytics():
    if "username" not in session:
        return redirect(url_for("login"))
    chart_labels = []
    present_counts = []
    absent_counts = []
    late_counts = []
    for day in sorted(attendance_data.keys()):
        chart_labels.append(day)
        prs = absn = late = 0
        for s in student_names:
            d = attendance_data[day].get(s, {})
            st = d.get("status")
            if st == "Present":
                prs += 1
            elif st == "Absent":
                absn += 1
            elif st == "Late":
                late += 1
        present_counts.append(prs)
        absent_counts.append(absn)
        late_counts.append(late)
    return render_template("attendance_analytics.html",
                           chart_labels=chart_labels,
                           present_counts=present_counts,
                           absent_counts=absent_counts,
                           late_counts=late_counts,
                           role=session.get("role"))

@app.route("/student_dashboard")
def student_dashboard():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
    username = session["username"]
    student_name = next((n for n in student_names if username == n.lower().replace(" ", "_")), None)
    if not student_name:
        flash("Student record not found.", "danger")
        return redirect(url_for("home"))

    attendance_history = []
    status_counter = Counter()
    for date in sorted(attendance_data.keys()):
        day_log = attendance_data[date]
        record = day_log.get(student_name)
        if record:
            status = record.get("status", "Not marked")
            attendance_history.append({"date": date, "status": status})
            status_counter[status] += 1
        else:
            attendance_history.append({"date": date, "status": "Not marked"})

    total_days = len(attendance_history)
    present_days = status_counter.get("Present", 0)
    absent_days = status_counter.get("Absent", 0)
    late_days = status_counter.get("Late", 0)
    attendance_percent = (present_days / total_days * 100) if total_days > 0 else 0

    return render_template("student_dashboard.html",
                           student=student_name,
                           attendance_history=attendance_history,
                           present_days=present_days,
                           absent_days=absent_days,
                           late_days=late_days,
                           attendance_percent=round(attendance_percent, 2),
                           total_days=total_days,
                           role=session.get("role"))

@app.route("/correction_requests", methods=["GET", "POST"])
def correction_requests_view():
    if "username" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    username = session.get("username")

    if request.method == "POST":
        if role == "student":
            req_date = request.form.get("date")
            req_status = request.form.get("requested_status")
            req_reason = request.form.get("reason")
            req_comments = request.form.get("comments")
            req_evidence = None
            if "evidence" in request.files and request.files["evidence"].filename:
                file = request.files["evidence"]
                if allowed_file(file.filename):
                    fname = f"correction_{username}_{secure_filename(file.filename)}"
                    path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                    file.save(path)
                    req_evidence = fname
                else:
                    flash("Invalid file format for correction evidence.", "danger")
                    return redirect(url_for("correction_requests_view"))
            correction_requests.append({
                "student": username,
                "date": req_date,
                "requested_status": req_status,
                "reason": req_reason,
                "comments": req_comments,
                "evidence": req_evidence,
                "status": "Pending",
                "response_comments": "",
            })
            flash("Correction request submitted successfully.", "success")
            return redirect(url_for("correction_requests_view"))
        elif role in ("teacher", "admin"):
            action = request.form.get("action")
            idx = int(request.form.get("request_index"))
            response_comments = request.form.get("response_comments")
            if 0 <= idx < len(correction_requests):
                req = correction_requests[idx]
                req["status"] = "Approved" if action == "approve" else "Rejected"
                req["response_comments"] = response_comments
                if req["status"] == "Approved":
                    date = req["date"]
                    student = next((n for n in student_names if req["student"] == n.lower().replace(" ", "_")), None)
                    if date and student:
                        if date not in attendance_data:
                            attendance_data[date] = {}
                        attendance_data[date][student] = {
                            "status": req["requested_status"],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "reason": req["reason"],
                            "evidence": req["evidence"]
                        }
                flash(f"Request {req['status'].lower()} successfully.", "success")
            else:
                flash("Invalid request index.", "danger")
            return redirect(url_for("correction_requests_view"))

    filtered_reqs = []
    if role == "student":
        filtered_reqs = [r for r in correction_requests if r["student"] == username]
    elif role in ("teacher", "admin"):
        filtered_reqs = correction_requests

    return render_template("correction_requests.html", requests=filtered_reqs, role=role)

@app.route("/bulk_mark", methods=["GET", "POST"])
def bulk_mark():
    if "username" not in session or session.get("role") not in ("teacher", "admin"):
        return redirect(url_for("login"))
    date = today_str()
    if date not in attendance_data:
        attendance_data[date] = {}
    day_attendance = attendance_data[date]

    if request.method == "POST":
        action = request.form.get("bulk_action")
        if action == "mark_all_present":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for student in student_names:
                if student not in day_attendance:
                    day_attendance[student] = {"status": "Present", "timestamp": now, "reason": None, "evidence": None}
            flash("All students marked as Present.", "success")
        elif action == "mark_all_absent":
            reason = request.form.get("absent_reason") or "Unknown"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for student in student_names:
                if student not in day_attendance:
                    day_attendance[student] = {"status": "Absent", "timestamp": now, "reason": reason, "evidence": None}
            flash(f"All students marked as Absent ({reason}).", "success")
        return redirect(url_for("bulk_mark"))

    return render_template("bulk_mark.html", absence_reasons=absence_reasons, role=session.get("role"))

@app.route("/admin_users", methods=["GET", "POST"])
def admin_users():
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "add_user":
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role")
            if username in users:
                flash("Username already exists.", "danger")
            else:
                users[username] = {"password": password, "role": role}
                flash(f"User {username} added successfully.", "success")
        elif form_type == "reset_password":
            username = request.form.get("reset_username")
            new_password = request.form.get("new_password")
            if username in users:
                users[username]["password"] = new_password
                flash(f"Password for {username} reset successfully.", "success")
            else:
                flash("Username not found.", "danger")
        return redirect(url_for("admin_users"))

    return render_template("admin_users.html", users=users, role=session.get("role"))

@app.route("/timetable")
def timetable():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("timetable.html", role=session.get("role"))

@app.route("/important_questions")
def important_questions():
    if "username" not in session:
        return redirect(url_for("login"))
    subjects = [
        ("DPLD", "dpld"),
        ("DS", "ds"),
        ("CA", "ca"),
        ("AS", "as"),
        ("JAVA", "java"),
        ("MATHS", "maths")
    ]
    return render_template("important_questions_subjects.html", subjects=subjects, role=session.get("role"))

@app.route("/important_questions/<subject>")
def important_questions_subject(subject):
    if "username" not in session:
        return redirect(url_for("login"))
    ds_questions = [
        "1. What is data structure? And explain about its type.",
        "2. What is ADT? Explain about it.",
        "3. What is linked list? Explain in detail.",
        "4. Explain about stack ADT.",
        "5. Explain about Queue ADT.",
        "6. Describe about types of Queue.",
        "7. Conversion of Infix to Postfix."
    ]
    subjects_dict = {
        "dpld": "DPLD",
        "ds": "DS",
        "ca": "CA",
        "as": "AS",
        "java": "JAVA",
        "maths": "MATHS"
    }
    subject_name = subjects_dict.get(subject, None)
    questions = ds_questions if subject == "ds" else []
    return render_template("important_questions_detail.html", subject=subject_name, questions=questions, role=session.get("role"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, port=port, host="127.0.0.1")