from django.contrib import admin
from .models import DailyDuel, TriviaQuestion, DuelAttempt

class TriviaQuestionInline(admin.StackedInline):
    model = TriviaQuestion
    extra = 3

@admin.register(DailyDuel)
class DailyDuelAdmin(admin.ModelAdmin):
    list_display = ('duel_date', 'title', 'is_active')
    inlines = [TriviaQuestionInline]

@admin.register(DuelAttempt)
class DuelAttemptAdmin(admin.ModelAdmin):
    list_display = ('player_handle', 'duel', 'correct_count', 'time_taken_seconds', 'final_score', 'completed_at')
    list_filter = ('duel__duel_date',)