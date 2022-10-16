import mysql.connector
from flask import *
import logging
import os
from werkzeug.utils import secure_filename
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static\images'
app.secret_key = 'afhbastkhoskhonstr'
db=mysql.connector.connect(host="localhost",user="root",password="1234",)
c=db.cursor()
db.autocommit=True
c.execute("CREATE DATABASE IF NOT EXISTS xcodebhs;")
c.execute("use xcodebhs;")
c.execute("""create table if not exists users (username varchar(15) primary key,password varchar(15) not null,usertype enum("patient","doctor"));""")
c.execute("create table if not exists userdata (username varchar(15) primary key,name varchar(50),address varchar(300),phone_no varchar(10),email_id varchar(50),foreign key (username) references users(username) on delete cascade);")
c.execute("create table if not exists items (itemid int primary key auto_increment,name varchar(30),imgid varchar(100),description varchar(300),price int,qty int);")
c.execute("create table if not exists orders (patient_username varchar(15) not null,billno int primary key auto_increment)")
c.execute("drop table if exists cart")
c.execute("create table cart (itemid int,name varchar(30),imgid varchar(100),description varchar(300),price int,qty int,max_qty int);")
c.execute("create table if not exists appointments (username varchar(50),doc_name varchar(50),symptoms varchar (500),imgid varchar(100))")



@app.route('/')
@app.route('/home',methods=['POST','GET'])
def home():
    msg1=""
    c.execute('select username from userdata')
    usernames=[]
    for i in c.fetchall():
        usernames.append(i[0])
    if 'loggedin' in session:
        if session['usertype']=="doctor":
            c.execute('select * from appointments;')
            b=[]
            for i in c.fetchmany(5):
                user=i[0]
                symptoms=i[2]
                img=i[3]
                c.execute(f'select * from userdata where username="{user}"')
                a=c.fetchone()
                name=a[1]
                phone=a[3]
                email=a[4]
                b.append([name,phone,email,symptoms,img])
            return render_template('home_doctor.html',msg1=msg1,appointments=b)
        elif session['usertype']=="patient":
            if request.method=="POST":
                if request.form['submit']=="appointments":
                    user=session['username']
                    img = request.files['img']
                    img_filename = secure_filename(img.filename)
                    img.save(os.path.join(os.path.join(app.root_path,app.config['UPLOAD_FOLDER']), img_filename))
                    symptoms=request.form['symptoms']
                    doctor=request.form['doctor']
                    app.logger.info("Yes!")
                    c.execute(f'insert into appointments values ("{user}","{doctor}","{symptoms}","{img_filename}")')
            c.execute('select username from users where usertype="doctor"')
            drnames=[]
            for i in c.fetchall():
                drnames.append(i[0])
            return render_template('home_patient.html',msg1=msg1,drnames=drnames)
    if request.method=='POST':
        if request.form['submit']=="Register":
            user=request.form['username']
            pwd=request.form['password']
            usertype=request.form['type']
            name=request.form['name']
            add=request.form['address']
            phone=request.form['phone']
            email=request.form['email']
            app.logger.info(user)
            if user in usernames:
                msg1="Username Taken"
                render_template('home.html',msg1=msg1)
            else:
                c.execute(f"insert into users values('{user}','{pwd}','{usertype}')")
                c.execute(f"insert into userdata values('{user}','{name}','{add}','{phone}','{email}')")
                msg1='Account Created! Please Login to your account now.'
                render_template('home.html',msg1=msg1)
        if request.form['submit']=="Login":
            username=request.form['username']
            password=request.form['password']
            c.execute(f'select * from users where username = "{username}" and password = "{password}"')
            account=c.fetchone()
            if account:
                session['loggedin']=True
                session['username']=account[0]
                session['usertype']=account[2]
                msg1='Logged in successfully !'
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username / password!'
                return render_template('home.html',msg1=msg)
    return render_template('home.html',msg1=msg1)
    
@app.route('/logout',methods=['POST','GET'])
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('usertype', None)
    return redirect(url_for('home'))

