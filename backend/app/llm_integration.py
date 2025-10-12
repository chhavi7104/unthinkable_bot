import json
import google.generativeai as genai
from typing import List, Dict, Any
import os

class LLMIntegration:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCvyBCmAxFbwgatMnkymEBs-DsCMRW7KEk")
        self.faqs = self.load_faqs()
    
        print(f"API Key: {'SET' if self.api_key else 'MISSING'}")
    
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
            
            # Try different model names
                model_names = [
                    "gemini-1.5-flash",  # Most likely to work
                    "gemini-1.0-pro",
                    "gemini-pro",
                ]
            
                self.model = None
                for model_name in model_names:
                    try:
                        print(f"Trying model: {model_name}")
                        self.model = genai.GenerativeModel(model_name)
                    # Test the model with a simple call
                        test_response = self.model.generate_content("Say hello")
                        print(f"✅ Model '{model_name}' works!")
                        self.model_name = model_name
                        break
                    except Exception as e:
                        print(f"❌ Model '{model_name}' failed: {e}")
                        continue
            
                if not self.model:
                    print("⚠️  No Gemini models worked, using fallback mode")
                  
            except Exception as e:
                print(f"❌ Gemini configuration failed: {e}")
                self.model = None
        else:
            self.model = None
            print("❌ No API key available")
    
    def load_faqs(self) -> List[Dict]:
        try:
            with open('data/faqs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  No FAQs file found")
            return []
    
    def find_faq_match(self, query: str) -> str:
        """Find best FAQ match using simple keyword matching"""
        query_lower = query.lower().strip()
        print(f"🔍 FAQ Search: '{query_lower}'")
    
    # Debug: print all FAQs
        print(f"Available FAQs: {len(self.faqs)}")
        for faq in self.faqs:
            print(f"  - {faq['question']}")
    
    # Simple keyword matching with common variations
        keyword_mapping = {
            'cancel': ['cancel', 'stop', 'end', 'terminate', 'unsubscribe'],
            'subscription': ['subscription', 'membership', 'plan', 'billing'],
            'password': ['password', 'login', 'forgot'],
            'refund': ['refund', 'money back', 'return'],
            'hours': ['hours', 'time', 'schedule', 'when', 'open'],
            'trial': ['trial', 'free'],
            'contact': ['contact', 'call', 'email', 'phone', 'support']
    }
    
    # Check each FAQ
        for faq in self.faqs:
            faq_lower = faq['question'].lower()
        
        # Count matching keywords
            match_score = 0
        
            for category, keywords in keyword_mapping.items():
            # Check if query has keywords from this category
                query_has_keywords = any(keyword in query_lower for keyword in keywords)
            # Check if FAQ question has keywords from this category  
                faq_has_keywords = any(keyword in faq_lower for keyword in keywords)
            
                if query_has_keywords and faq_has_keywords:
                    match_score += 2
                elif query_has_keywords or faq_has_keywords:
                    match_score += 1
        
        # Direct word overlap
            query_words = set(query_lower.split())
            faq_words = set(faq_lower.split())
            common_words = query_words.intersection(faq_words)
            match_score += len(common_words)
        
            print(f"  '{faq_lower}' -> score: {match_score}")
        
            if match_score >= 2:  # Lower threshold for matching
                print(f"✅ FAQ MATCHED: '{faq['question']}'")
                return faq['answer']
    
        print("❌ No FAQ match found")
        return "ESCALATE"
    
    def call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API with better error handling"""
        if not self.model:
            return self.get_fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self.get_fallback_response(prompt)
    
    def get_fallback_response(self, prompt: str) -> str:
        """Provide fallback responses when Gemini is unavailable"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["cancel", "subscription", "stop", "end"]):
            return "You can cancel your subscription from the 'Billing' section in your account settings. Cancellations take effect at the end of your billing cycle."
        elif any(word in prompt_lower for word in ["hour", "time", "open", "available"]):
            return "Our customer support is available Monday to Friday, 9 AM to 6 PM EST."
        elif any(word in prompt_lower for word in ["password", "reset", "login"]):
            return "You can reset your password by clicking 'Forgot Password' on the login page and following the instructions sent to your email."
        elif any(word in prompt_lower for word in ["refund", "money", "return"]):
            return "We offer 30-day money-back guarantee for all our premium plans. Contact support with your order details for refund requests."
        elif any(word in prompt_lower for word in ["trial", "free"]):
            return "Yes, we offer a 14-day free trial for all new users. No credit card required to start your trial."
        else:
            return "I'd be happy to help you! For detailed assistance, please contact our support team at support@company.com or call 1-800-123-4567."
    
    def generate_response(self, session_id: str, user_message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate AI response with contextual memory"""
        
        print(f"Processing message: {user_message}")
        
        # Check if FAQ can handle the query first
        faq_response = self.find_faq_match(user_message)
        
        if faq_response != "ESCALATE":
            print("✓ Using FAQ response")
            return {
                "response": faq_response,
                "requires_escalation": False,
                "next_action": "continue"
            }
        
        print("✓ Using Gemini AI response")
        # Generate custom response using Gemini
        ai_response = self.call_gemini(user_message)
        
        # Simple escalation detection
        requires_escalation = any(word in user_message.lower() for word in [
            'manager', 'supervisor', 'complaint', 'speak to human', 'human agent',
            'cancel', 'refund', 'billing', 'angry', 'frustrated', 'unsatisfied'
        ])
        
        return {
            "response": ai_response,
            "requires_escalation": requires_escalation,
            "next_action": "escalate" if requires_escalation else "continue"
        }
    
    def summarize_conversation(self, conversation_history: List[Dict]) -> str:
        """Summarize the conversation"""
        user_messages = [msg['message'] for msg in conversation_history if msg['is_user']]
        return f"User discussed: {', '.join(user_messages[-3:])}"