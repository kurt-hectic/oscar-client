"""This module is responsible for the interactions with the OSCAR/Surface system"""

import os
import requests
import json
import logging

#logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
__pdoc__ = {} 

class OscarClient(object):


    # do not document deprecated methods
    __pdoc__["OscarClient.oscarSearch"] = False
    __pdoc__["OscarClient.uploadXML"] = False
    __pdoc__["OscarClient.getInternalIDfromWigosId"] = False


    _OSCAR_SEARCH_URL = '//rest/api/search/station'
    _STATION_SEARCH_URL = '//rest/api/search/station?stationClass={stationClass}'
    _STATION_XML_UPLOAD = '//rest/api/wmd/upload'
    _STATION_XML_DOWNLOAD = '//rest/api/wmd/download/'

    OSCAR_DEFAULT = 'https://oscar.wmo.int/surface'
    """The URL of the production system"""
    
    OSCAR_DEPL = "https://oscardepl.wmo.int/surface"
    """The URL of the testing system"""


    def __init__(self,oscar_url=None,token=None):
        """
        Initializes an OSCAR client instance, where `oscar_url` is the URL of OSCAR, defaulting to the production system,
        `token` is the OSCAR API token needed for write operations.
        """
        self.oscar_url = oscar_url if oscar_url else OscarClient.OSCAR_DEFAULT
        self.token = token
        self.session = requests.Session()


    def upload_XML(self,xml):
        """
        Uploads the string content passed in `xml` as WMDR to OSCAR.
        Returns `SUCCESS`,`SUCCESS_WITH_WARNINGS`,`AUTH_ERROR` or `SERVER_ERROR`
        """
    
        if not self.token:
            raise AttributeError("no token configured.. cannot upload")
    
        headers = { 'X-WMO-WMDR-Token' : self.token } 

        content = xml.encode("utf8")
        xml_upload_url = self.oscar_url + OscarClient._STATION_XML_UPLOAD

        status=None
        with requests.post( xml_upload_url , data=content , headers=headers  ) as response:

            if response.status_code ==  200:
                # reponse:
                response = json.loads(response.content)
                if response["xmlStatus"] in ['SUCCESS_WITH_WARNINGS','SUCCESS']:
                    log.info("upload ok, new id {id} {logs}".format(id=response["id"],logs=response["logs"]))
                else:
                    log.info("upload failed.. the log is {logs}".format(logs=response["logs"]) )

                status = response["xmlStatus"]
            
            elif response.status_code == 401:
                log.info("Access not granted (401) error")
                status = "AUTH_ERROR"        
            else:
                log.info("processing error on server side {} {}".format(response.status_code,response.content))
                status = "SERVER_ERROR"
            
        return status

    def load_station(self,wigos_id=None,cache=False):
        """Loads the station identified by its WIGOS ID `wigos_id` as WMDR XML.
        If a directory path `cache` is supplied, the method will try to load a station from this directory instead of loading it from OSCAR/Surface. 
        In case the station is not cached, it will be loaded as usual from OSCAR/Surface and then saved to file in the cache directory.
        This method uses the OSCAR/Surface internal API that is used by the GUI.
        Returns a representation of the station in WMDR XML.
        """
        if not wigos_id:
            raise ValueError("need to supply wigos")
            
        if cache:
            cachedir="cache/"
        
            cache_filename = os.path.join(cachedir,"wigos-id-{}.xml".format(wigos_id))
                
            if os.path.isfile(cache_filename):
                return open(cache_filename,"rb").read()
        
        log.debug("getting XML for {}".format(wigos_id))
        with requests.get(self.oscar_url + OscarClient._STATION_XML_DOWNLOAD + wigos_id ) as r:
        
            if r.status_code != 200:
                raise KeyError("{} not contained in OSCAR or cannot be downloaded".format(wigos_id))
        
            wmdr = r.content 
        
            if cache:
                with open(cache_filename,"wb") as f:
                    f.write(wmdr)

            return wmdr
        
        
    def wigos_to_internal_id(self,wigos_id):
        """Maps the `wigosid` to the internal id of the corresponding station in OSCAR
        Returns the `internal_id` of OSCAR.
        """
    
        res = self.oscar_search( {"wigosId" : wigos_id } )
        
        if 'data' in res and res["meta"]["length"]==1:
            return int(res["data"][0]["id"])
        else:
            return None


    def oscar_search(self,params={}):
        """Performs a search in OSCAR for stations according to the parameters supplied.
        Returns a JSON structure with the result in the field `data` and meta information such as the length of the result contained in the field `meta`.
        The parameters and accepted values are documented in the OSCAR/Surface User Manual https://library.wmo.int/index.php?lvl=notice_display&id=20824#.XkQE9Ij_rRb
        """
        oscar_search_url = self.oscar_url + OscarClient._OSCAR_SEARCH_URL
        log.info("searching for {} at {}".format(params,oscar_search_url))
        with self.session.get( oscar_search_url , params=params ) as rsp:
            if rsp.status_code == 200:
                myjson={}
                myjson["data"] = json.loads(rsp.content)
                myjson["meta"] = { 'length' : len(myjson["data"]) }

                return myjson 

            else:
                ret = {}
                ret["status_code"] = rsp.status_code
                ret["message"] = str(rsp.content) 

                return ret
       

    def close(self):
        """Return allocated ressources"""
        self.session.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    # backwards compatibility methods
    def uploadXML(self,xml):
        log.warning("deprecated: use upload_XML instead")
        return self.upload_XML(xml)
        
    def oscarSearch(self,params={}):
        log.warning("deprecated: use oscar_search instead")
        return self.oscar_search(params)
        
    def getInternalIDfromWigosId(self,wigosid):
        log.warning("deprecated: use wigos_to_internal_id instead")
        return self.wigos_to_internal_id(wigosid)
