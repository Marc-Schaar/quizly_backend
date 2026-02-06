from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TestRefreshToken(APITestCase):
    """Test suite for the token refresh endpoint.

    This class tests both the successful token refresh flow (HTTP 200)
    and the unauthorized flow when no valid tokens are provided
    (HTTP 401). Tests use `self.user_client` with cookies set to
    simulate the presence or absence of JWT tokens.
    """

    def setUp(self):
        """Create a user, set refresh/access cookies and authenticate client.

        A `RefreshToken` is created for `self.user`; its access and refresh
        token strings are stored in the test client's cookies to mimic a
        real authenticated client that can request a token refresh.
        """
        self.user = User.objects.create_user(
            username="your_username",
            password="your_password",
            email="email@mail.de",
        )

        self.user_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.user_client.cookies["access_token"] = access_token
        self.user_client.cookies["refresh_token"] = str(refresh)
        self.user_client.force_authenticate(user=self.user)

    def test_refresh_token_200(self):
        """Happy-path: POST to refresh endpoint returns new access token.

        Verifies that the response status is 200 and that the JSON
        payload contains a `detail` message and an `access` token.
        """
        url = reverse("token_refresh")
        response = self.user_client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "detail": "Token refreshed",
                "access": response.data.get("access"),
            },
        )

    def test_refresh_token_401(self):
        """Negative case: unauthenticated client receives HTTP 401.

        The test clears forced authentication so the client has no
        associated user and posts an empty payload, expecting a 401.
        """
        url = reverse("token_refresh")
        payload = {}
        self.user_client.force_authenticate(user=None)
        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
