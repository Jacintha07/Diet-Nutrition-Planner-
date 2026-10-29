# Diet and Nutrition Planner using Image Based Recognition

A Flask web application that detects food items from images using YOLOv8 and provides diet and nutrition recommendations.

## Features
- Upload a food image and recognize the food item using YOLOv8
- Displays nutrition details: calories, protein, carbs and fat
- BMI calculator and daily calorie calculator
- Rule-based diet suggestions based on the user's details
- Simple web interface built with Flask
## Tech Stack
- Python
- Flask
- YOLOv8 (Ultralytics)
- HTML, CSS (templates and static)

## Project Structure
```
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML pages
├── static/             # CSS, images
├── yolov8/             # YOLOv8 related files
└── models/             # Trained model files
```

## How to Run
1. Clone the repository
   ```
   git clone https://github.com/Jacintha07/Diet-Nutrition-Planner-.git
   cd Diet-Nutrition-Planner-
   ```
2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
3. Run the app
   ```
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser

## Screenshots


## Team
- Jacintha Joseph Anto R
- Sakkina Sulfath B

## Future Improvements
- More food classes and mobile support
