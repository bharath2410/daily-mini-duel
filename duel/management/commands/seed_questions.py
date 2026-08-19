from django.core.management.base import BaseCommand
from django.utils import timezone
from duel.models import DailyDuel, TriviaQuestion


class Command(BaseCommand):
    help = "Seeds the database with today's trivia duel"

    def handle(self, *args, **options):
        today = timezone.now().date()
        duel, created = DailyDuel.objects.get_or_create(
            duel_date=today,
            defaults={'title': "Midnight Cyber-Run #01", 'is_active': True}
        )

        if created or duel.questions.count() == 0:
            questions_data = [
                {
                    'category': 'TECH',
                    'order': 1,
                    'prompt': 'Which computer architecture term was coined after an actual physical insect was found trapped inside a relay in 1947?',
                    'option_a': 'Spam',
                    'option_b': 'Bug',
                    'option_c': 'Glitch',
                    'option_d': 'Cookie',
                    'correct_option': 'B',
                },
                {
                    'category': 'LOGIC',
                    'order': 2,
                    'prompt': 'If a server cluster executes 4 jobs in 4 minutes, how many minutes do 100 identical servers take to execute 100 jobs?',
                    'option_a': '100 minutes',
                    'option_b': '25 minutes',
                    'option_c': '4 minutes',
                    'option_d': '1 minute',
                    'correct_option': 'C',
                },
                {
                    'category': 'POP',
                    'order': 3,
                    'prompt': 'In the arcade classic Pac-Man, what is the name of the red ghost that directly chases the player?',
                    'option_a': 'Blinky',
                    'option_b': 'Pinky',
                    'option_c': 'Inky',
                    'option_d': 'Clyde',
                    'correct_option': 'A',
                },
            ]
            for q in questions_data:
                TriviaQuestion.objects.create(duel=duel, **q)
            self.stdout.write(self.style.SUCCESS(f"Successfully seeded 3 questions for {today}"))
        else:
            self.stdout.write(self.style.WARNING(f"Duel already initialized for {today}"))