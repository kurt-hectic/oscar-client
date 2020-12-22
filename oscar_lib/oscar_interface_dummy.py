import os, json, datetime, logging

from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError

from .oscar_interface import FormalOscarInterface
from . import OscarClient, Station

from .utils import convert_schedule, convert_schedule_rev

mydir = os.path.dirname(__file__) + "/static/"

logger = logging.getLogger(__name__)

with open(mydir+"/json-schemas/create_station.json","r") as f:
    station_schema = json.load( f )

class OscarInterfaceDummy(FormalOscarInterface):
   
    def __init__(self, server: str = "DEPL", token : str = None) :
        """initialize the OscarInterface class for usage with the token at the specificed server.
        
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        """
        if server != "DEPL":
            raise Exception("only DEPL implemented at this stage")
            
        
        self.client = OscarClient(oscar_url = OscarClient.OSCAR_DEPL, token=token)
        logger.info("initalized OSCAR client for {}".format(server))   
   
    def _upload_station(self,new_station):
        """interal helper function to upload new station"""
        
        logger.debug("_upload station")
    
        try:
            new_station.validate() # TODO: need to check for invalid stations (maybe here, maybe in another place)

            status = self.client.upload_XML(str(new_station))
                    
            if status == 'AUTH_ERROR':
                ret = {"status": 403, "message" : "auth error. Check token"}
                
            if status == 'SERVER_ERROR':
                ret =  {"status": 500, "message" : "processing error on server"}
            
            if status in ['SUCCESS_WITH_WARNINGS','SUCCESS','VALID_XML_WITH_ERRORS_OR_WARNINGS']:
                ret =  {"status": 200, "message" : "request processed: {}".format(status) }
            else:
                ret =  {"status": 501, "message" : "unknown error ({})".format(status) }
                
        except Exception as ex:
            ret = {"status": 400 , "message": "XML invalid: {}".format(str(ex))}
 
        logger.debug("return {}".format(ret))
        return ret
    
    
    def create_station(self, station: dict, wigos_id: str = None  ) -> dict :
        """create an WDMR record for the information contained in dict and push it to OSCR
        station is a JSON object representing the status with a grammar.
           
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be created
        station (dict): a dictionary containing the information about the station that should be created. Note that this also includes the wigos id
        
        Returns:
        dict: status code (status) and message (message)
        """
        logger.debug("create_station {} ({})".format(wigos_id,station))
        try:
            validate( instance=station , schema=station_schema ,  format_checker=FormatChecker() )
        except ValidationError as ve:
            err_msg = "station object not valid {}".format(str(ve))
            logger.error(err_msg)
            return {"status":400,"message":"invalid format {}".format(err_msg) }
            
        schedule = convert_schedule(station["internationalReportingFrequency"])
        schedule["international"] = station["international"]
        schedule["real-time"] = station["realTime"]

        observation_ids = [int(o.strip()) for o in station["parametersObserved"].split(",")]
        
        if not "affiliations" in station:
            station["affiliations"] = "unknown"
        affiliations =  [a.strip() for a in station["affiliations"].split(",") ]
        
        if len(affiliations) > 1 and len(affiliations) != len(observation_ids):
            raise Exception("number of affiliations must be equal number of observations or 1")
            
        # same length as observation to facilitate loop underneath
        if len(affiliations) == 1:
            affiliations = affiliations[0] * len(observation_ids)
        

        observations = []
        observationsource = "automaticReading" if station["automatic"] else "manualReading"
        
        for idx,oid in enumerate(observation_ids):
            observations.append( { "variable" : oid , "observationsource" : observationsource , "affiliation": affiliations[idx] , "schedule": schedule } )

        required_parameter_map = { "name" : "name", "stationtype":"type", "status":"operationalStatus",
            "wigosid":"wigosID","timezone":"utc","latitude":"latitude","longitude":"longitude",
            "elevation":"altitude","country":"country","region":"region","established":"creation"
        }
        
        optional_parameter_map = { "description":"description", "manufacturer" : None, "observationsFrequency" : None , "organization":"supervisingOrganization" }

        station_params = { k:station[v] for k,v in required_parameter_map.items() }

        station_params["urls"] = ["http://test.de",]
        station_params["observations"] = observations
        station_params["default_schedule"] = schedule

        # add optional parameters if not empty
        for k,v in optional_parameter_map.items():
            if v:
                station_params[k]=station[v]

        new_station = Station(**station_params)
        
        ret = self._upload_station(new_station)
        
        logger.info("created new station: status: {}".format(ret["status"]))
       
        return ret
                        
    def update_wigosid(self, wigos_id: str = None , wigos_ids: dict = [] ) -> dict:
        """update wigos ids of station identified by wigos_id, as per information in wigos_ids""" 
        logger.debug("update_wigosid station:{},  wigos_ids: ({})".format(wigos_id,wigos_ids))

        try: 
            station=Station(self.client.load_station(wigos_id=wigos_id,cache=True))
            
            
            new_wigos_ids = [ wigos_ids['primaryWigosID'] , ]
            for wid in ['wigosID2','wigosID3','wigosID4']:
                if wid in wigos_ids.keys() and wigos_ids[wid]:
                    new_wigos_ids.append(wigos_ids[wid])
            
            
            station.update_wigosids(wigos_ids=new_wigos_ids) 
            ret=self._upload_station(station)
            
            
            if ret["status"] == 200 :
                ret = {"status": 200, "message" :  ret["message"] + " " +  "OK. new wigos ids {}".format(",".join(ret))}
            else:
                ret
                
        except KeyError as ke:
                message = "error: station {} does not exist {}".format(wigos_id,str(ke))
                ret = {"status": 400, "message" :  message }
                logger.error(message)

        logger.info("updated wigos ids: status: {} {}".format(ret["status"],ret["message"]))
        return ret
        
    def retrieve_wigosids(self, any_ids: list = []) -> dict:
        """retrieve information about current WIGOS IDs of stations passed as argument
        
        Parameters:
        any_ids (list): list of WIGOS Identifiers for which identifier information should be retrieved
        
        Returns:
        dict: Dict of dict containing primary and secondary WIGOS Identifiers. Key of the first dict is the any_id used in the request. The second level dict is encoded according to the JSON grammar specified for WIGOS IDs of a station.
        
        """
        logger.debug("retrieve_wigosids {}".format(any_ids))
        
        wigos_ids = self.client.get_wigos_ids(any_ids)       
        
        result = {}
            
        for idx,station in enumerate(wigos_ids):
            
            search_wid = any_ids[idx] # the wigos ID that was searched
           
            if not station:
                result[search_wid] = None # no match found
            else:
                        
                primary = [ wid["wigosStationIdentifier"] for wid in station if wid["primary"] ][0]
                rest = [ wid["wigosStationIdentifier"] for wid in station if not wid["primary"] ]
                rest = rest + [None for i in range(max(0,3-len(rest)))] # make sure that the array has at least 3 entries
                
                result[search_wid] = { "primaryWigosID": primary , "wigosID2" : rest[0], "wigosID3" : rest[1] , "wigosID4" : rest[2] , "all" : [primary,] + [r for r in rest if r] } 
             
        logger.info("retrieve_wigosids {}".format(result))
        return  result
        
        
    def retrieve_schedules(self, wigos_ids: list = [] , var_id: int = None ) -> list:
        """retrieve schedules of stations specified in the argument.
        
        
        Parameters:
        wigos_ids (list): list of WIGOS Identifiers for which schedules should be retrieved
        var_id (int): limit schedules to those related to variable. If nothing is supplied all schedules are returned
        
        Returns:
        list: List of dict containing individual schedules. Note that the result likely contains more schedules than number of stations passed as argument

        """
        logger.debug("retrieve_schedules for station {}, variable: {}".format(wigos_ids,var_id))
        
        schedules = {}
        
        for wid in wigos_ids:
            station=Station(self.client.load_station(wigos_id=wid,cache=True))
        
            schedules[wid] = station.schedules()
    
        ret = []
        
        for wigos_id,station in schedules.items():
            for var_id,observation in station.items():
                for deployment in observation["deployments"]:
                    for dg in deployment["datagenerations"]:
                        schedule = convert_schedule_rev(dg["schedule"])
                        
                        
                        new_schedule = {"wigosID": wigos_id, "variable" : var_id, "deployment_id" : deployment["gid"] , "deployment_name" : "{from}-{to}".format(**deployment) ,
            "schedule_id" : dg["gid"], "schedule_name" : "{from}-{to}".format(**schedule), "schedule" : "{startMonth}-{endMonth}/{startWeekday}-{endWeekday}/{startHour}:{startMinute}-{endHour}:{endMinute}/{interval}".format(**schedule) , "international" : dg["schedule"]["international"], "near-real-time" : True, "date_from" :  schedule["from"] , "status" : "operational" } if schedule else None
                    
                        ret.append(new_schedule)
                    
        logger.info("retrieve_schedules {}".format(ret))
        return ret
        #return [ {"wigosID":"0-20000-2-123456", "variable" : 16 , 
        #    "deployment_id" : "id_47312301-88df-44e8-a05d-f7423f17ad95" , "deployment_name" : "some deployment" ,
        #    "schedule_id" : "id_37b9eb94-869c-4c4d-8fbd-d7e112fbb418", "schedule_name" : "some schedule", "schedule" : "Jan-Jun/Mon-Fri/14-18/11-23/00-59:3600" , "international" : True, "near-real-time" : True,
        #    "date_from" : "2020-12-01", "status" : "operational"
        #    },  ]
    
    
    def update_affiliation(self, wigos_id: str,  affiliation: str = None ,  variables: list = [], operational_status: str = 'operational' , program_id: str = None ) -> dict:
        """updates the station and adds the affiliation as well as linking it to the variables passed in variables. 
        
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be updated
        affiliation (str): the affiliation that should be added to the station
        variables (list): the variables the affiliation should be linked to
        operational_status (str): the status of the affiliation (default: operational)
        program_id (str): the programme specific ID of the affiliation (default: None)
        
        Returns:
        dict: status code (status) and message (message)
        """ 
        logger.debug("update_affiliation station: {}, affiliation: {}, variables: {}, status: {}, id: {}".format(wigos_id,affiliation,variables,operational_status,program_id))
  
        try:
            station = Station(self.client.load_station(wigos_id=wigos_id, cache=True))
            
            station.update_affiliations(affiliation=affiliation,variables=variables,operational_status=operational_status,begin_date=datetime.datetime.now())
           
            print(str(station))
           
            ret=self._upload_station(station)
            
            if ret["status"] == 200 :
                ret = {"status": 200, "message" :  ret["message"] + " " +  "added affiliation {} to {}".format(affiliation,variables)}
            else:
                msg
        except KeyError as ke:
                message = "error: station {} does not exist {}".format(wigos_id,str(ke))
                ret = {"status": 400, "message" :  message }
                logger.error(message)
        
        logger.info("updated affiliations: status: {}, {}".format(ret["status"],ret["message"]))
        return ret
       
    def update_schedule(self, wigos_id: str, schedules: list = []) -> dict:
        """updates the schedules at station identified by wigos_id as indicated by schedules. 
        
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be updated
        schedules (list): list of schedules, represented as dict (schedule_schema.json), that should be updated. The gml identifier of a schedule as passed in the parameter is used to match.
        
        Returns:
        dict: status code (status) and message (message)
        """
        pass