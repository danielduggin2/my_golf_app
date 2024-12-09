from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
app = Flask(__name__, template_folder='templates')

def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Render the about page if user is not logged in
@app.route('/')
def about():
    if current_user.is_authenticated:
        return redirect(url_for('serve_frontend'))
    else:
        return render_template('about.html')

# Route to render the index.html file
@app.route('/home')
@login_required
def serve_frontend():
    return render_template('about.html', user=current_user)

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id))
        user = cursor.fetchone()
        conn.close()

        if user:
            return User(user[0], user[1], user[2], user[3])
        return None

# Sign up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Hash the password
        password_hash = generate_password_hash(password)
        # Check if the user already exists
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username or email already exists')
            return redirect(url_for('signup'))
        # Insert the new user into the database
        cursor.execute('''
            INSERT INTO Users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        conn.commit()
        conn.close()
        flash('Signup successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Find the user by username
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if not user or not check_password_hash(user[3], password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # Create the user object and log them in
        user_obj = User(user[0], user[1], user[2], user[3])
        login_user(user_obj)
        return redirect(url_for('index'))
    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))
    
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)


# this will return the courses from our db
@app.route('/get_courses')
def get_courses():
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row # Ensures rows are returned as dictionaries
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Course")
        rows = cursor.fetchall()
        conn.close()

        # Convert rows to a list of dictionaries
        courses = []
        for row in rows:
            courses.append(dict(row))

        return jsonify({'courses': courses})

    except Exception as e:
        # If an error occurs, return an error message
        return jsonify({'error': str(e)})

# Add Course - POST route to add a new course
@app.route('/add_courses', methods=['POST'])
def add_course():
    try:
        course_data = request.get_json()

        # Extract fields from the data (e.g. name or locations)
        name = course_data.get('name')
        address = course_data.get('address')
        phone = course_data.get('phone')  
        holes = course_data.get('holes') 
        par_course = course_data.get('par_course') 
        par_front_nine = course_data.get('par_front_nine')  
        par_back_nine = course_data.get('par_back_nine')  

        # Validate that required fields are provided
        if not name or not holes or not par_course:
            return jsonify({'error': 'Name, holes, par_course are required'}), 400
        
        #Connect to the db
        conn = connect_db()
        # Create a cursor object to interact with the database
        # Explanation:
        # A cursor is an object that allows you to execute SQL queries and fetch results.
        # When you open a cursor, you can execute SQL commands (INSERT, SELECT, UPDATE, DELETE, etc.)
        # and retrieve data (for SELECT queries). It essentially acts as a middleman between
        # your Python application and the database.
        cursor = conn.cursor()

        # Insert the course into the database
        cursor.execute(cursor.execute('''
            INSERT INTO Course (name, address, phone, holes, par_course, par_front_nine, par_back_nine)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, holes, par_course, par_front_nine, par_back_nine)))

        #commit the transaction
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({'message': 'Course added successfully'}), 201
    
    except Exception as e:
        # Handle the errors and return a response
        return jsonify({'error': str(e)}), 500
    
# Add tee info from Tee_Info Table
@app.route('/tee_info', methods=['POST'])
def add_tee_info():
    try:
        tee_data = request.get_json()

        # Extract fields from the data
        course_id = tee_data.get('course_id')  # fill in the blank: 'course_id'
        tee_color = tee_data.get('tee_color')  # fill in the blank: 'tee_color'
        out_yardage = tee_data.get('out_yardage')  # fill in the blank: 'out_yardage'
        in_yardage = tee_data.get('in_yardage')  # fill in the blank: 'in_yardage'
        total_yardage = tee_data.get('total_yardage')  # fill in the blank: 'total_yardage'

         # Validate that required fields are provided
        if not course_id or not tee_color:
            return jsonify({'error': 'Course ID and tee color are required'}), 400

        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Check if the course_id exists in the Course table
        cursor.execute('SELECT id FROM Course WHERE id = ?', (course_id,))
        course = cursor.fetchone()
        if not course:
            return jsonify({'error': 'Invalid course ID'}), 400

        # Insert the tee info into the Tee_Info table
        cursor.execute('''
            INSERT INTO Tee_Info (course_id, tee_color, out_yardage, in_yardage, total_yardage)
            VALUES (?, ?, ?, ?, ?)
        ''', (course_id, tee_color, out_yardage, in_yardage, total_yardage))

        # Commit the transaction
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({'message': 'Tee info added successfully'}), 201

    except Exception as e:
        # Handle errors and return a response
        return jsonify({'error': str(e)}), 500

