from django.db import models

class Laptop(models.Model):
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    screen_size = models.FloatField()
    screen = models.CharField(max_length=255)
    cpu = models.CharField(max_length=255)
    ram_gb = models.IntegerField()
    storage_original = models.CharField(max_length=100)
    gpu = models.CharField(max_length=255)
    os = models.CharField(max_length=100)
    weight_kg = models.FloatField()
    price_eur = models.FloatField()
    price_idr = models.FloatField()
    storage_gb = models.IntegerField()
    storage_type = models.CharField(max_length=50)
    cpu_brand = models.CharField(max_length=50)
    cpu_family = models.CharField(max_length=100)
    gpu_brand = models.CharField(max_length=50)
    cpu_key = models.CharField(max_length=255)
    gpu_key = models.CharField(max_length=255)
    cpu_score = models.FloatField()
    gpu_score = models.FloatField()
    cluster = models.IntegerField()
    cluster_label = models.CharField(max_length=50)
    d_plus = models.FloatField()
    d_minus = models.FloatField()
    preference_value = models.FloatField()
    ranking = models.IntegerField()

    class Meta:
        db_table = 'rekomendasi_laptop'
        ordering = ['ranking']

    def __str__(self):
        return f"{self.brand} {self.model_name} (Rank #{self.ranking})"