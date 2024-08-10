from flask import Flask, jsonify, Blueprint, request, session
from DAO import UserDAO, ProfessorDAO
import secrets
from entities.User import User

app = Flask(__name__)
users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
def get_users():
    users = UserDAO.getAllUsers()
    try:
        if users:
            serialized_users = [user.__dict__ for user in users]
            return jsonify({"data": serialized_users}), 200
        return jsonify({"message": "No content"}), 204
    except Exception as e:
        return jsonify({"message": "an error has occurred: " + str(e)}), 500


@users_bp.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = UserDAO.getOneUser(id)
    print(user)
    if user:
        serialized_user = user.__dict__
        return jsonify(serialized_user), 200
    return jsonify({"message": "User not found"}), 404

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(data['id'], data['name'], data['password'], data['ddd'], data['number'])
    try:
        UserDAO.insertUser(new_user)
    except Exception as e:
        return jsonify({"message": "an error has occurred: " + str(e)}), 500
    return jsonify({"message": "User created successfully"}), 200


@users_bp.route('/users/<id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    new_user = User(data['id'], data['name'], data['password'], data['ddd'], data['number'])
    try:
        UserDAO.updateUser(id, new_user)
    except Exception as e:
        return jsonify({"message": "an error has occurred: " + str(e)}), 500
    return jsonify({"message": "User updated successfully"}), 200


@users_bp.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        UserDAO.deleteUser(id)
    except Exception as e:
        return jsonify({"message": "an error has occurred: " + str(e)}), 500
    return jsonify({"message": "User deleted successfully"}), 200


@users_bp.route('/auth', methods=['POST'])
def auth():
    authorization = False
    data = request.get_json()
    id = data['id']
    password = str(data['password'])
    user = UserDAO.getOneUser(id)
    isProfessor = (ProfessorDAO.getOneProfessor(id) is not None)
    print(isProfessor)
    if user:
        if user.password == password:
            authorization = secrets.token_hex(16)  # Generate a random authorization token
    if authorization:
        print(user.id)
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"authorization": authorization, "user": {"id": user.id, "name": user.name, "isProfessor": isProfessor}})
    else:
        session.clear()  # Remove all session variables
        return jsonify({"authorization": False, "message": "Login failed"})
