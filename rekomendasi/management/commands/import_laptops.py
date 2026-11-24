import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from rekomendasi.models import Laptop


class Command(BaseCommand):
    help = 'Import Dataset_SPK_LaptopKu_Final.xlsx hasil olahan Google Colab ke MySQL'

    def handle(self, *args, **options):
        xlsx_path = os.path.join(settings.BASE_DIR, 'data', 'Dataset_SPK_LaptopKu_Final.xlsx')
        if not os.path.exists(xlsx_path):
            self.stderr.write(self.style.ERROR(f'File tidak ditemukan: {xlsx_path}'))
            return

        self.stdout.write(f'Membaca {xlsx_path}...')
        df = pd.read_excel(xlsx_path)

        Laptop.objects.all().delete()
        records = [
            Laptop(
                full_name=str(row['full_name']).strip(),
                status=str(row['status']).strip(),
                brand=str(row['brand']).strip(),
                model_name=str(row['model_name']).strip(),
                category=str(row['category']).strip(),
                screen_size=float(row['screen_size']),
                touchscreen=str(row['touchscreen']).strip(),
                cpu=str(row['cpu']).strip(),
                ram_gb=int(row['ram_gb']),
                storage_gb=int(row['storage_gb']),
                storage_type=str(row['storage_type']).strip(),
                gpu=str(row['gpu']).strip(),
                price_idr=float(row['price_idr']),
                cpu_score=float(row['cpu_score']),
                gpu_score=float(row['gpu_score']),
                cluster_id=int(row['cluster_id']),
                cluster_label=str(row['cluster_label']).strip(),
                preference_value=float(row['preference_value']),
                ranking=int(row['ranking']),
            )
            for _, row in df.iterrows()
        ]
        Laptop.objects.bulk_create(records, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f'Berhasil mengimpor {len(records)} unit laptop ke tabel rekomendasi_laptop!'
        ))