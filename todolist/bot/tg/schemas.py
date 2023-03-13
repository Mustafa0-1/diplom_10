from pydantic import BaseModel


class Chat(BaseModel):
    """Модель чата бота"""
    id: int


class Message(BaseModel):
    """Модель сообщения бота"""
    chat: Chat
    text: str | None = None


class UpdateObj(BaseModel):
    """Модель бота полученных сообщений"""
    update_id: int
    message: Message


class SendMessageResponse(BaseModel):
    """Модель бота для отправки сообщения"""
    ok: bool
    result: Message


class GetUpdatesResponse(BaseModel):
    """Модель бота для получения сообщений от пользователя"""
    ok: bool
    result: list[UpdateObj]
