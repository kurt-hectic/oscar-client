import requests
from bs4 import BeautifulSoup
import sys
import getopt
import logging
import json
import re
from flask import current_app

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)            

QLACK_TOKEN_NAME = "X-Qlack-Fuse-IDM-Token-GO"
USER_DETAILS_URL = "//rest/api/security-proxy/user-details"
LOGOUT_URL = "//auth?logout"

class OscarSaml(object):
    
    def __init__(self,**kwargs):
        self.oscar_url = kwargs.get('oscarurl')
        


    def __parseTicket(self,tokenstring):
        tmp = re.sub(r'(?<={|,)([a-zA-Z][a-zA-Z0-9]*)(?=:)', r'"\1"', tokenstring.strip('"'))
        tmp= re.sub(r'(?<=:)([^,"\[\]}]+)(?=[,}$])', r'"\1"',tmp)
        tmp = re.sub(r'(?<=[\[,])([_A-Z0-9]+)(?=[,\]])',r'"\1"',tmp)
        
        token = json.loads(tmp)
        ticket = token["ticket"]
        
        return ticket 

                
    # extract from html the form keys and values as dicctionary
    def __parseFormInputs(self,html,url):

        log.debug("got html {}".format(html))

        #log.debug("accessing {}".format(url))
        #log.debug("form {}".format(html))
        
        soup = BeautifulSoup(html, 'html.parser')

        #print(soup.prettify())

        params = {}

        for element in soup.find_all('input'):
            if 'name' in element.attrs.keys() and 'value' in  element.attrs.keys()  :
                params[element["name"]]=element["value"]
        
        element = soup.find("form")
        actionurl = None
        if element and element.get("action"):
            actionurl = element.get("action")
            if "http" not in actionurl: #not FQDN
                actionurl = "{}{}".format(url,actionurl)
        
            actionurl = ''.join(actionurl.split()) #remove whitespaces
         
        #action = element.attr["action"]
        #print("action:{}".format(action))
        log.debug("parsed action url ({}) and params: ({})".format(actionurl,params))
        
        return [params,actionurl]

    # we get a URL using a session and extract the form parameters, which are returned  
    def __requestUrlandGetForm(self,url,session,params,text,mode="POST"):
        
        headers = {"Accept-Language": "en-US,en;"}
        
        if mode=="POST":
            r = session.post(url,data=params,headers=headers)
        elif mode=="GET":
            r = session.get(url,headers=headers)
        else:
            print("{} not supported".format(mode))
            sys.exit(1)
            
        log.debug("{} .. {} status:{}".format(text,url,r.status_code))
        
        if not r.status_code == 200:
            log.warning("problem with request code: {}".format(r.status_code))
            sys.exit(1)

        html_doc = r.text
        
        if "?login" in url: #if it is the BIT login we check for error texts
            #print(html_doc)
            #if any(x in html_doc for x in  ['credential is permanently locked','The login attempt has failed','Die Anmeldung ist fehlgeschlagen'] ):
                
            soup = BeautifulSoup(html_doc, 'html.parser')
            element = soup.find('span', {"class":"iconDialogError"})
            if element:
                log.info("BIT Login failed: {}".format(element.string))
                raise Exception("login into BIT failed")
            else:
                log.info("BIT login ok..")

        
        [params,actionurl] = self.__parseFormInputs(html_doc,url)  

        return [params,actionurl]

    def performLogout(self,cookies,qlack_token):

        log.info("logging out")
    
        headers = {'Content-type':'application/json;charset=utf-8'}           
        headers = {'Accept': 'application/json' , }
        headers[QLACK_TOKEN_NAME]  =  "{"+qlack_token+"}" 
        r = requests.get(self.oscar_url+LOGOUT_URL , headers=headers ,  cookies=cookies )
        
        log.info("response {}".format(r))


        if r.status_code == 200:
            return True
        else:
            return False
        
        
    def getUserCredentials(self,cookies,qlack_token):
        
        headers = {'Content-type':'application/json;charset=utf-8'}           
        headers = {'Accept': 'application/json' , }
        headers[QLACK_TOKEN_NAME]  =  "{"+qlack_token+"}" 
        
        r = requests.get(self.oscar_url+USER_DETAILS_URL , headers=headers ,  cookies=cookies )

        if r.status_code == 200:
            login_data = json.loads(r.content)
            return login_data
        else:
            return False
        
    def performLogin(self,username,password):    

        try:        
            log.debug("step 1: oscar login button")
            oscarSession = requests.Session()
            login_url = self.oscar_url + "//save-state?programId="
            [params,nexturl]=self.__requestUrlandGetForm(login_url,oscarSession,None,"initiating oscar session","GET")
                
            log.debug("step 2: send SAML token to BIT")
            bitSession = requests.Session()
            [params2,nexturl]=self.__requestUrlandGetForm(nexturl,bitSession,params,"sending SAML token to BIT")

            log.debug("step 3: contacting IDP")
            [params3,nexturl]=self.__requestUrlandGetForm(nexturl,bitSession,params2,"SSO at BIT")
            
            #prepare for login
            params3['isiwebuserid']=username
            params3['isiwebpasswd']=password

            # login
            log.debug("step 4: sending username and password to BIT")
            [params4,nexturl]=self.__requestUrlandGetForm(nexturl,bitSession,params3,"sending username and password to BIT")
            
            log.debug("step 5: get SAML token")
            # get final SAML token
            [params5,nexturl]=self.__requestUrlandGetForm(nexturl,bitSession,params4,"SSO2 at BIT")
            
            log.debug("step 6: returning to OSCAR")
            # we're back to OSCAR
            [params6,nexturl]=self.__requestUrlandGetForm(nexturl,oscarSession,params5,"back to OSCAR")

            log.debug("step 7: SSO at OSCAR")    
            # OSCAR sso
            [params7,nexturl]=self.__requestUrlandGetForm(nexturl,oscarSession,params6,"SSO at OSCAR")

            log.debug("step 8: authentication at OSCAR")
            # OSCAR auth
            [params8,nexturl]=self.__requestUrlandGetForm(nexturl,oscarSession,params7,"auth at OSCAR")
            oscar_cookies = oscarSession.cookies.get_dict()

            log.debug("cookies: {}".format( oscar_cookies ))

            log.debug("cookies: {}".format(oscar_cookies))
            
            qlack_cookie = oscar_cookies[QLACK_TOKEN_NAME]
            log.debug("qlack cookie: {}".format(qlack_cookie))
            
            ticket = self.__parseTicket(qlack_cookie)
            qlack_token = '"ticketID":"{ticketID}","validUntil":{validUntil},"autoExtendValidUntil":{autoExtendValidUntil},"autoExtendDuration":{autoExtendDuration},"userID":"{userID}","username":"{username}","signature":"{signature}"'.format(**ticket)
            
            log.debug("token: {}".format(qlack_token))
                
            # test if we are logged in.

            login_data = self.getUserCredentials(oscar_cookies , qlack_token)

            # "username":"72119686-3962-4bc2-8652-59af15ba20bd"
            username_token = ticket["username"] 
            username_data = login_data["id"]
            log.debug("obtained usernames {} and {} ".format(username_token,username_data))
            
            if username_token == username_data:
                ret = {'token' : qlack_token , 'cookies' : oscar_cookies }
                log.debug("sucesfully logged on {}, session info {}".format(username_token,ret))
                return ret
            else:
                log.debug(" logged for {} {} unsucessfull".format(username_token,username_data))
                return False
                
        except Exception as e:
            log.warning("login problem.. {}".format(e))
            return False