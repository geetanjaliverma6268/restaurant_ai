import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key="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")

MENU = {
    "burger": 120,
    "pizza": 250,
    "pasta": 180,
    "cold drink": 50,
    "fries": 80,
    "sandwich": 100
}

def analyze_order(customer_text: str):
    menu_list = "\n".join([f"- {item}: Rs.{price}" for item, price in MENU.items()])
    
    prompt = f"""Tu ek restaurant ka AI assistant hai.
    
Menu:
{menu_list}

Customer ne kaha: "{customer_text}"

Tujhe JSON format mein response dena hai:
{{
    "items": ["item1", "item2"],
    "quantities": [1, 2],
    "total": 000,
    "message": "Hindi mein confirmation message"
}}

Sirf JSON do, kuch aur mat likho."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content