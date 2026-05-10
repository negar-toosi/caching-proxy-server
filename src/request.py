import re
from typing import Optional


class ClientRequest:
    async def validate_request(self, data: str) -> Optional[str]:
        url_pattern = re.compile(
            r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"
        )
        is_validate = url_pattern.match(data)

        if is_validate:
            return "true"
        return "false"
