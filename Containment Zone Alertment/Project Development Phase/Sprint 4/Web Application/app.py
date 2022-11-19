from flask import Flask, render_template, request, redirect, url_for,session

import ibm_db
import bcrypt
DATABASE_NAME = "bludb"
HOST_NAME = "3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
PORT_NUMBER = "31498"
USER_ID = "qtl83809"
PASSWORD = "55UvDW1scUf5jZJn"


conn = ibm_db.connect(f"DATABASE={DATABASE_NAME};HOSTNAME={HOST_NAME};PORT={PORT_NUMBER};SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID={USER_ID};PWD={PASSWORD}",'','')

app = Flask(__name__)

app.secret_key="rtyhbcrtr5478790675w4/8tuyg"

@app.route('/')
def index():
  return redirect(url_for('home'))
@app.route('/index', methods=['GET','POST'])
def home():
  if 'name' in session:
    return render_template('index.html',name=session['name']+"'s account")
  else:
    return render_template('index.html')

@app.route("/register",methods=['GET','POST'])
def register():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    cpassword = request.form['cpassword']

    if not email or not name or not password or not cpassword:
      return render_template('register.html',error='Please fill all fields')
    if password != cpassword:
        return render_template('register.html',error='The password is not same')
    else:
        hash=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

    query = "SELECT * FROM USER WHERE EMAIL=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    
    if not isUser:
      insert_sql = "INSERT INTO USER(NAME, EMAIL, PASSWORD) VALUES (?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, hash)
      ibm_db.execute(prep_stmt)
      return render_template('register.html',success="You can login")
    else:
      return render_template('register.html',error='Invalid Credentials')

  return render_template('register.html')

@app.route("/login",methods=['GET','POST'])
def login():

    if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']

      if not email or not password:
        return render_template('login.html',error='Please fill all fields')
      query = "SELECT * FROM USER WHERE email=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,email)
      ibm_db.execute(stmt)
      isUser = ibm_db.fetch_assoc(stmt)
      print(isUser,password)

      if not isUser:
        return render_template('login.html',error='Invalid Credentials1')
      #return render_template('login.html',error=isUser['PASSWORD'])
      isPasswordMatch = bcrypt.checkpw(password.encode('utf-8'),isUser['PASSWORD'].encode('utf-8'))


      if not isPasswordMatch:
        return render_template('login.html',error='Invalid Credentials2')

      session['email'] = isUser['EMAIL']
      session['name'] = isUser['NAME']
      return redirect(url_for('home'))
      #return render_template('/index.html')

    if 'name' in session:
      return render_template('/login.html',name=session['name'])
    return render_template('/login.html',name="")



#Storing latitude and langitude in db
@app.route('/latandlng', methods=['POST','GET'])
def storemark():
  if request.method == 'POST':
    lat = request.form['lati']
    lng = request.form['lang']
    desc = request.form['discript']
    insert_sql = "INSERT INTO LOCATION(LATTITUDE, LONGITUDE, DESCRIPTION) VALUES (?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, lat)
    ibm_db.bind_param(prep_stmt, 2, lng)
    ibm_db.bind_param(prep_stmt, 3, desc)
    ibm_db.execute(prep_stmt)

  return redirect(url_for('AdminMap'))

@app.route('/admin_map')
def AdminMap():
  mark = addMarker()
  return render_template('admin_map.html',name=mark)

def addMarker():
  query = "SELECT * FROM LOCATION;"
  stmt = ibm_db.prepare(conn, query)
  # ibm_db.bind_param(stmt,1,lat)
  # ibm_db.bind_param(stmt,2,lng)
  # ibm_db.bind_param(stmt,3,des)
  ibm_db.execute(stmt)
  isUser = ibm_db.fetch_assoc(stmt)
  data=[]
  while(isUser!=False):
    data.append(isUser)
    isUser = ibm_db.fetch_assoc(stmt)

  return data


@app.route('/user_map')
def UserMap():
  if 'email' not in session:
      return redirect(url_for('login'))
  else:
    mark = addMarker()
    
  return render_template('user_map.html',mark = mark, len = len(mark))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('home'))

addMarker()
if __name__ == "__main__":
    app.run(debug=True)


