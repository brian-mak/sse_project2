import openai

def generate_workout_plan(user_id):
    openai.api_key = ''

    # Example of fetching user preferences and saved exercises
    # preferences = get_user_preferences(user_id)
    # saved_exercises = get_saved_exercises(user_id)
    
    # # Constructing the prompt
    # prompt = f"Create a workout plan for the following preferences: Fitness Goal: {preferences['fitness_goal']}, Target Muscle Group: {preferences['target_muscle_group']}, Fitness Level: {preferences['fitness_level']}, Preferred Workout Duration: {preferences['preferred_workout_duration']} minutes. Include {preferences['no_of_exercises']} of these exercises: {', '.join([exercise['name'] for exercise in saved_exercises])}."

    prompt = f"Create a workout plan for the following preferences: Fitness Goal: Weight Gain, Target Muscle Group: Upper Body, Fitness Level: Beginner, Preferred Workout Duration: 60 minutes. Include {preferences['no_of_exercises']} of these exercises: 45° Side Bend, Air Bike, Barbell Bench Front Squat, Barbell Bent Over Row, Barbell Deadlift, Barbell Decline Bent Arm Pullover, Barbell Decline Wide-grip Pullover, Barbell Front Raise, Barbell Seated Behind Head Military Press, Dumbbell Around Pullover, Dumbbell Bench Press, Deep Push Up, Barbell Floor Calf Raise."

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0.7,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    # The generated plan will be in response.choices[0].text
    workout_plan = response.choices[0].text.strip()

    return workout_plan

@app.route('/my_custom_workout_plan')
def my_custom_workout_plan():
    user_id = session['user_id']
    workout_plan = generate_workout_plan(user_id)
    return render_template('custom_workout_plan.html', workout_plan=workout_plan)

