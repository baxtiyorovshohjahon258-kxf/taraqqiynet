from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Universal foydalanuvchi: rol orqali o'quvchi / markaz / admin farqlanadi."""

    class Role(models.TextChoices):
        STUDENT = "student", "O'quvchi"
        CENTER = "center", "Markaz"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    region = models.ForeignKey(
        "Region", null=True, blank=True, on_delete=models.SET_NULL, related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Center(models.Model):
    """Til markazi profili. owner — role=center bo'lgan User."""

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="center_profile")
    name = models.CharField(max_length=150)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="centers")
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Masalan: Ingliz tili (IELTS/CEFR), Matematika. Keyinchalik SAT ham shu yerga qo'shiladi."""

    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=30, unique=True)  # e.g. "english", "math", "sat"

    def __str__(self):
        return self.name


class Level(models.Model):
    """Fan ichidagi darajalar: A1-C1 (ingliz tili) yoki Boshlang'ich/O'rta/Yuqori (matematika)."""

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="levels")
    name = models.CharField(max_length=30)  # "A1", "B2", "Boshlang'ich" ...
    order = models.PositiveSmallIntegerField()  # saralash uchun: past -> yuqori
    min_score_percent = models.PositiveSmallIntegerField(
        help_text="Ushbu darajaga chiqish uchun kerakli minimal foiz"
    )

    class Meta:
        ordering = ["subject", "order"]
        unique_together = ("subject", "order")

    def __str__(self):
        return f"{self.subject.code}:{self.name}"


class Topic(models.Model):
    """127 grammatika mavzusi va matematika bo'limlari shu yerga kiradi."""

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["subject", "name"]

    def __str__(self):
        return self.name


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:40]


class TestAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attempts")
    center = models.ForeignKey(
        Center, null=True, blank=True, on_delete=models.SET_NULL, related_name="attempts"
    )
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score_percent = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    result_level = models.ForeignKey(
        Level, null=True, blank=True, on_delete=models.SET_NULL, related_name="attempts"
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} — {self.subject.name} — {self.score_percent}%"


class Answer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, null=True, on_delete=models.SET_NULL)
    is_correct = models.BooleanField(default=False)
