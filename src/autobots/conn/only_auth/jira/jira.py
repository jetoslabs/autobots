from typing import Dict


class Jira:

    @staticmethod
    async def create_auth_header(token: str) -> Dict[str, str]:
        return {"Authorization": f"Basic {token}"}
