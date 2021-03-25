import os
import sys
import logging
import uuid 
import jsonschema
import json
import isodate

from lxml import etree
from io import BytesIO
from jsonschema import validate
from copy import deepcopy
from dict2xml import dict2xml
import xmltodict

#logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


mydir = os.path.dirname(__file__) + "/static/"

namespaces = { 
    'wmdr':'http://def.wmo.int/wmdr/2017',
    'gml' : 'http://www.opengis.net/gml/3.2',        
    'xlink' : 'http://www.w3.org/1999/xlink',
    'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
    'om' : 'http://www.opengis.net/om/2.0'
}

internalDefaultSchedule = { 
    "from": "2016-04-28T00:00:00Z", "to" : None,     
    "startMonth": 1,"endMonth": 12,
    "startWeekday": 1, "endWeekday": 7,
    "startHour": 0, "startMinute": 0,          
    "endHour": 23,    "endMinute": 59,
    "interval": 3600,     "international": True   
}

def makeElemnt(prefix,name):
    ret =  "{"+namespaces[prefix]+"}" +  name 
    logger.debug("made {} from {},{}".format(ret,prefix,name))
    return ret

def makeXMLSchedule(schedule):

    tmpl = """
        <wmdr:Schedule xmlns:wmdr="http://def.wmo.int/wmdr/2017" >
            <wmdr:startMonth>{startMonth}</wmdr:startMonth>
            <wmdr:endMonth>{endMonth}</wmdr:endMonth>
            <wmdr:startWeekday>{startWeekday}</wmdr:startWeekday>
            <wmdr:endWeekday>{endWeekday}</wmdr:endWeekday>
            <wmdr:startHour>{startHour}</wmdr:startHour>
            <wmdr:endHour>{endHour}</wmdr:endHour>
            <wmdr:startMinute>{startMinute}</wmdr:startMinute>
            <wmdr:endMinute>{endMinute}</wmdr:endMinute>
            <wmdr:diurnalBaseTime>00:00:00Z</wmdr:diurnalBaseTime>
    </wmdr:Schedule>
    """.format(**schedule)
    
    return etree.fromstring(tmpl)

def makeAffiliation(affiliation,status,begin_date):

    tmpl = """
        <wmdr:programAffiliation xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml/3.2">
            <wmdr:ProgramAffiliation>
                <wmdr:programAffiliation xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/ProgramAffiliation/{affiliation}"/>
                <wmdr:reportingStatus>
                    <wmdr:ReportingStatus>
                        <wmdr:reportingStatus xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/ReportingStatus/{status}"/>
                        <wmdr:validPeriod xlink:type="simple">
                            <gml:TimePeriod gml:id="id_{gml_id}">
                                <gml:beginPosition>{begin_date:%Y-%m-%d}</gml:beginPosition>
                                <gml:endPosition/>
                            </gml:TimePeriod>
                        </wmdr:validPeriod>
                    </wmdr:ReportingStatus>
            </wmdr:reportingStatus>
            </wmdr:ProgramAffiliation>
        </wmdr:programAffiliation>
    """.format(affiliation=affiliation,status=status,begin_date=begin_date,gml_id=str(uuid.uuid1().int))

    return etree.fromstring(tmpl)


with open(mydir+"/json-schemas/schedule_schema.json","r") as f:
    schedule_schema = json.load( f )

with open(mydir+"/json-schemas/schedule_schema_small.json","r") as f:
    schedule_schema_small = json.load( f )

class DTDResolver(etree.Resolver):
    def resolve(self, url, id, context):
        doms = ["http://schemas.wmo.int","http://schemas.opengis.net","http://www.w3.org"]
        for d in doms:
            url = url.replace(d,"")
        
        filename = mydir+"/xml-schemas" + url
        logger.debug("resolving XML schema {} to {}".format(url, filename))
        return self.resolve_filename( filename, context )


logger.debug("loading schema files")
# open and read schema file
with open(mydir+"/xml-schemas/wmdr_RC9.xsd", 'r') as schema_file:
    schema_to_check = schema_file

    parser = etree.XMLParser(load_dtd=True)
    parser.resolvers.add( DTDResolver() )

    xmlschema_doc = etree.parse(schema_to_check,parser)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    logger.debug("schema parsed sucessfully")

