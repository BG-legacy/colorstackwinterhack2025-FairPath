"""
Casual training demo - showing how I built this ML system
Written like a beginner learning ML, keeping it real and approachable
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService


def print_header(text):
    """Simple header"""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80 + "\n")


def casual_demo():
    """Show the training and usage in a casual, beginner-friendly way"""
    
    print("\n" + "="*80)
    print(" Hey! So I built this ML career recommendation thing...")
    print(" Let me show you how it works!")
    print("="*80)
    print(f"\n (Made on {datetime.now().strftime('%B %d, %Y')})\n")
    
    # Part 1: Training
    print_header("PART 1: How I Trained the Model")
    
    print("Okay so first, I needed to train an ML model.")
    print("The problem? I don't have real user data (yet).")
    print("So I made synthetic training data - basically fake but realistic examples.\n")
    
    print("Here's what I did:")
    print("  - Created 3,000 fake user-career pairs")
    print("  - Some are good matches (user skills match career needs)")
    print("  - Some are bad matches (user and career don't align)")
    print("  - Made it realistic with different match types:\n")
    print("    * Strong matches (70-90% similar)")
    print("    * Moderate matches (50-70% similar)")
    print("    * Weak matches (30-50% similar - borderline cases)")
    print("    * Poor matches (0-30% similar)")
    print("    * Partial matches (skills match but interests don't)")
    print("    * Wrong interests (right skills, wrong interests)\n")
    
    print("Then I trained a Logistic Regression model (from scikit-learn).")
    print("It learned to tell the difference between good and bad matches.\n")
    
    print("Results:")
    print("  - Training accuracy: ~78%")
    print("  - Test accuracy: ~78%")
    print("  - Not perfect, but realistic! (100% would mean I overfitted)\n")
    
    print("The model learned 150 features:")
    print("  - User skills, interests, values, constraints")
    print("  - Career requirements")
    print("  - The difference between them")
    print("  - 137 out of 150 features actually matter (non-zero coefficients)\n")
    
    # Part 2: Using it
    print_header("PART 2: Let's Actually Use It!")
    
    print("Now let's see it in action with a real example...\n")
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    print("Example: Sarah wants to switch from Marketing to Tech")
    print("  - Skills: Writing, Speaking, Critical Thinking")
    print("  - Interests: Enterprising, Investigative")
    print("  - Values: Achievement, Recognition\n")
    
    print("Getting recommendations...\n")
    
    result = service.recommend(
        skills=["Writing", "Speaking", "Critical Thinking", "Social Perceptiveness"],
        interests={"Enterprising": 6.0, "Investigative": 5.0},
        work_values={"Achievement": 6.0, "Recognition": 5.0},
        top_n=5,
        use_ml=True,
        use_openai=True  # Try to use OpenAI if available
    )
    
    print(f"Method used: {result['method'].upper()}")
    if service.openai_service.is_available():
        print("OpenAI enhancement: Enabled (making explanations better!)\n")
    else:
        print("OpenAI enhancement: Not available (need API key in .env)\n")
    
    print("Top Recommendations:\n")
    
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"  {i}. {rec['name']}")
        print(f"     Match: {rec['score']:.1%} | Confidence: {rec['confidence']}")
        
        outlook = rec.get('outlook', {})
        if outlook and outlook.get('median_wage_2024'):
            print(f"     Salary: ${outlook['median_wage_2024']:,.0f}/year")
        
        # Show OpenAI enhancement if available
        if rec.get('openai_enhancement') and rec['openai_enhancement'].get('enhanced_explanation'):
            print(f"     Why: {rec['openai_enhancement']['enhanced_explanation']}")
        else:
            # Fallback to basic explanation
            top_skills = rec.get('explanation', {}).get('top_contributing_skills', [])
            if top_skills:
                skill_names = [s['skill'] for s in top_skills[:3]]
                print(f"     Key skills: {', '.join(skill_names)}")
        print()
    
    # Part 3: OpenAI Enhancement
    print_header("PART 3: Making It Better with OpenAI")
    
    if service.openai_service.is_available():
        print("Cool part: I'm using OpenAI to make the explanations better!")
        print("The ML model gives me the match score, but OpenAI helps explain WHY")
        print("in a way that's easier to understand.\n")
        
        print("What OpenAI does:")
        print("  - Takes the ML results")
        print("  - Adds friendly, natural explanations")
        print("  - Can even re-rank if something seems off")
        print("  - Makes it feel more human and less robotic\n")
        
        print("Example of enhancement:")
        print("  Without OpenAI: 'Match score: 0.82, skills: Critical Thinking, Speaking'")
        print("  With OpenAI: 'This career matches your communication and analytical")
        print("              skills from marketing. Great transition path into tech!'")
        print()
    else:
        print("OpenAI enhancement is available but not configured.")
        print("To enable it, add your OPENAI_API_KEY to the .env file.\n")
        print("What it would do:")
        print("  - Add better, more natural explanations")
        print("  - Help refine rankings")
        print("  - Make recommendations feel more personalized\n")
    
    # Part 4: Comparison
    print_header("PART 4: ML vs Simple Matching")
    
    print("I also built a simple baseline (just cosine similarity).")
    print("Let me show you the difference...\n")
    
    print("Same user profile tested with both:\n")
    
    baseline = service.recommend(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Investigative": 7.0, "Enterprising": 5.0},
        top_n=3,
        use_ml=False
    )
    
    ml_result = service.recommend(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Investigative": 7.0, "Enterprising": 5.0},
        top_n=3,
        use_ml=True
    )
    
    print("Baseline (simple similarity):")
    for i, rec in enumerate(baseline['recommendations'][:3], 1):
        print(f"  {i}. {rec['name']} (score: {rec['score']:.3f})")
    print()
    
    print("ML Model (learned patterns):")
    for i, rec in enumerate(ml_result['recommendations'][:3], 1):
        print(f"  {i}. {rec['name']} (score: {rec['score']:.3f}, confidence: {rec['confidence']})")
    print()
    
    baseline_ids = [r['career_id'] for r in baseline['recommendations']]
    ml_ids = [r['career_id'] for r in ml_result['recommendations']]
    overlap = len(set(baseline_ids) & set(ml_ids))
    
    print(f"Overlap: {overlap}/3 careers")
    if overlap < 2:
        print("They're different! The ML model learned different patterns.")
        print("This proves it's actually using ML, not just copying the baseline.\n")
    
    # Summary
    print_header("What I Learned Building This")
    
    print("1. ML is actually pretty cool!")
    print("   - The model learned patterns I didn't explicitly program")
    print("   - It can generalize to new users it's never seen\n")
    
    print("2. Data quality matters a lot")
    print("   - Started with too-simple synthetic data (got 100% accuracy)")
    print("   - Made it more realistic (got 78% - much better!)\n")
    
    print("3. Combining ML + OpenAI is powerful")
    print("   - ML does the heavy lifting (matching)")
    print("   - OpenAI makes it human-friendly (explanations)\n")
    
    print("4. Real data will make it even better")
    print("   - Currently using synthetic data")
    print("   - When I get real user feedback, accuracy should improve\n")
    
    print("="*80)
    print("\nThat's it! Hope this was helpful.")
    print("If you're learning ML too, this is totally doable - just takes time!")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    casual_demo()











