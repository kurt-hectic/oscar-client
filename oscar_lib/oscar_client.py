"""This module is responsible for the interactions with the OSCAR/Surface system"""

import os
import requests
import json
import datetime
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
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
    _WIGOSID_SEARCH_URL = '//rest/api/stations/approvedStations/wigosIds?q={wigosid}'
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

        response = requests.post( xml_upload_url , data=content , headers=headers  )

        status=None
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

    def load_station(self,wigos_id=None,internal_id=None,cache=False):
        """Loads the station identified by either its WIGOS ID `wigos_id` or OSCAR interal ID `internal_id` as WMDR XML.
        If a directory path `cache` is supplied, the method will try to load a station from this directory instead of loading it from OSCAR/Surface. 
        In case the station is not cached, it will be loaded as usual from OSCAR/Surface and then saved to file in the cache directory.
        This method uses the OSCAR/Surface internal API that is used by the GUI.
        Returns a representation of the station in WMDR XML.
        """
        if not wigos_id and not internal_id:
            raise ValueError("need either wigos id or internal ID")
            
        if cache:
            cachedir="cache/"
        
            if wigos_id:
                cache_filename = os.path.join(cachedir,"wigos-id-{}.xml".format(wigos_id))
            else:
                cache_filename = os.path.join(cachedir,"internal-id-{}.xml".format(internal_id))
                
            if os.path.isfile(cache_filename):
                return open(cache_filename,"rb").read()
        
        if not wigos_id:
            log.debug("trying to get wigos id for {}".format(internal_id))
            r = requests.get(self.oscar_url + "//rest/api/stations/station/{}/stationReport".format(internal_id))
            if r.status_code != 200:
                raise KeyError("{} not contained in OSCAR or cannot be downloaded {}".format(internal_id, r ))

            json = r.json()
            
            for wid in json["wigosIds"]:
                if wid["primary"]:
                    wigos_id = wid["wid"]
                    
            if not wigos_id:
                raise ValueError("station has not primary WIGOS ID")
        
        log.debug("getting XML for {}".format(wigos_id))
        r = requests.get(self.oscar_url + OscarClient._STATION_XML_DOWNLOAD + wigos_id )
        
        if r.status_code != 200:
            raise KeyError("{} not contained in OSCAR or cannot be downloaded".format(wigos_id))
        
        wmdr = r.content 
        
        if cache:
            with open(cache_filename,"wb") as f:
                f.write(wmdr)

        return wmdr


    def oscar_search(self,params={}):
        """Performs a search in OSCAR for stations according to the parameters supplied.
        Returns a JSON structure with the result in the field `data` and meta information such as the length of the result contained in the field `meta`.
        The parameters and accepted values are documented in the OSCAR/Surface User Manual https://library.wmo.int/index.php?lvl=notice_display&id=20824#.XkQE9Ij_rRb
        """
        oscar_search_url = self.oscar_url + OscarClient._OSCAR_SEARCH_URL
        log.info("searching for {} at {}".format(params,oscar_search_url))
        rsp = self.session.get( oscar_search_url , params=params )

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
       
    def wigos_to_internal_id(self,wigosid):
        """Maps the `wigosid` to the internal id of the corresponding station in OSCAR
        Returns the `internal_id` of OSCAR.
        """
    
        wigosid_search_url = self.oscar_url + OscarClient._WIGOSID_SEARCH_URL
        rsp=self.session.get( wigosid_search_url.format(wigosid=wigosid) )
        stations = json.loads(rsp.content)
        internal_id = stations[0]["id"]
        return internal_id
    
        
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
