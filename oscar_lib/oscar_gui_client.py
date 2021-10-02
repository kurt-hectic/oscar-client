"""This module can be used to interact with OSCAR/Surface using the internal API used by the GUI"""

import os
import requests
import json
import datetime
import logging
from .oscar_saml import OscarSaml
from .oscar_client import OscarClient

log = logging.getLogger(__name__)

class OscarGUIClient(object):


    _STATION_EDIT_URL = '/rest/api/stations/canEdit/station/{internal_id}'
    _STATION_UPDATE_URL = '/rest/api/stations/station-put/{internal_id}'
    _STATION_DETAILS_URL = '/rest/api/stations/station/{internal_id}/stationReport'
    _STATION_OSERVATIONS_GROUPING_URL = '/rest/api/stations/observation/grouping/{internal_id}'
    _DEPLOYMENT_URL = '/rest/api/stations/deployments/{observation_id}'
    _STATION_OBSERVATIONS_URL = '/rest/api/stations/stationObservations/{internal_id}'
    _STATION_CREATION_URL = '/rest/api/stations/station'
    _STATION_PREP_UPDATE = "/rest/api/stations/station/{internal_id}/false/secure"
    _WIGOSID_SEARCH_URL = '/rest/api/stations/approvedStations/wigosIds?q={wigosid}'
    _STATION_DELETE_URL = '/rest/api/stations/station-delete/{internal_id}'

    
    _QLACK_TOKEN_NAME = "X-Qlack-Fuse-IDM-Token-GO"
    
    
    def __init__(self,oscar_url=None,username=None,password=None):
        if not oscar_url:
            oscar_url = OscarClient.OSCAR_DEFAULT
           
        self.oscar_url = oscar_url
        self.session = requests.Session()
            
        if username and password:
            auth_client = OscarSaml(oscar_url=oscar_url,username=username,password=password)
            
            
            self.token = auth_client.qlack_token
            self.cookies = auth_client.cookies
        
        #TODO: login if needed

    def wigos_to_internal_id(self,wigosid):
        """Maps the `wigosid` to the internal id of the corresponding station in OSCAR
        Returns the `internal_id` of OSCAR.
        """
    
        wigosid_search_url = self.oscar_url + OscarGUIClient._WIGOSID_SEARCH_URL
        rsp=self.session.get( wigosid_search_url.format(wigosid=wigosid) )
        stations = rsp.json()
        
        if stations["total"] == 0:
            return None
        
        internal_id = int(stations["resultList"][0]["id"])
        return internal_id        
        
        
    def create_station(self,json_data,cookies,qlack_token):
        """Creates a station in OSCAR as represented by `json_data`. 
        This method uses the OSCAR internal API.
        """
        headers = { OscarGUIClient._QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_creation_url = (self.oscar_url + OscarClient._STATION_CREATION_URL) 
        log.debug("creating new station at {} with header: {} cookies: {} and data: {}".format(station_creation_url,headers,cookies,json_data))
        rsp=self.session.post( station_creation_url , json=json_data , headers=headers , cookies=cookies )
        
        if rsp.status_code == 200:
            return 200, int(rsp.content)
        if rsp.status_code == 400:
            return 400, json.loads( rsp.content )
        else:
            return 500, "server processing error"
            
            
    def _prepare_update(self,internal_id):
        headers = { OscarGUIClient._QLACK_TOKEN_NAME:"{"+self.token+"}", }           
        cookies = self.cookies
        
        current_status_url = (self.oscar_url +   OscarGUIClient._STATION_PREP_UPDATE.format(internal_id=internal_id))
        current_station = self.session.get( current_status_url , headers=headers, cookies=cookies  )
        log.debug("getting current station represenation {} ({}) with header: {} cookies: {}".format(current_status_url,current_station.status_code,headers,self.cookies))
        
        current_observations_url = (self.oscar_url + OscarGUIClient._STATION_OBSERVATIONS_URL.format(internal_id=internal_id) )
        current_observations = self.session.get( current_observations_url , headers=headers, cookies=cookies)
        log.debug("getting current station observations {} ({}) with header: {} cookies: {}".format(current_observations_url,current_observations.status_code,headers,self.cookies))
        
        if current_station.status_code == 200 and current_observations.status_code == 200:
            updated_station = current_station.json()
            updated_station["observations"] = current_observations.json()
            
            return updated_station
        else:
            return None
        

    def add_wigos_id(self,internal_id,wigos_id,primary=False):
        """Adds the WIGOS ID passed in `wigos_id` to the station `internal_id`. 
        The parameter `primary` with default value False indicates if this new WIGOS ID is the primary WIGOS iD"""
        
        current_station = self._prepare_update(internal_id)
        
        if current_station:
            updated_station = current_station.copy()
            
            if primary:
                for wid in updated_station["wigosIds"]:
                    wid["primary"] = False
            
            updated_station["wigosIds"].append( {"wid" : wigos_id , "primary" : primary } )

            return self.update_station(internal_id,updated_station)
            
        else:
            return 500, "server processing error"

    def add_timezone(self,internal_id,timezone,valid_since=None):
        """Adds the timezone specified in `timezone` to the station `internal_id`. 
        The parameter `valid_since` with default value today indicates from when the change takes effect"""
        
        # copy and paste from https://oscardepl.wmo.int/surface/rest/api/referenceData/list/TimezoneRef
        timezone_ids = { e["name"]:e["id"] for e in json.loads('[{"id":40,"name":"UTC-12"},{"id":39,"name":"UTC-11"},{"id":38,"name":"UTC-10"},{"id":37,"name":"UTC-9.5"},{"id":36,"name":"UTC-9"},{"id":35,"name":"UTC-8"},{"id":34,"name":"UTC-7"},{"id":33,"name":"UTC-6"},{"id":32,"name":"UTC-5"},{"id":31,"name":"UTC-4.5"},{"id":30,"name":"UTC-4"},{"id":29,"name":"UTC-3.5"},{"id":28,"name":"UTC-3"},{"id":27,"name":"UTC-2"},{"id":26,"name":"UTC-1"},{"id":1,"name":"UTC"},{"id":2,"name":"UTC+1"},{"id":3,"name":"UTC+2"},{"id":4,"name":"UTC+3"},{"id":5,"name":"UTC+3.5"},{"id":6,"name":"UTC+4"},{"id":7,"name":"UTC+4.5"},{"id":8,"name":"UTC+5"},{"id":9,"name":"UTC+5.5"},{"id":10,"name":"UTC+5.65"},{"id":11,"name":"UTC+6"},{"id":12,"name":"UTC+6.5"},{"id":13,"name":"UTC+7"},{"id":14,"name":"UTC+8"},{"id":15,"name":"UTC+8.65"},{"id":16,"name":"UTC+9"},{"id":17,"name":"UTC+9.5"},{"id":18,"name":"UTC+10"},{"id":19,"name":"UTC+10.5"},{"id":20,"name":"UTC+11"},{"id":21,"name":"UTC+11.5"},{"id":22,"name":"UTC+12"},{"id":23,"name":"UTC+12.65"},{"id":24,"name":"UTC+13"},{"id":25,"name":"UTC+14"}]') }
        
        current_station = self._prepare_update(internal_id)
        
        if current_station:
            updated_station = current_station.copy()

            if not 'timezones' in updated_station:
                updated_station["timezones"] = []
            
            if not timezone in timezone_ids:
                raise ValueError("{} not a valid timezone.. choose from {}".format(timezone,timezone_ids))
            timezone_id =  timezone_ids[timezone]
            
            if not valid_since:
                valid_since = datetime.date.today().strftime("%Y-%m-%d")
            else:
                valid_since = datetime.datetime.strptime(str(valid_since),"%Y-%m-%d").strftime("%Y-%m-%d")
            
            updated_station["timezones"].append( 
                {"validSince":valid_since,"timezoneId":timezone_id,"usedTimezones":None,"timezoneName":timezone} ) 
            
            return self.update_station(internal_id,updated_station)
            
        else:
            return 500, "server processing error"    
    
    
    def update_station(self,internal_id,station_data):    
        """Updated a station in OSCAR as represented by `station_data`. 
        This method uses the OSCAR internal API.
        """
        
        headers = { OscarGUIClient._QLACK_TOKEN_NAME:"{"+self.token+"}", }           
        cookies = self.cookies
     
        station_data["wmoIndex"] = {}
        station_data["submitNewStation"] = False
     
        station_update_url = (self.oscar_url + OscarGUIClient._STATION_UPDATE_URL).format(internal_id=internal_id) 
        rsp=self.session.post( station_update_url , json=station_data , headers=headers , cookies=cookies )
        log.debug("updating station details of {} with header: {} ({}) cookies: {} and data: {}".format(station_update_url,rsp.status_code,headers,cookies,station_data))
        
        return rsp.status_code
        
    def download_station(self,internal_id, **kwargs ):
        """Downloads a JSON station representation of the station with internal id `internal_id`. 
        Using the keyword argument `level` the amount of information in the result can be set. If set to `basic` only high level station information is returned. If set to `observation` the result also contains the list of observations. If set to`deployments` it also contains deployments and data generation.
        The argument `observations` can be used to narrow down the list of observations that are part of the result.
        This method uses the OSCAR internal API.
        """
        
        filterObs = False
        if 'observations' in kwargs:
            filterObs = True
            validObservations = kwargs['observations']
            log.debug("limiting observations to {}".format(validObservations))

        level = 0
        if 'level' in kwargs:
            if kwargs["level"] == 'basic':
                level = 0
            if kwargs["level"] == 'observations':
                level = 1
            if kwargs["level"] == 'deployments':
                level = 2
            
        station_details_url = self.oscar_url + OscarGUIClient._STATION_DETAILS_URL
        log.debug("getting station details for {} from {}".format(internal_id,station_details_url))
        rsp=self.session.get( station_details_url.format(internal_id=internal_id) )
        
        if not rsp.status_code == 200:
            log.debug("station {} not found".format(internal_id))
            return None
            
        station_info = json.loads(rsp.content)

        if level > 0:
            log.info("getting station observation groups for {}".format(internal_id))
            station_observations_url = (self.oscar_url + OscarGUIClient._STATION_OBSERVATIONS_URL).format(internal_id=internal_id)
            rsp=self.session.get( station_observations_url )
            observations = json.loads(rsp.content)

            station_info["observations"] = observations

            if level > 1:
                
                for observation in observations: 
                    observation_id = int(observation['id'])
                    
                    log.info("getting deployment {}".format(observation_id))
                    deployment_url = (self.oscar_url + OscarGUIClient._DEPLOYMENT_URL).format(observation_id=observation_id)
                    rsp = self.session.get( deployment_url )
                    
                    deployments = []
                    if rsp.status_code == 200:
                        deployments = json.loads(rsp.content)
                    
                    observation['deployments'] = deployments

        
        if not 'dateEstablished' in station_info:
            station_info["dateEstablished"] = None
        
        return station_info


    def extract_schedules(self,station_info, onlyActiveDeployments=True , referenceDate = datetime.datetime.today() ):
        """Tihs method extracts schedule information from a station representation passed in `station_info` (as for example obtained from `download_station`).
        The parameters `onlyActiveDeployments` can be used to limit the result to deplyoments that are active. The reference date can be passed in `referenceDate` (default today).
        The result is a dictionary in which schedules are grouped by variable id. 
        """
        
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
                        log.debug("skipping date from: {} to: {} today:".format(datefrom,dateto,referenceDate))
                        continue
                    
                if not 'dataGenerations' in deployment:
                    continue
                  
                data_generations = deployment['dataGenerations']
                
            for data_generation in data_generations:
                if not ( 'schedule' in data_generation and 'reporting' in data_generation   ) :
                   log.debug("skipping DG due to incomplete information {}".format(data_generation))
                   continue

                schedule = data_generation['schedule']
                reporting = data_generation['reporting']
                log.debug("adding schedule and reporting info to result")
                result[var_id].append( { 'schedule' : schedule , 'reporting': reporting } )

                    
        return result
        
    def delete_station(self,internal_id):
        """deletes station with the interal id specified as parameter"""
    
        headers = { OscarGUIClient._QLACK_TOKEN_NAME:"{"+self.token+"}", }           
        cookies = self.cookies
     
        station_delete_url = (self.oscar_url + OscarGUIClient._STATION_DELETE_URL).format(internal_id=internal_id) 
        
        rsp=self.session.post( station_delete_url, headers=headers, cookies=cookies )
        log.debug("deleting station {} with header: {} ({}) cookies: {}".format(internal_id,headers, rsp.status_code,cookies))
        
        return rsp.status_code
    
   
    def close(self):
        if self.session:
            self.session.close()