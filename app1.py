import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

GOOGLE_API_KEY = "AIzaSyDqKXshHbCRtVDrk8x7aIMK9PGWZwwCInQ"
genai.configure(api_key=GOOGLE_API_KEY)

if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
    'goals': 'Lose 10 pounds in 3 months\nImprove cardiovascular health',
    'conditions': 'None',
    'routines': '30-minute walk 3x/week',
    'preferences': 'Vegetarian\nLow carb',
    'restrictions': 'No dairy\nNo nuts'
    }
# function to get gemini response
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel('gemini-2.5-flash')

    content = [input_prompt]

    if image_data:
        content.extend(image_data)

    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"
    
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None
#App layout
st.set_page_config(page_title="AI Health Companion", layout="wide")
st.header(" 🥗 AI-Powered Health and Meal Planner ")
#Sidebar for health profile
with st.sidebar:
        st.subheader("Your Health Profile")
        health_goals = st.text_area("Health Goals",value=st.session_state.health_profile['goals'])
        medical_conditions = st.text_area("Medical Conditions", value=st.session_state.health_profile['conditions'])
        fitness_routines = st.text_area("Fitness Routines",value=st.session_state.health_profile['routines'])
        food_preferences = st.text_area("Food Preferences",value=st.session_state.health_profile['preferences'])
        restrictions = st.text_area("Dietary Restrictions",value=st.session_state.health_profile['restrictions'])

        if st.button("Update Profile"):
            st.session_state.health_profile = {
                'goals': health_goals,
                'conditions': medical_conditions,
                'routines': fitness_routines,
                'preferences': food_preferences,
                'restrictions': restrictions
            }
            st.success("Profile update!")

    #Main content area
tab1,tab2,tab3 = st.tabs(["Meal Planning","Food Analysis","Health Insights"])

with tab1:
        st.subheader("Personalized Meal Planning")

        col1,col2 = st.columns(2)

        with col1:
            st.write("### Your Current Needs")
            user_input = st.text_area("Describe any specific requirements for your meal",placeholder="e.g., 'I need quick meals for work related")

        with col2:
            st.write("### Your Health Profile")
            st.json(st.session_state.health_profile)
        
        if st.button("Generate Personalized Meal Plan"):
            if not any(st.session_state.health_profile.values()):
                st.warning("PLease complete your health profile in the sidebar first")
            else:
                with st.spinner("Creating your personalized meal plan...."):
                    # Construct the prompt
                    prompt = f""" Create a personalized meal plan based on the following health problems:
                    Health Goals: {st.session_state.health_profile['goals']}
                    Medical Conditions: {st.session_state.health_profile['conditions']}
                    Fitness Routines: {st.session_state.health_profile['routines']}
                    Food Preferences: {st.session_state.health_profile['preferences']}
                    Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                    Additional requirements: {user_input if user_input else "None provided "}
                    Provide:
                    1. A 7-day meal plan with breakfast,lunch,dinner and snacks
                    2. Nutritional breakdown for each day(calories,macros)
                    3. Contextual explanation for why each meal was chosen
                    4. Shopping list organized by category
                    5. Preparation tips and time-saving suggestions

                    Format the output clearly with headings and bullet points.
                    """

                    response = get_gemini_response(prompt)

                    st.subheader("Your Personalized Meal Plan")
                    st.markdown(response)

                    # Add download button

                    st.download_button(
                        label="Download Meal Plan",
                        data=response,
                        file_name="personalized_meal_plan.txt",
                        mime="text/plain"
                    )
with tab2:
        st.subheader("Food Analysis")

        uploaded_file = st.file_uploader("Upload an image of your food",type=["jpg","jpeg","png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image,caption="Upload Food Image.",use_column_width=True)

            if st.button("Analyze Food"):
                with st.spinner("Analyzing your food...."):
                    image_data = input_image_setup(uploaded_file)

                    prompt = f"""
                    You are an expert nutritionist. Analyze this food image.

                    Provide detailed information about:
                    - Estimated calories
                    - Macronutrient breakdown
                    - Potential health benefits
                    - Any concers based on common dietary restrictions
                    - Suggested portion sizes

                    If the food contains multiple items , analyze each separately.
                    """

                    response = get_gemini_response(prompt,image_data)
                    st.subheader("Food Analysis Results")
                    st.markdown(response)
with tab3:
        st.subheader("Health Insights")

        health_query = st.text_input("Ask any health/nutrition-related questions",placeholder="e.g., 'How can I improve my gut health")

        if st.button("Get Expert Insights"):
            if not health_query:
                st.warning("Please enter a health question")
            else:
                with st.spinner("Researching your question...."):
                    prompt = f"""
                    You are a certified nutritionist and health expert.
                    Provide detailed , science-backed insights about:
                    {health_query}
                    
                    Consider the user's health profile:
                    {st.session_state.health_profile}
                    
                    Include:
                    1. Clear explanation of the science
                    2. Practical recommendations
                    3. Any relevant precautions
                    4. References to studies (when applicable)
                    5. Suggested foods/supplements if appropriate

                    Use simple language but maintain accuracy.
                    """

                    response = get_gemini_response(prompt)
                    st.subheader("Expert Health Insights")
                    st.markdown(response)





