from flask import Flask, render_template, request, redirect,session
import pyttsx3
import speech_recognition as sr
from flask_sqlalchemy import SQLAlchemy
import smtplib
import email
import imaplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import time
import json

with open("config.json",'r') as c:
    params = json.load(c)["params"]

EMAIL_SENDER = params["email_sender"]
PASS = params["password"]
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = params["database"] 
app.config['SECRET_KEY'] = params["secret_key"]

db = SQLAlchemy(app)
class Userdetail(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)

class Sentemail(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(80), nullable=True)

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-20)
    engine.say(text)
    engine.runAndWait()

def speak1(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-20)
    engine.say(text)
    engine.runAndWait()
 
def is_confirm():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
        try:
            said = r.recognize_google(audio)
            return said
        except:
            speak("Didn't get that")
            speak("Speak again")
            speak1("speak")
            continue

def loginpage():
    speak("Enter Your Choice")
    speak("For Signup Say signup")
    speak("for Login Say Login")
    speak1("speak")
    choice = is_confirm()
    choice = choice.split(" ")
    choice = "".join(choice).lower()
    return choice

@app.route("/")
def index1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service Home page")
        count+=1
    return render_template("index.html")

@app.route("/index",methods=["POST","GET"])
def index2():
    if request.method =="POST":
        if len(request.form["choice"])!=0:
            choice = request.form["choice"]
            return redirect(choice)
        id =0
        if id ==0:
            while True:
                choice = loginpage()
                speak(f" your choice is {choice}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option = is_confirm()
                if option =="ok":
                    speak("please click to proceed")
                    return render_template("index.html",choice=choice)
                if option =="no":
                    speak("Welcome to mail service Home page")
                    break
    return render_template("index.html")

@app.route("/login")
def login1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service login page")
        count+=1
    return render_template("login.html")

@app.route("/login" ,methods=["POST","GET"])
def login2():
    if request.method =="POST":
        if len(request.form["username"])!=0:
            username = request.form["username"]
            password = request.form["pass"]
            login = Userdetail.query.filter_by(username=username,password=password).first()
            if login is not None:
                session['loggedin'] =True
                session["username"] = username
                session["password"] = password
                return redirect("mainpage")
            elif  login is None:
                speak("Please Enter valid username/password")
                return render_template("login.html")
        id = 0
        if id ==0:
            speak("Enter Your Username ")
            speak1("speak")
            emailid = is_confirm()
            emailid = emailid.split(" ")
            emailid = "".join(emailid).lower()
            while True:
                speak(f" the username you enter is {emailid}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option1 = is_confirm()
                if option1 =="ok":
                    speak("Enter Your Password ")
                    speak1("speak")
                    pss = is_confirm()
                    pss = pss.split(" ")
                    pss = "".join(pss).lower()
                    speak(f" the password you enter is {pss}")
                    speak("For confirmation say ok or for cancelling say no")
                    speak1("speak")
                    option2 = is_confirm()
                    if option2 =="ok":
                        speak("please click to proceed")
                        return render_template("login.html",emailid=emailid,pss=pss)
                    elif option2 =="no":
                        speak("Welcome to mail service login page")
                        break
                elif option1 =="no":
                    speak("Welcome to mail service login page")
                    break
            return render_template("login.html")
    return render_template("login.html")

@app.route("/signup")
def signup1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service signup page")
        count+=1
    return render_template("signup.html")

@app.route("/signup" ,methods=["POST","GET"])
def signup2():
    if request.method =="POST":
        if len(request.form["user"])!=0:
            username = request.form["user"]
            emails = request.form["email"]
            password = request.form["pass"]
            user = Userdetail.query.filter_by(username=username).all()
            if len(user)>0:
                speak("This username already exist")
                speak(" Please choose different username")
                return render_template("signup.html")
            else:
                details = Userdetail(username=username, email=emails, password=password)
                db.session.add(details)
                db.session.commit()
                speak("You have been signed up successfully")
                return redirect("login")
        id = 0
        if id ==0:
            speak("Enter Your Username ")
            speak1("speak")
            user = is_confirm()
            user = user.split(" ")
            user = "".join(user).lower()
            while True:
                speak(f" the username you enter is {user}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option1 = is_confirm()
                if option1 =="ok":
                    speak("Enter Your Email id ")
                    speak1("speak")
                    emailid = is_confirm() + "@gmail.com"
                    emailid = emailid.split(" ")
                    emailid = "".join(emailid).lower()
                    speak(f" the email id you enter is {emailid}")
                    speak("For confirmation say ok or for cancelling say no")
                    speak1("speak")
                    option2 = is_confirm()
                    if option2 =="ok":
                        speak("Enter Your Password ")
                        speak1("speak")
                        pss = is_confirm()
                        pss = pss.split(" ")
                        pss = "".join(pss).lower()
                        speak(f" the password  you enter is {pss}")
                        speak("For confirmation say ok or for cancelling say no")
                        speak1("speak")
                        option3 = is_confirm()
                        if option3 == "ok":
                            speak("please click to proceed")
                            return render_template("signup.html",emailid=emailid,pss=pss,user=user)
                        elif option3 =="no":
                            speak("Welcome to mail service signup page")
                            break
                    elif option2 =="no":
                        speak("Welcome to mail service signup page")
                        break
                elif option1 =="no":
                    speak("Welcome to mail service signup page")
                    break
            return render_template("signup.html")
    return render_template("signup.html")

@app.route("/mainpage")
def mainpage1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service Mainpage")
        count+=1
    return render_template("mainpage.html")

@app.route("/mainpage",methods=["POST","GET"])
def mainpage2():
    if request.method =="POST":
        if len(request.form["choice"])!=0:
            choices = request.form["choice"]
            if choices =="logout":
                session.pop("loggedin",None)
                session.pop("username",None)
                session.pop("password",None)
                speak("Welcome to mail service Home page")
                return redirect("index")
            else:
                return redirect(choices)
        id =0
        if id ==0:
            speak("Enter Your Choice")
            speak("For ComposeEmail Say Compose")
            speak("for Reademail Say read")
            speak("for reading the send emails say sent")
            speak("For logout say logout")
            speak1("speak")
            while True:
                choice = is_confirm()
                choice = choice.split(" ")
                choice = "".join(choice).lower()
                speak(f" your choice is {choice}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option = is_confirm()
                if option =="ok":
                    speak("please click to proceed")
                    return render_template("index.html",choice=choice)
                if option =="no":
                    speak("Welcome to mail service Mainpage")
                    break
            return render_template("mainpage.html")
    return render_template("mainpage.html")

@app.route("/compose")
def send1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service Compose email page")
        count+=1
    return render_template("send.html")

@app.route("/compose" ,methods=["POST","GET"])
def send2():
    if request.method =="POST":
        if len(request.form["email"])!=0:
            receiveremail = request.form["email"]
            subject = request.form["subject"]
            body = request.form["body"]
            if len(request.form["file"])!=0:
                filenamewithext = request.form["file"]
                filenamewithext = filenamewithext.split(".")
                filename = filenamewithext[0]
                extension = filenamewithext[1]
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']),"Desktop")
                file = desktop + f"\{filename}" + f".{extension}"
                file = file.split("\\")
                file.insert(3,"OneDrive")
                file = "//".join(file)
                details = Sentemail(email=receiveremail, subject=subject, message=body,username=session["username"],date=datetime.now(),filename=filename)
                db.session.add(details)
                db.session.commit()
            else:
                details = Sentemail(email=receiveremail, subject=subject, message=body,username=session["username"],date=datetime.now())
                db.session.add(details)
                db.session.commit()
            msg = MIMEMultipart()
            msg["From"] = EMAIL_SENDER
            msg["To"] = receiveremail
            msg["Subject"] = subject
            msg.attach(MIMEText(body,"plain"))
            if len(request.form["file"])!=0:
                with open(file,"rb") as f:
                    attachment = MIMEApplication(f.read(),_subtype=f"{extension}")
                    attachment.add_header("content-Disposition","attachment",filename=filename)
                    msg.attach(attachment)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.starttls
                smtp.login(EMAIL_SENDER, PASS)
                smtp.send_message(msg)
            speak("Mail has been send successfully")
            return redirect("mainpage")
        id = 0
        if id ==0:
            speak("Enter the Receiptent Email Id ")
            speak1("speak")
            emails = is_confirm()  + "@gmail.com"
            emails = emails.split(" ")
            emails = "".join(emails).lower()
            while True:
                speak(f" the receiptent email you entered is {emails}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option1 = is_confirm()
                if option1 =="ok":
                    speak("Enter the subject of the mail")
                    speak1("speak")
                    subject = is_confirm().lower()
                    speak(f" the subject you entered is {subject}")
                    speak("For confirmation say ok or for cancelling say no")
                    speak1("speak")
                    option2 = is_confirm()
                    if option2 =="ok":
                        speak("Enter the message")
                        speak1("speak")
                        message = is_confirm().lower()
                        speak(f" the message you entered is {message}")
                        speak("For confirmation say ok or for cancelling say no")
                        speak1("speak")
                        option3 = is_confirm()
                        if option3 =="ok":
                            speak("Do you want to attach any file")
                            speak("For confirmation say ok or for cancelling say no")
                            speak1("speak")
                            chance = is_confirm()
                            if chance =="ok":
                                speak("Enter the filename that you want to attach")
                                speak1("speak")
                                files = is_confirm()
                                files = files.split(" ")
                                files = "".join(files).lower()
                                speak(f" the filename you entered is {files}")
                                speak("For confirmation say ok or for cancelling say no")
                                speak1("speak")
                                option4 = is_confirm()
                                if option4 =="ok":
                                    speak("Enter the extension of the file that you want to attach")
                                    speak1("speak")
                                    fileext = is_confirm()
                                    fileext = fileext.split(" ")
                                    fileext = "".join(fileext).lower()
                                    speak(f" the extension of the file you entered is {fileext}")
                                    speak("For confirmation say ok or for cancelling say no")
                                    speak1("speak")
                                    option5 = is_confirm()
                                    if option5 =="ok":
                                        speak("please click to proceed")
                                        return render_template("send.html",emails=emails,subject=subject,message=message,files=files+".",fileext=fileext)
                                    elif option5 =="no":
                                        speak("Welcome to mail service send email page")
                                        break
                                elif option4 =="no":
                                    speak("Welcome to mail service send email page")
                                    break
                            elif chance =="no":
                                return render_template("send.html",emails=emails,subject=subject,message=message)
                        elif option3 =="no":
                            speak("Welcome to mail service send email page")
                            break
                    elif option2 =="no":
                        speak("Welcome to mail service send email page")
                        break
                elif option1 =="no":
                    speak("Welcome to mail service send email page")
                    break
            return render_template("send.html")
        return render_template("send.html")

@app.route("/read")
def read1():
    count = 0 
    if count == 0:
        speak("Welcome to mail service read email page")
        count+=1
    return render_template("read.html")

@app.route("/read" ,methods=["POST","GET"])
def read2():
    if request.method =="POST":
        if len(request.form["email"])!=0:
            emails = request.form["email"]
            password = request.form["pass"]
            imap_server = "imap.gmail.com"
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(emails,password)
            imap.select("Inbox")
            _, msgnums = imap.search(None, "ALL")
            status = False
            for msgnum in msgnums[0].split():
                _, data = imap.fetch(msgnum, "(RFC822)")
                message = email.message_from_bytes(data[0][1])
                speak(f"Message Number: {msgnum}")
                speak(f"From: {message.get('From')}")
                speak(f"To: {message.get('To')}")
                speak(f"Date: {message.get('Date')}")
                speak(f"Subject: {message.get('Subject')}")
            imap.close()
            return redirect("mainpage")
        id =0
        if id ==0:
            speak("Enter the Email Id ")
            speak1("speak")
            emails = is_confirm()  + "@gmail.com"
            emails = emails.split(" ")
            emails = "".join(emails).lower()
            while True:
                speak(f" the email you entered is {emails}")
                speak("For confirmation say ok or for cancelling say no")
                speak1("speak")
                option1 = is_confirm()
                if option1 =="ok":
                    pss = is_confirm()
                    pss = pss.split(" ")
                    pss = "".join(pss).lower()
                    speak(f"the password you entered is {pss}")
                    speak("For confirmation say ok or for cancelling say no")
                    speak1("speak")
                    option2 = is_confirm()
                    if option2 =="ok":
                        speak("please click to proceed")
                        return render_template("read.html",emails=emails,pss=pss)
                    elif option2 =="no":
                        speak("Welcome to mail service read email page")
                        break
                elif option1 =="no":
                    speak("Welcome to mail service read email page")
                    break
            return render_template("read.html")
        return render_template("read.html")
    
@app.route("/sent")
def sent1():
        speak("Welcome to mail service sent email page")
        value1 = Sentemail.query.filter_by(username=session["username"]).all()
        if len(value1)>0:
            receiveremail = []
            subject = []
            message = []
            filename=[]
            for i in range(len(value1)):
                sno = int(str(value1[i])[11:-1])
                data2 =  Sentemail.query.get(sno)
                receiveremail.append(data2.email)
                subject.append(data2.subject)
                message.append(data2.message)
                filename.append(data2.filename)
            num = len(receiveremail)
            return render_template("sent.html",receiveremail=receiveremail,subject=subject,message=message,num=num,filename=filename)
        return render_template("sent.html")

@app.route("/sent",methods=["POST","GET"])
def sent2():
    if request.method=="POST":
        value1 = Sentemail.query.filter_by(username=session["username"]).all()
        if len(value1)>0:
            count = 0
            for index,i in enumerate(range(len(value1))):
                sno = int(str(value1[i])[11:-1])
                data2 =  Sentemail.query.get(sno)
                speak(f"mail number {index+1} ")
                speak(f"Date {data2.date} ")
                speak(f"send to {data2.email}")
                speak(f"subject {data2.subject} ")
                speak(f"message {data2.message} ")
                if len(data2.filename)!=0:
                    speak(f"message {data2.message}")
                time.sleep(1)
                speak1("Do you want to read futher email if ok say yes or no then say no")
                speak1("speak")
                count+=1
                choice = is_confirm()
                if choice =="ok" and count!=len(value1):
                    continue
                elif choice =="no":
                    return redirect("mainpage")
            speak("all the mails has been readed")
            return redirect("mainpage")
        else:
            speak(" No mail in the send box")
            return redirect("mainpage")
    return render_template("sent.html")

app.run(debug=True)