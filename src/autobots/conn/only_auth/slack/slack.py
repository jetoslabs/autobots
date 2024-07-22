from typing import Dict


class Slack:

    @staticmethod
    async def create_auth_header(token: str) -> Dict[str, str]:
        assert "xoxb-" in token
        return {"Authorization": f"Bearer {token}"}
