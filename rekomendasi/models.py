from django.db import models


class Laptop(models.Model):
    full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, default='New')
    brand = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, default='Notebook')
    screen_size = models.FloatField(default=15.6)
    touchscreen = models.CharField(max_length=10, default='No')
    cpu = models.CharField(max_length=100)
    ram_gb = models.IntegerField(db_index=True)
    storage_gb = models.IntegerField(db_index=True)
    storage_type = models.CharField(max_length=50, default='SSD')
    gpu = models.CharField(max_length=100, default='Integrated Graphics')
    price_idr = models.FloatField(db_index=True)
    cpu_score = models.FloatField(default=50.0)
    gpu_score = models.FloatField(default=25.0)
    cluster_id = models.IntegerField(default=0)
    cluster_label = models.CharField(max_length=50, db_index=True)
    preference_value = models.FloatField(default=0.0)
    ranking = models.IntegerField(default=0)

    class Meta:
        db_table = 'rekomendasi_laptop'
        ordering = ['ranking', 'id']

    def __str__(self):
        return f"{self.brand} {self.model_name} (Rp {self.price_idr:,.0f})"