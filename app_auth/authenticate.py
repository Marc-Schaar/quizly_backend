from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Wir extrahieren den Token aus dem Cookie statt aus dem Header
        raw_token = request.COOKIES.get('access_token') or None

        if raw_token is None:
            return None

        # Der Rest wird von der Basis-Klasse erledigt
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
