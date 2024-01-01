from flask import Flask, request, jsonify, render_template
from neo4j import GraphDatabase

app = Flask(__name__)

# Configure Neo4j connection
uri = "neo4j+s://38f0f39c.databases.neo4j.io"  # Replace with your Neo4j database URI
username = "neo4j"  # Replace with your Neo4j username
password = "b4NTFDl3gzs6T7Ut7ZD0ntPKdpUyzs1_DR-x4FeuwPA"  # Replace with your Neo4j password


class Neo4jDriver:
    def __init__(self):
        self._driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self._driver.close()

    def run_query(self, query, params=None):
        with self._driver.session() as session:
            result = session.run(query, params)
            return result.data()


neo4j_driver = Neo4jDriver()


# Serve the HTML page
@app.route('/')
def serve_quiz_page():
    return render_template('quizUI.html')


@app.route('/api/log', methods=['POST'])
def log_responses():
    data = request.json
    batch_responses = data.get('batch_responses')
    batch_questions = data.get('batch_questions')

    for n in range(len(batch_questions)):
        # create a link between the question and response using cypher
        response = batch_questions[n]['responses'][batch_responses[n]]
        question = batch_questions[n]['question']
        user_id = 123

        print(user_id, response, question)

        question_response_query = """
        MATCH (q:Question {Question:$question})<-[:TO]-(r:Response {Response:$response}),(u:User {user_id:$user_id})
        CREATE (u)-[:GIVES]->(r)
        """

        try:
            result = neo4j_driver.run_query(question_response_query, params={'user_id': user_id, 'question': question,
                                                                             'response': response})
        except Exception as e:
            print("Couldn't log responses: " + str(e))

    return render_template('quizUI.html')


@app.route('/api/query', methods=['POST'])
def query_neo4j():
    data = request.json
    user_id = data.get('user_id')
    batch_size = data.get('batch_size')
    print("fetching question batch...")

    # Validate the batch_type
    if batch_size > 501:
        return jsonify({"error": "Batch too large"}), 400

    query = """
            MATCH (q:Question)
        WITH q, rand() AS randomOrder
        ORDER BY randomOrder
        LIMIT $batch_size
        MATCH (q)<-[t:TO]-(r:Response)
        WITH q.Question as question_text, COLLECT({response: r.Response, is_correct: t.Correct}) AS responses_data
        RETURN
          question_text as question,
          [response IN responses_data | response.response] as responses,
          REDUCE(s = -1, x IN RANGE(0, SIZE(responses_data) - 1) | CASE WHEN responses_data[x].is_correct = "True" 
          THEN x ELSE s END) as answer
    """

    try:
        result = neo4j_driver.run_query(query, params={'batch_size': batch_size})
        # print(len(result))
        # print(result[0])
        return jsonify({"data": result}), 200
    except Exception as e:
        print("Error " + str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
