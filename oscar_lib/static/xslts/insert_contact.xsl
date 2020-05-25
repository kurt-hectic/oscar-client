<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:wmdr="http://def.wmo.int/wmdr/2017" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gco="http://www.isotc211.org/2005/gco" version="1.0">
	<!-- Identity transform -->
	<xsl:output method="xml"/>
	<xsl:param name="email"/>
	<xsl:variable name="email_id" select="translate($email,'@','_')"/>
	
	<xsl:template match="@* | node()">
		<xsl:copy>
			<xsl:apply-templates select="@* | node()"/>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="/wmdr:WIGOSMetadataRecord/wmdr:facility/wmdr:ObservingFacility/wmdr:responsibleParty[last()]">
		<xsl:copy-of select="."/>
		<wmdr:responsibleParty>
			<wmdr:ResponsibleParty>
				<wmdr:responsibleParty>
					<gmd:CI_ResponsibleParty id="id_{$email_id}">
						<gmd:contactInfo xlink:type="simple">
							<gmd:CI_Contact>
								<gmd:address xlink:type="simple">
									<gmd:CI_Address>
										<gmd:electronicMailAddress>
											<gco:CharacterString><xsl:copy-of select="$email" /></gco:CharacterString>
										</gmd:electronicMailAddress>
									</gmd:CI_Address>
								</gmd:address>
							</gmd:CI_Contact>
						</gmd:contactInfo>
						<gmd:role>
							<gmd:CI_RoleCode codeList="https://standards.iso.org/iso/19115/resources/Codelists/gml/CI_RoleCode.xml/pointOfContact" codeListValue="pointOfContact"/>
						</gmd:role>
					</gmd:CI_ResponsibleParty>
				</wmdr:responsibleParty>
			</wmdr:ResponsibleParty>
		</wmdr:responsibleParty>
	</xsl:template>
</xsl:stylesheet>
