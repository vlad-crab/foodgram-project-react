from rest_framework.pagination import PageNumberPagination as DRF_Pagination


class PageNumberPagination(DRF_Pagination):
    page_size_query_param = 'limit'
