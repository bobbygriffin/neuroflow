from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import sqlite3

# Set up Flask/Api/Parser for handling our connection and API logic
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('mood')

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

# Anything with a /mood endpoint gets sent to the Mood class for handling
api.add_resource(Mood, '/mood')


if __name__ == '__main__':
	app.run(debug=True)
