# FoodWise AI - Personalized Nutrition & Exercise Recommendation System

An AI-powered nutrition and exercise recommendation system that provides personalized meal plans, exercises, and yoga poses based on your health profile.

## Features

- **Personalized Food Recommendations**: Get meal suggestions tailored to your health conditions
- **Exercise Recommendations**: Automatically receive exercise recommendations based on your health profile
- **Yoga Poses**: Get yoga pose suggestions appropriate for your age, BMI, and health conditions
- **User Authentication**: Secure Firebase-based authentication system
- **Health Profile**: Track your health metrics and conditions

## Setup

### Prerequisites

- Python 3.10 or higher
- Streamlit
- Firebase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/foodwise-ai.git
cd foodwise-ai
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Firebase configuration:
   ```
   FIREBASE_API_KEY=your_api_key_here
   FIREBASE_AUTH_DOMAIN=your_auth_domain_here
   FIREBASE_PROJECT_ID=your_project_id_here
   ```

   > **Important**: Never commit your `.env` file to version control. It's already included in the `.gitignore` file.

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Sign up or log in to your account
2. Fill in your health profile including:
   - Health conditions
   - Dietary preferences
   - Personal information
3. Click "Generate Meal Plan" to get your personalized recommendations
4. View your food recommendations, exercise suggestions, and yoga poses

## Data Privacy

All user data is securely stored in Firebase and protected with industry-standard encryption. We never share your data with third parties.

## License

This project is licensed under the MIT License - see the LICENSE file for details.