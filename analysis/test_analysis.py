from analysis.utils import analyze_conversation

messages = [
    {"sender": "user", "message": "Hi, I need help with my order."},
    {"sender": "ai", "message": "Sure, can you please share your order ID?"},
    {"sender": "user", "message": "It's 12345."},
    {"sender": "ai", "message": "Thanks! Your order has been shipped and will arrive tomorrow."}
]

result = analyze_conversation(messages)
print(result)
