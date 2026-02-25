from dotenv import load_dotenv
import os
import streamlit as st
import google.genai as genai
import re

# Load environment variables from project.env using absolute path
env_path = os.path.join(os.path.dirname(__file__), 'project.env')
load_dotenv(env_path)

# Configure the API key for GenAI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found in environment variables. Add it to .env file.")
    st.stop()

# Initialize the Genai client
client = genai.Client(api_key=api_key)


# Initialize session state for storing the generated content
if "study_profile" not in st.session_state:
    st.session_state.study_profile = {
        "Target":"Score 90+ in my next exam",
        "Level":"Intermediate",
        "Learning Preferences":"Detailed step-by-step",
        "Study Routine":"Two hours daily study"
    }

# Function to get Gemini response based on user input
def get_gemini_response(input_prompt, image_data=None):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=input_prompt
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

# App layout and user interface
st.set_page_config(page_title="AI-Powered Study Buddy", layout="wide")
st.header("📘 AI-Powered Study Buddy")
st.subheader("Ask me anything about your studies!")

# Sidebar for user input
with st.sidebar:
    st.subheader("Your Profile")

    Your_target = st.text_input("Set your Target", placeholder="e.g., Score 90+ in my next exam", value=st.session_state.study_profile["Target"])
    Your_level = st.text_input("Tell about your current level", placeholder="e.g., Beginner, Intermediate, Advanced", value=st.session_state.study_profile["Level"])
    Your_learning_preferences = st.text_input("What are your learning preferences?", placeholder="e.g., Detailed step-by-step explanations", value=st.session_state.study_profile["Learning Preferences"])
    Your_study_routine = st.text_input("What is your study routine?", placeholder="e.g., 2 hours daily", value=st.session_state.study_profile["Study Routine"])

    if st.button("Update Profile"):
        st.session_state.study_profile.update({
            "Target": Your_target,
            "Level": Your_level,
            "Learning Preferences": Your_learning_preferences,
            "Study Routine": Your_study_routine
        })
        st.success("Profile updated successfully!")

# Main content area for displaying the response
tab1, tab2, tab3,tab4 = st.tabs(["Study Help", "Summary Generator", "Quiz Generator", "Flash Cards"])

with tab1:
    st.subheader("📘 Your Personalized Study Assistance")
    cols1, cols2 = st.columns(2)
    with cols1:
        st.write("### Ask Study Question")
        user_input = st.text_area("Enter your question", placeholder="e.g., How do I study for a math exam?", height=200)

    with cols2:
        for key, value in st.session_state.study_profile.items():
            data = [{"Key": k, "Value": v} for k, v in st.session_state.study_profile.items()]
        st.write("### Your Study Profile")
        st.dataframe(data, use_container_width=True, hide_index=True)

    if st.button("Generate Text Response"):
        if not any(st.session_state.study_profile.values()):
            st.warning("Please fill in your profile information before generating a response.")
        else:
            with st.spinner("Generating response..."):
                prompt = f"""
                Based on the following user profile:
                Goal: {st.session_state.study_profile['Target']}
                Level: {st.session_state.study_profile['Level']}
                Learning Preferences: {st.session_state.study_profile['Learning Preferences']}
                Study Routine: {st.session_state.study_profile['Study Routine']}
                
                Please generate a personalized response that addresses these needs and preferences.
                """

                response = get_gemini_response(prompt)

                if response:
                    st.subheader("Generated Response")
                    st.success(response)
                    st.download_button(
                        label="Download Response",
                        data=response,
                        file_name="ai_response.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to generate response.")

with tab2:
    
    if "summary" not in st.session_state:
        st.session_state.summary = ""

    st.title("📄 AI Summary Generator")

    input_text = st.text_area("Paste your text here", height=200)

    summary_length = st.selectbox(
        "Select Summary Length",
        ["Short (3-4 lines)", "Medium (6-8 lines)", "Detailed"]
    )


    if st.button("Generate Summary"):

        if input_text.strip() == "":
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating summary..."):

                prompt = f"""
                Summarize the following text.

                Summary length: {summary_length}

                Text:
                {input_text}

                Only provide the summary.
                """

                try:
                    response = get_gemini_response(prompt)
                    st.session_state.summary = response

                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.summary:
        st.subheader("📌 Summary")
        st.success(st.session_state.summary)