@app.route('/index',methods=['POST','GET'])
def index():
    if 'usertype' in session:
        if session['usertype']=="patient":
            msg=""
            items=[]
            session['itemno']=0
            next,prev="",""
            m=0
            if request.method=='POST':
                if "ad" in request.form:
                    session['itemno']=0
                    b=request.form.to_dict()
                    ad=b["ad"]
                    np=b["np"]
                    min=b["min"]
                    max=b["max"]
                    m=1
                    a=browse_filter(np,ad,min,max)
                elif "nextprev" in request.form:
                    a=browse()
                    if request.form["nextprev"]=="next":
                        if (len(a)-session['itemno'])>20:
                            session['itemno']+=20
                    elif request.form["nextprev"]=="prev":
                        if (session['itemno']-len(a))>20:
                            session['itemno']-=20
                elif "search" in request.form:
                    a=search(request.form['search'])
                    m=1
                else:
                    b=request.form.to_dict()
                    app.logger.info(b)
                    c.execute("select itemid from cart")
                    z=c.fetchall()
                    for i in range(len(z)):
                        z[i]=str(z[i][0])
                    for i in b:
                        if i not in z:
                            c.execute(f"insert into cart (itemid,name,imgid,description,price,max_qty) select itemid,name,imgid,description,price,qty from items where itemid={i}")
                            c.execute(f"update cart set qty={b[i]} where itemid={i};")
                        else:
                            c.execute(f"update cart set qty=qty+{b[i]} where itemid={i};")
            if m==0:
                a=browse()
            if not (len(a)-session['itemno'])>20:
                next=" disabled"
            if not (session['itemno']-len(a))>0:
                prev=" disabled"
            if (len(a)-session['itemno'])>20:
                for i in range(session['itemno'],session['itemno']+20):
                    items.append(a[i])
            else:
                for i in range(session['itemno'],len(a)):
                    items.append((a[i]))
            if len(items)==0:
                msg="No Items Found"
            c.execute("select min(price),max(price) from items")
            r=c.fetchone()
            app.logger.info(items)
            return render_template('index_buyer.html',items=items, user=session['username'],msg=msg,min=r[0],max=r[1],next=next,prev=prev)
    else:
        items=[]
        return render_template('login.html')
@app.route('/cart',methods=['POST','GET'])
def cart():
    msg=""
    if session['usertype']=="patient":
        items=[]
        session['itemno']=0
        c.execute("select * from cart")
        a=c.fetchall()
        next,prev="",""
        if request.method=="POST":
            if 'remove' in request.form:
                itemid=request.form['remove']
                c.execute(f'delete from cart where itemid={itemid}')
                return redirect(url_for('cart'))
            elif 'update' in request.form:
                itemid=request.form['update']
                qty=request.form['qty']
                c.execute(f'update cart set qty={qty} where itemid={itemid}')
                return redirect(url_for('cart'))
            elif 'order' in request.form:
                order()
                return redirect(url_for('cart'))   
            elif "nextprev" in request.form:
                c.execute("select * from cart")
                a=c.fetchall()
                if request.form["nextprev"]=="next":
                    if (len(a)-session['itemno'])>20:
                        session['itemno']+=20
                elif request.form["nextprev"]=="prev":
                    if (session['itemno']-len(a))>20:
                        session['itemno']-=20
        if not (len(a)-session['itemno'])>20:
            next=" disabled"
        if not (session['itemno']-len(a))>20:
            prev=" disabled"
        items=[]
        if (len(a)-session['itemno'])>20:
            for i in range(session['itemno'],session['itemno']+20):
                items.append(a[i])
        else:
            for i in range(session['itemno'],len(a)):
                items.append((a[i]))
        if len(items)==0:
            msg="No Items in Cart."
        return render_template('cart.html',items=items,msg=msg)
################ add orders page and make cart ui better, add total value, change order button position ###############
    else:
        items=[]
        return render_template('index_login.html',items=items, user=session['username'])

def browse():
    c.execute("drop table if exists browse")
    c.execute("create table browse as select * from items")
    c.execute("select * from browse")
    r=c.fetchall()
    return r
def search(key):
    browse()
    c.execute("drop table if exists browse1")
    c.execute(f"create table browse1 as select * from browse where name like '%{key}%'")
    c.execute("select * from browse1")
    r=c.fetchall()
    c.execute("drop table browse")
    c.execute("create table browse as select * from browse1")
    c.execute("drop table browse1")
    return r
def browse_filter(np,ad,min,max):
    c.execute("drop table if exists browse1")
    c.execute(f"create table browse1 as select itemid,name,imgid,description,price,qty from browse where price>={min} and price<={max} order by {np} {ad}")
    c.execute("select * from browse1")
    r=c.fetchall()
    return r

def add():
    name=input("Insert Item Name: ")
    price=int(input("Insert Item Price: "))
    qty=int(input("Insert Quantity of Items: "))
    imgid="a"
    description="b"
    c.execute(f"insert into items values({id},'{name}','{imgid}','{description}',{price},{qty})")
    db.commit()
def lists(u):
    c.execute(f"select * from msgs where doctor_username='{u}'")
    return c.fetchall()


def order():
    c.execute("select billno from orders")
    a=c.fetchall()
    orderno='o'+str(len(a)+1)
    c.execute(f"insert into orders values ('{session['username']}',{len(a)+1})")
    c.execute(f"create table {orderno} as select * from cart")
    c.execute(f"select * from {orderno}")
    for i in c.fetchall():
        c.execute(f"update items set qty=qty-{i[5]} where itemid={i[0]};")
    c.execute("truncate table cart")


if __name__ == '__main__':
   app.run(debug=True)
