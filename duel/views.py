import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import DailyDuel, TriviaQuestion, DuelAttempt


def home_view(request):
    today = timezone.now().date()
    duel = DailyDuel.objects.filter(duel_date=today, is_active=True).first()

    top_scores = []
    if duel:
        top_scores = DuelAttempt.objects.filter(duel=duel).order_by('-final_score', 'time_taken_seconds')[:10]

    return render(request, 'duel/home.html', {
        'duel': duel,
        'top_scores': top_scores,
        'today': today,
    })


def play_view(request):
    today = timezone.now().date()
    duel = DailyDuel.objects.filter(duel_date=today, is_active=True).first()

    if not duel or duel.questions.count() == 0:
        return redirect('duel:home')

    # Serialize questions without revealing correct answer to client
    questions = list(
        duel.questions.values('id', 'category', 'prompt', 'option_a', 'option_b', 'option_c', 'option_d', 'order'))

    return render(request, 'duel/play.html', {
        'duel': duel,
        'questions_json': json.dumps(questions),
    })


@require_POST
def submit_attempt(request):
    try:
        data = json.loads(request.body)
        duel_id = data.get('duel_id')
        player_handle = data.get('handle', '').strip() or 'Anonymous Duelist'
        answers = data.get('answers', {})  # Dict mapping str(question_id) -> 'A'/'B'/'C'/'D'
        client_time = float(data.get('time_taken', 60.0))

        duel = get_object_or_404(DailyDuel, id=duel_id)
        questions = duel.questions.all()

        correct_count = 0
        for q in questions:
            user_choice = answers.get(str(q.id))
            if user_choice and user_choice.upper() == q.correct_option:
                correct_count += 1

        # Arcade scoring: 1000 base pts per correct answer + time bonus decay
        # Max bonus: 500 pts if finished within 5s, decaying to 0 at 60s
        time_bonus = max(0, int((60.0 - min(client_time, 60.0)) * 10))
        score = (correct_count * 1000) + (time_bonus if correct_count > 0 else 0)

        attempt = DuelAttempt.objects.create(
            duel=duel,
            player_handle=player_handle[:30],
            correct_count=correct_count,
            time_taken_seconds=round(client_time, 2),
            final_score=score,
            user=request.user if request.user.is_authenticated else None
        )

        return JsonResponse({'status': 'success', 'attempt_id': attempt.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def result_view(request, attempt_id):
    attempt = get_object_or_404(DuelAttempt, id=attempt_id)
    duel = attempt.duel
    leaderboard = DuelAttempt.objects.filter(duel=duel).order_by('-final_score', 'time_taken_seconds')[:10]

    # Calculate user's rank
    rank = DuelAttempt.objects.filter(duel=duel, final_score__gt=attempt.final_score).count() + 1
    total_players = DuelAttempt.objects.filter(duel=duel).count()

    percentile = 0
    if total_players > 1:
        percentile = round(((total_players - rank) / (total_players - 1)) * 100)
    elif total_players == 1:
        percentile = 100

    return render(request, 'duel/result.html', {
        'attempt': attempt,
        'duel': duel,
        'leaderboard': leaderboard,
        'rank': rank,
        'total_players': total_players,
        'percentile': percentile,
    })