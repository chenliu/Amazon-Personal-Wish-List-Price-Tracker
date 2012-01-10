'''
Created on Jan 9, 2012

@author: chenliu
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from pricetracker import handle_single_request

class SingleRequestHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        asin = self.request.get("asin")
        maxprice = self.request.get("maxprice", None)
        if(maxprice != None):
            maxprice = int(float(maxprice) * 100)
        minprice = self.request.get("minprice", None)
        if(minprice != None):
            minprice = int(float(minprice) * 100)
        mindiscount = self.request.get("mindiscount", None)
        if(mindiscount != None):
            mindiscount = int(mindiscount)
        data = handle_single_request(asin, maxprice, minprice, mindiscount)
        self.response.out.write(data)
        
application = webapp.WSGIApplication(
                                     [
                                      ('/singlerequest', SingleRequestHandler)],
                                     debug = True)

def main():
    run_wsgi_app(application)
    
if __name__ == '__main__':
    main()