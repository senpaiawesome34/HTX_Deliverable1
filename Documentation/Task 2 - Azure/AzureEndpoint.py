import os
from openai import AzureOpenAI

required_env = [
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
]

missing = [name for name in required_env if not os.environ.get(name)]
if missing:
    raise EnvironmentError(f"Missing environment variable(s): {', '.join(missing)}")

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

resp = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],  # deployment name, not raw model id
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Summarize Azure resource groups in 3 bullets"},
    ],
)

print(resp.choices[0].message.content)
