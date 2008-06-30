
#War3Blog 0.1

import datetime
from google.appengine.ext import db
from category import Category

class Blog(db.Model):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    category = db.ReferenceProperty(Category,required=True,collection_name='blogs')

class Comment(db.Model):
    detail = db.StringProperty(required=True)
    author = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    blog = db.ReferenceProperty(Blog,required=True,collection_name='comments')


