"""This module can be used to interact with OSCAR/Surface using the internal API used by the GUI"""

import os
import requests
import json
import datetime
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import logging
from .oscar_saml import OscarSaml
from .oscar_client import OscarClient

log = logging.getLogger(__name__)

class OscarGUIClient(object):


    _STATION_EDIT_URL = '//rest/api/stations/canEdit/station/{internal_id}'
    _STATION_UPDATE_URL = '//rest/api/stations/station-put/{internal_id}'
    _STATION_DETAILS_URL = '//rest/api/stations/station/{internal_id}/stationReport'
    _STATION_OSERVATIONS_GROUPING_URL = '//rest/api/stations/observation/grouping/{internal_id}'
    _DEPLOYMENT_URL = '//rest/api/stations/deployments/{observation_id}'
    _STATION_OBSERVATIONS_URL = '//rest/api/stations/stationObservations/{internal_id}'
    _STATION_CREATION_URL = '//rest/api/stations/station'
    
    
    
    _QLACK_TOKEN_NAME = "X-Qlack-Fuse-IDM-Token-GO"
    
    
    def __init__(self,oscar_url=None,username=None,password=None):
        if not oscar_url:
            oscar_url = OscarClient.OSCAR_DEFAULT
           
        self.oscar_url = oscar_url
            
        if username and password:
            auth_client = OscarSaml(oscar_url=oscar_url,username=username,password=password)
            
            self.session = requests.Session()
            
            self.token = auth_client.qlack_token
            self.cookies = auth_client.cookies
        
        #TODO: login if needed

    def wigos_to_internal_id(self,wigosid):
        """Maps the `wigosid` to the internal id of the corresponding station in OSCAR
        Returns the `internal_id` of OSCAR.
        """
    
        wigosid_search_url = self.oscar_url + OscarClient._WIGOSID_SEARCH_URL
        rsp=self.session.get( wigosid_search_url.format(wigosid=wigosid) )
        stations = json.loads(rsp.content)
        
        internal_id = int(stations[0]["id"])
        return internal_id        
        
        
    def create_station(self,json_data,cookies,qlack_token):
        """Creates a station in OSCAR as represented by `json_data`. 
        This method uses the OSCAR internal API.
        """
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_creation_url = (self.oscar_url + OscarClient._STATION_CREATION_URL) 
        log.debug("creating new station at {} with header: {} cookies: {} and data: {}".format(station_creation_url,headers,cookies,json_data))
        rsp=self.session.post( station_creation_url , json=json_data , headers=headers , cookies=cookies )
        
        if rsp.status_code == 200:
            return 200, int(rsp.content)
        if rsp.status_code == 400:
            return 400, json.loads( rsp.content )
        else:
            return 500, "server processing error"

    def add_wigos_id(self,internal_id,wigos_id,primary=False):
        """Adds the WIGOS ID passed in `wigos_id` to the station `internal_id`. 
        The parameter `primary` with default value False indicates if this new WIGOS ID is the primary WIGOS iD"""
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
        
        current_status_url = (self.oscar_url +     "/rest/api/stations/station/{internal_id}/false/secure".format(intetrnal_id=internal_id))
        log.debug("getting current station represenation {} with header: {} cookies: {}".format(current_status_url,headers,cookies))
        current_station = self.session.get( current_status_url )
        
        
        current_observations_url = (self.oscar_url + "/rest/api/stations/stationObservations/{internal_id}".format(internal_id=internal_id) )
        log.debug("getting current station observations {} with header: {} cookies: {}".format(current_observations_url,headers,cookies))
        current_observations = self.session.get( current_status_url )
        
        if current_station.status_code == 200 and current_observations.status_code == 200:
            station = current_station.json()
            station["observations"] = current_observations.json()
        else:
            return 500, "server processing error"
    
    
    
    def update_station(self,internal_id,json_data,cookies,qlack_token):    
        """Updated a station in OSCAR as represented by `json_data`. 
        This method uses the OSCAR internal API.
        """
        
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_update_url = (self.oscar_url + OscarClient._STATION_UPDATE_URL).format(internal_id=internal_id) 
        log.debug("updating station details of {} with header: {} cookies: {} and data: {}".format(station_update_url,headers,cookies,json_data))
        rsp=self.session.post( station_update_url , json=json_data , headers=headers , cookies=cookies )
        
        return rsp.status_code == 204
        
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
            
        station_details_url = self.oscar_url + OscarClient._STATION_DETAILS_URL
        log.debug("getting station details for {} from {}".format(internal_id,station_details_url))
        rsp=self.session.get( station_details_url.format(internal_id=internal_id) )
        
        if not rsp.status_code == 200:
            log.debug("station {} not found".format(internal_id))
            return None
            
        station_info = json.loads(rsp.content)

        if level > 0:
            log.info("getting station observation groups for {}".format(internal_id))
            station_observations_url = (self.oscar_url + OscarClient._STATION_OBSERVATIONS_URL).format(internal_id=internal_id)
            rsp=self.session.get( station_observations_url )
            observations = json.loads(rsp.content)

            station_info["observations"] = observations

            if level > 1:
                
                for observation in observations: 
                    observation_id = int(observation['id'])
                    
                    log.info("getting deployment {}".format(observation_id))
                    deployment_url = (self.oscar_url + OscarClient._DEPLOYMENT_URL).format(observation_id=observation_id)
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