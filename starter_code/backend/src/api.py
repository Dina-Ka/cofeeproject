import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import setup_db, Drink  # , db_drop_and_create_all
from auth.auth import AuthError, requires_auth

app = Flask(__name__)

setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_"POST /drinks and_create_all()


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns json {"success": True, "drinks": drinks}
        or appropriate status code indicating reason for failure
'''


# ************** GET drinks (done & tested) ***************
@app.route("/drinks", methods=['GET'])
def retrieve_drinks():
    allDrinks = Drink.query.all()
    drinks = []
    for drink in allDrinks:
        drinks.append(drink.short())
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# ********* Get Drinks Details (done & tested) **********
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(token):
    allDrinks = Drink.query.all()
    drinks = []
    for drink in allDrinks:
        drinks.append(drink.long())
    result = {
        'success': True,
        'drinks': drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


# ******** This endpoint is used to add new drink (done & tested) ***********
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drink(token):
    # if data is not empty
    if request.data:
        data = request.get_json()
        drinkstitle = data.get('title')
        if drinkstitle:
            drinkrecipe = data.get('recipe')
            try:
                drinkInsertion = Drink(
                    title=drinkstitle,
                    recipe=json.dumps(drinkrecipe)
                )
                Drink.insert(drinkInsertion)
                drinkInsertion = Drink.query.filter_by(
                    id=drinkInsertion.id
                ).first()
                drink = []
                drink.append(drinkInsertion.long())
                return jsonify({
                    'success': True,
                    'drinks': drink
                })
            except BaseException as error:
                print(error)
                abort(400)
        else:
            abort(400)
    else:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


# End point used to update and edit drinks (tested & done)
@app.route('/drinks/<int:drinkid>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(token, drinkid):
    drinksdata = request.get_json()
    drinktitle = drinksdata.get('title')
    drinkrecipe = drinksdata.get('recipe')
    if drinktitle:
        if drinkrecipe:
            try:
                editdrink = Drink.query.filter_by(id=drinkid).one_or_none()
                if editdrink is None:
                    abort(404)
                else:
                    editdrink.title = drinktitle
                    editdrink.recipe = json.dumps(drinkrecipe)
                    editdrink.update()
                    updatdrink = Drink.query.filter_by(id=drinkid).first()
                    drink = []
                    drink.append(updatdrink.long())
                    return jsonify({
                        'success': True,
                        'drinks': drink
                    })
            except BaseException as error:
                print(error)
                abort(400)
        else:
            abort(404)
    else:
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Delette a drink (done&tested)
@app.route('/drinks/<int:drinkid>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drinks(token, drinkid):
    try:
        deletedrink = Drink.query.filter_by(id=drinkid).one_or_none()
        if deletedrink:
            deletedrink.delete()
            return jsonify({
                'success': True,
                'deleted': drinkid
            })
        else:
            abort(404)
    except BaseException as error:
        print(error)
        abort(422)


'''
 error handling
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'unathorized to access this page'
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": 'Forbidden request'
    }), 403


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

