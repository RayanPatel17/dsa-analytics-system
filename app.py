from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            topic TEXT,
            difficulty TEXT,
            status TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- ADD PROBLEM ----------
@app.route('/add-problem', methods=['POST'])
def add_problem():
    data = request.json

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO problems (name, topic, difficulty, status, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['topic'],
        data['difficulty'],
        data['status'],
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Problem added successfully"})


# ---------- GET ALL PROBLEMS ----------
@app.route('/problems', methods=['GET'])
def get_problems():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM problems')
    rows = cursor.fetchall()

    conn.close()

    problems = []
    for row in rows:
        problems.append({
            "id": row[0],
            "name": row[1],
            "topic": row[2],
            "difficulty": row[3],
            "status": row[4],
            "date": row[5]
        })

    return jsonify(problems)


# ---------- DELETE PROBLEM ----------
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_problem(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM problems WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted successfully"})

@app.route('/update/<int:id>', methods=['PUT'])
def update_problem(id):
    data = request.json

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE problems
        SET name=?, topic=?, difficulty=?, status=?
        WHERE id=?
    ''', (
        data['name'],
        data['topic'],
        data['difficulty'],
        data['status'],
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated successfully"})

@app.route('/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Total solved problems
    cursor.execute("SELECT COUNT(*) FROM problems WHERE status='Solved'")
    solved = cursor.fetchone()[0]

    # Topic-wise distribution
    cursor.execute("SELECT topic, COUNT(*) FROM problems GROUP BY topic")
    topics = cursor.fetchall()

    conn.close()

    topic_data = {}
    for topic, count in topics:
        topic_data[topic] = count

    return jsonify({
        "total_solved": solved,
        "topics": topic_data
    })

@app.route('/weak-topic', methods=['GET'])
def weak_topic():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT topic, COUNT(*) as count FROM problems GROUP BY topic ORDER BY count ASC LIMIT 1')
    result = cursor.fetchone()

    conn.close()

    if result:
        return jsonify({
            "weakest_topic": result[0],
            "problems_solved": result[1]
        })
    else:
        return jsonify({"message": "No data available"})
    
@app.route('/revise', methods=['GET'])
def revise_problems():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM problems
        WHERE status='Solved'
        AND date <= date('now', '-7 day')
    ''')

    rows = cursor.fetchall()
    conn.close()

    problems = []
    for row in rows:
        problems.append({
            "id": row[0],
            "name": row[1],
            "topic": row[2],
            "difficulty": row[3],
            "status": row[4],
            "date": row[5]
        })

    return jsonify(problems)

@app.route('/recommend', methods=['GET'])
def recommend():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Get weakest topic
    cursor.execute('''
        SELECT topic, COUNT(*) as count
        FROM problems
        GROUP BY topic
        ORDER BY count ASC
        LIMIT 1
    ''')
    weak = cursor.fetchone()

    # Count solved problems
    cursor.execute("SELECT COUNT(*) FROM problems WHERE status='Solved'")
    solved = cursor.fetchone()[0]

    conn.close()

    if weak:
        return jsonify({
            "message": f"Practice more problems from {weak[0]}",
            "problems_solved": solved
        })
    else:
        return jsonify({"message": "Start solving problems!"})
    
from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')

# ---------- RUN SERVER ----------
if __name__ == '__main__':
    app.run(debug=True)

