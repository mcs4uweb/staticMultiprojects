import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_response(
    prompt: str,
    system_message: str = "You are a helpful, accurate, and privacy-conscious assistant.",
    model: str = "openai/gpt-oss-120b",  # or "llama3-70b-8192" for higher quality
    max_tokens: int = 1000,
    temperature: float = 0.3  # Lower = more predictable (good for checklists)
):
    """
    Generate a response from Llama 3 via Groq.
    
    Args:
        prompt: User input
        system_message: Sets behavior/context
        model: Choose 'llama3-8b-8192' (fast) or 'llama3-70b-8192' (smarter)
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=1,
            stream=False,
        )
        return chat_completion.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

# === Example Use Cases ===

if __name__ == "__main__":
    # Example 1: Retirement Checklist
    retirement_prompt = (
        "Generate a detailed retirement readiness checklist for someone planning to retire at age 73, "
        "covering finances, Social Security, healthcare, and estate planning. Use bullet points."
    )
    print("🔍 Retirement Checklist:\n")
    print(generate_response(retirement_prompt))

    print("\n" + "="*60 + "\n")

    # Example 2: Dyslexia-Friendly Writing Prompt
    writing_prompt = (
        "Create a fun, engaging writing exercise for a 10-year-old with dyslexia. "
        "Use simple words, clear structure, and encourage creativity without pressure."
    )
    print("✏️ Writing Exercise for Dyslexia:\n")
    print(generate_response(writing_prompt))

    print("\n" + "="*60 + "\n")

    # Example 3: Charity Tax Guidance
    charity_prompt = (
        "Explain how creating a donor-advised fund (DAF) can help with tax optimization for someone in a high tax bracket. "
        "Keep it concise and practical."
    )
    print("💰 Charity & Tax Tip:\n")
    print(generate_response(charity_prompt))