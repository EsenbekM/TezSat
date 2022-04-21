from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook
from category.models import Category
import json


class Command(BaseCommand):
    help = 'import category from mind master xlsx format'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
    raw_data = None
    row_max = None
    col_max = None

    def parse(self, row_start, row_end, col):
        splits = {}
        result = {}
        prev = None
        for row in range(row_start, row_end + 1):
            if self.raw_data[row][col] is not None:
                splits[self.raw_data[row][col]] = {
                    'start': row
                }
                if prev:
                    splits[prev]['end'] = row
                prev = self.raw_data[row][col]

        if prev in splits:
            splits[prev]['end'] = row_end
        for key, split in splits.items():
            ru, ky = key.split(',')
            ru = ru.replace('/', ',').strip()
            ky = ky.replace('/', ',').strip()
            if ru.lower() == 'все' or ru.lower() == 'все объявления категории':
                continue
            if col + 1 <= self.col_max:
                result[(ru, ky)] = self.parse(split['start'], split['end'], col +1)
            else:
                result[(ru, ky)] = {}
        return result

    def save_category(self, data, parent=None):
        for title, children in data.items():
            ru, ky = title
            category, created = Category.objects.get_or_create(title_ru=ru, title_ky=ky, parent_id=parent)
            if created:
                print('creating new category', ru)
            if children:
                self.save_category(children, category.id)

    def handle(self, *args, **options):
        wb = load_workbook(options['file_path'])
        ws = wb.active

        self.raw_data = []
        for i, row in enumerate(ws):
            if i == 0:
                continue
            values = []
            for j, cell in enumerate(row):
                values.append(cell.value)
            self.col_max = len(row) - 1
            self.raw_data.append(values)
        self.row_max = len(self.raw_data) - 1

        data = self.parse(0, self.row_max, 1)
        # print(data)
        self.save_category(data)
        # with open('category.json', 'w+', encoding='utf-8') as f:
        #     json.dump(data, f, indent=2)
        # print(json.dumps(data, indent=2))
