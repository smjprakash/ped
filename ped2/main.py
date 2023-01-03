from email import message
from http import client
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail
import MySQLdb.cursors
import re
from twilio.rest import Client
import random


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'pededu'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kgisl'
app.config['MYSQL_DB'] = 'ped'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'moses.jp@kgkite.ac.in'
app.config['MAIL_PASSWORD'] = 'Amyprakash@8'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
	return render_template('index.html')

'''@app.route('/staff', methods=['GET', 'POST'])
def staff():
    return render_template('staff_login.html')'''

@app.route('/staff', methods =['GET', 'POST'])
def staff():
    msg =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username,password FROM users WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('staff_dashboard.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('staff_login.html', msg=msg)

@app.route('/forgotpwd', methods =['GET', 'POST'])
def forgotpwd():
    msg = ''
    if request.method == 'POST' and 'emailid' in request.form:
        emailid = request.form['emailid']
		#password = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username, password FROM users WHERE emailid = % s ', (emailid,))
        account = cursor.fetchone()
        if account:
            msg = 'link to reset password had been sent to your registerd mail'

            return  render_template('credentials.html',msg = msg,account=account)
        else:
            msg = 'Invalid emailid !'
    return render_template('forgotpwd.html', msg = msg)

@app.route('/student', methods=['GET', 'POST'])
def student():
    msg =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username,password FROM users WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            msg = username
            return render_template('student_dashboard.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('student_login.html', msg=msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'emailid' in request.form and 'department' in request.form and 'section' in request.form and 'gender' in request.form and 'mobn1' in request.form and 'whatsappnum' in request.form and 'parentnum' in request.form and 'batch' in request.form and 'amode' in request.form and 'smode' in request.form and 'prefered_game' in request.form:
        rollnumber = request.form['rollnumber']
        username = request.form['username']
        email = request.form['emailid']
        dept = request.form['department']
        section = request.form['section']
        gender = request.form['gender']
        mobn1 = request.form['mobn1']
        whatsappnum  = request.form['whatsappnum']
        parent_num = request.form['parentnum']
        batch = request.form['batch']
        admission= request.form['amode']
        stay = request.form['smode']
        prefered_game = request.form['prefered_game']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username))
        account = cursor.fetchone()
        #If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not rollnumber or not username or  not email or not dept or not section or not gender or not mobn1 or not whatsappnum or not parent_num or not batch or not admission or not stay or not prefered_game:
            msg = 'Please fill out the form!'
        elif request.method == 'POST':
        # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
    # Show registration form with message (if any)
        else: 
            cursor.execute('INSERT INTO student_profile  VALUES (%s, %s ,%s ,%s, %s, %s, %d, %d, %d, %d, %s,%s, %s)', (rollnumber, username,email,dept,section,gender,mobn1,whatsappnum,parent_num,batch,admission,stay,prefered_game))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    # return render_template('register.html', msg = msg)    
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/enterotp', methods =["GET", "POST"])
def sendotp():
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        mobn1 = request.form['mobn1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            mobn1 = request.form('mobn1')
            getotpapi(mobn1)
    return render_template('enter_otp.html')
      
def generateotp():
    return random.randrange(1000,9999)

def getotpapi(mobn1):
    account_sid = 'AC18e9321cf24563c35c67d5683cd98680'
    auth_token = '0c3ecdc82bdd1ab1e1f47e740ebcb7a6'
    client = Client(account_sid, auth_token)
    otp = generateotp()
    body = ' your otp is ' + str(otp)
    session['response'] = str(otp)
    message = client.messages.create(
                                from_= '+15738792307',
                                body = body,
                                to = mobn1
       )
    if message.sid:
        return True
    else:
        False


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/staff_dashboard')
def staff_dashboard():
    data = ''
    rows = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from practice_schedule where date_of_practice=date_format(curdate(),'%d-%m-%Y');") 
    data = cursor.fetchall()
    cursor.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from items_issue where date_of_issue=date_format(curdate(),'%d-%m-%Y');") 
    rows = cursor.fetchall()
    cursor.close()
    return render_template('staff_dashboard.html',data=data,value=rows )



@app.route('/players')
def players():
    return render_template('players.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/student_onduty')
def student_onduty():
    data = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM student_onduty;") 
    data = cursor.fetchall()
    msg='Schedule successfuly created'
    cursor.close()
    return render_template('student_onduty.html',data=data, mgs=msg)


    

@app.route('/issue_register' ,methods =["GET", "POST"])
def issue_register():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        issued_by = request.form['issued_by']
        dateissue = request.form['dateissue']
        received_by = request.form['received_by']
        datereturned = request.form['datereturned']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('insert into items_issue(item_name,quantity,issued_by,date_of_issue,received_by,return_date ) values (%s, %s, %s, %s, %s, %s)',(item_name, quantity, issued_by, dateissue, received_by, datereturned))
        mysql.connection.commit()
        cursor.close()
        return render_template('staff_dashboard.html')
    return render_template('issue_register.html')
    
@app.route('/issue_details;')
def issue_details():
    rows = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM items_issue;") 
    rows = cursor.fetchall()
    cursor.close()
    return render_template("issue_details.html", rows=rows)
      

@app.route('/practice')
def practice():
    data = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM practice_schedule;") 
    data = cursor.fetchall()
    msg='Schedule successfuly created'
    cursor.close()
    return render_template("practice_schedule.html", data=data, msg=msg)
    
   
@app.route('/newschedule', methods=['GET' , 'POST'])
def newschedule():
    msg=''
    
    if request.method == 'POST':
        dp = request.form['dp']
        team_name = request.form['team_name']
        gender = request.form['gender']
        college_name = request.form['college_name']
        coach = request.form['coach']
        start_time = request.form['st']
        end_time = request.form['et']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('insert into practice_schedule values (%s, %s, %s, %s, %s, %s, %s)',(dp, team_name, gender, college_name, coach, start_time, end_time))
        mysql.connection.commit()
        cursor.close()
        msg='schedule created'
        return render_template('staff_dashboard.html',msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('new_schedule.html',msg=msg)
        
        


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('index'))


