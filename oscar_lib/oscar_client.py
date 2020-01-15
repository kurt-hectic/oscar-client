import os
import requests
import json
import datetime
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import logging


#logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class OscarClient(object):

    STATION_EDIT_URL = '//rest/api/stations/canEdit/station/{internal_id}'
    STATION_UPDATE_URL = '//rest/api/stations/station-put/{internal_id}'
    WIGOSID_SEARCH_URL = '//rest/api/stations/approvedStations/wigosIds?q={wigosid}'
    STATION_SEARCH_URL = '//rest/api/search/station?stationClass={stationClass}'
    STATION_DETAILS_URL = '//rest/api/stations/station/{internal_id}/stationReport'
    STATION_OSERVATIONS_GROUPING_URL = '//rest/api/stations/observation/grouping/{internal_id}'
    DEPLOYMENT_URL = '//rest/api/stations/deployments/{observation_id}'
    STATION_OBSERVATIONS_URL = '//rest/api/stations/stationObservations/{internal_id}'
    STATION_CREATION_URL = '//rest/api/stations/station'
    STATION_XML_UPLOAD = '//rest/api/wmd/upload'
    STATION_XML_DOWNLOAD = '//rest/api/wmd/download/'

    OSCAR_SEARCH_URL = '//rest/api/search/station'

    OSCAR_DEFAULT = 'https://oscar.wmo.int/surface'
    OSCAR_DEPL = "https://oscardepl.wmo.int/surface"

    QLACK_TOKEN_NAME = "X-Qlack-Fuse-IDM-Token-GO"


    def __init__(self,**kwargs):
        self.oscar_url = kwargs.get('oscarurl',OscarClient.OSCAR_DEFAULT)
        self.token = kwargs.get('token',None)
        self.session = requests.Session()

    def uploadXML(self,xml):
    
        if not self.token:
            raise AttributeError("no token configured.. cannot upload")
    
        headers = { 'X-WMO-WMDR-Token' : self.token } 

        content = xml.encode("utf8")
        xml_upload_url = self.oscar_url + OscarClient.STATION_XML_UPLOAD

        response = requests.post( xml_upload_url , data=content , headers=headers  )

        status=None
        if response.status_code ==  200:
            # reponse:
            response = json.loads(response.content)
            if response["xmlStatus"] in ['SUCCESS_WITH_WARNINGS','SUCCESS']:
                log.debug("upload ok, new id {id} {logs}".format(id=response["id"],logs=response["logs"]))
            else:
                log.debug("upload failed.. the log is {logs}".format(logs=response["logs"]) )

            status = response["xmlStatus"]
            
        else:
            log.debug("processing error on server side {} {}".format(response.status_code,response.content))
            status = "SERVER_ERROR"
            
        return status

    def load_station(self,wigos_id=None,internal_id=None,cache=False):
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
        r = requests.get(self.oscar_url + OscarClient.STATION_XML_DOWNLOAD + wigos_id )
        
        if r.status_code != 200:
            raise KeyError("{} not contained in OSCAR or cannot be downloaded".format(wigos_id))
            
        
        wmdr = r.content 
        
        if cache:
            with open(cache_filename,"wb") as f:
                f.write(wmdr)

        return wmdr

    def oscarSearch(self,params={}):
       oscar_search_url = self.oscar_url + OscarClient.OSCAR_SEARCH_URL
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
       
    def getInternalIDfromWigosId(self,wigosid):
        wigosid_search_url = self.oscar_url + OscarClient.WIGOSID_SEARCH_URL
        rsp=self.session.get( wigosid_search_url.format(wigosid=wigosid) )
        stations = json.loads(rsp.content)
        internal_id = stations[0]["id"]
        return internal_id
     

    def createStation(self,json_data,cookies,qlack_token):
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_creation_url = (self.oscar_url + OscarClient.STATION_CREATION_URL) 
        logging.debug("creating new station at {} with header: {} cookies: {} and data: {}".format(station_creation_url,headers,cookies,json_data))
        rsp=self.session.post( station_creation_url , json=json_data , headers=headers , cookies=cookies )
        
        if rsp.status_code == 200:
            return 200, int(rsp.content)
        if rsp.status_code == 400:
            return 400, json.loads( rsp.content )
        else:
            return 500, "server processing error"

    def updateStation(self,internal_id,json_data,cookies,qlack_token):    
        
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_update_url = (self.oscar_url + OscarClient.STATION_UPDATE_URL).format(internal_id=internal_id) 
        logging.debug("updating station details of {} with header: {} cookies: {} and data: {}".format(station_update_url,headers,cookies,json_data))
        rsp=self.session.post( station_update_url , json=json_data , headers=headers , cookies=cookies )
        
        return rsp.status_code == 204
        
    def getFullStationJson(self,internal_id, **kwargs ):
        
        filterObs = False
        if 'observations' in kwargs:
            filterObs = True
            validObservations = kwargs['observations']
            logging.debug("limiting observations to {}".format(validObservations))

        level = 0
        if 'level' in kwargs:
            if kwargs["level"] == 'basic':
                level = 0
            if kwargs["level"] == 'observations':
                level = 1
            if kwargs["level"] == 'deployments':
                level = 2
            
        station_details_url = self.oscar_url + OscarClient.STATION_DETAILS_URL
        logging.debug("getting station details for {} from {}".format(internal_id,station_details_url))
        rsp=self.session.get( station_details_url.format(internal_id=internal_id) )
        
        if not rsp.status_code == 200:
            logging.debug("station {} not found".format(internal_id))
            return None
            
        station_info = json.loads(rsp.content)

        if level > 0:
            logging.info("getting station observation groups for {}".format(internal_id))
            #station_observations_grouping_url = self.oscar_url +  STATION_OSERVATIONS_GROUPING_URL
            station_observations_url = (self.oscar_url + OscarClient.STATION_OBSERVATIONS_URL).format(internal_id=internal_id)
            rsp=self.session.get( station_observations_url )
            observations = json.loads(rsp.content)

            station_info["observations"] = observations

            if level > 1:
                
                for observation in observations: 
                    observation_id = int(observation['id'])
                    
                    logging.info("getting deployment {}".format(observation_id))
                    deployment_url = (self.oscar_url + OscarClient.DEPLOYMENT_URL).format(observation_id=observation_id)
                    rsp = self.session.get( deployment_url )
                    
                    deployments = []
                    if rsp.status_code == 200:
                        deployments = json.loads(rsp.content)
                    
                    observation['deployments'] = deployments

        
        if not 'dateEstablished' in station_info:
            station_info["dateEstablished"] = None
        
        return station_info


    def extractSchedulesByVariable(self,station_info, onlyActiveDeployments=True , referenceDate = datetime.datetime.today() ):
        
        result = {}
        if not 'observations' in station_info:
            return result
        
        observations = station_info['observations'] 
        
        for observation in observations:
            var_id = observation['observAccordionId'].split('_')[0]
            result[var_id] = []
            
            if not 'deployments' in observation:
                continue
            
            deployments = observation['deployments']
            
            for deployment in deployments:
                if onlyActiveDeployments:
                    datefrom = datetime.strptime(deployment['observationSince'],'%Y-%m-%d') if 'observationSince' in deployment else datetime.datetime(datetime.MINYEAR,1,1)
                    dateto =  datetime.strptime(deployment['observationTill'],'%Y-%m-%d') if 'observationTill' in deployment else datetime.datetime(datetime.MAXYEAR,1,1)

                    if not ( datefrom <= referenceDate and referenceDate <= referenceDate ):
                        logging.debug("skipping date from: {} to: {} today:".format(datefrom,dateto,referenceDate))
                        continue
                    
                if not 'dataGenerations' in deployment:
                    continue
                  
                data_generations = deployment['dataGenerations']
                
            for data_generation in data_generations:
                if not ( 'schedule' in data_generation and 'reporting' in data_generation   ) :
                   logging.debug("skipping DG due to incomplete information {}".format(data_generation))
                   continue

                schedule = data_generation['schedule']
                reporting = data_generation['reporting']
                logging.debug("adding schedule and reporting info to result")
                result[var_id].append( { 'schedule' : schedule , 'reporting': reporting } )

                    
        return result
             