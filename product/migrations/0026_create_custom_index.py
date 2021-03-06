# Generated by Django 3.1.3 on 2021-05-05 09:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('product', '0025_keyword'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE product ADD COLUMN fulltext_field tsvector GENERATED ALWAYS AS (setweight(to_tsvector('russian', title), 'A') || setweight(to_tsvector('russian', description), 'B')) STORED;",
        ),
        migrations.RunSQL(
            "CREATE INDEX fulltext_idx ON product USING GIN (fulltext_field);"
        )
    ]
