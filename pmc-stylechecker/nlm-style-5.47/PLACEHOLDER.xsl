<?xml version="1.0" encoding="UTF-8"?>
<!--
  PMC Style Checker Placeholder
  
  This is a placeholder file. To install the official NLM Style Checker 5.47:
  
  Run: ./tools/fetch_pmc_style.sh
  
  Or manually download from:
  https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
  
  The official nlm-stylechecker.xsl and supporting files should be placed in this directory.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  
  <xsl:template match="/">
    <html>
      <head>
        <title>NLM Style Checker Not Installed</title>
        <style>
          body { 
            font-family: Arial, sans-serif; 
            padding: 20px; 
            background: #f5f5f5; 
            max-width: 800px;
            margin: 0 auto;
          }
          .message { 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
          }
          h1 { 
            color: #d93025; 
            margin-top: 0;
          }
          code { 
            background: #f0f0f0; 
            padding: 3px 8px; 
            border-radius: 3px; 
            font-family: monospace;
          }
          .command {
            background: #2d2d2d;
            color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: monospace;
          }
          ol {
            line-height: 2;
          }
        </style>
      </head>
      <body>
        <div class="message">
          <h1>⚠️ Official NLM Style Checker 5.47 Not Installed</h1>
          <p>The official PMC Style Checker XSLT bundle (nlm-style-5.47) is not yet installed in this directory.</p>
          
          <h2>Quick Install:</h2>
          <div class="command">./tools/fetch_pmc_style.sh</div>
          
          <h2>Manual Installation:</h2>
          <ol>
            <li>Download the archive:<br/>
                <a href="https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz">
                  https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
                </a>
            </li>
            <li>Extract the tar.gz file</li>
            <li>Copy all <code>.xsl</code> files to <code>pmc-stylechecker/nlm-style-5.47/</code></li>
            <li>Preserve any LICENSE or documentation files</li>
            <li>Run your conversion again</li>
          </ol>
          
          <h2>About NLM Style Checker:</h2>
          <p>
            The NLM Style Checker is an XSLT-based tool from the National Library of Medicine
            that validates JATS XML files for PMC submission compliance.
          </p>
          <ul>
            <li><strong>Version:</strong> 5.47</li>
            <li><strong>Provider:</strong> National Library of Medicine (NLM)</li>
            <li><strong>License:</strong> Public domain (US Government work)</li>
            <li><strong>Documentation:</strong> 
                <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/">PMC Style Checker</a>
            </li>
          </ul>
          
          <p><strong>Note:</strong> The pipeline will continue without the style checker, but installing
             it is highly recommended for PMC submission validation.</p>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
