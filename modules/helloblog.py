import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class HelloBlog(webapp.RequestHandler):
    def check_login(self):
        pass

    def param(self,name,**kw):
        return self.request.get(name,**kw)

    def write(self,s):
        self.response.out.write(s)

    def render(self,name,values=None):
        if values==None:
            values=self.template_values

        self.response.out.write(template.render(name,values))
