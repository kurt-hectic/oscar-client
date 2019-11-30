import logging
from lxml import etree

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()



def extractSchedules(station,**kwargs):

    filterOperational = kwargs.get('filterOperational',False)
    filterInternational = kwargs.get('filterInternational',False)
    filterVariables = kwargs.get('filterVariables',None)
    
    logging.debug("extractSchedules {} {} {}".format(filterOperational,filterInternational,filterVariables))
    
    schedules = []

    for observation in station['observations']:
    
        if filterVariables and not observation['variableId'] in filterVariables:
            logging.debug("filtering out observation due to variable {}".format(observation['variableId']))
            continue
        
        if filterOperational and not any(  prog_s["declaredStatusName"] == filterOperational for prog in observation["programs"] for prog_s in prog["stationProgramStatuses"] ):
            logging.debug("filtering out observation due to operational status ")
            continue
            
        variable = observation['variableId']
        variableName = observation['variableName']
            
        for deployment in observation['deployments']:
            for dataGeneration in deployment['dataGenerations']:
        
                if filterInternational and (  'isInternationalExchange' not in dataGeneration['reporting'] or dataGeneration['reporting']['isInternationalExchange'] ):
                    logging.debug("filering out DG because of international exchange")
                    continue
                    
                scheduleprops = ['monthSince','weekdaySince','hourSince','minuteSince','monthTill','weekdayTill','hourTill','minuteTill']
                schedule =  {} 
                for k in scheduleprops:
                    schedule[k] = dataGeneration['schedule'][k] if ( 'schedule' in dataGeneration and k in dataGeneration['schedule']) else None
                
                for k in ['temporalReportingIntervalDB','isInternationalExchange']:
                    if k in dataGeneration['reporting']:
                        schedule[k] = dataGeneration['reporting'][k]
                    else:
                        schedule[k] = None
                    
                schedule['variable'] = variable
                schedule['variableName'] = variableName
                
                schedules.append(schedule)

    logging.debug("returning:  {}".format(schedules))
    return schedules    