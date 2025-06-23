# DPDzero-assignment

## Feedback Management System

A web-based feedback management system where managers can provide feedback to employees. Employees can view and acknowledge the feedback. The application includes sentiment analysis summaries and role-based dashboards.


## 🧪 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yashasp25/DPDzero-assignment.git
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Set up MySQL using XAMPP, Create a database named feedback_system and In SQL enter these commands
```bash
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manager_id INT NOT NULL,
    employee_id INT NOT NULL,
    strengths TEXT NOT NULL,
    improvements TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id),
    FOREIGN KEY (employee_id) REFERENCES users(id)
);
CREATE TABLE test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40)
);
```
### 4. Run the Application
```bash
python app.py
```
Visit http://127.0.0.1:5000 in your browser to run the application.


### 5. Test database connectivity
Visit http://127.0.0.1:5000/test in your browser.


## 🔧 Stack Used

- **Backend**: Flask, Flask-Login, SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, Jinja2 templates
- **Database**: MySQL (via XAMPP), pymysql
- **Other Tools**: Docker (optional), VS Code

