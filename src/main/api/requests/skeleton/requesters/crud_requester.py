from typing import Callable, Optional, TypeVar

import requests

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import CrudEndpointInterface
from src.main.api.requests.skeleton.swagger_coverage import coverage_path_for, get_tracker

T = TypeVar('T', bound=BaseModel)


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        return f"{Config.get('server')}{Config.get('api_version')}"

    def _tracked(
            self,
            request_call: Callable[[], requests.Response],
            id_in_path: bool = False
    ) -> Callable[[], requests.Response]:
        path = coverage_path_for(self.endpoint, id_in_path=id_in_path)
        return get_tracker().track_coverage_requests(path)(request_call)

    def post(self, model: Optional[T] = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''
        url = f'{self.base_url}{self.endpoint.value.url}'

        def _call() -> requests.Response:
            return requests.post(
                url=url,
                headers=self.request_spec,
                json=body
            )

        response = self._tracked(_call)()
        self.response_spec(response)
        return response

    def get(self, id: Optional[int] = None):
        suffix = f'/{id}' if id is not None else ''
        url = f'{self.base_url}{self.endpoint.value.url}{suffix}'

        def _call() -> requests.Response:
            return requests.get(url=url, headers=self.request_spec)

        response = self._tracked(_call, id_in_path=id is not None)()
        self.response_spec(response)
        return response

    def update(self, model: BaseModel, id: int): ...

    def delete(self, id: int) -> requests.Response:
        url = f'{self.base_url}{self.endpoint.value.url}/{id}'

        def _call() -> requests.Response:
            return requests.delete(url=url, headers=self.request_spec)

        response = self._tracked(_call, id_in_path=True)()
        self.response_spec(response)
        return response

    def put(self, model: Optional[T] = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''
        url = f'{self.base_url}{self.endpoint.value.url}'

        def _call() -> requests.Response:
            return requests.put(
                url=url,
                headers=self.request_spec,
                json=body
            )

        response = self._tracked(_call)()
        self.response_spec(response)
        return response

    def get_transactions(self, account_id: int):
        url = f'{self.base_url}{self.endpoint.value.url}/{account_id}/transactions'

        def _call() -> requests.Response:
            return requests.get(url=url, headers=self.request_spec)

        response = self._tracked(_call)()
        self.response_spec(response)
        return response
