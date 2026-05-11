import requests
import logging

logger = logging.getLogger(__name__)


class ClientRequest:
    async def fetch_content(self, data: str):
        try:
            response = requests.get(data)

            if response.status_code == 200:
                return response.content
            return f"the status code of your request is {response.status_code}"
        except requests.exceptions.MissingSchema as ex:
            logger.exception(ex)
            raise Exception(str(ex))
