from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Get all messages
@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_list = [{
        'id': msg.id,
        'body': msg.body,
        'username': msg.username,
        'created_at': msg.created_at,
        'updated_at': msg.updated_at
    } for msg in messages]
    
    return jsonify(messages_list), 200

# Get a message by ID
@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = Message.query.get(id)

    if message is None:
        return make_response(jsonify({"error": "Message not found"}), 404)

    return jsonify({
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    }), 200

# Create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()

    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return make_response(jsonify({"error": "Both body and username are required"}), 400)

    new_message = Message(
        body=body,
        username=username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        'id': new_message.id,
        'body': new_message.body,
        'username': new_message.username,
        'created_at': new_message.created_at,
        'updated_at': new_message.updated_at
    }), 201

# Update a message's body
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    
    if message is None:
        return make_response(jsonify({"error": "Message not found"}), 404)

    data = request.get_json()
    
    if 'body' in data:
        message.body = data['body']
    
    message.updated_at = datetime.utcnow()
    
    db.session.commit()

    return jsonify({
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    }), 200

# Delete a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    
    if message is None:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()

    return make_response(jsonify({"message": "Message deleted successfully"}), 200)

if __name__ == '__main__':
    app.run(port=5555)
