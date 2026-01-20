<?xml version="1.0" encoding="UTF-8"?>
<!-- 
PMC Style Checker XSLT - Simplified Version
This is a simplified version for basic PMC compliance checking.
For full validation, use the official PMC Style Checker at:
https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
-->
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL-Transform"
    xmlns:xlink="http://www.w3.org/1999/xlink">
    
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
    
    <xsl:template match="/">
        <pmc-style-check-results>
            <timestamp><xsl:value-of select="current-dateTime()"/></timestamp>
            <source>Simplified PMC Style Checker</source>
            <note>For full validation, use https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/</note>
            
            <checks>
                <!-- Check for DTD version -->
                <check name="dtd-version">
                    <xsl:choose>
                        <xsl:when test="/article/@dtd-version">
                            <status>pass</status>
                            <message>DTD version present: <xsl:value-of select="/article/@dtd-version"/></message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>warning</status>
                            <message>DTD version attribute missing on article element</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check for article-type -->
                <check name="article-type">
                    <xsl:choose>
                        <xsl:when test="/article/@article-type">
                            <status>pass</status>
                            <message>Article type present: <xsl:value-of select="/article/@article-type"/></message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>warning</status>
                            <message>Article type attribute missing</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check for DOI -->
                <check name="doi">
                    <xsl:choose>
                        <xsl:when test="//article-id[@pub-id-type='doi']">
                            <status>pass</status>
                            <message>DOI present</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>warning</status>
                            <message>DOI missing - highly recommended for PMC submission</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check for title -->
                <check name="article-title">
                    <xsl:choose>
                        <xsl:when test="//article-title">
                            <status>pass</status>
                            <message>Article title present</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>error</status>
                            <message>Article title missing - required</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check for abstract -->
                <check name="abstract">
                    <xsl:choose>
                        <xsl:when test="//abstract">
                            <status>pass</status>
                            <message>Abstract present</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>warning</status>
                            <message>Abstract missing - highly recommended</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check table-wrap positioning -->
                <check name="table-wrap-position">
                    <xsl:choose>
                        <xsl:when test="//table-wrap[not(@position) or (@position != 'float' and @position != 'anchor')]">
                            <status>warning</status>
                            <message>Some table-wrap elements missing proper position attribute (should be 'float' or 'anchor')</message>
                            <count><xsl:value-of select="count(//table-wrap[not(@position) or (@position != 'float' and @position != 'anchor')])"/></count>
                        </xsl:when>
                        <xsl:when test="//table-wrap">
                            <status>pass</status>
                            <message>All table-wrap elements have proper position attributes</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>info</status>
                            <message>No tables in document</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check figure elements -->
                <check name="figures">
                    <xsl:choose>
                        <xsl:when test="//fig">
                            <status>info</status>
                            <message>Document contains <xsl:value-of select="count(//fig)"/> figure(s)</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>info</status>
                            <message>No figures in document</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
                
                <!-- Check references -->
                <check name="references">
                    <xsl:choose>
                        <xsl:when test="//ref">
                            <status>info</status>
                            <message>Document contains <xsl:value-of select="count(//ref)"/> reference(s)</message>
                        </xsl:when>
                        <xsl:otherwise>
                            <status>info</status>
                            <message>No references in document</message>
                        </xsl:otherwise>
                    </xsl:choose>
                </check>
            </checks>
            
            <summary>
                <total-checks><xsl:value-of select="count(checks/check)"/></total-checks>
                <errors><xsl:value-of select="count(checks/check[status='error'])"/></errors>
                <warnings><xsl:value-of select="count(checks/check[status='warning'])"/></warnings>
                <passed><xsl:value-of select="count(checks/check[status='pass'])"/></passed>
            </summary>
        </pmc-style-check-results>
    </xsl:template>
    
</xsl:stylesheet>
