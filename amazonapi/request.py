'''
Created on Jan 8, 2012

@author: chenliu
'''

import urllib
import datetime
import hmac
import hashlib
import base64
from xml.dom import minidom

from tz import Pacific

class AWSRequest:
    """The base class of Amazon.com request"""
    
    ENDPOINT = "http://aws.amazonaws.com/onca/xml"
    SERVICE = "AWSECommerceService"
    AWSSECURITYKEY = "SecurityKey"
    AWSACCESSID = "AccessId"
    AWSASSOCIATEID = "personalprice-20"
    
    def __init__(self, operation = "", params = None, accesskeyid = None, associatetag = None):
        self.params = {}
        self.params["Operation"] = operation
        if(params != None):
            for k, v in params.items():
                self.params[k] = v
        if(accesskeyid != None):
            self.params["AWSAccessKeyId"] = accesskeyid
        else:
            self.params["AWSAccessKeyId"] = AWSRequest.AWSACCESSID
        if(associatetag != None):
            self.params["AssociateTag"] = associatetag
        else:
            self.params["AssociateTag"] = AWSRequest.AWSASSOCIATEID
        
    def set_id(self, accesskeyid, associatetag = None):
        """Set the access IDs for the request"""
        self.params["AWSAccessKeyId"] = accesskeyid
        self.params["AssociateTag"] = associatetag
        
    def set_param(self, k, v):
        """Set the parameter with key k and value v"""
        self.params[k] = v
        
    def set_response_group(self, responsegroup):
        """Set response group"""
        self.params["ResponseGroup"] = responsegroup
        
    def generate_url(self):
        '''Generate the timestamp, signature and give the final url'''
        timestamp = datetime.datetime.now(tz=Pacific).isoformat()
        self.params["Timestamp"] = timestamp
        sorted_params = []
        for k, v in self.params.items():
            sorted_params.append("%s=%s" % (k, urllib.quote(v)))
        sorted_params = sorted(sorted_params)
        req_str = "&".join(sorted_params)
        req_str = "GET\nwebservices.amazon.com\n/onca/xml\n" + req_str
        signature = base64.b64encode(hmac.new(AWSRequest.AWSSECURITYKEY, req_str, hashlib.sha256).digest())
        signature = urllib.quote(signature)
        req_url = "http://webservices.amazon.com/onca/xml?"
        req_url += '&'.join(sorted_params)
        req_url += "&Signature=%s" % signature
        print req_url
        return req_url
        
    def make_query(self):
        '''make a query, return the response'''
        resp = urllib.urlopen(self.generate_url())
        return resp
        
class ItemLookUpRequest(AWSRequest):
    """ItemLookupRequest
    Valid parameters:
    Condition [New | Used | Collectible | Refurbished, All]
    IdType [ASIN | SKU | UPC | EAN | ISBN]
    IncludeReviewsSummary [True | False]
    ItemId comma separated strings(up to 10)
    MerchantId Amazon
    RelatedItemPage int(x10)
    RelationshipType http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/SuggestingSimilarItemstoBuy.html#RelationshipTypes
    ReviewPage 1-20
    ReviewSort [-SubmissionDate | -HelpfulVotes | HelpfulVotes | -OverallRating | OverallRating | SubmissionDate]
    SearchIndex http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/APPNDX_SearchIndexValues.html
    TagPage 1-10
    TagsPerPage number of tags return int
    TagSort [-FirstUsed | -LastUsed | -Name | Usages]
    TruncateReviewsAt int
    VariationPage 1-150
    ResponseGroup [ Accessories | BrowseNodes | EditorialReview | Images | ItemAttributes | ItemIds | Large | Medium | OfferFull | Offers | PromotionSummary | OfferSummary| RelatedItems | Reviews | SalesRank | Similarities | Tracks | VariationImages | Variations (US only) | VariationSummary]"""
    
    def __init__(self):
        """Initializer"""
        AWSRequest.__init__(self, operation = "ItemLookup")
        
    def set_item_id(self, itemid, idtype = None):
        """Set Item Id"""
        self.params["ItemId"] = itemid
        if(idtype != None):
            self.params["IdType"] = idtype
    
class ItemSearchRequest(AWSRequest):
    """ItemSearchRequest
    It seems it has too many restrictions and may not work perfectly"""
    def __init__(self, index="All"):
        """Initializer"""
        AWSRequest.__init__(self, operation = "ItemSearch")
        self.params["SearchIndex"] = index
        
    def set_search_index(self, searchindex):
        """Set SearchIndex"""
        self.set_search_index(searchindex)
        
    def set_keywords(self, keywords):
        """Set the keywords"""
        self.params["Keywords"] = keywords
    
    def set_title(self, title):
        """Set the title keywords"""
        self.params["Title"] = title
        
    def set_max_price(self, max_price):
        """Set max_price
        Only available when SearchIndex != All"""
        if(self.params["SearchIndex"] != "All" and self.params["SearchIndex"] != "Blended"):
            self.params["MaximumPrice"] = str(max_price)
        
    def set_min_price(self, min_price):
        """Set min_price
        Only available when SearchIndex != All"""
        if(self.params["SearchIndex"] != "All" and self.params["SearchIndex"] != "Blended"):
            self.params["MinimumPrice"] = str(min_price)
        
    def set_min_percentage(self, min_percentage):
        """Set MinPercentageOff
        Only available when SearchIndex != All
        Other indices which do not support the parameters including virtual products, comp hardwares, music/video/games etc.
        Note: Not all the cases are caught by the program!!
        For all information, refer to http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/USSearchIndexParamForItemsearch.html"""
        if(self.params["SearchIndex"] != "All" and self.params["SearchIndex"] != "Blended"):
            self.parmas["MinPercentageOff"] = str(min_percentage)

if __name__ == "__main__":
    asin = "B000PFLKAY"
    request = ItemLookUpRequest()
    #request.params["ItemLookup.1.ItemId"] = asin
    request.params["ItemLookup.1.ItemId"] = asin
    request.params["ItemLookup.2.ItemId"] = asin
    request.params["ItemLookup.1.ResponseGroup"] = "ItemAttributes"
    request.params["ItemLookup.2.ResponseGroup"] = "OfferSummary"
    respdom = minidom.parse(request.make_query())
    print respdom.toprettyxml()