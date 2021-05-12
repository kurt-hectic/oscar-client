<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:ns6="http://def.wmo.int/opm/2013" xmlns:ns7="http://def.wmo.int/metce/2013" xmlns:om="http://www.opengis.net/om/2.0" xmlns:ns9="http://www.isotc211.org/2005/gts" xmlns:sam="http://www.opengis.net/sampling/2.0" xmlns:sams="http://www.opengis.net/samplingSpatial/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exclude-result-prefixes="xsl fo gml xlink wmdr gco gmd ns6 ns7 om ns9 sam sams xsi">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template name="add_observation">
		<xsl:param name="wigos_id"/>
		<xsl:param name="established"/>
		<xsl:param name="prefix"/>
		<wmdr:observation>
			<wmdr:ObservingCapability gml:id="{$prefix}_obsCap_{position()}">
				<wmdr:facility xlink:href="_{$wigos_id}"/>
				<wmdr:programAffiliation xlink:href="http://codes.wmo.int/wmdr/ProgramAffiliation/{affiliation/text()}"/>
				<wmdr:observation>
					<om:OM_Observation gml:id="{$prefix}_obs_{position()}">
						<om:type xlink:href="http://codes.wmo.int/wmdr/featureOfInterest/point"/>
						<om:phenomenonTime>
							<gml:TimePeriod gml:id="{$prefix}_pt_{position()}_1">
								<gml:beginPosition>
									<xsl:value-of select="$established"/>
								</gml:beginPosition>
								<gml:endPosition/>
							</gml:TimePeriod>
						</om:phenomenonTime>
						<om:resultTime/>
						<om:procedure>
							<wmdr:Process gml:id="{$prefix}_proc_{position()}_1">
								<wmdr:deployment>
									<wmdr:Deployment gml:id="{$prefix}_depl_{position()}_1">
										<wmdr:deployedEquipment xlink:type="simple">
											<wmdr:Equipment>
												<xsl:if test="instrumentcoordinates">
													<wmdr:geospatialLocation>
														<wmdr:GeospatialLocation>
															<wmdr:geoLocation xlink:type="simple">
																<gml:Point>
																	<gml:pos>
																		<xsl:value-of select="instrumentcoordinates/latitude/text()"/>
																		<xsl:text> </xsl:text>
																		<xsl:value-of select="instrumentcoordinates/longitude/text()"/>
																		<xsl:text> </xsl:text>
																		<xsl:value-of select="instrumentcoordinates/elevation/text()"/>
																	</gml:pos>
																</gml:Point>
															</wmdr:geoLocation>
															<wmdr:geopositioningMethod xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/GeopositioningMethod/gps"/>
															<wmdr:validPeriod xlink:type="simple">
																<gml:TimePeriod gml:id="{$prefix}_proc_instcord_{position()}_1">
																	<gml:beginPosition><xsl:value-of select="$established"/></gml:beginPosition>
																	<gml:endPosition/>
																</gml:TimePeriod>
															</wmdr:validPeriod>
														</wmdr:GeospatialLocation>
													</wmdr:geospatialLocation>
												</xsl:if>
												<wmdr:observingMethod xlink:type="simple" xlink:href="http://codes.wmo.int/wmdr/unknown"/>
											</wmdr:Equipment>
										</wmdr:deployedEquipment>
										<wmdr:dataGeneration>
											<wmdr:DataGeneration gml:id="{$prefix}_dg_{position()}_1">
												<wmdr:validPeriod>
													<gml:TimePeriod gml:id="{$prefix}_dg_tp_{position()}_1">
														<gml:beginPosition>
															<xsl:value-of select="$established"/>
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
											<gml:TimePeriod gml:id="{$prefix}_vp_{position()}_1">
												<gml:beginPosition>
													<xsl:value-of select="$established"/>
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
	</xsl:template>
</xsl:stylesheet>
