import os, sys
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv()
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(os.environ.get("DATABASE_NAME"),os.environ.get("DATABASE_PASSWORD"),'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])

    def test_get_questions_by_valid_page(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question_by_valid_question_id(self):
        question_id = Question.query.first().id
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(question)

    def test_delete_question_by_invalid_question_id(self):
        question_id = 1000
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_create_question(self):
        new_question = {
            'question': 'What is the capital of South Korea?',
            'answer': 'Seoul',
            'difficulty': '3',
            'category' : '3'
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        question = Question.query.filter(Question.answer == 'Seoul').first()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(question)

    def test_422_if_question_creation_fails(self):
        new_question = {
            'question': 1,
            'answer': 2,
            'category' : 10
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        question = Question.query.filter(Question.category == 10).one_or_none()

        self.assertIsNone(question, None)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_search_question_by_search_term_with_results(self):
        res = self.client().post('/questions', json={'searchTerm':'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_question_by_search_term_without_results(self):
        res = self.client().post('/questions', json={'searchTerm':'abcdefg'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) == 0)
        self.assertTrue(data['total_questions'] == 0)

    def test_get_questions_by_category_id_with_results(self):
        category_id = 1
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_category_id_without_results(self):
        category_id = 1000
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions'])==0)
        self.assertTrue(data['total_questions']==0)

    def test_get_questions_for_quiz_from_one_category(self):
        previous_questions = []
        quiz_category = {
            'id':'1',
            'type':'Science'
        }
        res = self.client().post('/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': quiz_category
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

        previous_questions.append(data['question']['id'])

        res = self.client().post('/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': quiz_category
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] != previous_questions[0])

    def test_get_questions_for_quiz_from_all_categories(self):
        previous_questions = []
        quiz_category = {
            'id':'0',
            'type':'Science'
        }
        res = self.client().post('/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': quiz_category
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

        previous_questions.append(data['question']['id'])

        res = self.client().post('/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': quiz_category
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] != previous_questions[0])

    def test_400_request_for_getting_questions_by_invalid_category(self):
        previous_questions = []
        quiz_category = {
            'id':'1000',
            'type':'Science'
        }
        res = self.client().post('/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': quiz_category
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()