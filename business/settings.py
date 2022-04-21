class ContactType:
    phone = 'phone'
    email = 'email'
    website = 'website'
    facebook = 'facebook'
    instagram = 'instagram'
    whatsapp = 'whatsapp'
    telegram = 'telegram'
    address = 'address'

    @classmethod
    def choices(cls):
        return (
            (cls.phone, cls.phone),
            (cls.email, cls.email),
            (cls.website, cls.website),
            (cls.facebook, cls.facebook),
            (cls.instagram, cls.instagram),
            (cls.whatsapp, cls.whatsapp),
            (cls.telegram, cls.telegram),
            (cls.address, cls.address)
        )


class Week:
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'

    @classmethod
    def choices(cls):
        return (
            (cls.monday, 'пн'),
            (cls.tuesday, 'вт'),
            (cls.wednesday, 'ср'),
            (cls.thursday, 'чт'),
            (cls.friday, 'пт'),
            (cls.saturday, 'сб'),
            (cls.sunday, 'вс'),
        )


BANNER_UPLOAD_DIR = 'business/banners/'
DEFAULT_BRANCH_LATITUDE = '41.668549'
DEFAULT_BRANCH_LONGITUDE = '74.961125'
