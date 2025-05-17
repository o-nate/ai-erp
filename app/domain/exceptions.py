from pydantic import UUID4


class RateLimitExceededError(Exception):
    pass


class ConversationNotFoundError(Exception):
    conversation_uuid: UUID4

    def __init__(self, conversation_uuid: UUID4, *args: object) -> None:
        super().__init__(*args)
        self.conversation_uuid = conversation_uuid


class UserNotAuthorizedError(Exception):
    user_id: str

    def __init__(self, user_id: str, *args: object) -> None:
        super().__init__(*args)
        self.user_id = user_id


class MalformedMessageError(Exception):
    detail: str

    def __init__(self, detail: str, *args: object) -> None:
        super().__init__(*args)
        self.detail = detail


class TranscriptionError(Exception):
    detail: str

    def __init__(self, detail: str, *args: object) -> None:
        super().__init__(*args)
        self.detail = detail
