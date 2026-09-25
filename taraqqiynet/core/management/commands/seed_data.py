from django.core.management.base import BaseCommand

from core.models import Region, Subject, Level, Topic, Question, Choice

REGIONS = [
    "Toshkent shahri", "Toshkent viloyati", "Samarqand", "Buxoro", "Andijon",
    "Farg'ona", "Namangan", "Qashqadaryo", "Surxondaryo", "Xorazm",
    "Navoiy", "Jizzax", "Sirdaryo", "Qoraqalpog'iston",
]

ENGLISH_LEVELS = [
    ("A1", 1, 0), ("A2", 2, 20), ("B1", 3, 40), ("B2", 4, 60), ("C1", 5, 80),
]
MATH_LEVELS = [
    ("Boshlang'ich", 1, 0), ("O'rta", 2, 40), ("Yuqori", 3, 70),
]

ENGLISH_QUESTIONS = [
    # (topic, level_name, question, choices[(text, is_correct), ...])
    ("Present Simple", "A1", "She ___ to school every day.", [("go", False), ("goes", True), ("going", False), ("gone", False)]),
    ("Articles", "A1", "I saw ___ elephant at the zoo.", [("a", False), ("an", True), ("the a", False), ("-", False)]),
    ("Plurals", "A1", "Choose the correct plural of 'child'.", [("childs", False), ("children", True), ("childes", False), ("child's", False)]),
    ("Past Simple", "A2", "They ___ to the cinema last night.", [("go", False), ("goes", False), ("went", True), ("gone", False)]),
    ("Comparatives", "A2", "This book is ___ than that one.", [("interesting", False), ("more interesting", True), ("most interesting", False), ("interestinger", False)]),
    ("Prepositions", "A2", "The keys are ___ the table.", [("on", True), ("in", False), ("at", False), ("by", False)]),
    ("Present Perfect", "B1", "I ___ never ___ sushi before.", [("have / eat", False), ("have / eaten", True), ("has / eaten", False), ("had / eat", False)]),
    ("Conditionals", "B1", "If it rains, we ___ stay home.", [("will", True), ("would", False), ("won't", False), ("had", False)]),
    ("Passive Voice", "B1", "The letter ___ yesterday.", [("was sent", True), ("sent", False), ("is sending", False), ("has send", False)]),
    ("Relative Clauses", "B2", "The man ___ called you is my uncle.", [("which", False), ("who", True), ("whom", False), ("whose", False)]),
    ("Modals", "B2", "You ___ have told me earlier!", [("should", True), ("can", False), ("may", False), ("must to", False)]),
    ("Reported Speech", "B2", "She said she ___ tired.", [("is", False), ("was", True), ("be", False), ("been", False)]),
    ("Inversion", "C1", "Never ___ I seen such a beautiful view.", [("did", False), ("have", True), ("had", False), ("do", False)]),
    ("Subjunctive", "C1", "It is essential that he ___ on time.", [("is", False), ("be", True), ("was", False), ("being", False)]),
    ("Collocations", "C1", "The company decided to ___ a new strategy.", [("make", False), ("do", False), ("adopt", True), ("take", False)]),
]

MATH_QUESTIONS = [
    ("Arifmetika", "Boshlang'ich", "12 + 15 = ?", [("25", False), ("27", True), ("26", False), ("28", False)]),
    ("Arifmetika", "Boshlang'ich", "9 x 6 = ?", [("54", True), ("56", False), ("52", False), ("48", False)]),
    ("Kasrlar", "Boshlang'ich", "1/2 + 1/4 = ?", [("2/6", False), ("3/4", True), ("1/6", False), ("2/4", False)]),
    ("Tenglamalar", "O'rta", "2x + 6 = 14. x = ?", [("3", False), ("4", True), ("5", False), ("6", False)]),
    ("Foizlar", "O'rta", "200 ning 15% qanchа?", [("20", False), ("30", True), ("25", False), ("35", False)]),
    ("Geometriya", "O'rta", "Tomoni 5 sm bo'lgan kvadrat perimetri?", [("15 sm", False), ("20 sm", True), ("25 sm", False), ("10 sm", False)]),
    ("Kvadrat tenglama", "Yuqori", "x^2 - 9 = 0 tenglamaning ildizlari?", [("x=3", False), ("x=±3", True), ("x=9", False), ("x=±9", False)]),
    ("Funksiyalar", "Yuqori", "f(x) = 2x+1 bo'lsa, f(3) = ?", [("6", False), ("7", True), ("5", False), ("8", False)]),
    ("Progressiya", "Yuqori", "2, 4, 8, 16, ... ketma-ketlikning keyingi hadi?", [("18", False), ("32", True), ("24", False), ("20", False)]),
]


class Command(BaseCommand):
    help = "TaraqqiyNET uchun demo ma'lumotlarni (hudud, fan, savol) yaratadi"

    def handle(self, *args, **options):
        for name in REGIONS:
            Region.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS(f"{len(REGIONS)} ta hudud tayyor"))

        english, _ = Subject.objects.get_or_create(code="english", defaults={"name": "Ingliz tili (IELTS/CEFR)"})
        math, _ = Subject.objects.get_or_create(code="math", defaults={"name": "Matematika"})

        level_map = {}
        for name, order, min_score in ENGLISH_LEVELS:
            lvl, _ = Level.objects.get_or_create(
                subject=english, order=order,
                defaults={"name": name, "min_score_percent": min_score},
            )
            level_map[("english", name)] = lvl
        for name, order, min_score in MATH_LEVELS:
            lvl, _ = Level.objects.get_or_create(
                subject=math, order=order,
                defaults={"name": name, "min_score_percent": min_score},
            )
            level_map[("math", name)] = lvl

        created = 0
        for topic_name, level_name, text, choices in ENGLISH_QUESTIONS:
            topic, _ = Topic.objects.get_or_create(subject=english, name=topic_name)
            if Question.objects.filter(topic=topic, text=text).exists():
                continue
            q = Question.objects.create(topic=topic, level=level_map[("english", level_name)], text=text)
            for ctext, is_correct in choices:
                Choice.objects.create(question=q, text=ctext, is_correct=is_correct)
            created += 1

        for topic_name, level_name, text, choices in MATH_QUESTIONS:
            topic, _ = Topic.objects.get_or_create(subject=math, name=topic_name)
            if Question.objects.filter(topic=topic, text=text).exists():
                continue
            q = Question.objects.create(topic=topic, level=level_map[("math", level_name)], text=text)
            for ctext, is_correct in choices:
                Choice.objects.create(question=q, text=ctext, is_correct=is_correct)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} ta yangi savol qo'shildi"))
        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor!"))
