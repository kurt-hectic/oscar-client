class OscarInterface:
    
    def validate_token(self, server: str = "DEPL", token: str = None) -> bool :
        """validate the token passed on the indicated server
        
        Parameters:
        server (str): whether the token is validated  in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the user API token
        
        Return:
        bool: whether the token is valid or not
        """
        return True
    
    def create_station(self, station: dict, wigos_id: str = None, server: str ="DEPL", token: str =None  ) -> dict :
        """create an WDMR record for the information contained in dict and push it to OSCR
        station is a JSON object representing the status with a grammar.
           
        Parameters:
        wigos_id (str): the WIGOS identifier of the station that should be created
        station (dict): a dictionary containing the information about the station that should be created. Note that this also includes the wigos id
        server (str): whether the station should be created in the production or testing system (PROD|DEPL) (default DEPL)
        token (str): the API token in OSCAR/Surface
        
        Returns:
        dict: status code (status) and message (message)
        """
        return {"status": 200, "message" : "I did nothing"}
        
            
    def update_wigosid(self, wigos_ids: dict,  wigos_id: str = None, server: str ="DEPL", token:str = None) -> dict:
        """update wigos ids of station identified by _wigos_id, as per informationn in _wigos_ids_"""        
        return {"status": 200, "message" : "I did nothing"}
        
        
    def retrieve_wigosids(self, any_ids: list = []) -> list:
        """retrieve information about current WIGOS IDs of stations passed as argument
        
        Parameter:
        any_ids (list): list of WIGOS Identifiers for which identifier information should be retrieved
        
        Returns:
        list: List of dict containing primary and secondary WIGOS Identifiers.
        
        """
        
        return [ { "primaryWigosID": "0-20000-0-123456" , "wigosID2" : "0-20000-2-123456", "wigosID3" : "0-20000-3-123456" , "wigosID4" : "0-20000-4-123456" }, ]