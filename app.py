from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from config import Config
from database import get_db, init_db

app = Flask(__name__, static_folder='static')
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
CORS(app)
jwt = JWTManager(app)

# ── Initialize DB tables on startup (works on Render too) ──
init_db()

# ── SERVE HTML PAGES ──
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ── REGISTER ──
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name     = data.get('name','').strip()
        email    = data.get('email','').strip()
        password = data.get('password','').strip()
        dept     = data.get('department','IT')
        sem      = data.get('semester', 6)
        roll     = data.get('roll_no','')

        if not name or not email or not password:
            return jsonify({'success':False,'message':'All fields are required!'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM students WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({'success':False,'message':'Email already registered!'}), 409

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO students (name,email,password,department,semester,roll_no)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, email, hashed, dept, sem, roll))
        conn.commit()

        student_id = cursor.lastrowid
        cursor.close(); conn.close()

        token = create_access_token(identity=str(student_id))
        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'token': token,
            'student': {'id':student_id,'name':name,'email':email,'department':dept,'semester':sem}
        }), 201

    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── LOGIN ──
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email    = data.get('email','').strip()
        password = data.get('password','').strip()

        if not email or not password:
            return jsonify({'success':False,'message':'Email and password required!'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
        student = cursor.fetchone()
        cursor.close(); conn.close()

        if not student:
            return jsonify({'success':False,'message':'Email not found!'}), 404

        stored_pw = student['password']
        if isinstance(stored_pw, str):
            stored_pw = stored_pw.encode('utf-8')

        if not bcrypt.checkpw(password.encode('utf-8'), stored_pw):
            return jsonify({'success':False,'message':'Wrong password!'}), 401

        token = create_access_token(identity=str(student['id']))
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'token': token,
            'student': {
                'id': student['id'],
                'name': student['name'],
                'email': student['email'],
                'department': student['department'],
                'semester': student['semester']
            }
        })

    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── GET TASKS ──
@app.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        student_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE student_id=%s ORDER BY created_at DESC", (student_id,))
        tasks = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify({'success':True,'tasks':tasks})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── ADD TASK ──
@app.route('/api/tasks', methods=['POST'])
@jwt_required()
def add_task():
    try:
        student_id = get_jwt_identity()
        data  = request.get_json()
        title = data.get('title','').strip()
        topic = data.get('topic','General')

        if not title:
            return jsonify({'success':False,'message':'Task title required!'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("INSERT INTO tasks (student_id,title,topic) VALUES (%s,%s,%s)",
                       (student_id, title, topic))
        conn.commit()
        task_id = cursor.lastrowid
        cursor.close(); conn.close()
        return jsonify({'success':True,'message':'Task added!','task_id':task_id}), 201

    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── UPDATE TASK ──
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        data = request.get_json()
        completed = data.get('completed', False)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed=%s WHERE id=%s", (completed, task_id))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({'success':True,'message':'Task updated!'})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── DELETE TASK ──
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({'success':True,'message':'Task deleted!'})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── SAVE TEST SCORE ──
@app.route('/api/scores', methods=['POST'])
@jwt_required()
def save_score():
    try:
        student_id = get_jwt_identity()
        data  = request.get_json()
        topic = data.get('topic')
        level = data.get('level','quick')
        score = data.get('score')
        total = data.get('total',10)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_scores (student_id,topic,level,score,total)
            VALUES (%s,%s,%s,%s,%s)
        """, (student_id, topic, level, score, total))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({'success':True,'message':'Score saved!'})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── GET SCORES ──
@app.route('/api/scores', methods=['GET'])
@jwt_required()
def get_scores():
    try:
        student_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT topic, level, MAX(score) as best_score, COUNT(*) as attempts
            FROM test_scores WHERE student_id=%s GROUP BY topic, level
        """, (student_id,))
        scores = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify({'success':True,'scores':scores})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── ADMIN — ALL STUDENTS ──
@app.route('/api/admin/students', methods=['GET'])
def get_all_students():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.name, s.email, s.department, s.semester, s.roll_no,
                   s.created_at,
                   COUNT(DISTINCT t.id) as total_tasks,
                   SUM(CASE WHEN t.completed=1 THEN 1 ELSE 0 END) as completed_tasks,
                   COUNT(DISTINCT ts.id) as tests_taken
            FROM students s
            LEFT JOIN tasks t ON s.id=t.student_id
            LEFT JOIN test_scores ts ON s.id=ts.student_id
            GROUP BY s.id ORDER BY s.created_at DESC
        """)
        students = cursor.fetchall()
        for s in students:
            if s.get('created_at'):
                s['created_at'] = str(s['created_at'])
        cursor.close(); conn.close()
        return jsonify({'success':True,'students':students,'total':len(students)})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)}), 500

# ── START SERVER ──
if __name__ == '__main__':
    print("🚀 PEC Placement Portal Starting...")
    app.run(debug=False, host='0.0.0.0', port=5000)
