from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Laptop
from .services_topsis import KEBUTUHAN_CLUSTER_MAP, hitung_topsis_dinamis

@require_GET
def api_rekomendasi_laptop(request):
    queryset = Laptop.objects.all()

    max_budget = request.GET.get('max_budget')
    if max_budget and max_budget.isdigit():
        queryset = queryset.filter(price_idr__lte=float(max_budget))

    kebutuhan = request.GET.get('kebutuhan')
    if kebutuhan in KEBUTUHAN_CLUSTER_MAP:
        queryset = queryset.filter(cluster_label=KEBUTUHAN_CLUSTER_MAP[kebutuhan])

    min_ram = request.GET.get('min_ram')
    if min_ram and min_ram.isdigit():
        queryset = queryset.filter(ram_gb__gte=int(min_ram))

    min_storage = request.GET.get('min_storage')
    if min_storage and min_storage.isdigit():
        queryset = queryset.filter(storage_gb__gte=int(min_storage))

    brand = request.GET.get('brand')
    if brand:
        queryset = queryset.filter(brand__iexact=brand)

    prioritas = request.GET.get('prioritas', 'seimbang')
    limit = int(request.GET.get('limit', 10))

    total_kandidat = queryset.count()
    hasil_ranking = hitung_topsis_dinamis(queryset, prioritas=prioritas, top_n=limit)

    # Catat log pencarian ke tabel riwayat_rekomendasi
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO riwayat_rekomendasi (max_budget, kebutuhan, min_ram, min_storage, prioritas, jumlah_hasil)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [
                float(max_budget) if (max_budget and max_budget.isdigit()) else None,
                kebutuhan if kebutuhan else None,
                int(min_ram) if (min_ram and min_ram.isdigit()) else None,
                int(min_storage) if (min_storage and min_storage.isdigit()) else None,
                prioritas,
                total_kandidat,
            ]
        )

    return JsonResponse({
        'status': 'success',
        'filter_applied': {
            'max_budget': max_budget,
            'kebutuhan': kebutuhan,
            'mapped_cluster': KEBUTUHAN_CLUSTER_MAP.get(kebutuhan, 'Semua Klaster'),
            'min_ram': min_ram,
            'min_storage': min_storage,
            'prioritas': prioritas,
        },
        'total_kandidat_ditemukan': total_kandidat,
        'jumlah_ditampilkan': len(hasil_ranking),
        'rekomendasi': hasil_ranking
    }, json_dumps_params={'ensure_ascii': False})


@require_GET
def api_best_per_cluster(request):
    hasil = {}
    for label in ['Rendah', 'Menengah', 'Tinggi']:
        top_laptop = Laptop.objects.filter(cluster_label=label).order_by('-preference_value').values(
            'id', 'brand', 'model_name', 'price_idr', 'cpu', 'gpu', 'ram_gb',
            'storage_gb', 'cluster_label', 'preference_value', 'ranking'
        ).first()
        hasil[label] = top_laptop

    return JsonResponse({
        'status': 'success',
        'best_per_cluster': hasil
    })

@require_GET
def api_filter_options(request):
    """
    Endpoint untuk mengisi dropdown filter di Frontend secara otomatis dari database.
    URL: /api/filter-options/
    """
    # 1. Ambil semua merek laptop unik (terurut A-Z)
    brands = list(
        Laptop.objects.values_list('brand', flat=True)
        .distinct()
        .order_by('brand')
    )

    # 2. Ambil opsi kapasitas RAM & Storage yang tersedia di dataset
    ram_options = sorted(list(Laptop.objects.values_list('ram_gb', flat=True).distinct()))
    storage_options = sorted(list(Laptop.objects.values_list('storage_gb', flat=True).distinct()))

    # 3. Ambil daftar kebutuhan mahasiswa dari tabel aturan_kebutuhan_survei
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_kebutuhan, nama_aktivitas, target_cluster_label,
                   rekomendasi_min_ram, rekomendasi_min_storage, deskripsi_profil
            FROM aturan_kebutuhan_survei
            ORDER BY id ASC
        """)
        columns = [col[0] for col in cursor.description]
        kebutuhan_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # 4. Opsi prioritas bobot TOPSIS
    prioritas_options = [
        {'kode': 'seimbang', 'label': 'Seimbang (Harga 30% : Spesifikasi 70%)'},
        {'kode': 'performa', 'label': 'Prioritas Performa Tinggi (Harga 15% : Spesifikasi 85%)'},
        {'kode': 'hemat', 'label': 'Prioritas Hemat Anggaran (Harga 45% : Spesifikasi 55%)'},
    ]

    return JsonResponse({
        'status': 'success',
        'brands': brands,
        'ram_options': ram_options,
        'storage_options': storage_options,
        'kebutuhan_options': kebutuhan_list,
        'prioritas_options': prioritas_options,
    }, json_dumps_params={'ensure_ascii': False})