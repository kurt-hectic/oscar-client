from .oscar_interface import FormalOscarInterface

class OscarInterfaceDummy(FormalOscarInterface):
   
    def __init__(self, server: str = "DEPL", token : str = None) :
        """initialize the OscarInterface class for usage with the token at the specificed server.
        
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        """
        pass

   
    def create_station(self, station: dict, wigos_id: str = None  ) -> dict :
        """create an WDMR record for the information contained in dict and push it to OSCR
        station is a JSON object representing the status with a grammar.
           
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be created
        station (dict): a dictionary containing the information about the station that should be created. Note that this also includes the wigos id
        
        Returns:
        dict: status code (status) and message (message)
        """
        return {"status": 200, "message" : "I did nothing"}
        
            
    def update_wigosid(self, wigos_ids: dict,  wigos_id: str = None) -> dict:
        """update wigos ids of station identified by _wigos_id, as per informationn in _wigos_ids_"""        
        return {"status": 200, "message" : "I did nothing"}
        
        
    def retrieve_wigosids(self, any_ids: list = []) -> list:
        """retrieve information about current WIGOS IDs of stations passed as argument
        
        Parameters:
        any_ids (list): list of WIGOS Identifiers for which identifier information should be retrieved
        
        Returns:
        dict: Dict of dict containing primary and secondary WIGOS Identifiers. Key of the first dict is the any_id used in the request. The second level dict is encoded according to the JSON grammar specified for WIGOS IDs of a station.
        
        """
        
        return  { "0-20000-2-123456" : { "primaryWigosID": "0-20000-0-123456" , "wigosID2" : "0-20000-2-123456", "wigosID3" : "0-20000-3-123456" , "wigosID4" : "0-20000-4-123456" }}
        
        
    def retrieve_schedules(self, wigos_ids: list = [] , var_id: int = None ) -> list:
        """retrieve schedules of stations specified in the argument.
        
        
        Parameters:
        wigos_ids (list): list of WIGOS Identifiers for which schedules should be retrieved
        var_id (int): limit schedules to those related to variable. If nothing is supplied all schedules are returned
        
        Returns:
        list: List of dict containing individual schedules. Note that the result likely contains more schedules than number of stations passed as argument

        """
    
        return [ {"wigosID":"0-20000-2-123456", "variable" : 16 , 
            "deployment_id" : "id_47312301-88df-44e8-a05d-f7423f17ad95" , "deployment_name" : "some deployment" ,
            "schedule_id" : "id_37b9eb94-869c-4c4d-8fbd-d7e112fbb418", "schedule_name" : "some schedule", "schedule" : "Jan-Jun/Mon-Fri/14-18/11-23/00-59:3600" , "international" : True, "near-real-time" : True,
            "date_from" : "2020-12-01", "status" : "operational"
            },  ]
    