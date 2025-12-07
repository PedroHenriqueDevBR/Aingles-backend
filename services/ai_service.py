import os
from uuid import UUID

from dotenv import load_dotenv
from openai import OpenAI

from models.chat_models import Chat, ChatMessage, MessageRole
from schemas.chat_schema import CreateChatRequest

load_dotenv()

START_MESSAGE = """
You are an "English Teacher" for Brazilian people, you speak English and Portuguese fluently, and you are specialized in $theme.
The user will talk with you about this theme in English, and sometimes in Portuguese.
Your tasks are:

- If the user makes a mistake, first correct it (showing the corrected version in a natural way).
- After correcting, answer the user to keep the conversation flowing.
- If the user doesn't understand something, explain it in a different way or in Portuguese if the user prefers.
- Your responses should be short and concise, like a text message.

Keep the conversation natural, immersive, and engaging, like a real-life situation.
Your main goal: help the user practice English through conversation, correction, and vocabulary expansion, without breaking the immersion of the chosen theme
"""


class AIService:

    def __init__(self):
        self.model = os.getenv("AI_MODEL", "gpt-5-nano")
        self.token = os.getenv("AI_TOKEN", "")
        self.client = OpenAI(api_key=self.token)

    def format_history(self, chat: Chat) -> list[dict]:
        history = []
        for message in chat.messages:
            history.append({"role": message.role, "content": message.content})
        return history

    def initialize_chat(
        self,
        user_id: UUID,
        chat_request: CreateChatRequest,
        theme: str = "",
    ) -> Chat:
        chat = Chat(title=chat_request.title, author_id=user_id)
        system_content = (
            START_MESSAGE.replace("$theme", theme)
            if theme
            else START_MESSAGE.replace("$theme", "general conversation")
        )
        system_message = ChatMessage(
            role=MessageRole.DEVELOPER,
            content=system_content,
            chat_id=chat.id,
        )
        chat.messages.append(system_message)
        return chat

    def send_message(self, chat: Chat, user_message_content: str) -> ChatMessage:
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=user_message_content,
            chat_id=chat.id,
        )
        chat.messages.append(user_message)
        messages = self.format_history(chat)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=500,
        )

        assistant_content = response.choices[0].message.content
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            chat_id=chat.id,
        )
        chat.messages.append(assistant_message)

        return assistant_message

    def send_message_stream(self, chat: Chat, user_message_content: str):
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=user_message_content,
            chat_id=chat.id,
        )

        chat.messages.append(user_message)
        messages = self.format_history(chat)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        if len(full_response) > 0:
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=full_response,
                chat_id=chat.id,
            )
            chat.messages.append(assistant_message)
        else:
            chat.messages.remove(user_message)
