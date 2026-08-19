import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from duel.models import DailyDuel, QuestionBank

class Command(BaseCommand):
    help = "Seeds question bank and ensures today's daily duel has 3 active questions"

    def handle(self, *args, **options):
        # 1. Master question library
        pool = [
            {
                'category': 'TECH',
                'prompt': 'Which computer architecture term was coined after an insect was found in a relay in 1947?',
                'option_a': 'Spam', 'option_b': 'Bug', 'option_c': 'Glitch', 'option_d': 'Cookie',
                'correct_option': 'B',
            },
            {
                'category': 'LOGIC',
                'prompt': 'If a server cluster executes 4 jobs in 4 minutes, how many minutes do 100 identical servers take to execute 100 jobs?',
                'option_a': '100 minutes', 'option_b': '25 minutes', 'option_c': '4 minutes', 'option_d': '1 minute',
                'correct_option': 'C',
            },
            {
                'category': 'POP',
                'prompt': 'In the arcade classic Pac-Man, what is the name of the red ghost that directly chases the player?',
                'option_a': 'Blinky', 'option_b': 'Pinky', 'option_c': 'Inky', 'option_d': 'Clyde',
                'correct_option': 'A',
            },
            {
                'category': 'TECH',
                'prompt': 'What does the "HTTP 418" status code officially indicate in standard RFC 2324?',
                'option_a': 'Internal Server Error', 'option_b': 'I\'m a teapot', 'option_c': 'Gateway Timeout', 'option_d': 'Payment Required',
                'correct_option': 'B',
            },
            {
                'category': 'HIST',
                'prompt': 'Who is widely credited with writing the first computer algorithm for Charles Babbage\'s Analytical Engine?',
                'option_a': 'Alan Turing', 'option_b': 'Ada Lovelace', 'option_c': 'Grace Hopper', 'option_d': 'John von Neumann',
                'correct_option': 'B',
            },
            {
                'category': 'LOGIC',
                'prompt': 'What comes next in the sequence: 2, 6, 12, 20, 30, ...?',
                'option_a': '40', 'option_b': '42', 'option_c': '44', 'option_d': '46',
                'correct_option': 'B',
            },
            {
                'category': 'POP',
                'prompt': 'Which legendary game studio created the Doom and Quake franchises in the 1990s?',
                'option_a': 'Valve', 'option_b': 'Epic Games', 'option_c': 'id Software', 'option_d': 'Bethesda',
                'correct_option': 'C',
            },
            {
                'category': 'HIST',
                'prompt': 'In what year was the Python programming language first publicly released by Guido van Rossum?',
                'option_a': '1989', 'option_b': '1991', 'option_c': '1995', 'option_d': '2000',
                'correct_option': 'B',
            }
        ]

        for item in pool:
            QuestionBank.objects.get_or_create(prompt=item['prompt'], defaults=item)

        today = timezone.now().date()
        duel, created = DailyDuel.objects.get_or_create(
            duel_date=today,
            defaults={'title': f"Cyber-Run Arena #{today.strftime('%j')}", 'is_active': True}
        )

        if duel.questions.count() < 3:
            # Pick 3 random questions that are not already over-used
            available = list(QuestionBank.objects.all())
            selected = random.sample(available, min(3, len(available)))
            duel.questions.set(selected)
            duel.save()
            self.stdout.write(self.style.SUCCESS(f"Assembled and activated today's duel with {len(selected)} questions."))
        else:
            self.stdout.write(self.style.WARNING("Today's duel already initialized with 3 questions."))