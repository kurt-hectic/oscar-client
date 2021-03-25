<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
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
						<wmdr:observation>
							<wmdr:ObservingCapability gml:id="obsCap_{position()}">
								<wmdr:facility xlink:href="_{../../wigosid/text()}"/>
								<wmdr:programAffiliation xlink:href="http://codes.wmo.int/wmdr/ProgramAffiliation/{affiliation/text()}"/>
								<wmdr:observation>
									<om:OM_Observation gml:id="obs_{position()}">
										<om:type xlink:href="http://codes.wmo.int/wmdr/featureOfInterest/point"/>										
										<om:phenomenonTime>
											<gml:TimePeriod gml:id="pt_tp_{position()}_1">
												<gml:beginPosition>
													<xsl:value-of select="../../established/text()"/>
												</gml:beginPosition>
												<gml:endPosition/>
											</gml:TimePeriod>
										</om:phenomenonTime>
										<om:resultTime/>
										<om:procedure>
											<wmdr:Process gml:id="proc_{position()}_1">
												<wmdr:deployment>
													<wmdr:Deployment gml:id="depl_{position()}_1">
														<wmdr:deployedEquipment xlink:type="simple">
															<wmdr:Equipment>
																<wmdr:observingMethod xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/unknown"/>
															</wmdr:Equipment>
														</wmdr:deployedEquipment>
														<wmdr:dataGeneration>
															<wmdr:DataGeneration gml:id="dg_{position()}_1">
																<wmdr:validPeriod>
																	<gml:TimePeriod gml:id="dg_tp_{position()}_1">
																		<gml:beginPosition>
																			<xsl:value-of select="../../established/text()"/>
																		</gml:beginPosition>
																		<gml:endPosition/>
																	</gml:TimePeriod>
																</wmdr:validPeriod>
																<wmdr:schedule>
																	<wmdr:Schedule>
																		<wmdr:startMonth>
																			<xsl:value-of select="schedule/startMonth/text()"/>
																		</wmdr:startMonth>
																		<wmdr:endMonth>
																			<xsl:value-of select="schedule/endMonth/text()"/>
																		</wmdr:endMonth>
																		<wmdr:startWeekday>
																			<xsl:value-of select="schedule/startWeekday/text()"/>
																		</wmdr:startWeekday>
																		<wmdr:endWeekday>
																			<xsl:value-of select="schedule/endWeekday/text()"/>
																		</wmdr:endWeekday>
																		<wmdr:startHour>
																			<xsl:value-of select="schedule/startHour/text()"/>
																		</wmdr:startHour>
																		<wmdr:endHour>
																			<xsl:value-of select="schedule/endHour/text()"/>
																		</wmdr:endHour>
																		<wmdr:startMinute>
																			<xsl:value-of select="schedule/startMinute/text()"/>
																		</wmdr:startMinute>
																		<wmdr:endMinute>
																			<xsl:value-of select="schedule/endMinute/text()"/>
																		</wmdr:endMinute>
																		<wmdr:diurnalBaseTime>00:00:00Z</wmdr:diurnalBaseTime>
																	</wmdr:Schedule>
																</wmdr:schedule>
																<wmdr:sampling>
																	<wmdr:Sampling>
																		<!--  6-03 sampling strategy  -->
																		<wmdr:samplingStrategy xlink:href="http://codes.wmo.int/common/wmdr/SamplingStrategy/continuous"/>
																	</wmdr:Sampling>
																</wmdr:sampling>
																<wmdr:reporting>
																	<wmdr:Reporting>
																		<wmdr:internationalExchange>
																			<xsl:value-of select="schedule/international/text()"/>
																		</wmdr:internationalExchange>
																		<wmdr:uom xlink:type="simple"/>
																		<wmdr:temporalReportingInterval>PT<xsl:value-of select="schedule/interval/text()"/>S</wmdr:temporalReportingInterval>
																	</wmdr:Reporting>
																</wmdr:reporting>
															</wmdr:DataGeneration>
														</wmdr:dataGeneration>
														<wmdr:validPeriod>
															<gml:TimePeriod gml:id="vp_{position()}_1">
																<gml:beginPosition>
																	<xsl:value-of select="../../established/text()"/>
																</gml:beginPosition>
																<gml:endPosition/>
															</gml:TimePeriod>
														</wmdr:validPeriod>
														<wmdr:applicationArea/>
														<wmdr:sourceOfObservation xlink:href="http://codes.wmo.int/wmdr/SourceOfObservation/{observationsource/text()}"/>
													</wmdr:Deployment>
												</wmdr:deployment>
											</wmdr:Process>
										</om:procedure>
										<om:observedProperty xlink:href="{variable/text()}"/>
										<om:featureOfInterest/>
										<om:result xlink:type="simple">
											<wmdr:ResultSet>
												<wmdr:distributionInfo>
													<gmd:MD_Distribution>
														<gmd:transferOptions xlink:type="simple">
															<gmd:MD_DigitalTransferOptions>
																<gmd:onLine xlink:type="simple">
																	<gmd:CI_OnlineResource>
																		<gmd:linkage/>
																		<gmd:description>
																			<xsl:choose>
																				<xsl:when test="schedule/real-time='true'">
																					<gco:CharacterString>NRT</gco:CharacterString>
																				</xsl:when>
																				<xsl:otherwise>
																					<gco:CharacterString>Archive</gco:CharacterString>
																				</xsl:otherwise>
																			</xsl:choose>
																		</gmd:description>
																	</gmd:CI_OnlineResource>
																</gmd:onLine>
															</gmd:MD_DigitalTransferOptions>
														</gmd:transferOptions>
													</gmd:MD_Distribution>
												</wmdr:distributionInfo>
											</wmdr:ResultSet>
										</om:result>
									</om:OM_Observation>
								</wmdr:observation>
							</wmdr:ObservingCapability>
						</wmdr:observation>
					</xsl:for-each>
				</wmdr:ObservingFacility>
			</wmdr:facility>
		</wmdr:WIGOSMetadataRecord>
	</xsl:template>
</xsl:stylesheet>
