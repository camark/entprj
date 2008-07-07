import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

class HelloBlog(webapp.RequestHandler):

    def initialize(self,request,response):
        webapp.RequestHandler.initialize(self,request,response)

        self.user = users.get_current_user()
        self.is_login = (self.user != None)
        self.is_admin = users.is_current_user_admin()
        
    def check_login(self, redirect_url='/'):
        if self.is_login:
            return True
        else:
            self.redirect(redirect_url)
            return False

    def check_admin(self, redirect_url='/'):
        if self.is_admin:
            return True
        else:
            self.redirect(redirect_url)
            return False
            

    def param(self,name,**kw):
        return self.request.get(name,**kw)

    def write(self,s):
        template_values={
            'msg':s
            }
        self.render('templates/message_blog.html',template_values)
        #self.response.out.write(s)

    def write_str(self,s):
        self.response.out.write(s)
        
    def render(self,name,values=None):
        if values==None:
            values=self.template_values

        self.response.out.write(template.render(name,values))
