from django.contrib import admin

# Register your models here.
from .models import PBLQuestion, NumQuestion, PBLChoice, NumChoice


class PBLChoiceInline(admin.TabularInline):
    model = PBLChoice
    extra = 3


class PBLQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']})
    ]
    inlines = [PBLChoiceInline]
    search_fields = ['question_text']


class NumChoiceInline(admin.TabularInline):
    model = NumChoice
    extra = 9


class NumQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']})
    ]
    inlines = [NumChoiceInline]
    search_fields = ['question_text']


admin.site.register(PBLQuestion, PBLQuestionAdmin)
admin.site.register(NumQuestion, NumQuestionAdmin)
