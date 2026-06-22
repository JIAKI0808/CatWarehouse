from dataManager.base import Validator


class ItemValidator(Validator):
    def __init__(self):
        self._errors: list[str] = []

    def validate(self, data: dict) -> bool:
        self._errors.clear()

        if not data.get("name") or not isinstance(data["name"], str):
            self._errors.append("name is required and must be a string")

        quantity = data.get("quantity", 0)
        if not isinstance(quantity, int) or quantity < 0:
            self._errors.append("quantity must be a non-negative integer")

        return len(self._errors) == 0

    def errors(self) -> list[str]:
        return self._errors
