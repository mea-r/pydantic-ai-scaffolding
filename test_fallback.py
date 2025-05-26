#!/usr/bin/env python3
"""
Simple test script for fallback functionality
"""

import sys
import os
sys.path.append('src')

def test_fallback_chain_building():
    """Test that fallback chain is built correctly"""
    try:
        from helpers.config_helper import ConfigHelper, FallbackModel
        
        # Test config helper
        config_helper = ConfigHelper()
        print("✓ ConfigHelper initialized successfully")
        
        # Test parsing model strings
        provider, model = config_helper.parse_model_string("openai/gpt-4o")
        assert provider == "openai" and model == "gpt-4o"
        print("✓ Model string parsing works")
        
        provider, model = config_helper.parse_model_string("google:gemini-pro")
        assert provider == "google" and model == "gemini-pro"
        print("✓ Alternative format parsing works")
        
        # Test fallback configuration access
        fallback_model = config_helper.get_fallback_model()
        fallback_chain = config_helper.get_fallback_chain()
        print(f"✓ System fallback model: {fallback_model}")
        print(f"✓ System fallback chain: {len(fallback_chain)} models")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_import_structure():
    """Test that imports work correctly"""
    try:
        from helpers.config_helper import ConfigHelper, FallbackModel
        from py_models.base import LLMReport
        print("✓ All imports successful")
        
        # Test LLMReport with new fields
        report = LLMReport(model_name="test/model")
        assert hasattr(report, 'fallback_used')
        assert hasattr(report, 'attempted_models')
        print("✓ LLMReport has fallback fields")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing fallback functionality...")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_import_structure()
    print()
    
    all_passed &= test_fallback_chain_building()
    print()
    
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()