import re

from django.db.models import Value, IntegerField, Case, When, F, Q
from django.db.models.functions import Length, Replace, Lower

from Newspaper.config import (PRICE_FOR_TOPIC,
                              PRICE_FOR_TITLE,
                              PRICE_FOR_CONTENT)


def sort_queryset(queryset, search_val):
    search_scheme = search_split(search_val)
    queryset = queryset.annotate(relevance=Value(0))
    for and_part in search_scheme.values():
        queryset = queryset.annotate(exept=Value(-1))
        for exept_part in and_part.get("exept", ""):
            queryset = queryset.annotate(
                exept=Case(When(exept=0, then=Value(0)),
                           When(content__icontains=exept_part,
                                then=Value(1)),
                           When(title__icontains=exept_part,
                                then=Value(1)),
                           When(topic__name__icontains=exept_part,
                                then=Value(1)),
                           When(exept=1, then=Value(0)),
                           default=Value(0))
            )

        queryset = queryset.annotate(max_or=Value(0))
        for or_part in and_part.get("or_part", ""):
            queryset = queryset.annotate(
                count_content=(
                    Length("content")
                    - Length(Replace(
                                  Lower("content"),
                                  Value(or_part.lower()),
                                  output_field=IntegerField()
                             ))
                ) / len(or_part)
            )
            queryset = queryset.annotate(
                max_or=F("max_or") + Case(
                    When(topic__name__icontains=or_part,
                         title__icontains=or_part,
                         then=Value(PRICE_FOR_TOPIC + PRICE_FOR_TITLE)),
                    When(topic__name__icontains=or_part,
                         then=Value(PRICE_FOR_TOPIC)),
                    When(title__icontains=or_part,
                         then=Value(PRICE_FOR_TITLE)),
                    default=Value(0),
                    output_field=IntegerField()
                ) + F("count_content") * PRICE_FOR_CONTENT)
        queryset = queryset.filter(Q(exept=0) | Q(max_or__gt=0))
        queryset = queryset.annotate(
            relevance=F("relevance") + F("max_or")
        ).order_by("-relevance")

    return queryset


def search_split(search_val: str) -> dict:
    search_scheme = {}
    for and_part in search_val.split("."):
        if and_part.count("-") == 0:
            search_scheme[and_part] = {"or_part": and_part.split(",")}
        else:
            search_scheme[and_part] = {"or_part": [], "exept": []}
            for or_part in re.split(",|-", and_part):
                if or_part:
                    pos_in_str = and_part.find(or_part)
                    if pos_in_str == 0 or and_part[pos_in_str - 1] == ",":
                        search_scheme[and_part]["or_part"].append(or_part)
                    else:
                        search_scheme[and_part]["exept"].append(or_part)

    return search_scheme
