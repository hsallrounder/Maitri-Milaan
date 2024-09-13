from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, db, auth
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime
import pytz
from retrieve_suggestions import get_sug
from retrieve_kundli import find_kundli_milan, find_data

app = Flask(__name__)

database_url = "https://maitri-milaan-default-rtdb.asia-southeast1.firebasedatabase.app/"

cred = credentials.Certificate("maitri-milaan-firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})
ref = db.reference('user_data')

@app.route('/')
def index():
    return render_template('home.html')

def find_Matches(email):
    user_data = ref.child(email.replace('.', ',')).get()
    df = pd.DataFrame.from_dict(ref.get(), orient='index')
    df.reset_index(drop=True, inplace=True)

    df['dob'] = df['dob'].apply(lambda date_str: datetime.strptime(date_str, "%Y-%m-%d").date())

    current_date = datetime.now().date()
    df['age'] = df['dob'].apply(lambda x: (current_date - x).days // 365)

    df['dob'] = df['dob'].apply(lambda x: x.strftime("%d-%b-%Y"))

    age_range = [user_data['min_age'], user_data['max_age']]

    filtered_data = df.drop(df[df['email'] == email].index)

    filtered_data = df[(df['age'] >= age_range[0]) & 
                       (df['age'] <= age_range[1]) & 
                       (df['gender'] == user_data['gender_preference'])]   

    filtered_data = filtered_data.drop(columns=['age', 'gender_preference'], axis=1)

    # Vectorize interests
    vectorizer = CountVectorizer()
    interests_matrix = vectorizer.fit_transform(filtered_data['interests'].apply(lambda x: ' '.join(x)))
    user_interests_vector = vectorizer.transform([', '.join(user_data['interests'])])

    # Calculate cosine similarity
    similarities = cosine_similarity(interests_matrix, user_interests_vector)

    # Add cosine similarity to DataFrame
    filtered_data['cosine_similarity'] = similarities.flatten()

    # Sort by cosine similarity in descending order
    filtered_data.sort_values(by='cosine_similarity', ascending=False, inplace=True)

    # Find the row corresponding to the user's email
    user_row = df[df['email'] == email].iloc[0]

    return filtered_data, user_row

@app.route('/get_score', methods=['POST'])
def get_score():
    data = request.json
    m_email = data.get('m_email')
    f_email = data.get('f_email')
    
    gdetail = find_data(f_email,ref)
    bdetail = find_data(m_email,ref)

    res = find_kundli_milan(gdetail,bdetail)
    # res = {
    #     "result_color":"score red",
    #     "score":"28",
    # }
    
    return jsonify(res)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    email = request.args.get('data')
    
    preferred_matches_df, user_row = find_Matches(email)
    
    user_data = user_row.to_dict()

    preferred_matches_df = preferred_matches_df[preferred_matches_df['email'] != email]
    
    preferred_matches = preferred_matches_df.to_dict('records')

    with open("milaan_result.html", "w", encoding="utf-8") as file:
        pass
    
    return render_template('dashboard.html', user_data=user_data, preferred_matches=preferred_matches)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email_error = None
    password_error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        tmp = ref.child(email.replace('.', ',')).get()
        if tmp is None:
            email_error = 'Email does not exist. Please choose a different email or sign up.'
        else:
            if tmp['password'] != password:
                password_error = 'Incorrect password.'
            else:
                return redirect(url_for('dashboard', data=email))
    return render_template('login.html', email_error=email_error, password_error=password_error)


def convert_to_ist(gmt_time_str):
    # Create a datetime object from the GMT time string
    gmt_time = datetime.strptime(gmt_time_str, "%H:%M")

    # Set the time zone to GMT
    gmt_timezone = pytz.timezone('GMT')
    gmt_time = gmt_timezone.localize(gmt_time)

    # Convert to IST
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = gmt_time.astimezone(ist_timezone)

    # Format the result as a string in 24-hour format
    ist_time_str = ist_time.strftime("%H:%M")

    return ist_time_str


@app.route('/get_sug', methods=['POST'])
def get_suggestions():
    input_city = request.form['pob']
    suggestions = get_sug(input_city)
    return jsonify(suggestions)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        dob = request.form['dob']
        tob = request.form['tob']
        pob = request.form['pob']
        gender = request.form['gender']
        address = request.form['address']
        interests = request.form.getlist('interest')
        gender_preference = request.form['gender_preference']
        min_age = int(request.form['min_age'])
        max_age = int(request.form['max_age'])
        tmp = ref.child(email.replace('.', ',')).get()
        if tmp is not None:
            return 'Email already exists. Please choose a different email or login. <br> <a href="/signup">Go Back</a>'
        else:
            data = {
                "email": email,
                "name": name,
                "password": password,
                "dob": dob,
                "tobinist": convert_to_ist(tob),
                "pob": pob,
                "gender": gender,
                "address": address,
                "interests": interests,
                "gender_preference": gender_preference,
                "min_age": min_age,
                "max_age": max_age
            }
            ref.child(email.replace('.', ',')).set(data)
            return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
