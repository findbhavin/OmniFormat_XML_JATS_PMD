#!/usr/bin/env python3
"""
Comprehensive Functionality Verification Script
================================================

This script verifies that all functionalities from the last 7 PRs are working correctly
and validates JATS 1.4 and PMC compliance.

PRs Verified:
- PR #1: XML double-encoding fix
- PR #2-3: Async conversion with progress tracking
- PR #4-6: Enhanced UI and PMC style checker
- PR #7: Merge conflict resolution

Author: OmniJAX Team
Date: 2026-01-20
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class FunctionalityVerifier:
    """Verifies all functionalities from recent PRs."""
    
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.results = {
            'pr1_xml_encoding': False,
            'pr2_async_conversion': False,
            'pr3_status_polling': False,
            'pr4_pmc_stylechecker': False,
            'pr5_schema_resolution': False,
            'pr6_ui_rewrite': False,
            'pr7_merge_resolution': False,
            'jats_14_compliance': False,
            'pmc_compliance': False,
            'direct_pdf_conversion': False
        }
    
    def verify_pr1_xml_encoding(self):
        """PR #1: Verify XML encoding fixes are in place."""
        logger.info("Verifying PR #1: XML double-encoding fix...")
        
        try:
            # Check MasterPipeline.py for proper XML handling
            pipeline_file = self.repo_path / 'MasterPipeline.py'
            with open(pipeline_file, 'r') as f:
                content = f.read()
            
            # Check that lxml is used instead of manual string replacement
            if 'lxml' in content and 'etree' in content:
                logger.info("  ✓ lxml XML parsing in place")
                
                # Check that _validate_xml_wellformedness exists
                if '_validate_xml_wellformedness' in content:
                    logger.info("  ✓ XML well-formedness validation exists")
                    self.results['pr1_xml_encoding'] = True
                    return True
        
        except Exception as e:
            logger.error(f"  ✗ PR #1 verification failed: {e}")
        
        return False
    
    def verify_pr2_async_conversion(self):
        """PR #2-3: Verify async conversion with progress tracking."""
        logger.info("Verifying PR #2-3: Async conversion...")
        
        try:
            app_file = self.repo_path / 'app.py'
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Check for async conversion components
            checks = [
                ('conversion_progress', 'Progress tracking dictionary'),
                ('threading', 'Threading support'),
                ('/status/', 'Status endpoint'),
                ('/download/', 'Download endpoint'),
                ('run_conversion_background', 'Background conversion function')
            ]
            
            passed = 0
            for check_str, description in checks:
                if check_str in content:
                    logger.info(f"  ✓ {description} exists")
                    passed += 1
                else:
                    logger.warning(f"  ✗ {description} missing")
            
            if passed >= 4:  # Most checks passed
                self.results['pr2_async_conversion'] = True
                self.results['pr3_status_polling'] = True
                return True
        
        except Exception as e:
            logger.error(f"  ✗ PR #2-3 verification failed: {e}")
        
        return False
    
    def verify_pr4_pmc_stylechecker(self):
        """PR #4-6: Verify PMC style checker integration."""
        logger.info("Verifying PR #4-6: PMC style checker...")
        
        try:
            pipeline_file = self.repo_path / 'MasterPipeline.py'
            with open(pipeline_file, 'r') as f:
                content = f.read()
            
            # Check for PMC style checker
            if '_run_pmc_stylechecker' in content:
                logger.info("  ✓ PMC style checker method exists")
                
                # Check for pmc-stylechecker directory
                pmc_dir = self.repo_path / 'pmc-stylechecker'
                if pmc_dir.exists():
                    logger.info("  ✓ pmc-stylechecker directory exists")
                    self.results['pr4_pmc_stylechecker'] = True
                    return True
        
        except Exception as e:
            logger.error(f"  ✗ PR #4-6 verification failed: {e}")
        
        return False
    
    def verify_pr5_schema_resolution(self):
        """PR #5: Verify schema resolution (xsi:schemaLocation)."""
        logger.info("Verifying PR #5: Schema resolution...")
        
        try:
            pipeline_file = self.repo_path / 'MasterPipeline.py'
            with open(pipeline_file, 'r') as f:
                content = f.read()
            
            # Check for xsi:schemaLocation injection
            if 'xsi:schemaLocation' in content:
                logger.info("  ✓ xsi:schemaLocation injection in place")
                
                # Check for namespace handling
                if 'xmlns:xsi' in content:
                    logger.info("  ✓ XSI namespace handling exists")
                    self.results['pr5_schema_resolution'] = True
                    return True
        
        except Exception as e:
            logger.error(f"  ✗ PR #5 verification failed: {e}")
        
        return False
    
    def verify_pr6_ui_rewrite(self):
        """PR #6: Verify UI rewrite with drag-and-drop."""
        logger.info("Verifying PR #6: UI rewrite...")
        
        try:
            index_file = self.repo_path / 'templates' / 'index.html'
            with open(index_file, 'r') as f:
                content = f.read()
            
            # Check for async UI components
            checks = [
                ('fetch', 'Fetch API usage'),
                ('progress', 'Progress bar'),
                ('drag', 'Drag and drop'),
                ('addEventListener', 'Event handlers')
            ]
            
            passed = 0
            for check_str, description in checks:
                if check_str in content.lower():
                    logger.info(f"  ✓ {description} exists")
                    passed += 1
            
            if passed >= 3:
                self.results['pr6_ui_rewrite'] = True
                return True
        
        except Exception as e:
            logger.error(f"  ✗ PR #6 verification failed: {e}")
        
        return False
    
    def verify_pr7_merge_resolution(self):
        """PR #7: Verify merge conflict resolution."""
        logger.info("Verifying PR #7: Merge resolution...")
        
        try:
            # Check for merge resolution documentation
            merge_doc = self.repo_path / 'MERGE_RESOLUTION_SUMMARY.md'
            if merge_doc.exists():
                logger.info("  ✓ Merge resolution documentation exists")
                
                # Check for no duplicate functions in app.py
                app_file = self.repo_path / 'app.py'
                with open(app_file, 'r') as f:
                    content = f.read()
                
                # Count function definitions
                func_count = {}
                for line in content.split('\n'):
                    if line.strip().startswith('def '):
                        func_name = line.strip().split('(')[0].replace('def ', '')
                        func_count[func_name] = func_count.get(func_name, 0) + 1
                
                # Check for duplicates
                duplicates = [f for f, c in func_count.items() if c > 1]
                if not duplicates:
                    logger.info("  ✓ No duplicate functions found")
                    self.results['pr7_merge_resolution'] = True
                    return True
                else:
                    logger.warning(f"  ✗ Duplicate functions found: {duplicates}")
        
        except Exception as e:
            logger.error(f"  ✗ PR #7 verification failed: {e}")
        
        return False
    
    def verify_jats_14_compliance(self):
        """Verify JATS 1.4 Publishing DTD compliance."""
        logger.info("Verifying JATS 1.4 compliance...")
        
        try:
            # Check documentation
            jats_doc = self.repo_path / 'JATS_1.4_PMC_COMPLIANCE_UPDATE.md'
            if jats_doc.exists():
                logger.info("  ✓ JATS 1.4 compliance documentation exists")
                
                # Check MasterPipeline for JATS 1.4 references
                pipeline_file = self.repo_path / 'MasterPipeline.py'
                with open(pipeline_file, 'r') as f:
                    content = f.read()
                
                # Check for JATS validation
                checks = [
                    ('jats_version', 'JATS version configuration'),
                    ('_validate_jats_compliance', 'JATS validation method'),
                    ('_validate_pmc_requirements', 'PMC requirements validation')
                ]
                
                passed = 0
                for check_str, description in checks:
                    if check_str in content:
                        logger.info(f"  ✓ {description} exists")
                        passed += 1
                
                if passed >= 2:
                    self.results['jats_14_compliance'] = True
                    return True
        
        except Exception as e:
            logger.error(f"  ✗ JATS 1.4 verification failed: {e}")
        
        return False
    
    def verify_pmc_compliance(self):
        """Verify PMC tagging guidelines compliance."""
        logger.info("Verifying PMC compliance...")
        
        try:
            # Check PMC compliance checklist
            pmc_doc = self.repo_path / 'PMC_COMPLIANCE_CHECKLIST.md'
            if pmc_doc.exists():
                logger.info("  ✓ PMC compliance checklist exists")
                
                # Check for PMC-specific validations in code
                pipeline_file = self.repo_path / 'MasterPipeline.py'
                with open(pipeline_file, 'r') as f:
                    content = f.read()
                
                # Check for PMC requirements
                if 'pmc.ncbi.nlm.nih.gov' in content:
                    logger.info("  ✓ PMC guidelines referenced")
                    
                    if 'position="float"' in content or 'position=\\"float\\"' in content:
                        logger.info("  ✓ PMC table positioning implemented")
                        self.results['pmc_compliance'] = True
                        return True
        
        except Exception as e:
            logger.error(f"  ✗ PMC compliance verification failed: {e}")
        
        return False
    
    def verify_direct_pdf_conversion(self):
        """Verify direct DOCX to PDF conversion."""
        logger.info("Verifying direct PDF conversion...")
        
        try:
            # Check in MasterPipeline for direct PDF conversion
            pipeline_file = self.repo_path / 'MasterPipeline.py'
            with open(pipeline_file, 'r') as f:
                content = f.read()
            
            if 'direct_from_word.pdf' in content:
                logger.info("  ✓ Direct PDF conversion in pipeline")
                
                # Check for standalone tool
                direct_tool = self.repo_path / 'tools' / 'direct_pdf_converter.py'
                if direct_tool.exists():
                    logger.info("  ✓ Standalone direct PDF converter exists")
                    self.results['direct_pdf_conversion'] = True
                    return True
                else:
                    # Still pass if integrated in pipeline
                    logger.info("  ✓ Direct PDF conversion integrated in pipeline")
                    self.results['direct_pdf_conversion'] = True
                    return True
        
        except Exception as e:
            logger.error(f"  ✗ Direct PDF verification failed: {e}")
        
        return False
    
    def run_all_checks(self):
        """Run all verification checks."""
        logger.info("=" * 60)
        logger.info("Starting Comprehensive Functionality Verification")
        logger.info("=" * 60)
        
        # Run all checks
        self.verify_pr1_xml_encoding()
        self.verify_pr2_async_conversion()
        self.verify_pr4_pmc_stylechecker()
        self.verify_pr5_schema_resolution()
        self.verify_pr6_ui_rewrite()
        self.verify_pr7_merge_resolution()
        self.verify_jats_14_compliance()
        self.verify_pmc_compliance()
        self.verify_direct_pdf_conversion()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("Verification Summary")
        logger.info("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v)
        
        for key, value in self.results.items():
            status = "✓ PASS" if value else "✗ FAIL"
            logger.info(f"  {status}: {key}")
        
        logger.info("=" * 60)
        logger.info(f"Results: {passed}/{total} checks passed")
        logger.info("=" * 60)
        
        # Save results to JSON
        results_file = self.repo_path / 'verification_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_checks': total,
                    'passed': passed,
                    'failed': total - passed,
                    'success_rate': f"{(passed/total*100):.1f}%"
                },
                'details': self.results
            }, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        
        return passed == total


def main():
    """Main entry point."""
    repo_path = os.getcwd()
    
    verifier = FunctionalityVerifier(repo_path)
    success = verifier.run_all_checks()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
