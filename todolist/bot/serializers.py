from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from todolist.bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора пользователя бота"""
    tg_id = serializers.SlugField(source='chat_id', read_only=True)

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора,
                                 и не изменяемых полей"""
        model = TgUser
        fields = ('tg_id', 'verification_code', 'user_id')
        read_only_fields = ('tg_id', 'user_id')

    def validate_verification_code(self, code: str) -> str:
        """Метод для валидации кода верификации"""
        try:
            self.tg_user = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise ValidationError('Field is incorrect')
        return code

    def update(self, instance, validated_data: dict):
        return self.tg_user
