from flask import Flask, render_template_string, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "timetable_secret"

DATABASE = "timetable.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM User
            WHERE Username = ?
            AND Password = ?
        """, (username, password)).fetchone()

        conn.close()

        if user:
            session["username"] = user["Username"]
            session["role"] = user["Role"]
            session["professor_id"] = user["ProfessorID"]
            return redirect("/dashboard")

        message = "Invalid username or password!"

    html = """
    <html>
    <head>
        <title>Login</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f6f8;
            }

            .box {
                width: 350px;
                margin: 100px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px #ccc;
            }

            h1 {
                text-align: center;
                color: #087f8c;
            }

            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                box-sizing: border-box;
            }

            button {
                width: 100%;
                padding: 12px;
                background: #087f8c;
                color: white;
                border: none;
            }

            .error {
                color: red;
                text-align: center;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <h1>Login</h1>

            <p style="text-align:center;">
                Timetable Management System
            </p>

            {% if message %}
                <p class="error">{{ message }}</p>
            {% endif %}

            <form method="POST">

                <input type="text"
                       name="username"
                       placeholder="Username"
                       required>

                <input type="password"
                       name="password"
                       placeholder="Password"
                       required>

                <button type="submit">
                    Login
                </button>

            </form>

        </div>

    </body>
    </html>
    """

    return render_template_string(html, message=message)


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    html = """
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f6f8;
            }

            .container {
                width: 80%;
                margin: 50px auto;
                background: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px;
                box-shadow: 0 2px 10px #ccc;
            }

            a {
                display: inline-block;
                padding: 12px 20px;
                margin: 10px;
                background: #087f8c;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>Timetable Management System</h1>

            <h2>Welcome, {{ username }}</h2>

            <h3>Role: {{ role }}</h3>

            <a href="/timetable">
                View Timetable
            </a>
{% if role == "Professor" %}

    <a href="/professor">
        My Professor Panel
    </a>

{% endif %}
            {% if role == "Admin" %}
                <a href="/admin">
                    Admin Panel
                </a>
            {% endif %}

            <a href="/logout">
                Logout
            </a>

        </div>

    </body>
    </html>
    """

    return render_template_string(
        html,
        username=session["username"],
        role=session["role"]
    )


@app.route("/timetable")
def timetable():

    if "username" not in session:
        return redirect("/")

    conn = get_db()

    timetable = conn.execute("""
        SELECT
            Timetable.TimetableID,
            Professor.Name AS Professor,
            Course.CourseName AS Course,
            ClassGroup.ClassName AS Class,
            Room.RoomNumber AS Room,
            Day.DayName AS Day,
            TimeSlot.StartTime || ' - ' || TimeSlot.EndTime AS Time
        FROM Timetable
        JOIN Professor
            ON Timetable.ProfessorID = Professor.ProfessorID
        JOIN Course
            ON Timetable.CourseID = Course.CourseID
        JOIN ClassGroup
            ON Timetable.ClassGroupID = ClassGroup.ClassGroupID
        JOIN Room
            ON Timetable.RoomID = Room.RoomID
        JOIN Day
            ON Timetable.DayID = Day.DayID
        JOIN TimeSlot
            ON Timetable.TimeSlotID = TimeSlot.TimeSlotID
        ORDER BY Day.DayID, TimeSlot.TimeSlotID
    """).fetchall()

    conn.close()

    html = """
    <html>
    <head>
        <title>Weekly Timetable</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f6f8;
            }

            .container {
                width: 95%;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 10px;
            }

            h1 {
                text-align: center;
                color: #087f8c;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th {
                background: #087f8c;
                color: white;
                padding: 12px;
            }

            td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: center;
            }

            a {
                color: #087f8c;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>Weekly Timetable</h1>

            <a href="/dashboard">
                ← Back to Dashboard
            </a>

            <table>

                <tr>
                    <th>ID</th>
                    <th>Professor</th>
                    <th>Course</th>
                    <th>Class</th>
                    <th>Room</th>
                    <th>Day</th>
                    <th>Time</th>
                    <th>action</th>
                </tr>

                {% for row in timetable %}

                <tr>
                    <td>{{ row["TimetableID"] }}</td>
                    <td>{{ row["Professor"] }}</td>
                    <td>{{ row["Course"] }}</td>
                    <td>{{ row["Class"] }}</td>
                    <td>{{ row["Room"] }}</td>
                    <td>{{ row["Day"] }}</td>
                    <td>{{ row["Time"] }}</td>
<td>
    <form method="POST"
          action="/delete/{{ row['TimetableID'] }}">
        <button type="submit">
            Delete
        </button>
    </form>
</td>
                </tr>

                {% endfor %}

            </table>

        </div>

    </body>
    </html>
    """

    return render_template_string(
        html,
        timetable=timetable
    )
@app.route("/delete/<int:timetable_id>", methods=["POST"])
def delete_timetable(timetable_id):

    if "username" not in session:
        return redirect("/")

    if session["role"] != "Admin":
        return "Access Denied"

    conn = get_db()

    conn.execute(
        "DELETE FROM Timetable WHERE TimetableID = ?",
        (timetable_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/timetable")

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if "username" not in session:
        return redirect("/")

    if session["role"] != "Admin":
        return "Access Denied"

    message = ""

    conn = get_db()

    professors = conn.execute(
        "SELECT * FROM Professor"
    ).fetchall()

    courses = conn.execute(
        "SELECT * FROM Course"
    ).fetchall()

    classes = conn.execute(
        "SELECT * FROM ClassGroup"
    ).fetchall()

    rooms = conn.execute(
        "SELECT * FROM Room"
    ).fetchall()

    days = conn.execute(
        "SELECT * FROM Day"
    ).fetchall()

    slots = conn.execute(
        "SELECT * FROM TimeSlot"
    ).fetchall()

    if request.method == "POST":

        try:

            conn.execute("""
                INSERT INTO Timetable
                (ProfessorID, CourseID, ClassGroupID,
                 RoomID, DayID, TimeSlotID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                request.form["professor"],
                request.form["course"],
                request.form["classgroup"],
                request.form["room"],
                request.form["day"],
                request.form["slot"]
            ))

            conn.commit()

            message = "Timetable added successfully!"

        except sqlite3.IntegrityError:

            message = "CLASH DETECTED! Professor, Room or Class is already busy."

    conn.close()

    html = """
    <html>

    <head>
        <title>Admin Panel</title>

        <style>

            body {
                font-family: Arial;
                background: #f2f6f8;
            }

            .box {
                width: 500px;
                margin: 30px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px #ccc;
            }

            h1 {
                text-align: center;
                color: #087f8c;
            }

            label {
                display: block;
                margin-top: 12px;
            }

            select {
                width: 100%;
                padding: 10px;
                margin-top: 5px;
            }

            button {
                width: 100%;
                padding: 12px;
                margin-top: 20px;
                background: #087f8c;
                color: white;
                border: none;
            }

            .message {
                text-align: center;
                font-weight: bold;
                margin: 15px;
            }

            a {
                display: block;
                text-align: center;
                margin-top: 15px;
            }

        </style>
    </head>

    <body>

        <div class="box">

            <h1>Admin Panel</h1>

            {% if message %}
                <div class="message">
                    {{ message }}
                </div>
            {% endif %}

            <form method="POST">

                <label>Professor</label>

                <select name="professor" required>
                    {% for p in professors %}
                    <option value="{{ p['ProfessorID'] }}">
                        {{ p['Name'] }}
                    </option>
                    {% endfor %}
                </select>


                <label>Course</label>

                <select name="course" required>
                    {% for c in courses %}
                    <option value="{{ c['CourseID'] }}">
                        {{ c['CourseName'] }}
                    </option>
                    {% endfor %}
                </select>


                <label>Class</label>

                <select name="classgroup" required>
                    {% for c in classes %}
                    <option value="{{ c['ClassGroupID'] }}">
                        {{ c['ClassName'] }}
                    </option>
                    {% endfor %}
                </select>


                <label>Room</label>

                <select name="room" required>
                    {% for r in rooms %}
                    <option value="{{ r['RoomID'] }}">
                        {{ r['RoomNumber'] }}
                    </option>
                    {% endfor %}
                </select>


                <label>Day</label>

                <select name="day" required>
                    {% for d in days %}
                    <option value="{{ d['DayID'] }}">
                        {{ d['DayName'] }}
                    </option>
                    {% endfor %}
                </select>


                <label>Time Slot</label>

                <select name="slot" required>
                    {% for s in slots %}
                    <option value="{{ s['TimeSlotID'] }}">
                        {{ s['StartTime'] }} - {{ s['EndTime'] }}
                    </option>
                    {% endfor %}
                </select>


                <button type="submit">
                    Add Timetable
                </button>

            </form>

            <a href="/timetable">
                View Timetable
            </a>

            <a href="/dashboard">
                Back to Dashboard
            </a>

        </div>

    </body>
    </html>
    """

    return render_template_string(
        html,
        professors=professors,
        courses=courses,
        classes=classes,
        rooms=rooms,
        days=days,
        slots=slots,
        message=message
    )
