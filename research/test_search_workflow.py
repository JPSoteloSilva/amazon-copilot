# %%
import start_research
# %%
from amazon_copilot.services.ai.chatbot.graph import run_conversation
# %%
def print_response(response):
    print("Conversation history:")
    for i in range(len(response["history"])):
        print(f"Message {i}: {response['history'][i].role} - {response['history'][i].content}")
    print(f"Products: {response['products']}")
    print(f"Preferences: {response['preferences']}")
    print("-" * 100)

# %%
response = run_conversation("I want to buy something for my dog")
print_response(response)
# %%
response2 = run_conversation("Around 10 dollars", response)
print_response(response2)
# %%
response3 = run_conversation("Do you have something to show me?", response2)
print_response(response3)
# %%
response4 = run_conversation("like a dog bed", response3)
print_response(response4)
# %%
response5 = run_conversation("Can you tell me more about the product?", response4)
print_response(response5)
# %%
response6 = run_conversation("Okey, thank you", response5)
print_response(response6)
# %%
response7 = run_conversation("I want to buy something for my cat now", response6)
print_response(response7)
# %%
response9 = run_conversation("The same as for my dog", response7)
print_response(response9)
# %%
response10 = run_conversation("A bed and the same price", response9)
print_response(response10)
# %%