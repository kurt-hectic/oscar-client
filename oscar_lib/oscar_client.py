"""This module is responsible for the interactions with the OSCAR/Surface system"""

import os
import requests
import json
import logging

logger = logging.getLogger(__name__)
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
    _WIGOS_ID_SEARCH_URL = '//rest/api/stations/identify'

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
        """Uploads the string content passed in `xml` as WMDR to OSCAR.
        
        Parameters:
        xml (str): the WIGOS MD record to be uploaded
        
        Returns:
        status code (str) with values: `SUCCESS`,`SUCCESS_WITH_WARNINGS`,`AUTH_ERROR`,`BUSINESS_RULE_ERROR` or `SERVER_ERROR`
        """
    
        logger.debug("upload_XML" + str(xml))
        status,message=self.upload_XML_detailed(xml)
        return status
    
    def upload_XML_detailed(self,xml):
        """Uploads the string content passed in `xml` as WMDR to OSCAR.
        
        Parameters:
        xml (str): the WIGOS MD record to be uploaded
        
        Returns:
        status code (str) with values: `SUCCESS`,`SUCCESS_WITH_WARNINGS`,`AUTH_ERROR`,`BUSINESS_RULE_ERROR` or `SERVER_ERROR`
        message (str): the log message
        """
        
        if not self.token:
            raise AttributeError("no token configured.. cannot upload")
    
        logger.debug("upload_XML_detailed" + str(xml))
        
    
        headers = { 'X-WMO-WMDR-Token' : self.token } 

        content = xml.encode("utf8")
        xml_upload_url = self.oscar_url + OscarClient._STATION_XML_UPLOAD

        status=None
        with requests.post( xml_upload_url , data=content , headers=headers  ) as resp:
            #logger.debug("response: ", resp.text )

            try:
                if resp.status_code ==  200:
                    # reponse:
                    #response = json.loads(resp.content)
                    response = resp.json()

                    if response["xmlStatus"] in ['SUCCESS_WITH_WARNINGS','SUCCESS']:
                        status = response["xmlStatus"]
                        message = "upload ok, new id {id} {logs}".format(id=response["id"],logs=response["logs"])
                    
                    elif response["xmlStatus"] == 'VALID_XML_WITH_ERRORS_OR_WARNINGS':
                        if 'The "facility" is discarded' in response["logs"]:
                            status = 'BUSINESS_RULE_ERROR'
                            message = "upload ok, but content rejected: {logs}".format(logs=response["logs"])
                        else:
                            status = response["xmlStatus"]
                            message = "upload ok, new id {id} {logs}".format(id=response["id"],logs=response["logs"])
                    else:
                        status = response["xmlStatus"]
                        message = "upload failed with status: {status} the log is {logs}".format(status=status,logs=response["logs"]) 

                    logger.info(message)
                
                elif resp.status_code == 401:
                    message = "Access not granted (401) error"
                    status = "AUTH_ERROR"        
                    logger.info(message)
                else:
                    status = "SERVER_ERROR"
                    message = "processing error on server side {} {}".format(response.status_code,response.content)
                    logger.info(message)
            except:
                status = "SERVER_ERROR"
                message = "OSCAR/Surface did not return the expected return format.. OSCAR may be down"
                
            
        logger.info("status: {} message: {} ".format(status,message))
        return status, message

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
        
        logger.debug("getting XML for {}".format(wigos_id))
        with requests.get(self.oscar_url + OscarClient._STATION_XML_DOWNLOAD + wigos_id ) as r:
        
            if r.status_code != 200:
                logger.info("cannot retrieve station: status: {} message: {} ".format(r.status_code,r.text))
                raise ValueError("{} not contained in OSCAR or cannot be downloaded".format(wigos_id))
        
            wmdr = r.content 
        
            if cache:
                with open(cache_filename,"wb") as f:
                    f.write(wmdr)

            return wmdr
        
        
    def get_wigos_ids(self,search_wigos_ids):
        """Returns all wigos identifiers of the indicated stations 
        The return result respects the order of the parameters passed. None indicated that the WIGOS ID was not found in OSCAR
        """
    
        wigosid_search_url = self.oscar_url + OscarClient._WIGOS_ID_SEARCH_URL
        logger.info("searching for {} at {}".format(search_wigos_ids,wigosid_search_url))
        
        params={'WIGOSStationIdentifier': ",".join(search_wigos_ids) }       
        
        with self.session.get( wigosid_search_url , params=params ) as rsp:
            if rsp.status_code == 200:
                json_stations = json.loads(rsp.content)
                wigos_ids = [station['wigosStationIdentifiers'] for station in json_stations]

                # add names to each wigos id
                names = [station['name'] for station in json_stations]
                for idx,station in enumerate(wigos_ids):
                    name = names[idx]
                    for wid in station:
                        wid["name"]=name
                
                wigos_ids_concat = [ ",".join([s['wigosStationIdentifier'] for s in wids]) for wids in wigos_ids ]

                result = [None for i in range(len(search_wigos_ids))]
                for idx,swid in enumerate(search_wigos_ids):
                    res = [pos for pos,i in enumerate(wigos_ids_concat) if swid in i] 
                    if len(res)>0:
                        result[idx]=wigos_ids[res[0]]
                    else:
                        result[idx] = None
                
                logger.debug("get_wigos_id: ret: {}".format(result))
                return result 

            else:
                ret = {}
                ret["status_code"] = rsp.status_code
                ret["message"] = str(rsp.content) 

                logger.debug("get_wigos_id: ret: {}".format(ret))
                return ret
                
                
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
        logger.info("searching for {} at {}".format(params,oscar_search_url))
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
        logger.warning("deprecated: use upload_XML instead")
        return self.upload_XML(xml)
        
    def oscarSearch(self,params={}):
        logger.warning("deprecated: use oscar_search instead")
        return self.oscar_search(params)
        
    def getInternalIDfromWigosId(self,wigosid):
        logger.warning("deprecated: use wigos_to_internal_id instead")
        return self.wigos_to_internal_id(wigosid)
