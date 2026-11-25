"""SEC005 in Django: ? placeholders do not apply, so the agent retries with %s."""
from django.db import connection


def book_detail(request):
    book_id = request.GET["id"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT title FROM books WHERE id = " + book_id)
        return cursor.fetchone()
