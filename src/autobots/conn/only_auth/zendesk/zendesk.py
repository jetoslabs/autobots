from typing import Dict


class Zendesk:

    @staticmethod
    async def create_auth_header(token: str) -> Dict[str, str]:
        return {"Authorization": f"basic {token}"}
