from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DailyDuel(models.Model):
    duel_date = models.DateField(unique=True, default=timezone.now)
    title = models.CharField(max_length=150, default="Daily Speed Arena")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Duel: {self.duel_date} - {self.title}"


class TriviaQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('TECH', 'Tech & Science'),
        ('POP', 'Pop Culture & Gaming'),
        ('HIST', 'World & History'),
        ('LOGIC', 'Puzzles & Logic'),
    ]

    duel = models.ForeignKey(DailyDuel, on_delete=models.CASCADE, related_name='questions')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='TECH')
    prompt = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.duel.duel_date}] Q{self.order}: {self.prompt[:40]}"


class DuelAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duel_attempts', null=True, blank=True)
    player_handle = models.CharField(max_length=30)
    duel = models.ForeignKey(DailyDuel, on_delete=models.CASCADE, related_name='attempts')
    correct_count = models.PositiveSmallIntegerField(default=0)
    time_taken_seconds = models.FloatField(default=0.0)
    final_score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-final_score', 'time_taken_seconds']

    def __str__(self):
        return f"{self.player_handle} - {self.final_score}pts ({self.duel.duel_date})"