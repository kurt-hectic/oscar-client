import abc 

class FormalOscarInterface(metaclass=abc.ABCMeta):

    @staticmethod
    def validate_token(server: str = "DEPL", token: str = None) -> bool :
        """validate the token passed on the indicated server
        
        Parameters:
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        
        Return:
        bool: whether the token is valid or not
        """
        return True

    @classmethod
    def __subclasshook__(cls, subclass):
    
        ret = True        
        for method in ['__init__','create_station','update_wigosid','retrieve_schedules','retrieve_wigosids']:
            print(method)
            real_method = getattr(subclass, method)
        
            ret = ret and ( hasattr(subclass,method) and callable(real_method) )
            
        return ret if ret else NotImplemented
    
    
    @abc.abstractmethod
    def __init__(self, server: str = "DEPL", token : str = None) :
        """initialize the OscarInterface class for usage with the token at the specificed server.
        
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        """
        raise NotImplementedError

    @abc.abstractmethod   
    def create_station(self, station: dict, wigos_id: str = None  ) -> dict :
        """create an WDMR record for the information contained in dict and push it to OSCR
        station is a JSON object representing the status with a grammar.
           
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be created
        station (dict): a dictionary containing the information about the station that should be created. Note that this also includes the wigos id
        
        Returns:
        dict: status code (status) and message (message)
        """
        raise NotImplementedError
        
    @abc.abstractmethod            
    def update_wigosid(self, wigos_ids: dict,  wigos_id: str = None) -> dict:
        """update wigos ids of station identified by _wigos_id, as per informationn in _wigos_ids_"""        
        raise NotImplementedError


    @abc.abstractmethod            
    def update_affiliation(self, wigos_id: str,  affiliation: str = None ,  variables: list = []) -> dict:
        """updates the station and adds the affiliation as well as linking it to the variables passed in variables. 
        
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be updated
        affiliation (str): the affiliation that should be added to the station
        variables (list): the variables the affiliation should be linked to
        
        Returns:
        dict: status code (status) and message (message)
        """     
        raise NotImplementedError
        
    def update_schedule(self, wigos_id: str, schedules: list = []): dict:
        """updates the schedules at station identified by wigos_id as indicated by schedules. 
        
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be updated
        schedules (list): list of schedules, represented as dict (schedule_schema.json), that should be updated. The gml identifier of a schedule as passed in the parameter is used to match.
        
        Returns:
        dict: status code (status) and message (message)
        """
        raise NotImplementedError

        
    @abc.abstractmethod        
    def retrieve_wigosids(self, any_ids: list = []) -> list:
        """retrieve information about current WIGOS IDs of stations passed as argument
        
        Parameters:
        any_ids (list): list of WIGOS Identifiers for which identifier information should be retrieved
        
        Returns:
        dict: Dict of dict containing primary and secondary WIGOS Identifiers. Key of the first dict is the any_id used in the request. The second level dict is encoded according to the JSON grammar specified for WIGOS IDs of a station.
        
        """
        raise NotImplementedError
        
    @abc.abstractmethod        
    def retrieve_schedules(self, wigos_ids: list = [] , var_id: int = None ) -> list:
        """retrieve schedules of stations specified in the argument.
        
        
        Parameters:
        wigos_ids (list): list of WIGOS Identifiers for which schedules should be retrieved
        var_id (int): limit schedules to those related to variable. If nothing is supplied all schedules are returned
        
        Returns:
        list: List of dict containing individual schedules. Note that the result likely contains more schedules than number of stations passed as argument

        """
        raise NotImplementedError