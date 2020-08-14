from flask import Flask, render_template, url_for, request, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from flask_bootstrap import Bootstrap

import os
import pandas as pd 
import pickle
import joblib

app = Flask(__name__)
#Bootstrap(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), unique = True, nullable = False)
	email = db.Column(db.String(120), unique = True, nullable = False)
	password = db.Column(db.String(60), nullable = False)
	feedbacks = db.relationship('Feedback', backref='author', lazy="dynamic")

	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"

class Feedback(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	firstname = db.Column(db.String(20), nullable = False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	areacode = db.Column(db.String(), nullable = False)
	telnum = db.Column(db.String(), nullable = False)
	email = db.Column(db.String(), nullable = False)
	choice = db.Column(db.String())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Feedback('{self.firstname}', '{self.date_posted}')"

@app.route('/', methods = ['GET'])
def home():
	return render_template("index.html")


@app.route('/contact', methods = ['GET', 'POST'])
def contact():
	if request.method == 'POST':
		firstname = request.form['firstname']
		lastname = request.form['lastname']
		areacode = request.form['areacode']
		telnum = request.form['telnum']
		email = request.form['emailid']
		choice = request.form['choice']
		feedback = request.form['feedback']
		return render_template("response.html")
	return render_template("contact.html")

@app.route('/explore', methods = ['GET'])
def explore():
	return render_template("explore.html")

@app.route('/predict', methods = ['GET' ,'POST'])
def predict():
	if request.method == "POST":
		features = request.form.copy()
		features['satisfaction_level'] = int(features['satisfaction_level'])/100
		features['last_evaluation'] = int(features['last_evaluation'])/100

		if features['Work_accident'] == 'No':
			features['Work_accident'] = 0
		else:
			features['Work_accident'] = 1

		if features['promotion_last_5years'] == "No":
			features['promotion_last_5years'] = 0
		else:
			features['promotion_last_5years'] = 1

		features['department_IT'] = 0
		features['department_RandD'] = 0
		features['department_accounting'] = 0
		features['department_hr'] = 0
		features['department_management'] = 0
		features['department_marketing'] = 0
		features['department_product_mng'] = 0
		features['department_sales'] = 0
		features['department_support'] = 0
		features['department_technical'] = 0
		if features['department'] == "IT":
			features['department_IT'] = 1
		elif features['department'] == "RandD":
			features['department_RandD'] = 1
		elif features['department'] == "accounting":
			features['department_accounting'] = 1
		elif features['department'] == "hr":
			features['department_hr'] = 1
		elif features['department'] == "managment":
			features['department_management'] = 1
		elif features['department'] == "marketing":
			features['department_marketing'] = 1
		elif features['department'] == "product_mng":
			features['department_product_mng'] = 1
		elif features['department'] == "sales":
			features['department_sales'] = 1
		elif features['department'] == "support":
			features['department_support'] = 1
		else:
			features['department_technical'] = 1

		features['salary_high'] = 0
		features['salary_low'] = 0
		features['salary_medium'] = 0
		if features['salary'] == "low":
			features['salary_low'] = 1
		elif features['salary'] == "medium":
			features['salary_medium'] = 1
		else:
			features['salary_high'] = 1

		df = pd.DataFrame(features, index  =[0])
		df.drop(columns = ['department', 'salary', 'model'], axis = 1, inplace = True)
		df = df.astype(dtype = "float64", errors = "ignore")

		if features['model'] == "Decision Tree Classifier":
			model = joblib.load(open("ml_models/decision_tree.sav", "rb"))
			prediction = model.predict(df)

		elif features['model'] == "K Nearest Neighbors":
			model = joblib.load(open("ml_models/knn.sav", "rb"))
			prediction = model.predict(df)

		elif features['model'] == "Logistic Regression":
			model = joblib.load(open("ml_models/logistic_regression.sav", "rb"))
			prediction = model.predict(df)

		elif features['model'] == "Multi Layer Perceptron":
			model = joblib.load(open("ml_models/mlp.sav", "rb"))
			prediction = model.predict(df)

		elif features['model'] == "Gaussian Naive Bayes":
			model = joblib.load(open("ml_models/naive_bayes.sav", "rb"))
			prediction = model.predict(df)

		elif features['model'] == "Random Forest Classifier":
			model = joblib.load(open("ml_models/random_forest.sav", "rb"))
			prediction = model.predict(df)

		else:
			model = joblib.load(open("ml_models/svm.sav", "rb"))
			prediction = model.predict(df)

		if prediction == 0:
			message = "The Employee will stay."
		else:
			message = "The Employee will quit."
		return render_template("result.html", text = message)
	return render_template("predict.html")

@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for("home"))
	return render_template("register.html", form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == 'admin@blog.com' and form.password.data == 'password':
			flash('Login successful!', 'success')
			return redirect(url_for('home'))
		else:
			flash('Login successful!', 'success')
			return redirect(url_for('home'))
	return render_template("login.html", form = form)


if __name__ == '__main__':
	app.run(debug = True)
