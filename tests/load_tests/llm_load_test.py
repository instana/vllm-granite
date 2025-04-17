import json
import random
from locust import HttpUser, task, between

# Sample prompts
SAMPLE_PROMPTS = [
    "Write a code to find the maximum value in a list of numbers.",
    "Explain quantum computing in simple terms.",
    "Write a function to check if a string is a palindrome.",
    "Create a recipe for chocolate chip cookies.",
    "Explain the concept of recursion in programming.",
    "Write a haiku about artificial intelligence.",
    "Describe the main causes of climate change.",
    "Compare and contrast REST and GraphQL APIs.",
    "Explain how blockchain technology works.",
    "Write a short story about a robot learning to feel emotions."
]

class LLMUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1-5 seconds between tasks
    
    @task
    def chat_completion(self):
        # Select a random prompt from our list
        prompt = random.choice(SAMPLE_PROMPTS)
        
        # Prepare the payload
        payload = {
            "messages": [
                {
                    "content": prompt,
                    "role": "user"
                }
            ],
            "model": "ibm-granite/granite-3.2-8b-instruct",
            "max_tokens": 100
        }
        
        # Make the request
        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            catch_response=True,
            name="Chat Completion"
        ) as response:
            # Validate response
            if response.status_code == 200:
                try:
                    # Try to parse the response to ensure it's valid JSON
                    response_data = response.json()
                    # Validate if generation choices present
                    if "choices" not in response_data:
                        response.failure("Missing 'choices' in response")
                except json.JSONDecodeError:
                    response.failure("Response was not valid JSON")
            else:
                response.failure(f"Request failed with status code: {response.status_code}")

if __name__ == "__main__":
    pass
