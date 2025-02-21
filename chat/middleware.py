from django.core.cache import cache
from django.utils.timezone import now


def set_user_online(user_id: int):
    cache.set(f'user_online_{user_id}', True, timeout=300)

def check_user_online(user_id: int) -> bool:
    return True if cache.get(f'user_online_{user_id}') else False

class UpdateOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            set_user_online(request.user.id)
        return response

