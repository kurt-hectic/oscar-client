<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:output method="xml" indent="yes"/>
	<xsl:template match="/wmdr:WIGOSMetadataRecord" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:ns6="http://def.wmo.int/opm/2013" xmlns:ns7="http://def.wmo.int/metce/2013" xmlns:om="http://www.opengis.net/om/2.0" xmlns:ns9="http://www.isotc211.org/2005/gts" xmlns:sam="http://www.opengis.net/sampling/2.0" xmlns:sams="http://www.opengis.net/samplingSpatial/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<station>
			<observations>
				<xsl:for-each select="wmdr:facility/wmdr:ObservingFacility/wmdr:observation/wmdr:ObservingCapability/wmdr:observation/om:OM_Observation">
					<observation>
						<gid>
							<xsl:value-of select="./@gml:id"/>
						</gid>
						<variableid>
							<xsl:value-of select="om:observedProperty/@xlink:href"/>
						</variableid>
						<from>
							<xsl:value-of select="om:phenomenonTime/gml:TimePeriod/gml:beginPosition"/>
						</from>
						<to>
							<xsl:value-of select="om:phenomenonTime/gml:TimePeriod/gml:endPosition"/>
						</to>
						<deployments>
							<xsl:for-each select="om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment">
								<deployment>
									<gid>
										<xsl:value-of select="./@gml:id"/>
									</gid>
									<from>
										<xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:beginPosition"/>
									</from>
									<to>
										<xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:endPosition"/>
									</to>
									<datagenerations>
										<xsl:for-each select="wmdr:dataGeneration/wmdr:DataGeneration">
										<datageneration>
											<gid>
												<xsl:value-of select="./@gml:id"/>
											</gid>
											<from>
												<xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:beginPosition"/>
											</from>
											<to>
												<xsl:value-of select="wmdr:validPeriod/gml:TimePeriod/gml:endPosition"/>
											</to>
											<schedule>
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
											</datageneration>
										</xsl:for-each>
									</datagenerations>
								</deployment>
							</xsl:for-each>
						</deployments>
					</observation>
				</xsl:for-each>
			</observations>
		</station>
	</xsl:template>
</xsl:stylesheet>