@app.route("/professor")
def professor_panel():

    if "username" not in session:
        return redirect("/")

    if session["role"] != "Professor":
        return "Access Denied"

    professor_id = session["professor_id"]
    username = session["username"]

    conn = get_db()

    timetable = conn.execute("""
        SELECT
            Course.CourseName AS Course,
            ClassGroup.ClassName AS Class,
            Room.RoomNumber AS Room,
            Day.DayName AS Day,
            TimeSlot.StartTime || ' - ' || TimeSlot.EndTime AS Time
        FROM Timetable
        JOIN Course
            ON Timetable.CourseID = Course.CourseID
        JOIN ClassGroup
            ON Timetable.ClassGroupID = ClassGroup.ClassGroupID
        JOIN Room
            ON Timetable.RoomID = Room.RoomID
        JOIN Day
            ON Timetable.DayID = Day.DayID
        JOIN TimeSlot
            ON Timetable.TimeSlotID = TimeSlot.TimeSlotID
        WHERE Timetable.ProfessorID = ?
        ORDER BY Day.DayID, TimeSlot.TimeSlotID
    """, (professor_id,)).fetchall()

    conn.close()

    html = """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Professor Panel</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f2f6f8;
                margin: 0;
            }

            header {
                background: #087f8c;
                color: white;
                padding: 20px;
                text-align: center;
            }

            .container {
                width: 90%;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 10px #ccc;
            }

            h2 {
                color: #087f8c;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }

            th {
                background: #087f8c;
                color: white;
                padding: 12px;
            }

            td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: center;
            }

            tr:nth-child(even) {
                background: #f5f5f5;
            }

            .button {
                display: inline-block;
                padding: 10px 18px;
                margin-top: 20px;
                background: #087f8c;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Professor Panel</h1>
            <p>Welcome, {{ username }}</p>
        </header>

        <div class="container">

            <h2>My Timetable</h2>

            <table>

                <tr>
                    <th>Course</th>
                    <th>Class</th>
                    <th>Room</th>
                    <th>Day</th>
                    <th>Time</th>
                </tr>

                {% for row in timetable %}

                <tr>
                    <td>{{ row["Course"] }}</td>
                    <td>{{ row["Class"] }}</td>
                    <td>{{ row["Room"] }}</td>
                    <td>{{ row["Day"] }}</td>
                    <td>{{ row["Time"] }}</td>
                </tr>

                {% endfor %}

            </table>

            <a class="button" href="/dashboard">
                Back to Dashboard
            </a>

            <a class="button" href="/logout">
                Logout
            </a>

        </div>

    </body>
    </html>
    """

    return render_template_string(
        html,
        timetable=timetable,
        username=username
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)