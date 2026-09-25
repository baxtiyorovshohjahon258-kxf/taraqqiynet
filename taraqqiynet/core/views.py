import random

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .forms import StudentSignUpForm, CenterSignUpForm
from .models import (
    User, Subject, Level, Question, TestAttempt, Answer, Center, Region,
)

QUESTIONS_PER_TEST = 10


class TaraqqiyLoginView(LoginView):
    """Programmer.uz uslubidagi login sahifasi. Muvaffaqiyatli kirgach,
    foydalanuvchi 'variant tanlash' (dashboard) sahifasiga yo'naltiriladi."""

    template_name = "core/login.html"
    redirect_authenticated_user = True


def register_choice(request):
    """Ro'yxatdan o'tishdan oldin: O'quvchi sifatidami yoki Markaz sifatidami?"""
    return render(request, "core/register_choice.html")


def student_signup(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect("choose_dashboard")
    else:
        form = StudentSignUpForm()
    return render(request, "core/signup.html", {"form": form, "role_label": "O'quvchi"})


def center_signup(request):
    if request.method == "POST":
        form = CenterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Markaz muvaffaqiyatli ro'yxatdan o'tdi!")
            return redirect("choose_dashboard")
    else:
        form = CenterSignUpForm()
    return render(request, "core/signup.html", {"form": form, "role_label": "Markaz"})


@login_required
def choose_dashboard(request):
    """Login tasdiqlangandan keyin chiqadigan 'variantlar' sahifasi.
    Foydalanuvchi faqat o'z roliga mos bo'limga kira oladi, qolganlari ko'rinadi-yu
    lekin bosilmaydi (kulrang holatda)."""
    return render(request, "core/choose_dashboard.html", {"role": request.user.role})


def _require_role(user, role):
    return user.is_authenticated and (user.role == role or user.is_superuser)


@login_required
def student_dashboard(request):
    if not _require_role(request.user, User.Role.STUDENT):
        messages.error(request, "Bu bo'lim faqat o'quvchilar uchun.")
        return redirect("choose_dashboard")
    subjects = Subject.objects.all()
    past_attempts = TestAttempt.objects.filter(student=request.user, finished_at__isnull=False)[:10]
    return render(
        request,
        "core/student_dashboard.html",
        {"subjects": subjects, "past_attempts": past_attempts},
    )


@login_required
def start_test(request, subject_code):
    if not _require_role(request.user, User.Role.STUDENT):
        return redirect("choose_dashboard")
    subject = get_object_or_404(Subject, code=subject_code)
    all_questions = list(Question.objects.filter(topic__subject=subject).select_related("level"))
    if not all_questions:
        messages.warning(request, "Bu fan uchun hozircha savollar mavjud emas.")
        return redirect("student_dashboard")

    sample_size = min(QUESTIONS_PER_TEST, len(all_questions))
    questions = random.sample(all_questions, sample_size)

    attempt = TestAttempt.objects.create(
        student=request.user,
        subject=subject,
        region=request.user.region,
    )
    request.session[f"test_{attempt.id}_question_ids"] = [q.id for q in questions]
    return render(
        request,
        "core/take_test.html",
        {"subject": subject, "questions": questions, "attempt": attempt},
    )


@login_required
def submit_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    question_ids = request.session.get(f"test_{attempt.id}_question_ids", [])
    questions = Question.objects.filter(id__in=question_ids).prefetch_related("choices")

    correct_count = 0
    for question in questions:
        selected_id = request.POST.get(f"question_{question.id}")
        selected_choice = None
        is_correct = False
        if selected_id:
            selected_choice = question.choices.filter(id=selected_id).first()
            is_correct = bool(selected_choice and selected_choice.is_correct)
        if is_correct:
            correct_count += 1
        Answer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct,
        )

    total = questions.count() or 1
    score_percent = round((correct_count / total) * 100)

    result_level = (
        Level.objects.filter(subject=attempt.subject, min_score_percent__lte=score_percent)
        .order_by("-order")
        .first()
    )

    attempt.finished_at = timezone.now()
    attempt.score_percent = score_percent
    attempt.result_level = result_level
    attempt.save()

    return redirect("test_result", attempt_id=attempt.id)


@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    centers = []
    if attempt.region:
        centers = Center.objects.filter(region=attempt.region)
    return render(request, "core/test_result.html", {"attempt": attempt, "centers": centers})


@login_required
def center_dashboard(request):
    if not _require_role(request.user, User.Role.CENTER):
        messages.error(request, "Bu bo'lim faqat markazlar uchun.")
        return redirect("choose_dashboard")
    center = getattr(request.user, "center_profile", None)
    attempts = []
    stats = {}
    if center:
        attempts = TestAttempt.objects.filter(
            region=center.region, finished_at__isnull=False
        ).select_related("student", "subject", "result_level")[:50]
        stats = (
            TestAttempt.objects.filter(region=center.region, finished_at__isnull=False)
            .values("result_level__name")
            .annotate(count=Count("id"))
            .order_by("result_level__name")
        )
    return render(
        request,
        "core/center_dashboard.html",
        {"center": center, "attempts": attempts, "stats": stats},
    )


@login_required
def admin_dashboard(request):
    if not _require_role(request.user, User.Role.ADMIN):
        messages.error(request, "Bu bo'lim faqat admin uchun.")
        return redirect("choose_dashboard")

    region_stats = (
        TestAttempt.objects.filter(finished_at__isnull=False)
        .values("region__name")
        .annotate(avg_score=Avg("score_percent"), attempts=Count("id"))
        .order_by("avg_score")
    )
    subject_stats = (
        TestAttempt.objects.filter(finished_at__isnull=False)
        .values("subject__name")
        .annotate(avg_score=Avg("score_percent"), attempts=Count("id"))
    )
    totals = {
        "students": User.objects.filter(role=User.Role.STUDENT).count(),
        "centers": Center.objects.count(),
        "regions": Region.objects.count(),
        "attempts": TestAttempt.objects.filter(finished_at__isnull=False).count(),
    }
    return render(
        request,
        "core/admin_dashboard.html",
        {"region_stats": region_stats, "subject_stats": subject_stats, "totals": totals},
    )
