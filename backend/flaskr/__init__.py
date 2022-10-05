from crypt import methods
import os
import sys
from tracemalloc import start
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db


QUESTIONS_PER_PAGE = 10

#paginate questions
def paginate_quiz(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    currentQuiz = questions[start:end]

    return currentQuiz

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    # CORS(app, resources={r"/api/*": {"origins": "*"}})


    #CORS Headers
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

# -------------------------------------------------------------------------------------
    # GET requests
# -------------------------------------------------------------------------------------

    #code to handle GET requests for all available categories
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_all_categories():
        #get all the categories
        categories =  Category.query.all()

        cat_dictionary = {}

    #add all categories to the dictionary
        for cat in categories:
            cat_dictionary[cat.id] = cat.type

        #display the categories in the view
        return jsonify({
            'success': True,
            'categories': cat_dictionary
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        totalQuiz = len(selection)
        currentQuiz = paginate_quiz(request, selection)

        if (len(currentQuiz) == 0):
            abort(404)

        try:
            categories = Category.query.all()
            cat_dictionary = {}
            for cat in categories:
                cat_dictionary[cat.id] = cat.type

            return jsonify({
                'success': True,
                'questions': currentQuiz,
                'total_questions': totalQuiz,
                'categories': cat_dictionary
            })
        except Exception as e:
            print(e)
            abort(400)
        finally:
            db.session.close() 
    
    # -----------------------------------------------------------
    # DELETE question
    # -----------------------------------------------------------

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            currentQuiz = paginate_quiz(request, selection)

            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            abort(422)



    # -----------------------------------------------------------
    # Create question with POST
    # -----------------------------------------------------------
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)
        
        get_new_question = body.get('question')
        get_new_answer = body.get('answer')
        get_new_difficulty = body.get('difficulty')
        get_new_category = body.get('category')

        if (get_new_question, get_new_answer, get_new_difficulty, get_new_category) == None:
            abort(422)

        try:
            quiz = Question(
                question = get_new_question,
                answer = get_new_answer,
                difficulty = get_new_difficulty,
                category = get_new_category
            )

            quiz.insert()

            totalQuiz = Question.query.order_by(Question.id).all()

            currQuiz = paginate_quiz(request, totalQuiz)

            return jsonify({
                'success': True,
                'created': quiz.id,
                'questions': currQuiz,
                'total_questions': len(totalQuiz)
            })

        except:
            abort(422)

    # -----------------------------------------------------------
    # Search questions
    # -----------------------------------------------------------
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        #Get user input
        body = request.get_json()
        searchTerm = body.get('search_term', None)
        
        select_question= Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
        if select_question:
            currentQuiz = paginate_quiz(request, select_question)

            return jsonify({
                'success': True,
                'questions': currentQuiz,
                'total_questions': len(select_question),
                'current_directory': None
            })
        else:
            abort(404)

    # -----------------------------------------------------------
    # GET questions based on category
    # -----------------------------------------------------------

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        try:
            selection = Question.query.filter_by(category=category.id).all()
            paginatedQuiz = paginate_quiz(request, selection)

            return jsonify({
                'success': True,
                'questions': paginatedQuiz,
                'total_questions': len(selection),
                'current_category': category.type
            })
        except:
            abort(400)


# -----------------------------------------------------------
# Quiz play using POST
# -----------------------------------------------------------

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
# -----------------------------------------------------------
# Quiz play using POST
# -----------------------------------------------------------

    @app.route('/quizzes', methods=['POST'])
    def trivia_quiz():
        try:
            body = request.get_json()
            quizCategory = body.get('quiz_category')
            previous_quiz = body.get('previous_questions')
            category_id = quizCategory['id']

            if category_id == 0:
                queryQuiz = Question.query.filter(Question.id.notin_(previous_quiz), Question.category == category_id).all()

            else:
                queryQuiz = Question.query.filter(Question.id.notin_(previous_quiz), Question.category == category_id).all()

            quiz = None
            if(queryQuiz):
                quiz = random.choice(queryQuiz)

            # newQuiz = queryQuiz[random.randrange(0, len(queryQuiz))].format() if len(queryQuiz) > 0 else None

            return jsonify({
                'success': True,
                'question': quiz.format()
            })
        except:
            abort(422)



# -----------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'page not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed_error(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405


    @app.errorhandler(422)
    def unprocessed(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500




    return app

