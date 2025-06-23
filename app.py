from flask import Flask, render_template, redirect, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()


with open('config.json', 'r') as config_file:
    params = json.load(config_file)["params"]

app = Flask(__name__)
app.secret_key = "feedback_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/feedback_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'manager' or 'employee'
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationship to get employees under a manager
    employees = db.relationship('User', backref=db.backref('manager', remote_side=[id]), lazy='dynamic')

    # Feedback relationships
    given_feedbacks = db.relationship('Feedback', backref='manager', foreign_keys='Feedback.manager_id', lazy='dynamic')
    received_feedbacks = db.relationship('Feedback', backref='employee', foreign_keys='Feedback.employee_id', lazy='dynamic')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strengths = db.Column(db.Text, nullable=False)
    improvements = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    acknowledged = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


class Test(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(40))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        manager_id = request.form.get('manager_id') if role == 'employee' else None

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'warning')
            return redirect('/signup')

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password, role=role, manager_id=manager_id)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful. Please log in.', 'success')
        return redirect('/login')
    managers = User.query.filter_by(role='manager').all()
    return render_template('signup.html', managers=managers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful', 'info')
            return redirect('/manager_dashboard' if user.role == 'manager' else '/employee_dashboard')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/feedback', methods=['GET'])
@login_required
def feedback_form():
    # Assuming only managers are allowed
    if current_user.role != 'manager':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    # Load team members for dropdown
    employees = User.query.filter_by(manager_id=current_user.id).all()
    return render_template('feedback_form.html', employees=employees)

from collections import Counter, defaultdict

@app.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if current_user.role != 'manager':
        flash('Access denied', 'danger')
        return redirect('/')

    team = User.query.filter_by(manager_id=current_user.id).all()
    feedbacks = Feedback.query.filter_by(manager_id=current_user.id).all()

    # Count sentiment summary
    sentiment_counts = Counter([fb.sentiment for fb in feedbacks])
    sentiment_summary = {
        'positive': sentiment_counts.get('positive', 0),
        'neutral': sentiment_counts.get('neutral', 0),
        'negative': sentiment_counts.get('negative', 0)
    }

    # Count feedback per employee
    employee_feedback_counts = defaultdict(int)
    for fb in feedbacks:
        employee_feedback_counts[fb.employee_id] += 1

    # Map employee info with count
    feedback_count_summary = []
    for employee in team:
        feedback_count_summary.append({
            'id': employee.id,
            'username': employee.username,
            'count': employee_feedback_counts.get(employee.id, 0)
        })

    return render_template(
        'dashboard_manager.html',
        team=team,
        feedbacks=feedbacks,
        employees=team,
        sentiment_summary=sentiment_summary,
        feedback_count_summary=feedback_count_summary
    )

@app.route('/give_feedback', methods=['POST'])
@login_required
def give_feedback():
    if current_user.role != 'manager':
        flash('Access denied', 'danger')
        return redirect('/')

    employee_id = request.form['employee_id']
    strengths = request.form['strengths']
    improvements = request.form['improvements']
    sentiment = request.form['sentiment']

    feedback = Feedback(
        manager_id=current_user.id,
        employee_id=employee_id,
        strengths=strengths,
        improvements=improvements,
        sentiment=sentiment
    )
    db.session.add(feedback)
    db.session.commit()
    flash('Feedback submitted successfully!', 'success')
    
    # ✅ Redirect back to dashboard (where all variables are loaded correctly)
    return redirect(url_for('manager_dashboard'))

@app.route('/employee_dashboard')
@login_required
def employee_dashboard():
    if current_user.role != 'employee':
        flash('Access denied', 'danger')
        return redirect('/')
    feedbacks = Feedback.query.filter_by(employee_id=current_user.id).order_by(Feedback.timestamp.desc()).all()
    return render_template('dashboard_employee.html', feedbacks=feedbacks)

@app.route('/acknowledge/<int:id>')
@login_required
def acknowledge_feedback(id):
    feedback = Feedback.query.filter_by(id=id, employee_id=current_user.id).first()
    if feedback:
        feedback.acknowledged = True
        db.session.commit()
        flash('Feedback acknowledged.', 'success')
    return redirect('/employee_dashboard')

@app.route('/edit_feedback/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_feedback(id):
    feedback = Feedback.query.filter_by(id=id, manager_id=current_user.id).first()
    if not feedback:
        flash('Not found or unauthorized.', 'danger')
        return redirect('/')
    if request.method == 'POST':
        feedback.strengths = request.form['strengths']
        feedback.improvements = request.form['improvements']
        feedback.sentiment = request.form['sentiment']
        db.session.commit()
        flash('Feedback updated.', 'success')
        return redirect('/manager_dashboard')
    return render_template('edit_feedback.html', feedback=feedback)

@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return 'My database is connected'
    except Exception as e:
        print(e)
        return 'My database is not connected'

if __name__ == '__main__':
    app.run(debug=True)
