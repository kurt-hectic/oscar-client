import requests
import csv
import sys
from jellyfish import jaro_winkler

def minimumEditDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]

class CodelistResolver:





    def __init__(self,codelist):
    
        codelists = [codelist,]
        if codelist == "variables":
            codelists = ["ObservedVariableTerrestrial","ObservedVariableAtmosphere","ObservedVariableEarth","ObservedVariableOcean","ObservedVariableOuterSpace"]
        
        self.map={}
        for codelist in codelists:
            r=requests.get("http://codes.wmo.int/wmdr/{}?_format=csv".format(codelist))
            decoded_content = r.content.decode('utf-8')
            
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            
            for row in my_list:
                key,val = row[3:5]
                self.map[key.lower()]=val
        
        
    def resolve(self,key):
        key=key.lower()
        if key in self.map:
            return (self.map[key],key)
        
        else:
            min=sys.maxsize
            minval=None
            
            for mykey,myval in self.map.items():
                #sdist = minimumEditDistance(mykey,key)
                dist = jaro_winkler(mykey,key)
                if dist<min:
                    min=dist
                    minval=mykey
                    
            return (self.map[minval],minval)
        
