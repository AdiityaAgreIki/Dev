from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from diet_extractor_tool import extract_diet_report_tool

# 1. Register the tool
my_tool = Tool(
    name="extract_diet_report_from_image",
    func=extract_diet_report_tool,
    description="Extracts diet/body composition report data from an image file (path or bytes) and returns JSON. Input should be an image path or bytes."
)

# 2. Set up Gemini (Google Generative AI) LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.2,
    tools=[my_tool],  # Register the tool for tool-calling
)

# 3. Initialize the agent with tool-calling
agent = initialize_agent(
    tools=[my_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

# 4. Example usage: send an image to Gemini and get the extracted report
if __name__ == "__main__":
    # Example: use a local image file
    image_path = "diet.jpg"  # Replace with your image file path
    prompt = "Extract the diet/body composition report from this image."
    # Gemini will automatically call the tool if it detects an image input
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    result = agent.run({"image": image_bytes, "input": prompt})
    print("\n--- Gemini Tool Output ---\n")
    print(result)
