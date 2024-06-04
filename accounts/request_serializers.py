from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

class OAuthSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    name = serializers.CharField(required=False)
    picture = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ["email", "name", "picture"]

    def validate(self, data):
        email = data.get("email", None)
        name = data.get("name", None)
        picture = data.get("picture", None)

        user = User.get_user_or_none_by_email(email=email)
    

        if user is None:
            # Create a new user if one does not exist
            user = User.objects.create(email=email, username=name, name=name, picture=picture)

        token = RefreshToken.for_user(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        data = {
            "user": user,
            "name": name,
            "picture":picture,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        return data
