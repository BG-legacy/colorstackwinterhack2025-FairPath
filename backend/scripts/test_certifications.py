"""
Test script for certifications feature
Tests that certifications are properly generated and included in both
OutlookService and CareerSwitchService responses
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.openai_enhancement import OpenAIEnhancementService
from services.outlook_service import OutlookService
from services.career_switch_service import CareerSwitchService
from app.config import settings


def test_openai_availability():
    """Test if OpenAI is available"""
    print("=" * 80)
    print("TEST 1: OpenAI Availability Check")
    print("=" * 80)
    
    service = OpenAIEnhancementService()
    is_available = service.is_available()
    
    if is_available:
        print("✅ OpenAI is available and configured")
        print(f"   Model: {settings.OPENAI_MODEL}")
    else:
        print("⚠️  OpenAI is not available")
        print("   Set OPENAI_API_KEY in .env file to enable certifications")
        print("   Certifications will still appear in responses but will be empty")
    
    print()
    return is_available


def test_certifications_direct():
    """Test certifications generation directly from OpenAI service"""
    print("=" * 80)
    print("TEST 2: Direct Certifications Generation")
    print("=" * 80)
    
    service = OpenAIEnhancementService()
    
    if not service.is_available():
        print("⚠️  Skipping - OpenAI not available")
        print()
        return False
    
    # Test with a common career
    test_career = "Software Developer"
    print(f"Testing certifications for: {test_career}")
    print()
    
    try:
        result = service.get_career_certifications(
            career_name=test_career,
            career_data=None
        )
        
        print(f"Available: {result.get('available', False)}")
        print()
        
        if result.get('available'):
            print("✅ Entry-Level Certifications:")
            for cert in result.get('entry_level', []):
                print(f"   ✅ {cert.get('name', 'N/A')}")
                print(f"      Provider: {cert.get('provider', 'N/A')}")
                print(f"      Description: {cert.get('description', 'N/A')}")
                print()
            
            print("🚀 Career-Advancing Certifications:")
            for cert in result.get('career_advancing', []):
                print(f"   🚀 {cert.get('name', 'N/A')}")
                print(f"      Provider: {cert.get('provider', 'N/A')}")
                print(f"      Description: {cert.get('description', 'N/A')}")
                print()
            
            print("⚠️  Optional/Overhyped Certifications:")
            for cert in result.get('optional_overhyped', []):
                print(f"   ⚠️  {cert.get('name', 'N/A')}")
                print(f"      Provider: {cert.get('provider', 'N/A')}")
                print(f"      Description: {cert.get('description', 'N/A')}")
                print()
            
            # Validate structure
            has_entry = len(result.get('entry_level', [])) > 0
            has_advancing = len(result.get('career_advancing', [])) > 0
            has_optional = len(result.get('optional_overhyped', [])) > 0
            
            if has_entry and has_advancing and has_optional:
                print("✅ All certification categories populated")
                return True
            else:
                print(f"⚠️  Missing categories - Entry: {has_entry}, Advancing: {has_advancing}, Optional: {has_optional}")
                return False
        else:
            print("❌ Certifications not available")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_outlook_certifications():
    """Test that certifications are included in outlook analysis"""
    print("=" * 80)
    print("TEST 3: Certifications in Outlook Service")
    print("=" * 80)
    
    service = OutlookService()
    
    # Load processed data to get a career ID
    try:
        processed_data = service.load_processed_data()
        if not processed_data or not processed_data.get("occupations"):
            print("❌ No processed data found. Run process_data.py first.")
            print()
            return False
        
        # Get first occupation
        test_occupation = processed_data["occupations"][0]
        career_id = test_occupation["career_id"]
        career_name = test_occupation["name"]
        
        print(f"Testing outlook analysis for: {career_name}")
        print(f"Career ID: {career_id}")
        print()
        
        result = service.analyze_outlook(career_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            print()
            return False
        
        # Check if certifications are in the result
        if "certifications" not in result:
            print("❌ Certifications not found in outlook result")
            print()
            return False
        
        print("✅ Certifications found in outlook result")
        certifications = result["certifications"]
        
        print(f"   Available: {certifications.get('available', False)}")
        print(f"   Entry-level count: {len(certifications.get('entry_level', []))}")
        print(f"   Career-advancing count: {len(certifications.get('career_advancing', []))}")
        print(f"   Optional/overhyped count: {len(certifications.get('optional_overhyped', []))}")
        
        if certifications.get('available'):
            print("\n   Sample certifications:")
            if certifications.get('entry_level'):
                cert = certifications['entry_level'][0]
                print(f"   ✅ Entry: {cert.get('name', 'N/A')}")
            if certifications.get('career_advancing'):
                cert = certifications['career_advancing'][0]
                print(f"   🚀 Advancing: {cert.get('name', 'N/A')}")
            if certifications.get('optional_overhyped'):
                cert = certifications['optional_overhyped'][0]
                print(f"   ⚠️  Optional: {cert.get('name', 'N/A')}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_career_switch_certifications():
    """Test that certifications are included in career switch analysis"""
    print("=" * 80)
    print("TEST 4: Certifications in Career Switch Service")
    print("=" * 80)
    
    service = CareerSwitchService()
    
    # Load processed data to get career IDs
    try:
        processed_data = service.load_processed_data()
        if not processed_data or not processed_data.get("occupations"):
            print("❌ No processed data found. Run process_data.py first.")
            print()
            return False
        
        if len(processed_data["occupations"]) < 2:
            print("❌ Need at least 2 occupations to test career switch")
            print()
            return False
        
        # Get two occupations
        source_occ = processed_data["occupations"][0]
        target_occ = processed_data["occupations"][1]
        
        source_id = source_occ["career_id"]
        target_id = target_occ["career_id"]
        
        print(f"Testing career switch:")
        print(f"   From: {source_occ['name']} ({source_id})")
        print(f"   To: {target_occ['name']} ({target_id})")
        print()
        
        result = service.analyze_career_switch(source_id, target_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            print()
            return False
        
        # Check if certifications are in the result
        if "certifications" not in result:
            print("❌ Certifications not found in career switch result")
            print()
            return False
        
        print("✅ Certifications found in career switch result")
        certifications = result["certifications"]
        
        print(f"   Available: {certifications.get('available', False)}")
        print(f"   Entry-level count: {len(certifications.get('entry_level', []))}")
        print(f"   Career-advancing count: {len(certifications.get('career_advancing', []))}")
        print(f"   Optional/overhyped count: {len(certifications.get('optional_overhyped', []))}")
        
        # Note: Certifications should be for the TARGET career
        print(f"\n   Note: Certifications are for the TARGET career: {target_occ['name']}")
        
        if certifications.get('available'):
            print("\n   Sample certifications:")
            if certifications.get('entry_level'):
                cert = certifications['entry_level'][0]
                print(f"   ✅ Entry: {cert.get('name', 'N/A')}")
            if certifications.get('career_advancing'):
                cert = certifications['career_advancing'][0]
                print(f"   🚀 Advancing: {cert.get('name', 'N/A')}")
            if certifications.get('optional_overhyped'):
                cert = certifications['optional_overhyped'][0]
                print(f"   ⚠️  Optional: {cert.get('name', 'N/A')}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """Run all certification tests"""
    print("\n" + "=" * 80)
    print("CERTIFICATIONS FEATURE TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        ("OpenAI Availability", test_openai_availability),
        ("Direct Certifications Generation", test_certifications_direct),
        ("Outlook Service Certifications", test_outlook_certifications),
        ("Career Switch Service Certifications", test_career_switch_certifications),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Certifications feature is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review the output above")
        print("\nNote: If OpenAI is not configured, some tests will fail.")
        print("      Set OPENAI_API_KEY in .env file to enable full functionality.")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()










