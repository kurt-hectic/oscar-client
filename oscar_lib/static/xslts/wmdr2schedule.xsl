<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:ns6="http://def.wmo.int/opm/2013" xmlns:ns7="http://def.wmo.int/metce/2013" xmlns:om="http://www.opengis.net/om/2.0" xmlns:ns9="http://www.isotc211.org/2005/gts" xmlns:sam="http://www.opengis.net/sampling/2.0" xmlns:sams="http://www.opengis.net/samplingSpatial/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exclude-result-prefixes="xsl fo gml xlink wmdr gco gmd ns6 ns7 om ns9 sam sams xsi" >
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/wmdr:WIGOSMetadataRecord"  >
        <station >
            <xsl:for-each select="wmdr:facility/wmdr:ObservingFacility/wmdr:observation/wmdr:ObservingCapability">
                <observations>
                    <gid>
                        <xsl:value-of select="./@gml:id"/>
                    </gid>
                    <variableid>
                        <xsl:value-of select="wmdr:observation/om:OM_Observation/om:observedProperty/@xlink:href"/>
                    </variableid>

                    <xsl:for-each select="wmdr:observation/om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment">
                        <deployments>
                            <gid>
                                <xsl:value-of select="./@gml:id"/>
                            </gid>
                            <from>
                                <xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:beginPosition"/>
                            </from>
                            <to>
                                <xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:endPosition"/>
                            </to>
                            <xsl:for-each select="wmdr:dataGeneration/wmdr:DataGeneration">
                                <datagenerations>
                                    <gid>
                                        <xsl:value-of select="./@gml:id"/>
                                    </gid>
                                    <schedule>
                                        <from>
                                            <xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:beginPosition"/>
                                        </from>
                                        <to>
                                            <xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:endPosition"/>
                                        </to>
                                        <startMonth>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:startMonth"/>
                                        </startMonth>
                                        <endMonth>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:endMonth"/>
                                        </endMonth>
                                        <startWeekday>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:startWeekday"/>
                                        </startWeekday>
                                        <endWeekday>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:endWeekday"/>
                                        </endWeekday>
                                        <startHour>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:startHour"/>
                                        </startHour>
                                        <endHour>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:endHour"/>
                                        </endHour>
                                        <startMinute>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:startMinute"/>
                                        </startMinute>
                                        <endMinute>
                                            <xsl:value-of select="wmdr:schedule/wmdr:Schedule/wmdr:endMinute"/>
                                        </endMinute>
                                        <interval><xsl:value-of select="wmdr:reporting/wmdr:Reporting/wmdr:temporalReportingInterval"/></interval>
                                        <international><xsl:value-of select="wmdr:reporting/wmdr:Reporting/wmdr:internationalExchange"/></international>
                                    </schedule>
                                </datagenerations>
                            </xsl:for-each>
                        </deployments>
                    </xsl:for-each>
                </observations>
            </xsl:for-each>
        </station>
    </xsl:template>
</xsl:stylesheet>
