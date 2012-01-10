'''
Created on Jan 9, 2012

@author: chenliu
'''

from xml.dom import minidom

class AWSResponse:
    """The base class for all Amazon Webservice Response"""
    def __init__(self, respfile):
        """Constructor"""
        self.dom = minidom.parse(respfile)
        self.responsedict = {}
        self.validate()
        
    def validate(self):
        """Validate whether the response is correct"""
        validnodes = self.dom.getElementsByTagName("IsValid")
        for n in validnodes:
            if(n.firstChild.nodeValue != "True"):
                self.responsedict["isValid"] = False
                return
        self.responsedict["isValid"] = True
    
    
