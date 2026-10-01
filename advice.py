"""
Plant Disease Advice Module
Provides treatment recommendations based on detected disease class
NO external API used - fully local CSV-based responses
"""

import pandas as pd
import os

# Locate CSV relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'plant_faq.csv')

# Load disease database ONCE when module is imported
_faq_df = pd.read_csv(CSV_PATH)


def get_disease_info(disease_class):
    """
    Get detailed information about a disease
    
    Args:
        disease_class (str): Full class name e.g. 'Tomato___Early_blight'
        
    Returns:
        dict or None
    """
    row = _faq_df[_faq_df['disease_class'] == disease_class]
    
    if row.empty:
        return None
    
    row = row.iloc[0]
    return {
        'crop': row['crop'],
        'disease_name': row['disease_name'],
        'symptoms': row['symptoms'],
        'cause': row['cause'] if 'cause' in _faq_df.columns else 'Not specified',
        'treatment': row['treatment'],
        'prevention': row['prevention'],
        'severity': row['severity']
    }


def get_advice(disease_class, confidence=None):
    """
    Generate formatted chatbot-style advice message
    
    Args:
        disease_class (str): Full class name e.g. 'Tomato___Early_blight'
        confidence (float, optional): Model confidence score (0-1)
        
    Returns:
        str: Formatted advice message
    """
    info = get_disease_info(disease_class)
    
    if info is None:
        return "⚠️ Sorry, no information available for this disease yet."
    
    if info['severity'] == 'None':
        message = f"🎉 Great news! Your {info['crop']} plant is Healthy!\n\n"
        message += f"💡 Maintenance Tips:\n{info['prevention']}\n\n"
        message += "Keep up the good care! 🌱"
        return message
    
    severity_emoji = {
        'Low': '🟢',
        'Medium': '🟡',
        'High': '🟠',
        'Critical': '🔴'
    }
    emoji = severity_emoji.get(info['severity'], '⚠️')
    
    message = f"{emoji} Diagnosis: {info['disease_name']}\n"
    message += f"🌿 Crop: {info['crop']}\n"
    
    if confidence is not None:
        message += f"📊 Confidence: {confidence:.1%}\n"
    
    message += f"⚠️ Severity: {info['severity']}\n\n"
    message += f"🔍 Symptoms:\n{info['symptoms']}\n\n"
    message += f"🦠 Cause:\n{info['cause']}\n\n"
    message += f"💊 Treatment:\n{info['treatment']}\n\n"
    message += f"🛡️ Prevention:\n{info['prevention']}"
    
    if info['severity'] == 'Critical':
        message += "\n\n⚠️ URGENT: This is a critical disease. Take immediate action!"
    
    return message


def handle_text_query(user_message):
    """
    Handle general text-based chatbot queries (greetings, crop questions, etc.)
    
    Args:
        user_message (str): User's typed message
        
    Returns:
        str: Chatbot response
    """
    message_lower = user_message.lower().strip()
    
    greetings = ['hi', 'hello', 'hey', 'namaste', 'good morning', 'good afternoon']
    if any(g in message_lower for g in greetings):
        return "👋 Hello! I'm your Plant Doctor Assistant. Upload a leaf image and I'll help diagnose any diseases!"
    
    if any(t in message_lower for t in ['thank you', 'thanks', 'thank u', 'ty']):
        return "😊 You're welcome! Feel free to ask if you need more help with your plants!"
    
    if any(b in message_lower for b in ['bye', 'goodbye', 'see you']):
        return "👋 Goodbye! Take care of your plants. Come back anytime!"
    
    if 'help' in message_lower:
        return (
            "🤖 Here's how I can help:\n\n"
            "1. 📸 Upload a leaf image for disease diagnosis\n"
            "2. 💬 Ask about specific diseases (e.g. 'What is early blight?')\n"
            "3. 🌱 Ask about a crop (e.g. 'Tell me about tomato diseases')\n\n"
            "Just type your question or upload an image!"
        )
    
    for _, row in _faq_df.iterrows():
        if row['disease_name'].lower() in message_lower and row['disease_name'] != 'Healthy':
            return get_advice(row['disease_class'])
    
    for crop in _faq_df['crop'].unique():
        if crop.lower() in message_lower:
            diseases = _faq_df[(_faq_df['crop'] == crop) & (_faq_df['disease_name'] != 'Healthy')]
            response = f"🌱 Common {crop} diseases:\n\n"
            for _, d in diseases.iterrows():
                response += f"• {d['disease_name']} (Severity: {d['severity']})\n"
            response += "\n📸 Upload a leaf image for accurate diagnosis!"
            return response
    
    return (
        "🤔 I'm not sure I understood that.\n\n"
        "Try uploading a leaf image, or type 'help' to see what I can do!"
    )


def get_all_diseases():
    """Return list of all disease classes in database"""
    return _faq_df['disease_class'].tolist()


def get_statistics():
    """Get database statistics"""
    return {
        'total_entries': len(_faq_df),
        'total_diseases': len(_faq_df[_faq_df['severity'] != 'None']),
        'total_crops': _faq_df['crop'].nunique(),
        'critical_diseases': len(_faq_df[_faq_df['severity'] == 'Critical']),
        'crops_list': sorted(_faq_df['crop'].unique().tolist())
    }


if __name__ == '__main__':
    print("Testing advice.py...")
    print(get_advice('Tomato___Early_blight', confidence=0.95))
    print("\nStatistics:")
    print(get_statistics())