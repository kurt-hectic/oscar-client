<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:import href="add_observation.xsl"/>
	<xsl:param name="prefix"/>
	<xsl:param name="wigos_id"/>
	<xsl:param name="date_from"/>
	<xsl:output method="xml"/>
	<xsl:template match="/observations">
	<root>
		<xsl:for-each select="./observation">
			<xsl:call-template name="add_observation">
				<xsl:with-param name="wigos_id" select="$wigos_id"/>
				<xsl:with-param name="established" select="$date_from"/>
				<xsl:with-param name="prefix" select="$prefix"/>
			</xsl:call-template>
		</xsl:for-each>
	</root>
	</xsl:template>
</xsl:stylesheet>
