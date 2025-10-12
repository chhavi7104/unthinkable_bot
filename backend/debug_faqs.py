import json
import os

def debug_faqs():
    print("=== Debugging FAQs ===")
    
    # Check if file exists
    faq_path = os.path.join('data', 'faqs.json')
    print(f"FAQ file exists: {os.path.exists(faq_path)}")
    
    if os.path.exists(faq_path):
        try:
            with open(faq_path, 'r') as f:
                faqs = json.load(f)
            print(f"Number of FAQs: {len(faqs)}")
            for i, faq in enumerate(faqs):
                print(f"{i+1}. Q: {faq['question']}")
                print(f"   A: {faq['answer'][:50]}...")
        except Exception as e:
            print(f"Error loading FAQs: {e}")
    else:
        print("Creating sample FAQs file...")
        sample_faqs = [
            {
                "question": "How do I cancel my subscription?",
                "answer": "You can cancel your subscription from the 'Billing' section in your account settings. Cancellations take effect at the end of your billing cycle."
            },
            {
                "question": "What are your business hours?",
                "answer": "Our customer support is available Monday to Friday, 9 AM to 6 PM EST."
            }
        ]
        os.makedirs('data', exist_ok=True)
        with open(faq_path, 'w') as f:
            json.dump(sample_faqs, f, indent=2)
        print("Sample FAQs created!")

if __name__ == "__main__":
    debug_faqs()