from django.db import models

months = [
    ('january', 'january'),
    ('february', 'february'),
    ('march', 'march'),
    ('april', 'april'),
    ('may', 'may'),
    ('june', 'june'),
    ('july', 'july'),
    ('august', 'august'),
    ('september', 'september'),
    ('october', 'october'),
    ('november', 'november'),
    ('december', 'december')
]

# Create your models here.
class Crop(models.Model):
    id = models.AutoField(primary_key=True)
    name_eng = models.CharField(max_length=50, default='Crop')
    name_de = models.CharField(max_length=50, default='Crop')
    harvest_month = models.CharField(max_length=50, choices=months, default='january')
    harvest_interval = models.IntegerField(default=0)
    planting_month = models.CharField(max_length=50, choices=months, default='january')
    planting_interval = models.IntegerField(default=0)
    price_jan = models.FloatField(default=0)
    price_feb = models.FloatField(default=0)
    price_mar = models.FloatField(default=0)
    price_apr = models.FloatField(default=0)
    price_may = models.FloatField(default=0)
    price_jun = models.FloatField(default=0)
    price_jul = models.FloatField(default=0)
    price_aug = models.FloatField(default=0)
    price_sep = models.FloatField(default=0)
    price_oct = models.FloatField(default=0)
    price_nov = models.FloatField(default=0)
    price_dec = models.FloatField(default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name_eng

    def json(self):
        prices = {
            'january': self.price_jan,
            'february': self.price_feb,
            'march': self.price_mar,
            'april': self.price_apr,
            'may': self.price_may,
            'june': self.price_jun,
            'july': self.price_jul,
            'august': self.price_aug,
            'september': self.price_sep,
            'october': self.price_oct,
            'november': self.price_nov,
            'december': self.price_dec
        }

        best_selling_month = max(prices, key=prices.get)
        best_buying_month = min(prices, key=prices.get)

        start_harvest_month = list(prices.keys()).index(self.harvest_month)
        start_planting_month = list(prices.keys()).index(self.planting_month)
        end_harvest_month = (start_harvest_month + self.harvest_interval) % 12
        end_planting_month = (start_planting_month + self.planting_interval) % 12

        return {
            'name': {
                'de': self.name_de,
                'en': self.name_eng,
                'yoda': self.name_eng
            },
            'harvest_month': {
                'start': list(prices.keys())[start_harvest_month],
                'end': list(prices.keys())[end_harvest_month] if end_harvest_month < 11 else 'end_of_december'
            },
            'planting_month': {
                'start': list(prices.keys())[start_planting_month],
                'end': list(prices.keys())[end_planting_month] if end_planting_month > 0 else 'end_of_december'
            },
            'prices': [
                self.price_jan,
                self.price_feb,
                self.price_mar,
                self.price_apr,
                self.price_may,
                self.price_jun,
                self.price_jul,
                self.price_aug,
                self.price_sep,
                self.price_oct,
                self.price_nov,
                self.price_dec,
                self.price_dec
            ],
            'best_selling_month': {
                'month': best_selling_month,
                'price': prices[best_selling_month]
            },
            'best_buying_month': {
                'month': best_buying_month,
                'price': prices[best_buying_month]
            }
        }


class Commodity(models.Model):
    id = models.AutoField(primary_key=True)
    name_eng = models.CharField(max_length=50, default='Crop')
    name_de = models.CharField(max_length=50, default='Crop')
    price_jan = models.FloatField(default=0)
    price_feb = models.FloatField(default=0)
    price_mar = models.FloatField(default=0)
    price_apr = models.FloatField(default=0)
    price_may = models.FloatField(default=0)
    price_jun = models.FloatField(default=0)
    price_jul = models.FloatField(default=0)
    price_aug = models.FloatField(default=0)
    price_sep = models.FloatField(default=0)
    price_oct = models.FloatField(default=0)
    price_nov = models.FloatField(default=0)
    price_dec = models.FloatField(default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name_eng

    def json(self):
        prices = {
            'january': self.price_jan,
            'february': self.price_feb,
            'march': self.price_mar,
            'april': self.price_apr,
            'may': self.price_may,
            'june': self.price_jun,
            'july': self.price_jul,
            'august': self.price_aug,
            'september': self.price_sep,
            'october': self.price_oct,
            'november': self.price_nov,
            'december': self.price_dec
        }

        best_selling_month = max(prices, key=prices.get)
        best_buying_month = min(prices, key=prices.get)

        return {
            'name': {
                'de': self.name_de,
                'en': self.name_eng,
                'yoda': self.name_eng
            },
            'prices': [
                self.price_jan,
                self.price_feb,
                self.price_mar,
                self.price_apr,
                self.price_may,
                self.price_jun,
                self.price_jul,
                self.price_aug,
                self.price_sep,
                self.price_oct,
                self.price_nov,
                self.price_dec,
                self.price_dec
            ],
            'best_selling_month': {
                'month': best_selling_month,
                'price': prices[best_selling_month]
            },
            'best_buying_month': {
                'month': best_buying_month,
                'price': prices[best_buying_month]
            }
        }
