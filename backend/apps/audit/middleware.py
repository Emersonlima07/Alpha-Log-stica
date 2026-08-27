import threading

_thread_locals = threading.local()


class CurrentRequestMiddleware:
    """
    Guarda o request atual em thread-local storage para que o
    AuditoriaService (chamado a partir de qualquer service layer)
    consiga capturar o IP de origem sem precisar receber o request
    explicitamente em toda chamada.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.request = None
        return response


def get_current_request():
    return getattr(_thread_locals, "request", None)


def get_client_ip():
    request = get_current_request()
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