# open and read schema file for simple station type    
with open(mydir+"/xml-schemas/simplestation.xsd", 'r') as schema_file:
    schema_to_check = schema_file

    parser = etree.XMLParser(load_dtd=True)
    parser.resolvers.add( DTDResolver() )

    xmlschema_doc_simple = etree.parse(schema_to_check,parser)
    xmlschema_simple = etree.XMLSchema(xmlschema_doc_simple)
    logger.debug("schema parsed sucessfully")
    

logger.debug("loading XSLT files")
# open and read schema file
with open(mydir+"/xslts/wmdr2schedule.xsl", 'r') as xslt_file:
    xslt_root  = etree.parse(xslt_file)
    transform_schedules = etree.XSLT(xslt_root)

    logger.debug("XSLT parsed sucessfully")

# open and read schema file
with open(mydir+"/xslts/insert_contact.xsl", 'r') as xslt_file:
    xslt_root  = etree.parse(xslt_file)
    transform_insertcontact = etree.XSLT(xslt_root)

    logger.debug("XSLT parsed sucessfully")


# open and read schema file
with open(mydir+"/xslts/simple2wmdr.xsl", 'r') as xslt_file:
    xslt_root  = etree.parse(xslt_file)
    transform_simple = etree.XSLT(xslt_root)

    logger.debug("XSLT simple2wmdr parsed sucessfully")