with tab3:
    st.subheader("Quiz Generator")

    st.title("🧠 AI Topic Based Quiz")

    # Initialize Session State
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "topic" not in st.session_state:
        st.session_state.topic = ""

    if "num_questions" not in st.session_state:
        st.session_state.num_questions = 5

    # Input Section
    st.subheader("⚙️ Quiz Settings")

    topic = st.text_input("Enter Quiz Topic:", value=st.session_state.topic)

    num_questions = st.slider("Number of Questions", 1, 20, 5)

    if st.button("Generate Quiz"):

        if topic.strip() == "":
            st.warning("⚠️ Please enter a topic.")
        else:
            # 🔥 Replace this with your AI-generated response
            response = ""

            with st.spinner("Generating quiz..."):
                prompt = f"""
            Generate {num_questions} multiple choice questions about {topic}.
            Only provide the question and 4 options (A, B, C, D) for each question. Do not include any explanations or additional text.:
            Format strictly like this:

            Q1. Question text?
            A) Option
            B) Option
            C) Option
            D) Option
           
            Answer: [Correct Option Letter]
            Explanation: [Detailed explanation of the answer]

            Repeat for all questions.
            """

                response = get_gemini_response(prompt)

                if response:
                    st.subheader("Generated Quiz")
                    st.session_state.quiz_data = response
                    st.session_state.submitted = False
                    st.session_state.score = 0
                    st.session_state.topic = topic
                    st.session_state.num_questions = num_questions
                else:
                    st.error("Failed to generate quiz.")

    # Show Quiz
    if st.session_state.quiz_data:

        questions = re.split(r"\n(?=Q\d+\.)", st.session_state.quiz_data.strip())

        st.markdown(f"## 📘 Topic: {st.session_state.topic}")
        st.markdown(f"### 📝 Total Questions: {len(questions)}")
        st.markdown("---")

        with st.form("quiz_form"):

            user_answers = []

            for i, q in enumerate(questions):

                question_text = q.split("Answer:")[0].strip()
                st.markdown(f"### {question_text}")

                options = re.findall(r"[A-D]\) .*", q)

                correct_match = re.search(r"Answer:\s*([A-D])", q)
                correct_letter = correct_match.group(1) if correct_match else None

                explanation_match = re.search(r"Explanation:\s*(.*)", q, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ""

                selected = st.radio(
                    "Select answer:",
                    ["-- Select an option --"] + options,
                    key=f"q_{i}"
                )

                user_answers.append((selected, correct_letter, explanation))

                st.markdown("---")

            submitted = st.form_submit_button("Submit Exam")

        # Score Calculation
        if submitted:

            unanswered = any(
                ans[0] == "-- Select an option --"
                for ans in user_answers
            )

            if unanswered:
                st.warning("⚠️ Please answer all questions before submitting.")
            else:
                score = 0

                for selected, correct_letter, _ in user_answers:
                    if correct_letter and selected[0] == correct_letter:
                        score += 1

                st.session_state.score = score
                st.session_state.submitted = True

        # Show Results
        if st.session_state.submitted:

            total = len(questions)
            percentage = (st.session_state.score / total) * 100 if total > 0 else 0

            st.success(f"🎯 Final Score: {st.session_state.score} / {total}")
            st.info(f"📊 Percentage: {percentage:.2f}%")

            st.markdown("## 📖 Answer Review")
            st.markdown("---")

            for i, (_, correct_letter, explanation) in enumerate(user_answers):
                    st.write(f"Q{i+1} Correct Answer: {correct_letter}")
                    st.write(f"Explanation: {explanation}")
                    st.markdown("---")

            if st.button("Generate New Quiz"):
                st.session_state.quiz_data = None
                st.session_state.submitted = False
                st.session_state.score = 0
                st.rerun()

with tab4:
    

    # Session State Setup
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    st.title("🧠 AI Flash Cards Generator")

    topic = st.text_input("Enter Topic")
    num_cards = st.slider("Number of Flash Cards", 1, 20, 5)

    # Generate Flash Cards

    if st.button("Generate Flash Cards"):

        if topic.strip() == "":
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating flash cards..."):

                prompt = f"""
                Generate {num_cards} different flash cards on topic "{topic}".

                Format strictly like this:

                Q: Question here
                A: Answer here

                Only provide flash cards. No extra text.
                """

                response = get_gemini_response(prompt)

                cards_text = response.split("Q:")

                flashcards = []
                for card in cards_text:
                    if "A:" in card:
                        question = card.split("A:")[0].strip()
                        answer = card.split("A:")[1].strip()
                        flashcards.append((question, answer))

                st.session_state.flashcards = flashcards
                st.session_state.current_index = 0
                st.session_state.show_answer = False

    # Display Flash Card

    if st.session_state.flashcards:

        question, answer = st.session_state.flashcards[st.session_state.current_index]

        st.markdown("### 📌 Question")
        st.info(question)

        if st.button("Show Answer"):
            st.session_state.show_answer = True

        if st.session_state.show_answer:
            st.markdown("### ✅ Answer")
            st.success(answer)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.session_state.show_answer = False

        with col2:
            if st.button("Next ➡"):
                if st.session_state.current_index < len(st.session_state.flashcards) - 1:
                    st.session_state.current_index += 1
                    st.session_state.show_answer = False

        st.write(f"Card {st.session_state.current_index + 1} of {len(st.session_state.flashcards)}")


