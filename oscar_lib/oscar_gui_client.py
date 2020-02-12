"""This module can be used to interact with OSCAR/Surface using the internal API used by the GUI"""

import os
import requests
import json
import datetime
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import logging

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
        pass
        
        
        
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

    def update_station(self,internal_id,json_data,cookies,qlack_token):    
        
        headers = { QLACK_TOKEN_NAME:"{"+qlack_token+"}", }           
     
        station_update_url = (self.oscar_url + OscarClient._STATION_UPDATE_URL).format(internal_id=internal_id) 
        log.debug("updating station details of {} with header: {} cookies: {} and data: {}".format(station_update_url,headers,cookies,json_data))
        rsp=self.session.post( station_update_url , json=json_data , headers=headers , cookies=cookies )
        
        return rsp.status_code == 204
        
    def download_station(self,internal_id, **kwargs ):
        
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