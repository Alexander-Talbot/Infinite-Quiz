import random
import streamlit as st
from neo4j import GraphDatabase

st.set_page_config(page_title="Infinite Quiz", page_icon=":shark:")
st.markdown(
    """
    <style>
    /* Style for the main content area */
    .content {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
    }

    /* Style for buttons */
    .stButton>button {
        background-color: #007bff;
        color: #ffffff;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
</style>
    """,
    unsafe_allow_html=True,
)
driver = GraphDatabase.driver("neo4j+s://38f0f39c.databases.neo4j.io", auth=("neo4j", "b4NTFDl3gzs6T7Ut7ZD0ntPKdpUyzs1_DR-x4FeuwPA"))

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# TODO get batch of 20 questions with the goal of maximizing completion rate
def get_question_batch():
    return


# Some qs crash this function atm
def get_question():
    with driver.session() as sesh:
        print("Getting question...")
        result = sesh.run("""
        MATCH (q:Question)
        WITH q, rand() AS randomOrder
        ORDER BY randomOrder
        LIMIT 1
        MATCH (q)<-[t:TO]-(r:Response)
        RETURN q, t{.*}, Collect(r) as responses
        """)

        # Check if any records were returned
        if result:
            # Initialize variables to store question details
            # Create the JSON object
            question = {
                "question": "",
                "options": [],
                "correct_answer": ""
            }
            records = [record for record in result.data()]
            # first record contains dummy responses, second contains correct response

            record = records[0]

            question_properties = record["q"]
            question_text = question_properties["Question"]
            question["question"] = question_text
            #print(question_text)

            for rt in record['responses']:
                response_text = rt['Response']
                #print("Dummy:")
                #print(response_text)
                question["options"].append(response_text)

            record = records[1]

            response_text = record['responses'][0]['Response']
            #print(response_text)
            question["options"].append(response_text)
            question["correct_answer"] = response_text
            return question
        else:
            # Handle the case where no records were found
            return {"error": "No question found"}


# TODO setup an initial experience for new users, choose the questions with the highest retention rates
def cold_start():
    """"""
    pass


def offline_batch():
    pass
    # download a large batch (500) to play while offline


def main():
    streak = 0
    score = 0

    # Create two columns
    col1, col2 = st.columns(2)

    # Add text to the first column
    col1.write("Score: 0")

    # Add text to the second column
    col2.write("Streak: 0")

    active_question = get_question()

    # print("question")
    # print(active_question)

    st.subheader(f"Question: {active_question['question']}")

    # Display buttons for options
    for option in active_question["options"]:
        if st.button(option, on_click=print("ayy")):
            st.write("Confirming Answer...")
            if option == active_question["correct_answer"]:
                st.write(option)
                score += 1
            else:
                st.write(option)
                st.write(active_question["correct_answer"])

            # Get a new question
            active_question = get_question()
            st.experimental_rerun()


if __name__ == "__main__":
    main()
    driver.close()
