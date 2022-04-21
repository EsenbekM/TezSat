
from location.models import Location
from location.settings import LocationType


def _get_parent_region(location: object, start_location=None) -> None:
    if location.parent:
        if location.parent.type == LocationType.REGION:
            start_location.region = location.parent.title_ru
            start_location.save()
        else:
            _get_parent_region(location.parent, start_location)

def get_region_in_location():
    locations = Location.objects.all()
    for i in locations:
        _get_parent_region(i, i)
    return None