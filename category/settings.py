ICON_UPLOAD_DIR = 'category/icons'

PRODUCT_MULTIPLE = 2


class ParameterType:
    SELECT = 'select'
    ENTER = 'enter'

    @classmethod
    def choices(cls):
        return (
            (cls.SELECT, cls.SELECT),
            (cls.ENTER, cls.ENTER)
        )
