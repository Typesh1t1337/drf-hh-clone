import os
from openai import OpenAI
from dotenv import load_dotenv

def get_llm_response(text: str) -> str:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    help_prompt = "You are virtual assistant of website called Job on demand its a website as a indeed, there simple system, people apply for hiring, and waiting for invitation, you will help for users, to achieve their goals and targets"

    openai = OpenAI(api_key=openai_api_key)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{
                "role": "system",
                "content": help_prompt
            },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        reply = response.choices[0].message.content

        return reply

    except Exception as e:
        return str(e)