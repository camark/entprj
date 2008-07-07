import wsgiref.handlers
import xmlrpclib
import sys
import cgi
from datetime import datetime
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from google.appengine.api import users
from google.appengine.ext import db

sys.path.append('modules')
sys.path.append('models')
from helloblog import *
from blog import *
from category import *

def check_api_user_pass(username,password):
    user = users.User(username)

    if not user or password != '1234':
        return None

    return user

def metaWeblog_newPost(blogid,username,password,content,publish):
    user = check_api_user_pass(username,password)

    if not user:
        raise Exception, ' access denied'

    if publish:
        if content.has_key('categories') and len(content['categories'])>0:            
            category = Category.all().filter('name=',(content['categories'])[0]).fetch(1)
            if not category:
                category = Category.all().fetch(1)
        else:
            category = Category.all().fetch(1)

        _blog=Blog(
            title = content['title'],
            content = unicode(content['description']),
            author = user,
            category = category[0]
            )

        key=_blog.put()
        return str(key.id())

def metaWeblog_editPost(blogid,username,password,content,publish):
    user = check_api_user_pass(username,password)

    if not user:
        raise Exception, ' access denied'

    if publish:
        if content.has_key('categories') and len(content['categories'])>0:
            category = Category.all().filter('name=',content['categories'][0]).fetch(1)
            if not category:
                category = Category.all().fetch(1)
        else:
            category = Category.all().fetch(1)
            
        _blog=Blog.get_by_id(int(blogid))

        if not _blog:
            raise Exception,'no such blog by id %s' %(blogid)
        
        _blog.title=content['title']
        _blog.content=unicode(content['description'])
        _blog.author=user
        _blog.category=category[0]

        _blog.put()

        return True
    else:
        return True

def metaWeblog_getCategories(blogid, username, password):
    user = check_api_user_pass(username, password)
    if not user:
        raise Exception, 'access denied'

    categories = []
    all_category = Category.all()
    for _cat in all_category:
        categories.append({'description' : _cat.name, 'title' : _cat.name})

    return categories

def metaWeblog_getPost(postid, username, password):
    user = check_api_user_pass(username, password)
    if not user:
            raise Exception, 'access denied'

    _blog = Blog.get_by_id(int(postid))

    if not _blog:
        raise Exception,'no such blog'
    
    return {
        'postid' : postid,
        'dateCreated' : _blog.date,
        'title' : _blog.title,
        'description' : unicode(_blog.content),
        'categories' : [_blog.category.name],
        'publish' : True
        }

def metaWeblog_getRecentPosts(postid, username, password, numberOfPosts):
    _blogs = Blog.all().order('-date').fetch(min(int(numberOfPosts),5))

    result = []

    for _blog in _blogs:
        result.append({
            'postid' : _blog.key().id(),
            'dateCreated' : _blog.date,
            'title' : _blog.title,
            'description' : unicode(_blog.content),
            'categories' : _blog.category.name,
            'publish' : True
            }
                      )
    return result

def blogger_getUsersBlogs(discard, username, password):
    if not check_api_user_pass(username, password):
            raise Exception, 'access denied'

    return [{'url' : 'http://superwar3fan.appspot.com' + '/', 'blogid' : 'helloblog_001', 'blogName' : 'HelloBlog'}]

def blogger_deletePost(appkey, postid, username, password, publish):
    user = check_api_user_pass(username, password)
    if not user:
            raise Exception, 'access denied'

    _blog = Blog.get_by_id(int(postid))

    if not blog:
        raise Exception,'no such blog'

    _blog.delete()

    return True
    
    
class HelloBlogXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    def __init__(self,funs):
        SimpleXMLRPCDispatcher.__init__(self,True,'utf-8')
        self.funcs=funs
        
dispatcher = HelloBlogXMLRPCDispatcher({
    'blogger.getUsersBlogs' : blogger_getUsersBlogs,
    'blogger.deletePost' : blogger_deletePost,
    'metaWeblog.newPost' : metaWeblog_newPost,
    'metaWeblog.editPost' : metaWeblog_editPost,
    'metaWeblog.getCategories' : metaWeblog_getCategories,
    'metaWeblog.getPost' : metaWeblog_getPost,
    'metaWeblog.getRecentPosts' : metaWeblog_getRecentPosts,
    }
                                       )


# {{{ Handlers
class CallApi(HelloBlog):
	def get(self):
		#Logger(request = self.request.uri, response = '----------------------------------').put()
		self.write('<h1>please use POST</h1>')

	def post(self):
		#self.response.headers['Content-Type'] = 'application/xml; charset=utf-8'
		request = self.request.body
		response = dispatcher._marshaled_dispatch(request)
		#Logger(request = unicode(request, 'utf-8'), response = unicode(response, 'utf-8')).put()
		self.write(response)

class View(HelloBlog):
	def get(self):
		if self.check_admin(users.create_login_url(self.request.uri)):
			self.write('<html><body><h1>Logger</h1>')
			for log in Logger.all().order('-date'):
				self.write("<p>date: %s</p>" % log.date)
				self.write("<h1>Request</h1>")
				self.write('<pre>%s</pre>' % cgi.escape(log.request))
				self.write("<h1>Reponse</h1>")
				self.write('<pre>%s</pre>' % cgi.escape(log.response))
				self.write("<hr />")
			self.write('</body></html>')		
def main():
	application = webapp.WSGIApplication(
			[
			    ('/api/xml-rpc', CallApi),
                            ('.*',View),
				],
			debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
