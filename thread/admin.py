from django.contrib import admin
from .models import Answer, Question, Tag, Vote


class VoteInline(admin.TabularInline):
    model = Vote


class AnswerAdmin(admin.ModelAdmin):
    inlines = [VoteInline]
    list_display = ['content', 'question']


admin.site.register(Question)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tag)
