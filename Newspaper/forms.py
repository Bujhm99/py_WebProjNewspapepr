from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from Newspaper.models import Article


class RedactorCreationForm(UserCreationForm):
    years_of_experience = forms.IntegerField(
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (UserCreationForm.Meta.fields
                  + ("years_of_experience", "first_name", "last_name",))


class RedactorUpdateForm(forms.ModelForm):

    years_of_experience = forms.IntegerField(
        required=True,

    )

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "years_of_experience",)


class ArticleForm(forms.ModelForm):
    publishers = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    published_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "placeholder": "YYYY-MM-DD"
        })
    )

    class Meta:
        model = Article
        fields = "__all__"


class ArticleSearchForm(forms.Form):
    relevant_search = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Relevant_search"})
    )


class TopicSearchForm(forms.Form):
    topic_name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by name"})
    )


class RedactorSearchForm(forms.Form):
    redactor_name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search by redactor"})
    )
