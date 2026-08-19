from django.contrib import admin
from .models import QuestionBank, DailyDuel, DuelAttempt

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('prompt_summary', 'category', 'correct_option', 'created_at')
    list_filter = ('category',)
    search_fields = ('prompt',)

    def prompt_summary(self, obj):
        return obj.prompt[:60] + "..."

@admin.register(DailyDuel)
class DailyDuelAdmin(admin.ModelAdmin):
    list_display = ('duel_date', 'title', 'is_active', 'question_count')
    filter_horizontal = ('questions',)

    def question_count(self, obj):
        return obj.questions.count()

@admin.register(DuelAttempt)
class DuelAttemptAdmin(admin.ModelAdmin):
    list_display = ('player_handle', 'user', 'duel', 'correct_count', 'time_taken_seconds', 'final_score', 'completed_at')
    list_filter = ('duel__duel_date',)
    search_fields = ('player_handle', 'user__username')