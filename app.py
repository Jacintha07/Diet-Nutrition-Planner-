from ultralytics import YOLO
import os
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "diet and nutrition _planner123"

# ==========================
# MySQL Configuration
# ==========================

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'diet and nutrition _planner'
mysql = MySQL(app)
# Load YOLO Model
model = YOLO("models/best.pt")
# ==========================
# Home Page
# ==========================

@app.route('/')
def home():
    return render_template('index.html')


# ==========================
# Register Page
# ==========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        goal = request.form['goal']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO users
            (fullname, email, phone, gender, age, height, weight, goal, password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (fullname, email, phone, gender, age, height, weight, goal, password))

        mysql.connection.commit()
        cursor.close()

        return redirect('/login')

    return render_template('register.html')


# ==========================
# Login Page
# ==========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        if user:
            session["email"] = email
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')


# ==========================
# Dashboard
# ==========================

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route("/bmi", methods=["GET", "POST"])
def bmi():

    bmi = None
    category = ""

    if request.method == "POST":

        height = float(request.form["height"])
        weight = float(request.form["weight"])

        height = height / 100

        bmi = round(weight / (height * height), 2)

        if bmi < 18.5:
            category = "Underweight"

        elif bmi < 25:
            category = "Normal Weight"

        elif bmi < 30:
            category = "Overweight"

        else:
            category = "Obese"

    return render_template("bmi.html", bmi=bmi, category=category)

@app.route("/diet", methods=["GET", "POST"])
def diet():
    bmi = None
    category = ""
    breakfast = ""
    lunch = ""
    dinner = ""

    if request.method == "POST":
        height = float(request.form["height"])
        weight = float(request.form["weight"])

        height = height / 100
        bmi = round(weight / (height * height), 2)

        if bmi < 18.5:
            category = "Underweight"
            breakfast = "Milk, Banana, Peanut Butter Toast"
            lunch = "Rice, Chicken, Vegetables"
            dinner = "Chapati, Egg Curry"

        elif bmi < 25:
            category = "Normal Weight"
            breakfast = "Oats, Milk, Apple"
            lunch = "Brown Rice, Dal, Salad"
            dinner = "Chapati, Vegetables"

        elif bmi < 30:
            category = "Overweight"
            breakfast = "Oats, Green Tea"
            lunch = "Grilled Chicken, Salad"
            dinner = "Soup, Chapati"

        else:
            category = "Obese"
            breakfast = "Boiled Eggs, Green Tea"
            lunch = "Salad, Grilled Fish"
            dinner = "Vegetable Soup"

        # Save diet plan into database
        if "email" in session:

            cursor = mysql.connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email=%s",
                (session["email"],)
            )

            user = cursor.fetchone()

            if user:

                user_id = user[0]

                cursor.execute("""
                    INSERT INTO diet_plans
                    (user_id, plan_date, breakfast, lunch, snack, dinner)
                    VALUES (%s, CURDATE(), %s, %s, %s, %s)
                """, (
                    user_id,
                    breakfast,
                    lunch,
                    "Fruit / Nuts",
                    dinner
                ))

                mysql.connection.commit()

            cursor.close()

    return render_template(
        "diet.html",
        bmi=bmi,
        category=category,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )
@app.route("/nutrition")
def nutrition():

    food = {
        "name": "Apple",
        "calories": "95 kcal",
        "protein": "0.5 g",
        "carbohydrates": "25 g",
        "fat": "0.3 g",
        "fiber": "4.4 g"
    }

    return render_template("nutrition.html", food=food)


@app.route("/profile")
def profile():

    if "email" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT fullname,email,phone,gender,age,height,weight,goal FROM users WHERE email=%s",
        (session["email"],)
    )

    user = cursor.fetchone()

    cursor.close()

    return render_template("profile.html", user=user)
