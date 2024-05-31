import random

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic


from Newspaper.forms import (ArticleForm, ArticleSearchForm,
                             RedactorCreationForm,
                             RedactorUpdateForm,
                             TopicSearchForm,
                             RedactorSearchForm, )
from Newspaper.models import Topic, Article
from Newspaper.utils import sort_queryset

User_model = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    num_articles = Article.objects.count()
    num_redactors = User_model.objects.count()
    num_topics = Topic.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {"num_articles": num_articles,
               "num_redactors": num_redactors,
               "num_topics": num_topics,
               "num_visits": request.session["num_visits"]}
    return render(
        request, template_name="newspaper/index.html", context=context
    )


class RedactorsListView(LoginRequiredMixin, generic.ListView):
    model = User_model
    paginate_by = 5
    template_name = "newspaper/redactors_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        redactor_name = self.request.GET.get("redactor_name", "")
        context["search_form"] = RedactorSearchForm(
            initial={"redactor_name": redactor_name})
        return context

    def get_queryset(self):
        self.queryset = User_model.objects.all()
        redactor_search = self.request.GET.get("redactor_name")
        if redactor_search:
            return self.queryset.filter(
                Q(first_name__icontains=redactor_search)
                | Q(last_name__icontains=redactor_search)
            )
        return self.queryset


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = User_model
    template_name = "newspaper/redactor_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles_data = Article.objects.select_related("topic").filter(
            publishers=context["redactor"]
        )
        context["articles_data"] = articles_data
        return context


class RedactorCreateView(LoginRequiredMixin, generic.CreateView):
    model = User_model
    form_class = RedactorCreationForm
    template_name = "newspaper/redactor_form.html"


class RedactorUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User_model
    form_class = RedactorUpdateForm
    template_name = "newspaper/redactor_form.html"


class RedactorDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User_model
    success_url = reverse_lazy("newspaper:redactors-list")
    template_name = "newspaper/redactor_confirm_delete.html"


class ArticlesListView(LoginRequiredMixin, generic.ListView):
    model = Article
    paginate_by = 5
    template_name = "newspaper/articles_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        relevant_search = self.request.GET.get("relevant_search", "")
        context["rand_num"] = self.request.session["rand_num"]
        context["search_form"] = ArticleSearchForm(
            initial={"relevant_search": relevant_search}
        )
        return context

    def get_queryset(self):
        self.queryset = Article.objects.select_related("topic")
        form = ArticleSearchForm(self.request.GET)

        if form.is_valid():

            search_query = form.cleaned_data["relevant_search"]
            if search_query:
                self.queryset = sort_queryset(self.queryset, search_query)
            rand_num = str(random.randint(1000, 9999))
            self.request.session["rand_num"] = rand_num
            self.request.session[
                "pass_quer" + rand_num
            ] = serializers.serialize("json", self.queryset)
        return self.queryset


class ArticleDetailView(LoginRequiredMixin, generic.DetailView):
    model = Article
    queryset = Article.objects.select_related("topic")
    template_name = "newspaper/article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rand_num = str(self.kwargs["rand_num"])
        redactors_list = User_model.objects.filter(articles=context["article"])
        sort_order = serializers.deserialize(
            "json", self.request.session["pass_quer" + rand_num]
        )

        sort_order = list(sort_order)
        for i, obj in enumerate(sort_order):
            if obj.object.pk == self.kwargs["pk"]:
                break
        prev_article = sort_order[i - 1].object
        if i != len(sort_order) - 1:
            next_article = sort_order[i + 1].object
        else:
            next_article = sort_order[0].object

        context["rand_num"] = rand_num
        context["redactors_list"] = redactors_list
        context["prev_article"] = prev_article
        context["next_article"] = next_article
        return context


class ArticleCreateView(LoginRequiredMixin, generic.CreateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("newspaper:articles-list")
    template_name = "newspaper/article_form.html"


class ArticleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Article
    fields = "__all__"
    success_url = reverse_lazy("newspaper:articles-list")
    template_name = "newspaper/article_form.html"


class ArticleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Article
    success_url = reverse_lazy("newspaper:articles-list")
    template_name = "newspaper/article_confirm_delete.html"


@login_required
def toggle_assign_to_article(request, rand_num, pk) -> HttpResponseRedirect:
    redactor = User_model.objects.get(id=request.user.id)
    if Article.objects.get(id=pk) in redactor.articles.all():
        redactor.articles.remove(pk)
    else:
        redactor.articles.add(pk)
    return HttpResponseRedirect(
        reverse_lazy("newspaper:article-detail", args=[rand_num, pk])
    )


class TopicsListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    paginate_by = 5
    template_name = "newspaper/topics_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_name = self.request.GET.get("topic_name", "")
        context["search_form"] = TopicSearchForm(
            initial={"topic_name": topic_name}
        )
        return context

    def get_queryset(self):
        self.queryset = Topic.objects.all()
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(
                name__icontains=form.cleaned_data["topic_name"],
            )
        return self.queryset


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper:topics-list")
    template_name = "newspaper/topic_form.html"


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper:topics-list")
    template_name = "newspaper/topic_form.html"


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    success_url = reverse_lazy("newspaper:topics-list")
    template_name = "newspaper/topic_confirm_delete.html"
