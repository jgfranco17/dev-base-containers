class CoreError(Exception):
    """Base class for all core-related errors."""

    def __init__(self, category: str, message: str, additional_info: str = "") -> None:
        self.category = category
        self.message = message
        self.additional_info = additional_info
        full_message = f"[{self.category.upper()}] {self.message}"
        if self.additional_info:
            full_message += f"\n\nAdditional information: {self.additional_info}"
        super().__init__(full_message)


class ClientError(CoreError):
    """Error related to client operations."""

    def __init__(self, message: str, additional_info: str = "") -> None:
        super().__init__("CLIENT", message, additional_info)