@app.route("/upload", methods=["GET", "POST"])
def upload():
    filename = None
    detected_food = "No Food Detected"
    nutrition = {}

    nutrition_data = {
        "Apple": {
            "Calories": "95 kcal",
            "Protein": "0.5 g",
            "Carbohydrates": "25 g",
            "Fat": "0.3 g"
        },
        "banana": {
            "Calories": "105 kcal",
            "Protein": "1.3 g",
            "Carbohydrates": "27 g",
            "Fat": "0.4 g"
        },
        "Pizza": {
            "Calories": "285 kcal",
            "Protein": "12 g",
            "Carbohydrates": "36 g",
            "Fat": "10 g"
        },
        "burger": {
            "Calories": "354 kcal",
            "Protein": "17 g",
            "Carbohydrates": "29 g",
            "Fat": "17 g"
        },
        "Rice": {
            "Calories": "130 kcal",
            "Protein": "2.7 g",
            "Carbohydrates": "28 g",
            "Fat": "0.3 g"
        },
        "Chapathi": {
            "Calories": "104 kcal",
            "Protein": "3 g",
            "Carbohydrates": "18 g",
            "Fat": "3 g"
        },
        "Chicken Gravy": {
            "Calories": "210 kcal",
            "Protein": "18 g",
            "Carbohydrates": "6 g",
            "Fat": "12 g"
        },
        "Fries": {
            "Calories": "312 kcal",
            "Protein": "3.4 g",
            "Carbohydrates": "41 g",
            "Fat": "15 g"
        },
        "Idli": {
            "Calories": "58 kcal",
            "Protein": "2 g",
            "Carbohydrates": "12 g",
            "Fat": "0.4 g"
        },
        "Tomato": {
            "Calories": "18 kcal",
            "Protein": "0.9 g",
            "Carbohydrates": "3.9 g",
            "Fat": "0.2 g"
        },
        "Vada": {
            "Calories": "97 kcal",
            "Protein": "3 g",
            "Carbohydrates": "8 g",
            "Fat": "6 g"
        },
        "Soda": {
            "Calories": "150 kcal",
            "Protein": "0 g",
            "Carbohydrates": "39 g",
            "Fat": "0 g"
        }
    }

    if request.method == "POST":

        image = request.files["image"]
        meal_type = request.form["meal_type"]
        quantity = float(request.form["quantity"])

        if image.filename != "":

            filepath = os.path.join("static/uploads", image.filename)
            image.save(filepath)

            filename = image.filename

            # YOLO food detection
            results = model(filepath)
            names = model.names

            if len(results[0].boxes) > 0:

                class_id = int(results[0].boxes[0].cls[0])
                detected_food = names[class_id]

                if detected_food in nutrition_data:

                    nutrition = nutrition_data[detected_food]

                    # ==========================
                    # Save Detection History
                    # ==========================

                    cursor = mysql.connection.cursor()

                    cursor.execute("""
                        INSERT INTO detection_history
                        (food_name, calories, protein, carbohydrates, fat, image_name)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        detected_food,
                        nutrition["Calories"],
                        nutrition["Protein"],
                        nutrition["Carbohydrates"],
                        nutrition["Fat"],
                        filename
                    ))

                    mysql.connection.commit()

                    # ==========================
                    # Find Food ID
                    # ==========================

                    cursor.execute(
                        "SELECT id FROM food_items WHERE LOWER(food_name)=LOWER(%s)",
                        (detected_food,)
                    )

                    food = cursor.fetchone()

                    # ==========================
                    # Save Food Log
                    # ==========================

                    if food:

                        food_id = food[0]

                        cursor.execute("""
                            INSERT INTO food_logs
                            (user_id, food_id, quantity, meal_type)
                            SELECT id, %s, %s, %s
                            FROM users
                            WHERE email=%s
                        """, (
                            food_id,
                            quantity,
                            meal_type,
                            session.get("email")
                        ))

                        mysql.connection.commit()

                    cursor.close()

    return render_template(
        "upload.html",
        filename=filename,
        detected_food=detected_food,
        nutrition=nutrition
    )
@app.route("/reminder")
def reminder():
    return render_template("reminder.html")

@app.route("/calorie", methods=["GET", "POST"])
def calorie():

    calories = None

    if request.method == "POST":

        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        activity = request.form["activity"]

        if gender == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity_factor = {
            "Sedentary": 1.2,
            "Light": 1.375,
            "Moderate": 1.55,
            "Active": 1.725
        }

        calories = round(bmr * activity_factor[activity])

        # Save nutrition goal for logged-in user
        if "email" in session:

            cursor = mysql.connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email=%s",
                (session["email"],)
            )

            user = cursor.fetchone()

            if user:

                user_id = user[0]

                cursor.execute("""
                    INSERT INTO nutrition_goals
                    (user_id, daily_calories, daily_protein,
                     daily_carbohydrates, daily_fat)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id,
                    calories,
                    0,
                    0,
                    0
                ))

                mysql.connection.commit()

            cursor.close()

    return render_template(
        "calorie.html",
        calories=calories
    )
