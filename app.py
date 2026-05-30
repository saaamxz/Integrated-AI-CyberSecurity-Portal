from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)

# إنشاء قاعدة البيانات لبروجكت الـ SQL تلقائياً
def init_db():
    conn = sqlite3.connect('cyber_security.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT
        )
    ''')
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'SuperSecret123')")
        conn.commit()
    conn.close()

init_db()

# 1. الصفحة الرئيسية (الـ Dashboard اللي بتجمع البروجكتين)
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# ==================== [ الجزء الأول: AI Salary Predictor ] ====================
@app.route('/ai-model', methods=['GET', 'POST'])
def ai_model():
    prediction = None
    exp_value = ""
    rating_value = ""
    
    if request.method == 'POST':
        try:
            exp = float(request.form['experience'])
            rating = float(request.form['rating'])
            exp_value = request.form['experience']
            rating_value = request.form['rating']
            
            # معادلة الموديل
            predicted_salary = 2000 + (exp * 500) + (rating * 300)
            prediction = "{:,.0f}".format(predicted_salary)
        except:
            pass
            
    return render_template('model_form.html', prediction=prediction, exp_value=exp_value, rating_value=rating_value)


# ==================== [ الجزء الثاني: SQL Injection ] ====================
@app.route('/sqli-demo', methods=['GET', 'POST'])
def sqli_demo():
    msg = None
    success = False
    info = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mode = request.form['mode'] 
        
        # الـ Input Validation
        is_valid = bool(re.match("^[a-zA-Z0-9_]*$", username))
        validation_status = "Pass (المدخلات سليمة)" if is_valid else "Fail (تم رصد رموز مشبوهة!)"
        db_info = {"entered_user": username, "entered_pass": password, "validation": validation_status, "mode": mode}
        
        conn = sqlite3.connect('cyber_security.db')
        cursor = conn.cursor()
        
        # الوضع غير الآمن
        if mode == "unsecure":
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            db_info["executed_query"] = query
            try:
                cursor.execute(query)
                user = cursor.fetchone()
                if user:
                    success = True
                    msg = "🔓 تم اختراق النظام وتخطى الحماية بنجاح! (SQL Injection Success)"
                else:
                    msg = "❌ خطأ في اسم المستخدم أو كلمة المرور."
            except Exception as e:
                msg = f"💥 خطأ في قاعدة البيانات: {e}"
                
        # الوضع الآمن
        else:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            db_info["executed_query"] = "SELECT * FROM users WHERE username = ? AND password = ?"
            
            if not is_valid:
                conn.close()
                return render_template('login_form.html', success=False, msg="🛡️ تم حظر المحاولة بالـ Validation قبل وصولها للداتابيز.", info=db_info)
            
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            if user:
                success = True
                msg = "✅ تم تسجيل الدخول بأمان للمستخدم الشرعي."
            else:
                msg = "❌ بيانات الدخول غير صحيحة، والنظام محمي."
                
        conn.close()
        info = db_info
        return render_template('login_form.html', success=success, msg=msg, info=info)
        
    return render_template('login_form.html', msg=msg, success=success, info=info)

if __name__ == '__main__':
    app.run(debug=True, port=5000)