from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook
from location.models import Location
from location.settings import LocationType


class Command(BaseCommand):
    help = 'import category from mind master xlsx format'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
    raw_data = None
    row_max = None
    col_max = None
    i = 1

    def parse_title(self, title):
        title = title.split(',')
        if len(title) == 2:
            return title[0].strip(), title[1].strip(), None
        if len(title) == 3:
            resp = []
            for name in title:
                name = name.strip()
                if name == '#':
                    name = None
                resp.append(name)
            return resp

    def parse_coordinates(self, coord):
        coord = coord.split(',')
        return coord[0].strip(), coord[1].strip()

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
            if col + 1 <= self.col_max:
                result[key] = self.parse(split['start'], split['end'], col +1)
            else:
                result[key] = {}
        return result

    def save(self, data, parent=None):
        if parent is None:
            parent, exist = Location.objects.get_or_create(title_ky='/', title_ru='/')
            parent = parent.id
        for titles, children in data.items():
            title_ru, title_ky, coordinates = titles.split('/')
            title_ru, type_ru, request_ru = self.parse_title(title_ru)
            title_ky, type_ky, request_ky = self.parse_title(title_ky)
            lat, lng = self.parse_coordinates(coordinates)
            type = LocationType.REVERSE_NOTATIONS_RU[type_ru]
            location, created = Location.objects.get_or_create(type=type, title_ru=title_ru,
                                                               title_ky=title_ky, request_ru=request_ru,
                                                               request_ky=request_ky, parent_id=parent, lat=lat, lng=lng)
            if created:
                print('creating new location', title_ru)
            if children:
                self.save(children, location.id)

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

        data = self.parse(0, self.row_max, 0)
        self.save(data)
        # print(json.dumps(data, indent=2))
