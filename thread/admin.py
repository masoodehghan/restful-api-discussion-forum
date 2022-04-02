from django.contrib import admin
from .models import Answer, Question, Tag

class QuestionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Tag, TagAdmin)