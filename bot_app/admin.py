from django.contrib import admin
from .models import BotUser, Question, TestAttempt, AttemptDetail, BotState

@admin.register(BotState)
class BotStateAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'state', 'data')

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'telegram_id', 'username', 'created_at')
    search_fields = ('full_name', 'telegram_id', 'username')
    list_filter = ('created_at',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'correct_answer', 'is_active')
    list_filter = ('is_active', 'correct_answer')
    search_fields = ('text',)

    # Soraw tekstiniń tek bir bólegin kórsetiw ushın metod
    def text_short(self, obj):
        return obj.text[:50] if obj.text else "Súwretli soraw"
    text_short.short_description = "Soraw teksti"

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'total_questions', 'created_at')
    list_filter = ('created_at', 'score')
    search_fields = ('user__full_name',)

@admin.register(AttemptDetail)
class AttemptDetailAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'user_answer', 'is_correct')
    list_filter = ('is_correct',)