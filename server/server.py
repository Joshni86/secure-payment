from flask import Flask, request,jsonify
import re
import os
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask_cors import CORS
import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask_jwt_extended import JWTManager,create_access_token, set_access_cookies,jwt_required,get_jwt_identity
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
ph=PasswordHasher()
load_dotenv()
app=Flask(__name__)
app.config['JWT_SECRET_KEY']=os.getenv("SECRET")
app.config.update({
    "JWT_TOKEN_LOCATION": ["cookies"],
    "JWT_COOKIE_SECURE": False,      
    "JWT_COOKIE_SAMESITE": "Lax",    
    "JWT_COOKIE_CSRF_PROTECT": False
})
jwt = JWTManager(app)
limiter=Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per day","10 per hour"]
)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
logging.basicConfig(
    filename="security.log",
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s |%(message)s"

)

def log_security_event(event_type, user_identifier=None, details=None):
    parts = [f"event={event_type}"]
    if user_identifier:
        parts.append(f"user={user_identifier}")
    if details:
        parts.append(f"details={details}")
    logging.warning(" | ".join(parts))

def connection():
    conn=sqlite3.connect("payment.sqlite",check_same_thread=False)
    return conn

@app.errorhandler(RateLimitExceeded)
def handle_rate(e):
    log_security_event(
        event_type="RATE_LIMITED_LOGIN",
        details="Login rate limit exceeded"
    )
    return jsonify({"error":"login rate exceeded"}),429
@app.route("/register",methods=["POST"])
def register():
    try:
        if request.method=="POST":
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"error": "No data provided"}), 400
            email=data.get('email','')
            if check_user_exists(email):
                return jsonify({"error": "User already exists - please login"}), 400
            pwd=data.get('password','')
            if not password_checker(pwd):
                return jsonify({"message":"Password must contain atleast 8 characters, a captial letter, a number and a special symbol"}),400
            hash_pwd=ph.hash(pwd)
            conn=connection()
            cursor=conn.cursor()
            email=email.lower()
            insert_query="""INSERT INTO Users(email, password) VALUES(?,?)"""
            cursor.execute(insert_query,(email,hash_pwd))
            conn.commit()
            conn.close()
            access_token=create_access_token(identity=email)
            response = jsonify({"message": "Registration successful"})
            set_access_cookies(response, access_token)
            return response, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        if request.method=="POST":
            data = request.get_json(silent=True)
            conn=connection()
            cursor=conn.cursor()
            if data is None:
                return jsonify({"error": "No data provided"}), 400
            email=data.get("email",'').lower()
            if not check_user_exists(email):
                return jsonify({"error":"User does not exist, please register"}),400
            pwd=data.get("password",'')
            cursor.execute("SELECT password FROM Users where email=?",(email,))
            stored_pwd=cursor.fetchone()
            conn.close()
            try:
                if ph.verify(stored_pwd[0],pwd):
                    access_token=create_access_token(identity=email)
                    response = jsonify({"message":"Authentication successful"})
                    set_access_cookies(response, access_token)
                    return response, 200
            except VerifyMismatchError as e:
                log_security_event(
                    "FAILED LOGIN",
                    user_identifier=email,
                    details="Incorrect password"
                )
                return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500
    
@app.route("/payment",methods=["POST"])
@jwt_required()
def payment():

    conn=connection()
    cursor=conn.cursor()
    data=request.json
    amount=float(data.get("amount",''))
    currency=data.get("currency",'')
    merchant_id=data.get("merchantId",'')
    if amount <= 0:
        conn.close()
        return jsonify({"error": "Invalid amount"}), 400
    email=get_jwt_identity()
    cursor.execute("SELECT id,balance from Users where email=?",(email,))
    user=cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
    id,balance=user
    if merchant_id==id:
        log_security_event(
        "FAILED LOGIN",
        user_identifier=email,
        details="Attempted to pay self"
         )
        conn.close()
        return jsonify({"error":"Cannot pay yourself"}),400
    cursor.execute("SELECT id from Users where id=?",(merchant_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error":"merchant does not exist"}),404
    if amount>balance:
        conn.close()
        return jsonify({"error":"balance inadequate"}),400

    insert_query="""INSERT INTO Transactions(user_id, amount, currency, merchant_id,pay_hash) VALUES (?,?,?,?,?)"""
    raw=f"{amount}|{currency}|{merchant_id}|{datetime.utcnow().isoformat()}"
    pay_hash=hashlib.sha256(raw.encode()).hexdigest()
    cursor.execute(insert_query,(id,amount,currency,merchant_id,pay_hash))
    cursor.execute("UPDATE Users set balance = balance + ? where id=?",(amount,merchant_id))
    cursor.execute("UPDATE Users set balance = balance - ? where id=?",(amount,id))
    conn.commit()
    conn.close()
    return jsonify({"message":"Payment successful"})

@app.route("/transactions",methods=["GET"])
@jwt_required()
def transactions():
    email=get_jwt_identity()
    conn=connection()
    cursor=conn.cursor()
    cursor.execute("SELECT id from Users where email=?",(email,))
    user=cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
    id=user[0]
    get_query="""SELECT amount, currency, merchant_id from Transactions where user_id=?"""
    cursor.execute(get_query,(id,))
    data=[]
    rows=cursor.fetchall()
    for i in rows:
        data.append({"amount":i[0],"currency":i[1],"merchant_id":i[2]})
    conn.close()
    return jsonify(data)

def check_user_exists(email):
    conn=connection()
    cursor=conn.cursor()
    email=email.lower()
    cursor.execute("SELECT * FROM Users where email=?",(email,))
    user=cursor.fetchone()
    conn.close()
    if user is not None:
        return True
    return False
def password_checker(password):
    reg="^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]{8,}$"
    if re.search(reg,password):
        return True
    return False


if __name__=="__main__":
    app.run()