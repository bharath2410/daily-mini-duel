import json
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import DailyDuel, QuestionBank, DuelAttempt


def home_view(request):
    today = timezone.now().date()
    duel = DailyDuel.objects.filter(duel_date=today, is_active=True).first()

    top_scores = []
    if duel:
        top_scores = DuelAttempt.objects.filter(duel=duel).order_by('-final_score', 'time_taken_seconds')[:10]

    has_played = False
    if request.user.is_authenticated and duel:
        has_played = DuelAttempt.objects.filter(user=request.user, duel=duel).exists()
    else:
        has_played = bool(request.session.get(f'played_{today}'))

    return render(request, 'duel/home.html', {
        'duel': duel,
        'top_scores': top_scores,
        'today': today,
        'has_played': has_played,
    })


def play_view(request):
    today = timezone.now().date()
    duel = DailyDuel.objects.filter(duel_date=today, is_active=True).first()

    if not duel or duel.questions.count() == 0:
        return redirect('duel:home')

    # 1. Enforce 1-play check
    if request.user.is_authenticated:
        if DuelAttempt.objects.filter(user=request.user, duel=duel).exists():
            return redirect('duel:home')
    elif request.session.get(f'played_{today}'):
        return redirect('duel:home')

    # 2. Server-side start timestamp recorded in session
    request.session['duel_start_time'] = time.time()
    request.session['active_duel_id'] = duel.id

    questions = list(duel.questions.values('id', 'category', 'prompt', 'option_a', 'option_b', 'option_c', 'option_d'))

    return render(request, 'duel/play.html', {
        'duel': duel,
        'questions_json': json.dumps(questions),
        'default_handle': request.user.username if request.user.is_authenticated else '',
    })


@require_POST
def submit_attempt(request):
    today = timezone.now().date()
    server_now = time.time()

    # Retrieve and validate server-side session start time
    start_time = request.session.get('duel_start_time')
    session_duel_id = request.session.get('active_duel_id')

    if not start_time or not session_duel_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid session or duel expired. Please restart.'},
                            status=400)

    # Server-calculated duration (immune to client DevTools manipulation)
    raw_time_taken = server_now - start_time
    server_time_taken = max(1.0, min(raw_time_taken, 60.0))

    try:
        data = json.loads(request.body)
        duel_id = data.get('duel_id')
        player_handle = data.get('handle', '').strip()

        if request.user.is_authenticated:
            player_handle = request.user.username
        elif not player_handle:
            player_handle = 'Guest Duelist'

        answers = data.get('answers', {})
        duel = get_object_or_404(DailyDuel, id=duel_id)

        # Enforce single play at database / session level
        if request.user.is_authenticated and DuelAttempt.objects.filter(user=request.user, duel=duel).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already completed today\'s duel.'}, status=403)
        elif not request.user.is_authenticated and request.session.get(f'played_{today}'):
            return JsonResponse({'status': 'error', 'message': 'You have already completed today\'s duel.'}, status=403)

        correct_count = 0
        for q in duel.questions.all():
            user_choice = answers.get(str(q.id))
            if user_choice and user_choice.upper() == q.correct_option:
                correct_count += 1

        # Calculate score using SERVER time
        time_bonus = max(0, int((60.0 - server_time_taken) * 10))
        score = (correct_count * 1000) + (time_bonus if correct_count > 0 else 0)

        attempt = DuelAttempt.objects.create(
            duel=duel,
            player_handle=player_handle[:30],
            correct_count=correct_count,
            time_taken_seconds=round(server_time_taken, 2),
            final_score=score,
            user=request.user if request.user.is_authenticated else None
        )

        # Clear session start lock & tag played
        request.session[f'played_{today}'] = True
        request.session.pop('duel_start_time', None)
        request.session.pop('active_duel_id', None)

        return JsonResponse({'status': 'success', 'attempt_id': attempt.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def result_view(request, attempt_id):
    attempt = get_object_or_404(DuelAttempt, id=attempt_id)
    duel = attempt.duel
    leaderboard = DuelAttempt.objects.filter(duel=duel).order_by('-final_score', 'time_taken_seconds')[:10]

    rank = DuelAttempt.objects.filter(duel=duel, final_score__gt=attempt.final_score).count() + 1
    total_players = DuelAttempt.objects.filter(duel=duel).count()

    percentile = 100 if total_players <= 1 else round(((total_players - rank) / (total_players - 1)) * 100)

    return render(request, 'duel/result.html', {
        'attempt': attempt,
        'duel': duel,
        'leaderboard': leaderboard,
        'rank': rank,
        'total_players': total_players,
        'percentile': percentile,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('duel:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('duel:home')
    else:
        form = UserCreationForm()
    return render(request, 'duel/auth.html', {'form': form, 'title': 'CREATE DUELIST ACCOUNT', 'btn_text': 'SIGN UP'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('duel:home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('duel:home')
    else:
        form = AuthenticationForm()
    return render(request, 'duel/auth.html', {'form': form, 'title': 'DUELIST LOGIN', 'btn_text': 'LOG IN'})


def logout_view(request):
    logout(request)
    return redirect('duel:home')