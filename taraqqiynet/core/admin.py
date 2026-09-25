from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User, Region, Center, Subject, Level, Topic, Question, Choice, TestAttempt, Answer,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "role", "region", "phone", "is_staff")
    list_filter = ("role", "region")
    fieldsets = UserAdmin.fieldsets + (
        ("TaraqqiyNET", {"fields": ("role", "phone", "region")}),
    )


admin.site.register(Region)
admin.site.register(Center)
admin.site.register(Subject)
admin.site.register(Level)
admin.site.register(Topic)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "topic", "level")
    list_filter = ("topic__subject", "level")
    inlines = [ChoiceInline]


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "region", "score_percent", "result_level", "started_at")
    list_filter = ("subject", "region", "result_level")


admin.site.register(Answer)
