from flask import Flask, jsonify, current_app
from flask_restful import Resource, Api, reqparse
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import sqlite3
import datetime

# Set up Flask/Api/JWT/Parser for handling our connection and API logic
app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'DFJLDKJFD23432jnkdjfsSDjkh3'
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('mood')
parser.add_argument('username')
parser.add_argument('password')

bcrypt = Bcrypt(app)

class AppModel(Resource):
	''' Simple Model to be shared by all our API End Points with any helper variables/functions we need'''
	db_path = 'neuroflow.db'
		
	def __init__(self):
		''' Initialize database connection to be used by SubClasses'''
		self.con = sqlite3.connect(self.db_path)
		self.cur = self.con.cursor()
		super(AppModel, self).__init__()
		

class Mood(AppModel):
	''' Serves as Model for the Mood table and all /mood endpoints'''
	def get(self):
		''' Handle GET requests on the /mood endpoint. 
			For now there is just a single record in the DB and we return that.
		'''
		self.cur.execute('SELECT id,user_id,mood,created FROM moods ORDER BY created DESC LIMIT 1')
		rows = self.cur.fetchall()
		results = {}
		for row in rows:
			results.update({row[0]: {'user_id': row[1], 'mood': row[2], 'created': row[3]}})
		return jsonify(results)
		
	def post(self):
		''' Handle POST requests on the /mood endpoint.
			Update the single mood in the DB with args['mood'] that's been POSTed
		'''
		args = parser.parse_args()
		self.cur.execute('UPDATE moods SET mood = ?', [args['mood']])
		self.con.commit()
		return self.get()
		
class Auth(AppModel):
	''' Handles user login authorization'''
	
	def post(self):
		''' Check POSTed username/password and login with token if valid'''
		args = parser.parse_args()
		self.cur.execute('SELECT id,password FROM users WHERE username = ? LIMIT 1' , [args['username']])
		user = self.cur.fetchone()
		
		# No matching user with this username was found
		if user is None:
			return {'error': 'Bad username or password1'},401
			
		# The POSTed password does not match the hashed saved password
		if not check_password_hash(user[1], args['password']):
			return {'error': 'Bad username or password2'},401
			
		# Allow their token to be used for 7 days
		expires = datetime.timedelta(days=7)
		
		# Create token with the user.id as the identifier
		access_token = create_access_token(identity=str(user[0]), expires_delta=expires)
		
		# Return token so it can be set in the headers of other requests for the API
		return {'token': access_token}
		

# Anything with a /mood endpoint gets sent to the Mood class for handling
api.add_resource(Mood, '/mood')
api.add_resource(Auth, '/auth')


if __name__ == '__main__':
	app.run(debug=True)