# Add hole info from Hole_Info Table
@app.route('/hole_info', methods=['POST'])
def add_hole_data():
    try:
        # Get hole data from the request
        hole_data = request.get_json()

        # Extract fields from the data
        course_id = hole_data.get('course_id')  # fill in the blank: 'course_id'
        hole_number = hole_data.get('hole_number')  # fill in the blank: 'hole_number'
        par = hole_data.get('par')  # fill in the blank: 'par'
        handicap = hole_data.get('handicap')  # fill in the blank: 'handicap'
        tee_color = hole_data.get('tee_color')  # fill in the blank: 'tee_color'
        yardage = hole_data.get('yardage')  # fill in the blank: 'yardage'

        # Validate that required fields are provided
        if not course_id or not hole_number or not par or not handicap or not tee_color or not yardage:
            return jsonify({'error': 'All fields are required'}), 400

        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Check if the course_id exists in the Course table
        cursor.execute('SELECT id FROM Course WHERE id = ?', (course_id,))
        course = cursor.fetchone()
        if not course:
            return jsonify({'error': 'Invalid course ID'}), 400

        # Insert the hole data into the Hole_Data table
        cursor.execute('''
            INSERT INTO Hole_Data (course_id, hole_number, par, handicap, tee_color, yardage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (course_id, hole_number, par, handicap, tee_color, yardage))

        # Commit the transaction
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({'message': 'Hole data added successfully'}), 201

    except Exception as e:
        # Handle errors and return a response
        return jsonify({'error': str(e)}), 500


# Update Course
@app.route('/courses/<int:id>', methods=['PUT'])
def update_course(id):
    try:
        # Get updated course data from the request
        updated_data = request.get_json()

        # Extract fields from the data
        name = updated_data.get('name')  # fill in the blank: 'name'
        address = updated_data.get('address')  # fill in the blank: 'address'
        phone = updated_data.get('phone')  # fill in the blank: 'phone'
        holes = updated_data.get('holes')  # fill in the blank: 'holes'
        par_course = updated_data.get('par_course')  # fill in the blank: 'par_course'
        par_front_nine = updated_data.get('par_front_nine')  # fill in the blank: 'par_front_nine'
        par_back_nine = updated_data.get('par_back_nine')  # fill in the blank: 'par_back_nine'

        # Validate that required fields are provided (at least name, holes, and par_course should be updated)
        if not name or not holes or not par_course:
            return jsonify({'error': 'Name, holes, and par_course are required'}), 400

        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Update the course in the database where the id matches
        cursor.execute('''
            UPDATE Course
            SET name = ?, address = ?, phone = ?, holes = ?, par_course = ?, par_front_nine = ?, par_back_nine = ?
            WHERE id = ?
        ''', (name, address, phone, holes, par_course, par_front_nine, par_back_nine, id))

        # Commit the transaction
        conn.commit()
        conn.close()

        # Check if any rows were updated
        if cursor.rowcount == 0:
            return jsonify({'error': 'Course not found'}), 404

        # Return success response
        return jsonify({'message': 'Course updated successfully'}), 200

    except Exception as e:
        # Handle errors and return a response
        return jsonify({'error': str(e)}), 500


# Delete Course
@app.route('/courses/<int:id>', methods=['DELETE'])
def delete_course(id):
    try:
        # Connect to the database
        conn = connect_db()
        cursor = conn.cursor()

        # Delete the course from the database where the id matches
        cursor.execute('DELETE FROM Course WHERE id = ?')  # fill in the blank: 'id'

        # Commit the transaction
        conn.commit()
        conn.close()

        # Check if any rows were deleted
        if cursor.rowcount == 0:
            return jsonify({'error': 'Course not found'}), 404

        # Return success response
        return jsonify({'message': 'Course deleted successfully'}), 200

    except Exception as e:
        # Handle errors and return a response
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 