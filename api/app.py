from flask_restful import Api
from models import User, Tweet, UserAuthenticator, Comments, Like, Perfil, Description, HomeImage, Hashtags, CountriesInteraction, LikesAnalytics, AnalyticsComments, TweetsPerYear, Fans, TweetComment
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
api.add_resource(Like, '/like/')
api.add_resource(Perfil, '/perfil/')
api.add_resource(Hashtags, '/hashtags/')
api.add_resource(LikesAnalytics, '/LikesA/')
api.add_resource(CountriesInteraction, '/countries/')
api.add_resource(AnalyticsComments, '/commentsA/')
api.add_resource(TweetsPerYear, '/tweets-per-year/')
api.add_resource(Fans, '/fans/')
api.add_resource(TweetComment, '/tweetComment/')
api.add_resource(HomeImage, '/homeImage/')
api.add_resource(Description, '/description/')



  
# driver function
if __name__ == '__main__':
  
    app.run(debug = True)