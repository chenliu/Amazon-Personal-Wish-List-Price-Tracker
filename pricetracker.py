'''
Created on Jan 9, 2012

@author: chenliu
'''

import sys
import json
import logging

from amazonapi.request import ItemLookUpRequest
from amazonapi.response import AWSResponse

class PriceTrackResponse(AWSResponse):
    """A typical price-tracker response. Two items in one request with same item id. 
    One is the item attributes response group. And the other is the offer summary response group"""
    
    def __init__(self, respfile):
        AWSResponse.__init__(self, respfile)
    
    def validate(self):
        AWSResponse.validate(self)
        if(self.responsedict["isValid"] == True):
            if(len(self.dom.getElementsByTagName("OfferSummary")) != 1 and len(self.dom.getElementsByTagName("ItemAttributes")) != 1):
                self.responsedict["isValid"] = False
     
    def get_lowest_price(self):
        if(self.responsedict["isValid"] == False):
            sys.stderr.write("The response is not valid")
            return None
        newprice = self.dom.getElementsByTagName("LowestNewPrice")
        if(len(newprice) == 1):
            self.responsedict["Price(New)"] = int(newprice[0].getElementsByTagName("Amount")[0].firstChild.nodeValue)
        usedprice = self.dom.getElementsByTagName("LowestUsedPrice")
        if(len(usedprice) == 1):
            self.responsedict["Price(Used)"] = int(usedprice[0].getElementsByTagName("Amount")[0].firstChild.nodeValue)
    
    def get_list_price(self):
        """Get the list price of the product"""
        if(self.responsedict["isValid"] == False):
            sys.stderr.write("The response is not valid")
            return None
        listprice = self.dom.getElementsByTagName("ListPrice")
        if(len(listprice) == 1):
            self.responsedict["ListPrice"] = int(listprice[0].getElementsByTagName("Amount")[0].firstChild.nodeValue)
            
    def get_discount(self):
        """Get the discount of the product"""
        price = self.responsedict.get("Price(New)", None)
        list_price = self.responsedict.get("ListPrice", None)
        if(price != None and list_price != None):
            self.responsedict["Discount"] = int((1 - (float(price) / list_price)) * 100)
            
    def get_item_info(self):
        """Get the item info of the product"""
        self.responsedict["Title"] = self.dom.getElementsByTagName("Title")[0].firstChild.nodeValue
        self.responsedict["Url"] = self.dom.getElementsByTagName("DetailPageURL")[0].firstChild.nodeValue
        
            
    def dump_result(self):
        """Return the result dict"""
        return self.responsedict
            
class PriceTrackRequest(ItemLookUpRequest):
    """A standard price track request"""
    def __init__(self, itemid, maxprice = None, minprice = None, mindiscount = None):
        """Constructor"""
        self.max_price = maxprice
        self.min_price = minprice
        self.min_discount = mindiscount
        ItemLookUpRequest.__init__(self)
        self.params["ItemLookup.1.ItemId"] = itemid
        self.params["ItemLookup.2.ItemId"] = itemid
        self.params["ItemLookup.1.ResponseGroup"] = "ItemAttributes"
        self.params["ItemLookup.2.ResponseGroup"] = "OfferSummary"
    
    def get_response(self):
        response = PriceTrackResponse(respfile = self.make_query())
        response.get_lowest_price()
        response.get_list_price()
        response.get_discount()
        response.get_item_info()
        if(self.min_discount != None and self.min_discount > response.responsedict.get("Discount", 0)):
            logging.debug(self.min_discount)
            response.responsedict["match"] = False
        else:
            maxp = sys.maxint
            if(self.max_price != None):
                maxp = self.max_price + 1
                logging.debug(maxp)
            minp = -1
            if(self.min_price != None):
                minp = self.min_price - 1
                logging.debug(minp)
            p = min(response.responsedict.get("Price(New)", sys.maxint), response.responsedict.get("Price(Used)", sys.maxint))
            if(minp < p < maxp):
                response.responsedict["match"] = True
            else:
                response.responsedict["match"] = False
        return response
    
    def get_json_response(self):
        return json.dumps(self.get_response().responsedict)
    
def handle_single_request(asin, maxprice = None, minprice = None, mindiscount = None):
    request = PriceTrackRequest(asin, maxprice, minprice, mindiscount)
    response = request.get_response()
    return json.dumps(response.dump_result())
    
if __name__ == '__main__':
    request = PriceTrackRequest("B000PFLKAY", 200000, 0, 10)
    response = request.get_response()
    print response.dom.toprettyxml()
    print json.dumps(response.dump_result())