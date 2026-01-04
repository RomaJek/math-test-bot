from rest_framework import serializers
from .models import BotUser, Question, TestAttempt

class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class TestAttemptSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = TestAttempt
        fields = ['id', 'user', 'user_name', 'score', 'total_questions', 'created_at']



