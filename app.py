import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "todo.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                due_date TEXT
            )
        """)


@app.route("/")
def index():
    with get_db() as conn:
        todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return render_template("index.html", todos=todos)


@app.route("/create", methods=["POST"])
def create():
    title = request.form["title"].strip()
    due_date = request.form.get("due_date", "").strip() or None
    if title:
        with get_db() as conn:
            conn.execute("INSERT INTO todos (title, due_date) VALUES (?, ?)", (title, due_date))
    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip() or None
    if title:
        with get_db() as conn:
            conn.execute("UPDATE todos SET title = ?, due_date = ? WHERE id = ?", (title, due_date, todo_id))
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    with get_db() as conn:
        todo = conn.execute("SELECT done FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if todo:
            conn.execute("UPDATE todos SET done = ? WHERE id = ?", (1 - todo["done"], todo_id))
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
