from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Пагинация для привычек.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 5  # По ТЗ 5 привычек на страницу
