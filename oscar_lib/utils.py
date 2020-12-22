import re
import logging
import datetime
from lxml import etree

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()

month_map = { "JAN":1, "FEB":2, "MAR":3, "APR":4, "MAR":5, "JUN":6, "JUL":7, "AUG":8, "SEP":9, "OCT":10, "NOV":11, "DEC":12  }
weekday_map = { "MON":1, "TUE":2, "WED":3, "THU":4, "FRI":5, "SAT":6, "SUN":7 }

month_map_rev = {v: k.capitalize() for k, v in month_map.items()}
weekday_map_rev = {v: k.capitalize() for k, v in weekday_map.items()}

def convert_schedule_rev(schedule):

    logger.debug("convert_schedule_rev: {}".format(schedule))

    for elem in ["startMonth","endMonth","startWeekday","endWeekday"]:
        if "Month" in elem:
            schedule[elem] = month_map_rev[schedule[elem]] if schedule[elem] else None
        else:
            schedule[elem] = weekday_map_rev[schedule[elem]] if schedule[elem] else None
      
    #if schedule["interval"]:
    #    timedelta = isodate.parse_duration(schedule['interval'])
    #    schedule["interval"]=int(timedelta.total_seconds())
    schedule["interval"]=int(schedule["interval"])
    
    empty=True
    for k,v in schedule.items():
        empty = empty and (v==None or v==False)
    
    
    return None if empty else schedule


def convert_schedule(new_schedule):

    p = re.compile( r"^(?P<startMonth>\w{3})-(?P<endMonth>\w{3})\/(?P<startWeekday>\w{3})-(?P<endWeekday>\w{3})\/(?P<startHour>\d{1,2}):(?P<startMinute>\d{1,2})-(?P<endHour>\d{1,2}):(?P<endMinute>\d{1,2})\/(?P<interval>\d+)$")

    m = p.search(new_schedule)
    
    if not m:
        return False

    schedule = m.groupdict()

    schedule["startMonth"]=month_map[schedule["startMonth"].upper()] 
    schedule["endMonth"]=month_map[schedule["endMonth"].upper()]
    
    schedule["startWeekday"]=weekday_map[schedule["startWeekday"].upper()]
    schedule["endWeekday"]=weekday_map[schedule["endWeekday"].upper()]
    
    schedule["startHour"] = int(schedule["startHour"])
    schedule["endHour"] = int(schedule["endHour"])
    schedule["startMinute"] = int(schedule["startMinute"])
    schedule["endMinute"] = int(schedule["endMinute"])
    
    #schedule["interval"] = isodate.duration_isoformat(datetime.timedelta(seconds=int(schedule["interval"])))
    
    return schedule


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