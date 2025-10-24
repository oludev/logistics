from django.conf import settings

class SeparateAdminSessionMiddleware:
    """
    Use a different session cookie for Django admin (Jazzmin) and frontend users.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Save the original session cookie name
        original_cookie_name = settings.SESSION_COOKIE_NAME  

        # If request is for admin panel, change session cookie name
        if request.path.startswith("/admin/") or request.path.startswith("/panel/"):
            settings.SESSION_COOKIE_NAME = "admin_sessionid"
        else:
            settings.SESSION_COOKIE_NAME = "user_sessionid"

        response = self.get_response(request)

        # Reset back after request (important!)
        settings.SESSION_COOKIE_NAME = original_cookie_name  

        return response
