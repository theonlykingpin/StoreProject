from djoser.serializers import UserCreateSerializer, UserSerializer


class CustomDjoserUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('first_name', 'last_name')


class CustomDjoserUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('first_name', 'last_name')
