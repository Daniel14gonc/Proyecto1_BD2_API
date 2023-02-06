from flask_restful import Api
from models import User, Tweet, UserAuthenticator, Comments
from flask import Flask
from flask_cors import CORS
  
# creating the flask app
app = Flask(__name__)
cors = CORS(app)
# creating an API object
api = Api(app)


# adding the defined resources along with their corresponding urls
api.add_resource(User, '/user/')
api.add_resource(Tweet, '/tweet/')
api.add_resource(UserAuthenticator, '/userAuth/')
api.add_resource(Comments, '/comments/')


  
# driver function
if __name__ == '__main__':
  
    app.run(debug = True)