"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Users endpoints
@app.route('/user', methods=['GET'])
def get_all_users():
    user_query = User.query.all()
    user_list = list(map(lambda x: x.serialize(), user_query))
    return jsonify(user_list), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.serialize()), 200

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return jsonify({"msg": "Email and password are required"}), 400

    user = User(email=email, password=password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback() # Si hay un error, deshacemos los cambios
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting user", "error": str(e)}), 500

# Characters endpoints
@app.route('/character', methods=['GET'])
def get_all_characters():
    character_query = Character.query.all()
    character_list = list(map(lambda x: x.serialize(), character_query))
    return jsonify(character_list), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/character', methods=['POST'])
def create_character():
    body = request.get_json()
    name = body.get("name")
    description = body.get("description")

    if name is None:
        return jsonify({"msg": "Name is required"}), 400

    character = Character(name=name, description=description)

    try:
        db.session.add(character)
        db.session.commit()
        return jsonify({"msg": "Character created successfully"}), 201
    except Exception as e:
        db.session.rollback() # Si hay un error, deshacemos los cambios
        return jsonify({"msg": "Error creating character", "error": str(e)}), 500
    
@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)

    if character is None:
        return jsonify({"msg": "Character not found"}), 404

    try:
        db.session.delete(character)
        db.session.commit()
        return jsonify({"msg": "Character deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting character", "error": str(e)}), 500

# Planets endpoints
@app.route('/planet', methods=['GET'])
def get_all_planets():
    planet_query = Planet.query.all()
    planet_list = list(map(lambda x: x.serialize(), planet_query))
    return jsonify(planet_list), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/planet', methods=['POST'])
def create_planet():
    body = request.get_json()
    name = body.get("name")
    climate = body.get("climate")
    population = body.get("population")

    if name is None:
        return jsonify({"msg": "Name is required"}), 400

    planet = Planet(name=name, climate=climate, population=population)

    try:
        db.session.add(planet)
        db.session.commit()
        return jsonify({"msg": "Planet created successfully"}), 201
    except Exception as e:
        db.session.rollback() # Si hay un error, deshacemos los cambios
        return jsonify({"msg": "Error creating planet", "error": str(e)}), 500
    
@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    try:
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": "Planet deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting planet", "error": str(e)}), 500

# favorites endpoints

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites_query = Favorite.query.filter_by(user_id=user_id).all()
    favorites_list = list(map(lambda x: x.serialize(), favorites_query))
    
    return jsonify(favorites_list), 200

@app.route('/user/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    body = request.get_json()
    character_id = body.get("character_id")
    planet_id = body.get("planet_id")

    if character_id is None and planet_id is None:
        return jsonify({"msg": "Must provide either character_id or planet_id"}), 400

    if character_id is not None and planet_id is not None:
        return jsonify({"msg": "Cannot provide both character_id and planet_id"}), 400

    if character_id is not None:
        favorite = Favorite(user_id=user_id, character_id=character_id)
    else:
        favorite = Favorite(user_id=user_id, planet_id=planet_id)

    try:
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite added successfully"}), 201
    except Exception as e:
        db.session.rollback() # Si hay un error, deshacemos los cambios
        return jsonify({"msg": "Error adding favorite", "error": str(e)}), 500


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    # 1. Obtenemos el user_id (por ahora del body para simplificar)
    body = request.get_json()
    user_id = body.get("user_id")

    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()

    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite character deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting favorite", "error": str(e)}), 500

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # 1. Obtenemos el user_id (por ahora del body para simplificar)
    body = request.get_json()
    user_id = body.get("user_id")

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite planet deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting favorite", "error": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
