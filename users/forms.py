from django import forms
from django.db import transaction
from django.shortcuts import _get_queryset

from .models import User, Teacher, Student
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Subject, Batch, User, Teacher


class TeacherRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True,
                                              widget=forms.CheckboxSelectMultiple)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'subjects', 'batches']

    def clean_first_name(self):
        if self.cleaned_data["first_name"].strip() == '':
            raise ValidationError("First name is required.")
        return self.cleaned_data["first_name"].capitalize()

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise ValidationError("Last name is required.")
        return self.cleaned_data["last_name"].capitalize()

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
            teacher = Teacher.objects.create(teacher=user)
            teacher.batches.set(self.cleaned_data.get('batches'))
            teacher.subjects.set(self.cleaned_data.get('subjects'))
        return user


class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True, )
    roll_no = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'roll_no', 'batch']

    def clean_first_name(self):
        if self.cleaned_data["first_name"].strip() == '':
            raise ValidationError("First name is required.")
        return self.cleaned_data["first_name"].capitalize()

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise ValidationError("Last name is required.")
        return self.cleaned_data["last_name"].capitalize()

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = False
        if commit:
            user.save()
            student = Student.objects.create(student=user, batch=self.cleaned_data.get('batch'),
                                             roll_no=self.cleaned_data.get('roll_no'))
        return user


class TeacherUpdateForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True,
                                              widget=forms.CheckboxSelectMultiple)
    batches = forms.ModelMultipleChoiceField(queryset=Batch.objects.all(), required=True,
                                             widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Teacher
        exclude = ['teacher']

    def __init__(self, *args, **kwargs):
        super(TeacherUpdateForm, self).__init__(*args, **kwargs)
        self.fields["subjects"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["subjects"].help_text = ""
        self.fields["subjects"].queryset = Subject.objects.all()
        self.fields["batches"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["batches"].help_text = ""
        self.fields["batches"].queryset = Batch.objects.filter()


class StudentUpdateForm(forms.ModelForm):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=True)
    roll_no = forms.IntegerField(required=True)

    class Meta:
        model = Student
        exclude = ['student']
