import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from functools import wraps
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from jose import jwt
from six.moves.urllib.request import urlopen
app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code indicating
     reason for failure
'''


@app.route("/drinks")
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        list_drinks = [dr.short() for dr in drinks]
        print("list_drinks")
        print(list_drinks)
        if len(drinks) == 0:
            abort(404)
        return jsonify({
            'status': 200,
            'success': True,
            'drinks': list_drinks
        })
    except Exception:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_details(jwt):

    try:
        drinks = Drink.query.order_by(Drink.id).all()
        list_drinks = [dr.long() for dr in drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({
            'status': 200,
            'success': True,
            'drinks': list_drinks
        })
    except Exception:
        # print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink or appropriate
    status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def post_drink_details(jwt):
    body = request.get_json()
    print(body)
    returned_drinks = []
    try:
        new_title = body['title']
        new_recipe = json.dumps(body['recipe'])
        if (new_title is not None):
            added_drink = Drink(title=new_title, recipe=new_recipe)
            print("rec")
            # print(added_drink)
            added_drink.insert()
            print("rec after")
            returned_drinks.append(added_drink)
            return jsonify({
                            'success': True,
                            'drinks': [dr.long() for dr in returned_drinks]
                        })
        if len(returned_drinks) == 0:
            abort(404)
    except Exception:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drinkor appropriate status code
    indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(jwt, id):
    body = request.get_json()
    returned_drinks = []
    drink_to_be_update = Drink.query.filter(Drink.id == id).one_or_none()
    try:
        updated_title = body.get('title', None)
        updated_receipe = body.get('recipe', None)
        if drink_to_be_update is None:
            abort(404)
        if (updated_title is not None) and (updated_receipe is not None):
            drink_to_be_update.title = updated_title
            drink_to_be_update.receipe = json.dumps(updated_receipe)
            drink_to_be_update.update()
            returned_drinks.append(drink_to_be_update)

            return jsonify({
                            'status': 200,
                            'success': True,
                            'drinks': [dr.long() for dr in returned_drinks]
                        })
    except Exception:
        # print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where
    id is the id of the deleted record or appropriate status code indicating
     reason for failure
'''


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        deleted_drink = Drink.query.filter(Drink.id == id).one_or_none()
        if deleted_drink is None:
            raise abort(404)
        deleted_drink.delete()
        return jsonify({
                            'success': True,
                            'delete': deleted_drink.id
                        })
    except Exception:
        # print(sys.exc_info())
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found_hand(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
      }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

if __name__ == "__main__":
    app.debug = True
    app.run()
