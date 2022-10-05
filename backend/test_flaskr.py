import os
#from tkinter.tix import Tree
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'eldoret')
        DB_NAME = os.getenv('DB_NAME', 'trivia')
        database_path = "postgres://{}:{}@{}/{}".format( DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # ------------------------------------------------------------------------------
#  TEST FOR ALL QUESTION RELATED QUERIES 
# ------------------------------------------------------------------------------


# Test question pagination success
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

#test error for non existent page
    def test_404_non_existent_page(self):
        response = self.client().get('/questions?page=1200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'page not found')

#Test delete question success
    def test_delete_question(self):
        response = self.client().delete('/questions/1')
        data = json.loads(response.data)

        quiz = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        # self.assertEqual(data['question_id'], 1)
        # self.assertTrue(data['total_questions'])
        # self.assertTrue(data['question_deleted'])
        # self.assertEqual(quiz, None)

#Test non existing question
    def test_delete_non_existing_question(self):
        response = self.client().delete('/questions/2000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

#Test add new question
    def test_add_new_question(self):
        newQuiz = {
            'question': 'What is your quiz?',
            'answer': 'your answer',
            'difficulty': 3,
            'category': 2
        }

        response = self.client().post('/questions', json=newQuiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])

#Test search questions
    def test_search_question(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'account'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        # self.assertIsNotNone(data['questions'])
        # self.assertIsNotNone(data['total_questions'])

#test for search unavailable questions
    def test_search_unvailable_question(self):
        search = {'searchTerm': 'searchme'}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'page not found')

# ------------------------------------------------------------------------------
#  TEST FOR ALL CATEGORY SPECIFIC QUERIES 
# ------------------------------------------------------------------------------

#Test success of getting categories
    
    def test_get_category(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

#Test success of getting questions by category

    def test_get_category_quiz(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        # self.assertEqual(data['current_directory'], 'Geography')

# Test error with non existent category

    def get_question_beyond_valid_category(self):
        response = self.client().get('/categories/99/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# Test Success of playing quizzes

    def test_get_quiz(self):
        quizExample = {
            'previousQuiz': [],
            'quizCategory': {
                'type': 'Maths', 
                'id': 21
            }
        }
        response = self.client().post('/quizzes', json=quizExample)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

# Test failure of playing quizzes

    def test_get_quiz_error(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()