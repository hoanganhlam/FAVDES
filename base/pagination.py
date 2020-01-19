#!/usr/bin/python
# -*- coding: utf8 -*-


import json
from rest_framework import pagination
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def __init__(self):
        pass

    def paginate_queryset(self, queryset, request, view=None):
        url_params = request.query_params
        if 'flt' in url_params:
            try:
                filter_arr = json.loads(url_params.get('flt') or '')
                if 'page_size' in filter_arr:
                    self.page_size = int(filter_arr.get('page_size'))
            except Exception as ex:
                print(ex)
                filter_arr = None

        return super(Pagination, self).paginate_queryset(queryset=queryset, request=request, view=view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'results': data
        })
