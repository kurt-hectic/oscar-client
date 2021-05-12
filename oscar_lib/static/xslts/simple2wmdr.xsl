<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:import href="add_observation.xsl"></xsl:import>
	<xsl:output method="xml"/>
	<xsl:template match="/">
		<wmdr:WIGOSMetadataRecord xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:om="http://www.opengis.net/om/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:sam="http://www.opengis.net/sampling/2.0" xmlns:sams="http://www.opengis.net/samplingSpatial/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" gml:id="id1" xsi:schemaLocation="http://def.wmo.int/wmdr/2017 http://schemas.wmo.int/wmdr/1.0RC9/wmdr.xsd">
			<wmdr:headerInformation owns="false">
				<wmdr:Header/>
			</wmdr:headerInformation>
			<wmdr:facility>
				<wmdr:ObservingFacility gml:id="_{station/wigosid/text()}">
					<gml:identifier codeSpace="http://wigos.wmo.int">
						<xsl:value-of select="station/wigosid/text()"/>
					</gml:identifier>
					<gml:name>
						<xsl:value-of select="station/name/text()"/>
					</gml:name>
					<wmdr:responsibleParty>
						<wmdr:ResponsibleParty>
							<wmdr:responsibleParty>
								<gmd:CI_ResponsibleParty id="first_responsible_party">
									<xsl:if test="station/organization/text()">
										<gmd:organisationName>
											<gco:CharacterString><xsl:value-of select="station/organization/text()"/></gco:CharacterString>
										</gmd:organisationName>
									</xsl:if>
									<gmd:role>
										<gmd:CI_RoleCode codeList="https://standards.iso.org/iso/19115/resources/Codelists/gml/CI_RoleCode.xml/owner" codeListValue="owner"/>
									</gmd:role>
								</gmd:CI_ResponsibleParty>
							</wmdr:responsibleParty>
							<wmdr:validPeriod>
								<gml:TimePeriod gml:id="tp_party_1">
									<gml:beginPosition>
										<xsl:value-of select="station/established/text()"/>
									</gml:beginPosition>
									<gml:endPosition/>
								</gml:TimePeriod>
							</wmdr:validPeriod>
						</wmdr:ResponsibleParty>
					</wmdr:responsibleParty>
					<wmdr:geospatialLocation>
						<wmdr:GeospatialLocation>
							<wmdr:geoLocation>
								<gml:Point gml:id="p1">
									<gml:pos>
										<xsl:value-of select="station/latitude/text()"/>
										<xsl:text> </xsl:text>
										<xsl:value-of select="station/longitude/text()"/>
										<xsl:text> </xsl:text>
										<xsl:value-of select="station/elevation/text()"/>
									</gml:pos>
								</gml:Point>
							</wmdr:geoLocation>
							<wmdr:validPeriod>
								<gml:TimePeriod gml:id="tp_geop_1">
									<gml:beginPosition>
										<xsl:value-of select="station/established/text()"/>
									</gml:beginPosition>
									<gml:endPosition/>
								</gml:TimePeriod>
							</wmdr:validPeriod>
						</wmdr:GeospatialLocation>
					</wmdr:geospatialLocation>
					
					<xsl:for-each select="station/urls/url">
						<wmdr:onlineResource>
							<gmd:CI_OnlineResource>
								<gmd:linkage>
									<gmd:URL>
										<xsl:value-of select="./text()"/>
									</gmd:URL>
								</gmd:linkage>
							</gmd:CI_OnlineResource>
						</wmdr:onlineResource>
					</xsl:for-each>
					<xsl:if test="station/description/text()">
						<wmdr:description>
							<wmdr:Description>
								<wmdr:description>
									<xsl:value-of select="station/description/text()"/>
								</wmdr:description>
								<wmdr:validPeriod xlink:type="simple">
									<gml:TimePeriod gml:id="desc_1">
										<gml:beginPosition>
											<xsl:value-of select="station/established/text()"/>
										</gml:beginPosition>
										<gml:endPosition/>
									</gml:TimePeriod>
								</wmdr:validPeriod>
							</wmdr:Description>
						</wmdr:description>
					</xsl:if>
					<wmdr:facilityType xlink:href="http://codes.wmo.int/wmdr/FacilityType/{station/stationtype/text()}"/>
					<wmdr:dateEstablished>
						<xsl:value-of select="station/established/text()"/>
					</wmdr:dateEstablished>
					<wmdr:wmoRegion xlink:href="http://codes.wmo.int/wmdr/WMORegion/{station/region/text()}"/>
					<wmdr:territory>
						<wmdr:Territory>
							<wmdr:territoryName xlink:href="http://codes.wmo.int/wmdr/TerritoryName/{station/country/text()}"/>
							<wmdr:validPeriod>
								<gml:TimePeriod gml:id="tp_territory_1">
									<gml:beginPosition>
										<xsl:value-of select="station/established/text()"/>
									</gml:beginPosition>
									<gml:endPosition/>
								</gml:TimePeriod>
							</wmdr:validPeriod>
						</wmdr:Territory>
					</wmdr:territory>
					<xsl:for-each select="station/affiliations/affiliation">
						<wmdr:programAffiliation>
							<wmdr:ProgramAffiliation>
								<wmdr:programAffiliation xlink:href="http://codes.wmo.int/wmdr/ProgramAffiliation/{./text()}"/>
								<wmdr:reportingStatus>
									<wmdr:ReportingStatus>
										<wmdr:reportingStatus xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/{/station/status/text()}"/>
										<wmdr:validPeriod xlink:type="simple">
											<gml:TimePeriod gml:id="affiliation_{position()}_status">
												<gml:beginPosition>
													<xsl:value-of select="/station/established/text()"/>
												</gml:beginPosition>
												<gml:endPosition/>
											</gml:TimePeriod>
										</wmdr:validPeriod>
									</wmdr:ReportingStatus>
								</wmdr:reportingStatus>
							</wmdr:ProgramAffiliation>
						</wmdr:programAffiliation>
					</xsl:for-each>
					<xsl:for-each select="station/observations/observation">
						<xsl:call-template name="add_observation"  >
							<xsl:with-param name="wigos_id" select="../../wigosid/text()"></xsl:with-param>
							<xsl:with-param name="established" select="../../established/text()"></xsl:with-param>
							<xsl:with-param name="prefix" select="'create'"></xsl:with-param>
						</xsl:call-template>
					</xsl:for-each>
				</wmdr:ObservingFacility>
			</wmdr:facility>
		</wmdr:WIGOSMetadataRecord>
	</xsl:template>
</xsl:stylesheet>
