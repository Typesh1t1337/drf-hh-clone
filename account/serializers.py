from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

class RegisterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username', 'first_name', 'last_name', 'status')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5}}


    def create(self, validated_data):

        if get_user_model().objects.filter(email=validated_data['email']).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if get_user_model().objects.filter(username=validated_data['username']).exists():
            return Response(
                {'error': 'Username already registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
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
        fields = ('email', 'password', 'username', 'status','first_name', 'last_name')


    def create(self,validated_data):

        if get_user_model().objects.filter(email=validated_data['email']).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if get_user_model().objects.filter(username=validated_data['username']).exists():
            return Response(
                {'error': 'Username already registered'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            status="User"
        )

        user.save()

        return user

    def get_token(self,user) -> dict:
        refresh_token = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        }


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.IntegerField()
