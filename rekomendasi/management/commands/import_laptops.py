import pandas as pd
from django.core.management.base import BaseCommand
from rekomendasi.models import Laptop

class Command(BaseCommand):
    help = 'Mengimpor 1.273 data laptop dari data/Dataset_SPK.xlsx ke database laptopku'

    def handle(self, *args, **kwargs):
        file_path = 'data/Dataset_SPK.xlsx'
        self.stdout.write(f"Membaca {file_path}...")

        df = pd.read_excel(file_path, sheet_name='Sheet1')
        Laptop.objects.all().delete()

        laptop_objects = [
            Laptop(
                brand=row['Brand'],
                model_name=row['Model'],
                category=row['Category'],
                screen_size=float(row['Screen_Size']),
                screen=row['Screen'],
                cpu=row['CPU'],
                ram_gb=int(row['RAM_GB']),
                storage_original=row['Storage_Original'],
                gpu=row['GPU'],
                os=row['OS'],
                weight_kg=float(row['Weight_KG']),
                price_eur=float(row['Price_EUR']),
                price_idr=float(row['Price_IDR']),
                storage_gb=int(row['Storage_GB']),
                storage_type=row['Storage_Type'],
                cpu_brand=row['CPU_Brand'],
                cpu_family=row['CPU_Family'],
                gpu_brand=row['GPU_Brand'],
                cpu_key=row['CPU_key'],
                gpu_key=row['GPU_key'],
                cpu_score=float(row['CPU_Score']),
                gpu_score=float(row['GPU_Score']),
                cluster=int(row['Cluster']),
                cluster_label=row['Cluster_Label'],
                d_plus=float(row['D+']),
                d_minus=float(row['D-']),
                preference_value=float(row['Preference_Value']),
                ranking=int(row['Ranking']),
            )
            for _, row in df.iterrows()
        ]

        Laptop.objects.bulk_create(laptop_objects, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"Berhasil mengimpor {len(laptop_objects)} data laptop ke database laptopku!"))