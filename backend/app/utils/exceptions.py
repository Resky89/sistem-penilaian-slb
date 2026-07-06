from http import HTTPStatus

class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = None, headers: dict = None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}

# Buat class status untuk meniru fastapi.status secara kompatibel
class status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500