@app.route("/disease", methods=["GET", "POST"])
def disease():

    guidance = None

    if request.method == "POST":

        disease_name = request.form["disease"]
        age = request.form["age"]
        preference = request.form["preference"]
        goal = request.form["goal"]

        # General food guidance
        recommendations = {

            "Diabetes": {
                "include": "Vegetables, whole grains, pulses, eggs, fish, nuts and fresh fruits in suitable portions.",
                "limit": "Sugary drinks, sweets, highly processed foods and foods with large amounts of added sugar.",
                "meal": "Breakfast: oats with vegetables. Lunch: whole-grain rice with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            },

            "Hypertension": {
                "include": "Vegetables, fruits, oats, pulses, unsalted nuts and other minimally processed foods.",
                "limit": "Very salty foods, processed foods, pickles and heavily salted snacks.",
                "meal": "Breakfast: oats with fruit. Lunch: rice or chapati with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            },

            "High Cholesterol": {
                "include": "Oats, vegetables, fruits, beans, lentils, whole grains and nuts.",
                "limit": "Deep-fried foods, foods high in saturated fat and highly processed foods.",
                "meal": "Breakfast: oats with fruit. Lunch: brown rice with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            },

            "Anemia": {
                "include": "Iron-rich foods such as leafy green vegetables, lentils, beans, eggs and other suitable iron-containing foods.",
                "limit": "Avoid relying mainly on highly processed foods with little nutritional value.",
                "meal": "Breakfast: egg or iron-rich vegetarian option with whole grains. Lunch: dal with leafy vegetables. Dinner: chapati with vegetables and a protein source."
            },

            "PCOS": {
                "include": "Vegetables, whole grains, pulses, nuts, seeds and balanced protein sources.",
                "limit": "Highly processed foods, sugary drinks and foods with large amounts of added sugar.",
                "meal": "Breakfast: oats with nuts. Lunch: whole grains with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            },

            "Obesity": {
                "include": "Vegetables, fruits, whole grains, pulses and balanced protein sources.",
                "limit": "Sugary drinks, frequent fried foods, fast food and highly processed snacks.",
                "meal": "Breakfast: oats with fruit. Lunch: vegetables with whole grains and protein. Dinner: vegetables with chapati and protein."
            },

            "Heart Disease": {
                "include": "Vegetables, fruits, whole grains, pulses, nuts and fish or other suitable protein sources.",
                "limit": "Deep-fried foods, highly processed foods and foods high in saturated fat.",
                "meal": "Breakfast: oats with fruit. Lunch: whole grains with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            },

            "Fatty Liver": {
                "include": "Vegetables, fruits, whole grains, pulses and balanced protein sources.",
                "limit": "Sugary drinks, excessive added sugar, highly processed foods and frequent fried foods.",
                "meal": "Breakfast: oats with fruit. Lunch: whole grains with vegetables and dal. Dinner: chapati with vegetables and a protein source."
            }
        }

        data = recommendations.get(disease_name)

        if data:

            guidance = f"""
Disease/Condition: {disease_name}

Age: {age}

Food Preference: {preference}

Goal: {goal}

✅ Foods that can generally be included:
{data["include"]}

⚠️ Foods that may be better to limit:
{data["limit"]}

🍽 Simple one-day food idea:
{data["meal"]}

Note:
This is general nutrition information, not medical advice.
For an individualized diet plan, consult a qualified healthcare professional.
"""

    return render_template(
        "disease.html",
        guidance=guidance
    )
@app.route("/water", methods=["GET", "POST"])
def water():

    water = None

    if request.method == "POST":

        weight = float(request.form["weight"])

        water = round(weight * 0.04, 2)

    return render_template(
        "water.html",
        water=water
    )

# ==========================
# Run Flask
# ==========================

if __name__ == '__main__':
    app.run(debug=True)
