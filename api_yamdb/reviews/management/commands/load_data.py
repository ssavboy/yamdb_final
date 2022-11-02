from django.core.management import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)
from users.models import User

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the title data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    """Загрузка данных в модели."""

    help = "Loads data from static/data/titles.csv"

    def handle(self, *args, **options):
        if (
            Category.objects.exists()
            or Genre.objects.exists()
            or Title.objects.exists()
            or Review.objects.exists()
            or Comment.objects.exists()
            or User.objects.exists()
        ):
            return (ALREDY_LOADED_ERROR_MESSAGE)

        print("Loading categories data")
        with open('static/data/category.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:]
            for row in input_file_without_header:
                category = Category(*row.split(','))
                category.save()

        print("Loading genres data")
        with open('static/data/genre.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:]
            for row in input_file_without_header:
                genre = Genre(*row.split(','))
                genre.save()

        print("Loading users data")
        with open('static/data/users.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:]
            for row in input_file_without_header:
                (
                    id,
                    username,
                    email,
                    role,
                    bio,
                    first_name,
                    last_name
                ) = row.split(',')
                user = User(
                    id=id,
                    username=username,
                    email=email,
                    role=role,
                    bio=bio,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()

        print("Loading titles data")
        with open('static/data/titles.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:]
            for row in input_file_without_header:
                id, name, year, id_category = row.split(',')
                category = Category.objects.get(pk=id_category)
                title = Title(
                    id=id,
                    name=name,
                    year=year,
                    category=category
                )
                title.save()

        print("Loading reviews data")
        with open('static/data/review.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:5]
            for row in input_file_without_header:
                if '"' in row:
                    opening_quotation = row.index('"')
                    closing_quotation = len(row) - row[::-1].index('"')
                    id, id_title = row[:opening_quotation - 1].split(',')
                    text = row[opening_quotation + 1: closing_quotation - 1]
                    (
                        id_author,
                        score,
                        pub_date) = row[closing_quotation + 1:].split(',')
                    review = Review(
                        id=id,
                        title=Title.objects.get(pk=id_title),
                        text=text,
                        author=User.objects.get(pk=id_author),
                        score=score,
                        pub_date=pub_date
                    )
                    review.save()

        print("Loading comments data")
        with open('static/data/comments.csv', encoding='utf8') as input_file:
            input_file_without_header = input_file.read().splitlines[1:5]
            for row in input_file_without_header:
                if '"' in row:
                    opening_quotation = row.index('"')
                    closing_quotation = len(row) - row[::-1].index('"')
                    id, id_review = row[:opening_quotation - 1].split(',')
                    text = row[opening_quotation + 1: closing_quotation - 1]
                    (
                        id_author,
                        pub_date) = row[closing_quotation + 1:].split(',')
                    comment = Comment(
                        id=id,
                        review=Review.objects.get(pk=id_review),
                        text=text,
                        author=User.objects.get(pk=id_author),
                        pub_date=pub_date
                    )
                    comment.save()
