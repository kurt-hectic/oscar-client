import requests 
import logging
import xml.etree.ElementTree as ET
from lxml import etree
from io import BytesIO


logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()

class DTDResolver(etree.Resolver):
    def resolve(self, url, id, context):
        doms = ["http://schemas.wmo.int","http://schemas.opengis.net","http://www.w3.org"]
        for d in doms:
            url = url.replace(d,"")
        
        filename = "./schemas" + url
        return self.resolve_filename( filename, context )


logger.info("loading schema files")
# open and read schema file
with open(r"schemas/wmdr_RC9.xsd", 'r') as schema_file:
    schema_to_check = schema_file

    parser = etree.XMLParser(load_dtd=True)
    parser.resolvers.add( DTDResolver() )

    xmlschema_doc = etree.parse(schema_to_check,parser)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    logger.info("schema parsed sucessfully")


class Station:

    def __init__(self,wmdr):
        logging.debug("init")
        
        self.syntax_error=False
        self.invalid_schema=False
        
        try:
            logger.debug("validating XML")
            self.xml_root = etree.parse(BytesIO(wmdr))
            logger.debug('XML well formed, syntax ok.')
            xmlschema.assertValid(self.xml_root)
        except etree.XMLSyntaxError as err:
            msg = str(err.error_log)
            logger.warning("station has XML syntax error {}".format(msg))
            self.syntax_error = True
            self.invalid_schema = True
        except etree.DocumentInvalid as err:
            msg = str(err.error_log)
            logger.warning("XML has a schema syntax error {}".format(msg))
            self.invalid_schema = True

    
    
    
    def load_station(wigos_id=None,internal_id=None):
        if not wigos_id and not internal_id:
            raise ValueError("need either wigos id or internal ID")
            
        if not wigos_id:
            logger.debug("trying to get wigos id for {}".format(internal_id))
            r = requests.get("https://oscar.wmo.int/surface/rest/api/stations/station/{}/stationReport".format(internal_id))
            if r.status_code != 200:
                raise KeyError("{} not contained in OSCAR or cannot be downloaded".format(internal_id))

            json = r.json()
            
            for wid in json["wigosIds"]:
                if wid["primary"]:
                    wigos_id = wid["wid"]
                    
            if not wigos_id:
                raise ValueError("station has not primary WIGOS ID")
        
        logger.debug("getting XML for {}".format(wigos_id))
        r = requests.get("https://oscar.wmo.int/surface/rest/api/wmd/download/{}".format(wigos_id))
        
        if r.status_code != 200:
            raise KeyError("{} not contained in OSCAR or cannot be downloaded".format(wigos_id))
            
        
        wmdr = r.content 
        
        station = Station(wmdr)
        
        
    def fixDeployments(self,delete=True,defaultSchedule=None):
    
        if self.syntax_error:
            raise Exception("invalid XML")
        
        try:
            xmlschema.assertValid(self.xml_root)
        except etree.DocumentInvalid as err:
            for error in xmlschema.error_log:
                pass
                #print("ERROR ON LINE %s: %s" % (error.line, error.message))
                #print(error)
            
            namespaces = { 
                'wmdr':'http://def.wmo.int/wmdr/2017',
                'gml' : 'http://www.opengis.net/gml/3.2'        
            }
        
            xpath = '//wmdr:dataGeneration/wmdr:DataGeneration[ wmdr:schedule[not( wmdr:Schedule )] and wmdr:reporting/wmdr:Reporting[not ( wmdr:temporalReportingInterval) ] ]/../../../..' # identify wmdr:Process of empty deployments
        
            known_invalid_elements = self.xml_root.xpath(xpath , namespaces=namespaces)
            
            for elem in known_invalid_elements:
                logger.debug("removing {}".format(elem))
                om_procedure = elem.getparent()
                om_procedure.attrib.pop('{http://www.w3.org/1999/xlink}type')
                om_procedure.remove(elem)
                om_procedure.text = None
                om_procedure.attrib["{http://www.w3.org/2001/XMLSchema-instance}nil"] = "true"
            
            #with open("test_out.xml","wb") as f:
            #    f.write( etree.tostring(self.xml_root,  pretty_print=True, xml_declaration=True))
            
            xmlschema.assertValid(self.xml_root)
            