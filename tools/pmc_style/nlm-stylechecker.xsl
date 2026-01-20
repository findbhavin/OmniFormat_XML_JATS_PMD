<?xml version="1.0" encoding="UTF-8"?>
<!--
  PMC Style Checker XSLT Placeholder
  
  To use the PMC Style Checker:
  
  1. Download the official nlm-stylechecker from:
     https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
     
  2. Extract the nlm-stylechecker.xsl file
  
  3. Place it in this directory: tools/pmc_style/
  
  4. The conversion pipeline will automatically use it
  
  Note: The style checker requires xsltproc to be installed.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  
  <xsl:template match="/">
    <html>
      <head>
        <title>PMC Style Checker Not Available</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
          .message { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
          h1 { color: #d93025; }
          code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        </style>
      </head>
      <body>
        <div class="message">
          <h1>⚠️ PMC Style Checker Not Available</h1>
          <p>The PMC Style Checker XSLT is not properly installed.</p>
          <h2>To install:</h2>
          <ol>
            <li>Visit <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/">PMC Style Checker</a></li>
            <li>Download the nlm-stylechecker XSLT files</li>
            <li>Place <code>nlm-stylechecker.xsl</code> in <code>tools/pmc_style/</code></li>
            <li>Run your conversion again</li>
          </ol>
          <p><strong>Note:</strong> The style checker requires <code>xsltproc</code> to be installed.</p>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
