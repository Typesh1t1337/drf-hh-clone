from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

class RegisterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username', 'status')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5}}


    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            status="Company"
        )

        user.save()

        return user

    def get_token(self,user):
        refresh_token = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        }

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username', 'status')


    def create(self,validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            status="User"
        )

        user.save()

        return user

    def get_token(self,user):
        refresh_token = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        }