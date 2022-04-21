
class LocationType:
    ru = 'ru'
    ky = 'ky'
    lat = '41.668549'
    lng = '74.961125'

    COUNTRY = 'country'
    REGION = 'region'
    CITY = 'city'
    DISTRICT = 'district'
    PGT = 'pgt'
    AIMAK = 'aimak'

    NOTATIONS_RU = {
        COUNTRY: 'Страна',
        REGION: 'Область',
        CITY: 'Город',
        DISTRICT: 'Район',
        PGT: 'ПГТ',
        AIMAK: 'Айылный аймак'
    }
    NOTATIONS_KY = {
        COUNTRY: 'Өлкө',
        REGION: 'Облус',
        CITY: 'Шаар',
        DISTRICT: 'Район',
        PGT: 'ШТК',
        AIMAK: 'Айыл аймак'
    }

    NOTATIONS = {
        COUNTRY: {
            ru: NOTATIONS_RU[COUNTRY],
            ky: NOTATIONS_KY[COUNTRY]
        },
        REGION: {
            ru: NOTATIONS_RU[REGION],
            ky: NOTATIONS_KY[REGION]
        },
        CITY: {
            ru: NOTATIONS_RU[CITY],
            ky: NOTATIONS_KY[CITY]
        },
        DISTRICT: {
            ru: NOTATIONS_RU[DISTRICT],
            ky: NOTATIONS_KY[DISTRICT]
        },
        PGT: {
            ru: NOTATIONS_RU[PGT],
            ky: NOTATIONS_KY[PGT]
        },
        AIMAK: {
            ru: NOTATIONS_RU[AIMAK],
            ky: NOTATIONS_KY[AIMAK]
        }
    }

    REVERSE_NOTATIONS_RU = {
        NOTATIONS_RU[COUNTRY]: COUNTRY,
        NOTATIONS_RU[REGION]: REGION,
        NOTATIONS_RU[CITY]: CITY,
        NOTATIONS_RU[DISTRICT]: DISTRICT,
        NOTATIONS_RU[PGT]: PGT,
        NOTATIONS_RU[AIMAK]: AIMAK
    }

    @classmethod
    def choices(cls):
        return (
            (cls.COUNTRY, cls.NOTATIONS[cls.COUNTRY][cls.ru]),
            (cls.REGION, cls.NOTATIONS[cls.REGION][cls.ru]),
            (cls.CITY, cls.NOTATIONS[cls.CITY][cls.ru]),
            (cls.DISTRICT, cls.NOTATIONS[cls.DISTRICT][cls.ru]),
            (cls.PGT, cls.NOTATIONS[cls.PGT][cls.ru]),
            (cls.AIMAK, cls.NOTATIONS_RU[cls.AIMAK])
        )

    @classmethod
    def get_notation(cls, field, language):
        if field is None:
            return None
        return cls.NOTATIONS[field][language]
