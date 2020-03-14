# Generated by Django 2.2 on 2019-04-08 11:49

from django.db import migrations
from django.conf import settings
import os.path
import csv
from django.core.files import File
from django.utils.text import slugify
from django.contrib.auth.models import User

def load_decks_data(apps, schema_editor):
    """
    Read a CSV file full of decks and insert them into the database
    """
    Deck = apps.get_model('core', 'Deck')
    Category = apps.get_model('core', 'Category')
    User = apps.get_model('auth', 'User')

    datapath = os.path.join(settings.BASE_DIR, 'initial_data')
        # data to be read is stored in the 'initial_data' directory
    datafile = os.path.join(datapath, 'decks.csv')
        # data file to be read is named 'decks.csv'
    Deck.objects.all().delete()
        # delete all existing 'Deck' objects in the database
    Category.objects.all().delete()
        # delete all existing 'Category' objects in the database

    with open(datafile) as file: 
        reader = csv.DictReader(file)
        for row in reader:
            deck_title = row['title']
            if Deck.objects.filter(title=deck_title).count():
                continue

            if User.objects.filter(username=row['creator']).count():
                creator = User.objects.filter(username=row['creator'])[0]
            else:
                user, _ = User.objects.get_or_create(username=row['creator'])
                user.save()
                creator = user

            if not row['categories']:
                categories, _ = Category.objects.get_or_create(name='No Category', slug="no-category")
                categories = [categories]
            else:
                categories = []
                category_list = [category.strip() for category in row['categories'].split('/')]
                for category in category_list:
                    new_category, _ = Category.objects.get_or_create(name=category, slug=slugify(category))
                    categories.append(new_category)

            deck = Deck.objects.create(
                title=row['title'],
                creator=creator,
            )

            for category in categories:
                deck.categories.add(category)
            deck.save()

            if row['slug'] == '':
                base_slug = slugify(row['title'])
                slug = base_slug
                n = 0
                while Deck.objects.filter(slug=slug).count():
                    n += 1
                    slug = base_slug + "-" + str(n)
                deck.slug = slug[:50]

            deck.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20190408_1145'),
    ]

    operations = [
        migrations.RunPython(load_decks_data)
    ]