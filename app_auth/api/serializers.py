from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer used to register a new `User`.

    Fields:
    - `username`, `email`, `password` are provided by the client.
    - `repeated_password` is a write-only confirmation field.

    Validation:
    - `validate_repeated_password` ensures the two password fields match.
    - `validate_email` checks uniqueness of the email address.

    The `save` method creates the `User` instance and sets the hashed
    password using `set_password`.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True, "allow_blank": False},
        }

    def validate_repeated_password(self, value):
        """Ensure that `repeated_password` matches `password`.

        Raises `serializers.ValidationError` with a clear message when they
        differ.
        """
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match")
        return value

    def validate_email(self, value):
        """Validate email uniqueness. Raises ValidationError if already used."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def save(self):
        """Create and return a new `User` with a hashed password."""
        pw = self.validated_data["password"]

        account = User(
            email=self.validated_data["email"], username=self.validated_data["username"]
        )
        account.set_password(pw)
        account.save()
        return account
