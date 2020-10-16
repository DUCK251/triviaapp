import os, sys, random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10
CATEGORY_ALL = 0

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, origins=['*'])

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categroies():
    formatted_categories = {}
    categories = Category.query.all()

    for category in categories:
      formatted_categories[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    questions = paginate_questions(request, Question.query.all())

    if not questions:
      abort(404)

    formatted_categories = {}
    categories = Category.query.all()
    for category in categories:
      formatted_categories[category.id] = category.type
    
    return jsonify({
      'questions': questions,
      'total_questions': db.session.query(Question).count(),
      'categories': formatted_categories,
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if not question:
        abort(422)
      
      question.delete()
      return jsonify({
        'success':True
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    search = body.get('searchTerm', None)

    try:
      if search:
        selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
        total_questions = len(selection)
        questions = [question.format() for question in selection]
        return jsonify({
          'questions': questions,
          'total_questions': total_questions,
          'current_category': None
        })
      else:
        if None in [new_question, new_answer, new_difficulty, new_category]:
          abort(422)

        created_question = Question(
          question = new_question,
          answer = new_answer,
          difficulty = new_difficulty,
          category = new_category
        )
        created_question.insert()
        
        return jsonify({
          'success': True
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category_id(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).all()
      total_questions = len(questions)
      questions = paginate_questions(request, questions)

      return jsonify({
        'questions':questions,
        'total_questions':total_questions,
        'current_category':None
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    category_id = body['quiz_category']['id']

    questions = []
    try:
      if(int(category_id) == CATEGORY_ALL):
        questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.category == category_id).all()
    except:
      abort(422)

    if not questions:
      abort(400)

    filtered_questions = []
    
    for question in questions:
      is_previous_question = False
      for previous_question_id in previous_questions:
        if question.id == int(previous_question_id):
          is_previous_question = True
          break
      if not is_previous_question:
        filtered_questions.append(question.format())

    if filtered_questions:
      return jsonify({
        'question': random.choice(filtered_questions)
      })
    else:
      return jsonify({
        'question': None
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad request"
      }), 400
  
  @app.errorhandler(403)
  def forbidden(error):
    return jsonify({
      "success": False, 
      "error": 403,
      "message": "Forbidden"
      }), 403
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal server error"
      }), 500
      
  return app

    