class Station:
    
    def _initializeFromXML(self,wmdr,remove_comments=False):
    
        logger.debug("initializing station from XML: {}".format(wmdr))
        
    
        self.syntax_error=False
        self.invalid_schema=False
        self.has_been_fixed = False
        
        try:
            logger.debug("validating XML")
            parser = etree.XMLParser(remove_comments=remove_comments)
            self.xml_root = etree.parse(BytesIO(wmdr),parser)
            logger.debug('XML well formed, syntax ok.')
            # hold internal copy of original XML. Needs to be valid so that we can submit it 
            self.original_xml = deepcopy(self.xml_root)
            xmlschema.assertValid(self.xml_root)
        except etree.XMLSyntaxError as err:
            msg = str(err.error_log)
            logger.debug("station has XML syntax error {}".format(msg))
            self.syntax_error = True
            self.invalid_schema = True
        except etree.DocumentInvalid as err:
            msg = str(err.error_log)
            logger.debug("XML has a schema syntax error {}".format(msg))
            self.invalid_schema = True
            Station.__fix_deployments(self.original_xml,mode="update",defaultSchedule=internalDefaultSchedule)
            xmlschema.assertValid(self.original_xml)
            
    def _initializeFromDict(self,mydict):
    
        logger.debug("initializing station from Dict: {}".format(mydict))


        affiliations = [o["affiliation"] for o in mydict["observations"] ]
        mydict["affiliations"]=sorted(list(set(affiliations)),reverse = True)

        mydict = {"station": mydict}
        
        # remove dicttoxml code
        #my_item_func = lambda x: 'observation' if x=="observations" else ('url' if x=='urls' else 'affiliation')
        #xml = dicttoxml(mydict,attr_type=False,item_func=my_item_func,root=False).decode("utf-8")
        #xml = xml.replace("True","true").replace("False","false")
        
        # adjust our dict format to the format required by xml2dict
        mydict["station"]["affiliations"] =  {"affiliation": mydict["station"]["affiliations"]  }

        if "urls" in mydict["station"]:
            mydict["station"]["urls"] =  {"url": mydict["station"]["urls"]  }         
        
        mydict["station"]["observations"] =  {"observation": mydict["station"]["observations"]  }         
        
        xml = dict2xml(mydict, wrap=None, indent="  ")
        xml = xml.replace("True","true").replace("False","false")
        
        self._initializeFromSimpleXML(xml)
        
        
        
    def _initializeFromSimpleXML(self,xml):
        
        logger.debug("initializing station from XML: {}".format(xml))
    
        xml_root = etree.fromstring(xml)
        
        try:
            xmlschema_simple.assertValid(xml_root)
        except etree.DocumentInvalid as di:
            logger.warning("XML invalid:",di,xml)
            #sys.exit(1)

        wmdr_tree  = transform_simple(xml_root) # 
        self._initializeFromXML( str(wmdr_tree).encode("utf-8") )
        
        self.simplexml = xml


    
    def __init__(self,*args, **kwargs):
        """initializes a Station object. The object can be initialized by passing a WMRD record as string, a string encoded JSON representation, a simplified XML representation or using keyword parameters."""
        logger.debug("initializing station {}".format(kwargs))
        self.simplexml=None
        
        if len(args) == 1 and (len(kwargs) == 0 or (len(kwargs)==1 and 'remove_comments' in kwargs)) :
            info = args[0]
            try:
                if not type(info) is dict:                    
                    mydict = json.loads(info)
                self._initializeFromDict(info)
            except json.decoder.JSONDecodeError: 
                try:
                    logger.debug("input not JSON.. try XML in WMDR")
                    remove_comments = kwargs.get('remove_comments',False)
                    self._initializeFromXML(info,remove_comments=remove_comments)
                except etree.DocumentInvalid:
                    logger.debug("input not WMDR, trying simple XML")
                    try:
                        self._initializeFromSimpleXML(info)
                    except Exception as e:
                        logger.warning("could not parse XML {}".format(e))
            logger.debug("station initialized")
        else: 
            try:
                params = ['name','wigosid','latitude','longitude','elevation','country','established','region','observations','stationtype','status']
                mydict = { p:kwargs[p] for p in params }
                optional_params = ['urls','description','timezone','organization']
                for p in optional_params:
                    if p in kwargs:
                        mydict[p] = kwargs[p]
                
                default_schedule = kwargs.get("default_schedule",None)

                # assign default schedule and validate 
                for o in kwargs["observations"]:
                    if default_schedule and not "schedule" in o.keys():
                        o["schedule"] = default_schedule.copy()
                    
                    validate( instance=o["schedule"] , schema=schedule_schema_small ,  format_checker=jsonschema.FormatChecker() )
                
                self._initializeFromDict(mydict)
            
            except KeyError as ke:
                msg = "required param {} not present {}".format(ke,kwargs.keys())
                logger.warning(msg)
                raise ValueError(msg)
                
            except jsonschema.exceptions.ValidationError as va:
                msg = "schedule object not valid {}".format(va)
                logger.warning(msg)
                raise ValueError(msg)
        

    
    def save(self,client,override_doublesave=False):
        """submits the station to OSCAR using the client object passed in via `client`
        This method allows to get around a bug in OSCAR todo with incorrect gml:id, as this method first saves the originally downloaded XML back to OSCAR,
        therefore setting the gml:id and then re-submits the modified XML.
        """
        self.validate(original= (not override_doublesave))
        # need to first save the original XML to make sure the gml:id are set
        if not override_doublesave:
            original_xml = etree.tostring(self.original_xml,  pretty_print=True, xml_declaration=False, encoding="unicode")
        
            # with open("tmp/out1.xml","w",encoding="utf8") as f:
                # f.write(original_xml)
            
            status = client.uploadXML( original_xml )
            logger.debug("uploaded original XML to set gml:id. Status: {}".format(status))
        
            if not status in ['SUCCESS_WITH_WARNINGS','SUCCESS']:
                raise Exception("error saving original XML ({})".format(status))
        
        new_xml = str(self)
        
        # with open("tmp/out2.xml","w",encoding="utf8") as f:
                # f.write(new_xml)
            
        status = client.upload_XML(new_xml)
        if not status in ['SUCCESS_WITH_WARNINGS','SUCCESS','VALID_XML_WITH_ERRORS_OR_WARNINGS']:
            raise Exception("error saving updated XML ({})".format(status))

        logger.debug("uploaded updated XML. Status: {}".format(status))
     
    def fix_and_update_datageneration(self,gid,defaultSchedule):
        """repairs the datageneration referenced by the gml:id `gid` using the schedule information passed in `defaultSchedule`
        additionally, the datageneration element is updated with the information passed in via `defaultSchedule`
        """
        self.fix_datageneration(gid,defaultSchedule)
        self.update_schedule(gid,defaultSchedule,override=True)
    
    def fix_datageneration(self,gid,defaultSchedule):
        """repairs the datageneration referenced by the gml:id `gid` using the schedule information passed in `defaultSchedule` """
        return Station.__fix_datageneration(self.xml_root,gid,defaultSchedule)
    
    def __fix_datageneration(xml_root,gid,defaultSchedule):
    
        xpath = "//wmdr:dataGeneration/wmdr:DataGeneration[@gml:id='{}']".format(gid)
        elem = xml_root.xpath(xpath,namespaces=namespaces)
        
        if not elem:
            raise ValueError("no schedule (datageneration) with gid='{}' xpath: {}".format(gid,xpath))
        
        elem=elem[0]
        logger.debug("fix_dg: fixing {}".format(elem))
                    
        schedule_elem = elem.find( makeElemnt("wmdr","schedule") )
        if schedule_elem.find( makeElemnt("wmdr","Schedule") ) is None:
            schedule = makeXMLSchedule(defaultSchedule) 
            schedule_elem.append ( schedule )
        
        reporting_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:temporalReportingInterval",namespaces=namespaces)
        if not reporting_elem:
            reporting_elem = etree.Element(makeElemnt("wmdr","temporalReportingInterval"))
            uom_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:uom",namespaces=namespaces)[0]
            uom_elem.addnext( reporting_elem )
        else:
            reporting_elem=reporting_elem[0]
        reporting_elem.text =  "PT{}S".format(defaultSchedule["interval"]) 
        
        exchange_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:internationalExchange",namespaces=namespaces)
        if not exchange_elem:
            exchange_elem = etree.Element(makeElemnt("wmdr","internationalExchange"))
            uom_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:uom",namespaces=namespaces)[0]
            uom_elem.addprevious( exchange_elem )
        else:
           exchange_elem=exchange_elem[0] 
        exchange_elem.text = "true" if defaultSchedule["international"] else "false"
        
    
    def fix_deployments(self,mode="update",defaultSchedule=None):
        """repairs the corrupted deployments downloaded from OSCAR/Surface according to known issues with the XML export in some stations.
        In `mode` : update the schedule and datageneration object is complemtend with the information passed in `defaultSchedule`.
        In `mode` : delete the corrupted datageneration elements from the station
        """
    
        if self.syntax_error:
            raise Exception("invalid XML")

    
        if self.has_been_fixed:
            txt = "XML has already been fixed, doing nothing"
            logger.warning(txt)
            print(txt)
            return False

        Station.__fix_deployments(self.xml_root,mode,defaultSchedule)
        
        try:
            xmlschema.assertValid(self.xml_root)
            logger.debug("XML schema sucessfully fixed. Schema valid.")
            self.has_been_fixed=True
            self.invalid_schema=False
            return True
        except:
            return False

        
    
    def __fix_deployments(xml_root,mode="update",defaultSchedule=None):

        if not mode in ["delete","update"]:
            raise ValueError("invalid mode {} . Use one of merge,update,delete".format(mode))
        if mode in ["update",] and not defaultSchedule:
            raise ValueError("specifiy a defaultSchedule")
        
        if mode in ["update",]:
            try:
                validate( instance=defaultSchedule , schema=schedule_schema ,  format_checker=jsonschema.FormatChecker() )
            except jsonschema.exceptions.ValidationError as ve:
                logger.debug("invalud schedule")
                raise ValueError("schedule not valid {}".format(str(ve)))

        try:
            xmlschema.assertValid(xml_root)
        except etree.DocumentInvalid as err:
            for error in xmlschema.error_log:
                pass
                #print("ERROR ON LINE %s: %s" % (error.line, error.message))
                #print(error)
            
            if mode=="delete": # remove invalid deployments
        
                xpath = '//wmdr:dataGeneration/wmdr:DataGeneration[ wmdr:schedule[not( wmdr:Schedule )] or wmdr:reporting/wmdr:Reporting[not ( wmdr:temporalReportingInterval) ] ]/../../../..' # identify wmdr:Process of empty deployments
            
                known_invalid_elements = xml_root.xpath(xpath , namespaces=namespaces)
                
                for elem in known_invalid_elements:
                    logger.debug("removing {}".format(elem))
                    om_procedure = elem.getparent()
                    om_procedure.attrib.pop( makeElemnt("xlink","type") )
                    om_procedure.remove(elem)
                    om_procedure.text = None
                    om_procedure.attrib[ makeElemnt("xsi","nil")] = "true"
                
            if mode=="update":
                logger.debug("assigning default schedule to corrupted items")
            
                # xpath = '//wmdr:dataGeneration/wmdr:DataGeneration[ wmdr:schedule[not( wmdr:Schedule )] or wmdr:reporting/wmdr:Reporting[not ( wmdr:temporalReportingInterval) ] or wmdr:reporting/wmdr:Reporting[not ( wmdr:internationalExchange) ]  ]'

                xpath = '//wmdr:dataGeneration/wmdr:DataGeneration[ wmdr:schedule[not( wmdr:Schedule )] or wmdr:reporting/wmdr:Reporting[not ( wmdr:temporalReportingInterval) ] or wmdr:reporting/wmdr:Reporting[not ( wmdr:internationalExchange) ]  ]/@gml:id'
                
                known_invalid_elements = xml_root.xpath(xpath , namespaces=namespaces)
                
                for elem in known_invalid_elements:
                    gid = elem
                    Station.__fix_datageneration(xml_root,gid,defaultSchedule)
                    
                    # logger.debug("fixing {}".format(elem))
                    
                    # schedule_elem = elem.find( makeElemnt("wmdr","schedule") )
                    # if not schedule_elem.find( makeElemnt("wmdr","Schedule") ):
                        # schedule = makeXMLSchedule(defaultSchedule) 
                        # schedule_elem.append ( schedule )
                    
                    # reporting_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:temporalReportingInterval",namespaces=namespaces)
                    # if not reporting_elem:
                        # reporting_elem = etree.Element(makeElemnt("wmdr","temporalReportingInterval"))
                        # uom_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:uom",namespaces=namespaces)[0]
                        # uom_elem.addnext( reporting_elem )
                    # else:
                        # reporting_elem=reporting_elem[0]
                    # reporting_elem.text = defaultSchedule["interval"]
                    
                    # exchange_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:internationalExchange",namespaces=namespaces)
                    # if not exchange_elem:
                        # exchange_elem = etree.Element(makeElemnt("wmdr","internationalExchange"))
                        # uom_elem = elem.xpath("wmdr:reporting/wmdr:Reporting/wmdr:uom",namespaces=namespaces)[0]
                        # uom_elem.addprevious( exchange_elem )
                    # else:
                       # exchange_elem=exchange_elem[0] 
                    # exchange_elem.text = "true" if defaultSchedule["international"] else "false"
                    
                        

            # with open("test_out.xml","wb") as f:
                # f.write( etree.tostring(xml_root,  pretty_print=True, xml_declaration=True))
            
    def update_affiliations(self,affiliation: str = None ,  variables: list = [], operational_status = 'operational', program_id = None , begin_date = None ):        
    
        logger.debug("update_affiliations: affiliation: {}, vars: {}, status: {}, id: {}, date:{} ".format(affiliation,variables,operational_status,program_id,begin_date))
    
        if not affiliation in self.affiliations(): # need to add new affiliation element
            affiliation_element = self.xml_root.xpath('/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:programAffiliation',namespaces=namespaces)[0]
            
            if len(affiliation_element)==0:
                raise Exception("could not find existing affiliation to append to.. XML should already have at least one affiliation")

            affiliation_element.addnext( makeAffiliation(affiliation,operational_status,begin_date) )
    
        # now add the affiliations under the observations
        updated_variables = { var:True for var in variables }
        for var in variables:
            #xpath = "/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:observation/wmdr:ObservingCapability[wmdr:observation/om:OM_Observation/om:observedProperty[@xlink:href='http://codes.wmo.int/wmdr/ObservedVariableAtmosphere/{}']]/wmdr:programAffiliation".format(var)
            xpath = "/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:observation/wmdr:ObservingCapability[wmdr:observation/om:OM_Observation/om:observedProperty[contains(@xlink:href,'http://codes.wmo.int/wmdr/') and contains(@xlink:href,'/{}')]]/wmdr:programAffiliation".format(var)
            
            observation_affiliations = self.xml_root.xpath(xpath,namespaces=namespaces)
            
            if len(observation_affiliations)==0:
                logging.info("no observation for variable {}, skipping".format(var))
                updated_variables[var]=False
                continue
                        
            existing_affiliations = [elem.get("{http://www.w3.org/1999/xlink}href").split('/')[-1] for elem in observation_affiliations]
            
            if not affiliation in existing_affiliations:
                # need to get the wmdr:/programAffiliation element. The xpath before selected the 
                observation_affiliations[-1].addnext( etree.fromstring("""
                    <wmdr:programAffiliation  
                        xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wmdr="http://def.wmo.int/wmdr/2017"
                        xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/{}"/>""".format(affiliation)
                ))
                
        logger.debug("update_affiliations returns: {}".format(updated_variables))
        return updated_variables
        
    
    
    def affiliations(self):
        """extract the affiliations of the station"""
        
        xpath = '/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:programAffiliation/wmdr:ProgramAffiliation/wmdr:programAffiliation/@xlink:href'

        affiliation_elements = self.xml_root.xpath(xpath , namespaces=namespaces)
        ret = [str(elem).split('/')[-1] for elem in affiliation_elements]

        return ret


    def schedules(self): 
        """extracts the schedules of the station and returns them grouped by variable"""
        result_tree = transform_schedules(self.xml_root)
        
        def convert_types(path,key,value):
            int_fields = ['startMonth','endMonth','startWeekday','endWeekday','startHour','endHour','startMinute','endMinute']
            bool_fields = ['international',]
            interval_fields = ['interval',]
            
            try:
                if key in int_fields:
                    return key , int(value)
                    
                if key in bool_fields:
                    return key , value in ['True','true']
                    
                if key in interval_fields:
                    return key, int(isodate.parse_duration(value).total_seconds())
                    
                return key, value
            except (ValueError, TypeError):
                return key, value
                
        station = xmltodict.parse(result_tree,postprocessor=convert_types, force_list=('observations','deployments','datagenerations'))
        
        res = {}
        for o in station['station']['observations']:  
            var_id = int(o['variableid'].split('/')[-1])
            res[var_id] = o
            
        return res
        
    def variables(self):
        """returns the variables of the station"""

        xpath = "/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:observation/wmdr:ObservingCapability/wmdr:observation/om:OM_Observation/om:observedProperty/@xlink:href"

        variables_elements = self.xml_root.xpath(xpath,namespaces=namespaces)
        
        if not variables_elements:
            raise ValueError("no variable element")
            
        result = []
        
        for elem in variables_elements:
            result.append(int(elem.split('/')[-1]))
            
        return list(set(result)) 

        
        
    def current_schedules(self,variables=None):
        """returns the ongoing schedules grouped by variable. Can filter by list of `variables`"""
        
        observations = self.schedules()
        
        if variables:
            observations = {var:obs for (var,obs) in observations.items() if var in variables }
        
        for var,obs in observations.items():
            for d in obs['deployments']:
                d['datagenerations'] = [ dg for dg in d['datagenerations'] if not dg['schedule']['to']  ] # filter out schedules with end date
                
            obs['deployments'] = [ d for d in obs['deployments'] if d['datagenerations'] ]
            
        observations = {var:obs for (var,obs) in observations.items() if obs['deployments'] }
                
        return observations
        
    def current_schedules_by_var(self,var_id):
        """returns the ongoing schedules corresponding to the variable `var_id` grouped by variable"""
        
        schedules = self.current_schedules()
        codelistid = "http://codes.wmo.int/wmdr/{}".format(var_id)
        
        observation = None
        for var,o in schedules.items():
            if var == codelistid:
                observation = o
                
        return observation
        
    def get_name(self):
        """return the name of the station"""
        
        xpath = '/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/gml:name'
        name_elem = self.xml_root.xpath(xpath,namespaces=namespaces)
        
        if not name_elem:
            raise ValueError("no name element")
            
        return str(name_elem[0].text)
    
    
    def get_wigos_ids(self,primary=True):
        """returns the WIGOS IDs of a station"""
        
        xpath = '/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/gml:identifier'
        wigosid_elem = self.xml_root.xpath(xpath,namespaces=namespaces)
        
        if not wigosid_elem:
            raise ValueError("no WIGOS ID element")
            
        return (wigosid_elem[0].text).split(",") 


    def add_existing_contact(self,email):
        """adds a station contact to the station. 
        The station contact must already exits in OSCAR and is referenced by it's email address
        """
        
        if not email:
            raise Exception("need to provide email address")
            
       
        self.xml_root = transform_insertcontact(self.xml_root, email= etree.XSLT.strparam(email) )
        

    def update_wigosids(self,wigos_ids=[]):
        """updates the stations adding the wigos ids passed as parameters. The first wigos id passed will be set a primary. Existing wigos identifiers will be kept, since the OSCAR data model does not allow to remove wigos ids.
        
        Parameters:
        wigos_id (list): the list of WIGOS identifiers to add
        
        Returns:
        list: ordered list of new wigos identifiers
        """
        
        if len(wigos_ids) == 0 or not isinstance(wigos_ids,list):
            return False

        new_wigos_ids = list(dict.fromkeys( wigos_ids + self.get_wigos_ids() )) # remove duplicates but keep order
        
        xpath = '/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/gml:identifier'
        wigosid_elem = self.xml_root.xpath(xpath,namespaces=namespaces)
        
        if not wigosid_elem:
            raise ValueError("no WIGOS ID element")
        
        wigosid_elem[0].text = ",".join(new_wigos_ids)
        
        return new_wigos_ids
    
    
    def update_schedule(self,gid,schedule,override=False):
        """updates the schedule indicated by `gid` with the `schedule` element"""
    
        if self.invalid_schema and not override:
            raise Exception("schema invalid. Fix schema by running fix_deployments first or use override=True")
            
        try:
            validate( instance=schedule , schema=schedule_schema ,  format_checker=jsonschema.FormatChecker() )
        except jsonschema.exceptions.ValidationError as ve:
            logger.debug("invalid schedule")
            raise ValueError("schedule not valid {}".format(str(ve)))

        xpath = "//wmdr:dataGeneration/wmdr:DataGeneration[@gml:id='{}']".format(gid)
        dg_elem = self.xml_root.xpath(xpath,namespaces=namespaces)
        
        if not dg_elem:
            raise ValueError("no schedule (datageneration) with gid='{}'".format(gid))
            
        dg_elem=dg_elem[0]
        from_elem = dg_elem.xpath("./wmdr:validPeriod/gml:TimePeriod/gml:beginPosition",namespaces=namespaces)
        to_elem = dg_elem.xpath("./wmdr:validPeriod/gml:TimePeriod/gml:endPosition",namespaces=namespaces)
        interval_elem = dg_elem.xpath("./wmdr:reporting/wmdr:Reporting/wmdr:temporalReportingInterval",namespaces=namespaces) 
        international_elem = dg_elem.xpath("./wmdr:reporting/wmdr:Reporting/wmdr:internationalExchange",namespaces=namespaces) 
        schedule_elem = dg_elem.xpath("./wmdr:schedule/wmdr:Schedule",namespaces=namespaces)
        
        # convert values to String for setting in XML.. except when None
        #schedule = { key: str(val) if val else None for (key,val) in schedule.items() }
        
        elements_present =  len(from_elem)>0 and len(to_elem)>0 and len(interval_elem)>0 and len(international_elem)>0 and len(schedule_elem)>0
        
        if from_elem:
            from_elem[0].text = schedule["from"]
        if to_elem:
            to_elem[0].text = schedule["to"] #if schedule["to"] else ""
        if interval_elem:
            interval_elem[0].text =  "PT{}S".format(str(schedule["interval"]))
        if international_elem:
            international_elem[0].text = str(schedule["international"]).lower()
            
        for key,val in schedule.items():
            if key in ['from','to','interval','international']:
                continue
                
            elem = dg_elem.xpath("./wmdr:schedule/wmdr:Schedule/wmdr:{}".format(key),namespaces=namespaces)
            if elem:
                logger.debug("setting element '{}' to '{}'".format(key,val))
                elem[0].text = str(val)
                
        return elements_present
    
    def __str__(self):
        return etree.tostring(self.xml_root,  pretty_print=True, xml_declaration=False, encoding="unicode"  )
        
    def simple_xml(self):
        """returns the simplified XML represtnations of the station
        The method only works if the station object has been initialized via JSON, parameters or simplifieed XML (and not when initialized by WMDR)
        """
        if self.simplexml:
            return self.simplexml
        else:
            return None
        
    def validate(self,original=False):
        """Validates the station against the WMDR schema"""
        
        xmlschema.assert_(self.xml_root)
        if original:
            try:
                xmlschema.assertValid(self.original_xml)
            except etree.DocumentInvalid as err:
                raise Exception("original XML not valid ({})".format(str(err)))
        