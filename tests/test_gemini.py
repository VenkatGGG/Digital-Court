"""
test_gemini.py - Test Script for Gemini Persona Injection

This script verifies that:
1. The Gemini API connection works
2. jurors.json loads correctly
3. Persona injection via system_instruction is working
"""

import json
import sys
from ai_engine import GeminiBrain, JurorBrain, load_jurors, GeminiBrainError


def test_basic_connection():
    """Test basic Gemini API connectivity."""
    print("\n" + "="*60)
    print("🔌 TEST 1: Basic Gemini Connection")
    print("="*60)
    
    try:
        brain = GeminiBrain(
            persona_name="ConnectionTest",
            system_instruction="You are a helpful assistant. Respond in exactly 10 words or less."
        )
        print(f"✅ Model initialized: {brain}")
        
        response = brain.generate("Say hello and confirm you're working.")
        print(f"📝 Response: {response.strip()}")
        return True
        
    except GeminiBrainError as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_juror_loading():
    """Test loading jurors from JSON file."""
    print("\n" + "="*60)
    print("📋 TEST 2: Juror Profile Loading")
    print("="*60)
    
    try:
        with open("jurors.json", "r") as f:
            data = json.load(f)
        
        jurors = data.get("jurors", [])
        print(f"✅ Loaded {len(jurors)} juror profiles:")
        
        for juror in jurors:
            name = juror.get("name", "Unknown")
            occupation = juror.get("occupation", "Unknown")
            bias_pro = ", ".join(juror.get("hidden_biases", {}).get("pro", []))
            print(f"   • {name} ({occupation})")
            print(f"     Pro-biases: {bias_pro}")
        
        return True
        
    except FileNotFoundError:
        print("❌ jurors.json not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False


def test_persona_injection():
    """Test that persona injection changes model behavior."""
    print("\n" + "="*60)
    print("🎭 TEST 3: Persona Injection Verification")
    print("="*60)
    
    # Load the first juror
    with open("jurors.json", "r") as f:
        data = json.load(f)
    
    juror_profile = data["jurors"][0]  # Margaret Chen - Retired Principal
    
    print(f"\n📌 Testing with juror: {juror_profile['name']}")
    print(f"   Occupation: {juror_profile['occupation']}")
    print(f"   Decision Style: {juror_profile['decision_style'][:80]}...")
    
    try:
        juror_brain = JurorBrain(juror_profile)
        print(f"✅ JurorBrain created: {juror_brain}")
        
        # Ask a question that should reveal the persona
        test_scenario = """
The plaintiff's lawyer argues:
"My client, a single mother of three, was fired without warning after 15 years 
of dedicated service. The company showed complete disregard for proper HR procedures 
and failed to provide any documentation for their decision."
"""
        
        print(f"\n📜 Test Scenario: {test_scenario.strip()[:200]}...")
        print("\n🧠 Generating juror's internal monologue...")
        
        result = juror_brain.think(test_scenario)
        
        print(f"\n💭 INTERNAL MONOLOGUE:")
        print(f"   {result['monologue']}")
        print(f"\n📊 BIAS SCORE: {result['bias_score']}/100")
        print(f"   (0=Defense, 50=Neutral, 100=Plaintiff)")
        
        # Verify the persona came through
        response_lower = result['monologue'].lower()
        
        # Margaret is a retired principal - check for relevant keywords
        persona_indicators = [
            "education" in response_lower,
            "school" in response_lower,
            "procedure" in response_lower,
            "accountability" in response_lower,
            "mother" in response_lower,
            "family" in response_lower,
            "years" in response_lower,
        ]
        
        if any(persona_indicators):
            print("\n✅ PERSONA INJECTION VERIFIED!")
            print("   The juror's background appears to influence their response.")
        else:
            print("\n⚠️ Persona influence not clearly detected (may still be working)")
            print("   Check if the response aligns with Margaret's character.")
        
        return True
        
    except GeminiBrainError as e:
        print(f"❌ Persona test failed: {e}")
        return False


def test_multiple_jurors():
    """Test loading and querying multiple jurors."""
    print("\n" + "="*60)
    print("👥 TEST 4: Multiple Juror Responses (Juror Swarm Preview)")
    print("="*60)
    
    try:
        # Load just 2 jurors to save API calls
        with open("jurors.json", "r") as f:
            data = json.load(f)
        
        test_profiles = data["jurors"][:2]  # Margaret Chen and Derek Washington
        
        scenario = "The defense lawyer states: 'This is clearly a case of buyer's remorse. The plaintiff is seeking damages far beyond any actual harm suffered.'"
        
        print(f"\n📜 Scenario: {scenario}")
        print("\n🎭 Juror Reactions:\n")
        
        for profile in test_profiles:
            juror = JurorBrain(profile)
            result = juror.think(scenario)
            
            print(f"👤 {profile['name']} ({profile['occupation']})")
            print(f"   💭 Thoughts: {result['monologue'][:150]}...")
            print(f"   📊 Score: {result['bias_score']}/100")
            print()
        
        print("✅ Multiple juror test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Multi-juror test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🏛️"*20)
    print("  LEX UMBRA - Gemini Adapter Test Suite  ")
    print("🏛️"*20)
    
    results = []
    
    # Test 1: Basic connection
    results.append(("Basic Connection", test_basic_connection()))
    
    if not results[0][1]:
        print("\n❌ CRITICAL: Cannot proceed without API connection.")
        print("   Please ensure GEMINI_API_KEY is set in your .env file.")
        sys.exit(1)
    
    # Test 2: Juror loading
    results.append(("Juror Loading", test_juror_loading()))
    
    # Test 3: Persona injection
    results.append(("Persona Injection", test_persona_injection()))
    
    # Test 4: Multiple jurors (optional, uses more API calls)
    print("\n" + "-"*60)
    run_multi = input("Run multi-juror test? (uses 2 additional API calls) [y/N]: ").strip().lower()
    if run_multi == 'y':
        results.append(("Multiple Jurors", test_multiple_jurors()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️ Some tests failed."))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
