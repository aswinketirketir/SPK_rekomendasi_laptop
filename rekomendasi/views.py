from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Laptop
from .services_topsis import KEBUTUHAN_CLUSTER_MAP, hitung_topsis_dinamis, get_laptop_image_url


def halaman_utama(request):
    return render(request, 'index.html')


def halaman_katalog(request):
    return render(request, 'katalog.html')


def halaman_rekomendasi(request):
    return render(request, 'rekomendasi.html')


@require_GET
def api_katalog_laptop(request):
    queryset = Laptop.objects.all().order_by('ranking', 'id')

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(full_name__icontains=q) |
            Q(brand__icontains=q) |
            Q(model_name__icontains=q) |
            Q(cpu__icontains=q) |
            Q(gpu__icontains=q)
        )

    brand = request.GET.get('brand', '').strip()
    if brand:
        queryset = queryset.filter(brand__iexact=brand)

    cluster = request.GET.get('cluster', '').strip()
    if cluster in ['Rendah', 'Menengah', 'Tinggi']:
        queryset = queryset.filter(cluster_label=cluster)

    page_number = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)

    items = [
        {
            'id': obj.id,
            'full_name': obj.full_name,
            'status': obj.status,
            'brand': obj.brand,
            'model_name': obj.model_name,
            'category': obj.category,
            'screen_size': obj.screen_size,
            'touchscreen': obj.touchscreen,
            'cpu': obj.cpu,
            'ram_gb': obj.ram_gb,
            'storage_gb': obj.storage_gb,
            'storage_type': obj.storage_type,
            'gpu': obj.gpu,
            'price_idr': obj.price_idr,
            'cpu_score': obj.cpu_score,
            'gpu_score': obj.gpu_score,
            'cluster_label': obj.cluster_label,
            'preference_value': obj.preference_value,
            'ranking': obj.ranking,
            'image_url': get_laptop_image_url(obj.brand, obj.category),
        }
        for obj in page_obj.object_list
    ]

    return JsonResponse({
        'status': 'success',
        'total_items': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'laptops': items,
    }, json_dumps_params={'ensure_ascii': False})


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
    limit = int(request.GET.get('limit', 12))

    total_kandidat = queryset.count()
    hasil_ranking = hitung_topsis_dinamis(queryset, prioritas=prioritas, top_n=limit)

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
            'id', 'full_name', 'status', 'brand', 'model_name', 'category', 'screen_size', 'touchscreen',
            'price_idr', 'cpu', 'gpu', 'ram_gb', 'storage_gb', 'storage_type',
            'cpu_score', 'gpu_score', 'cluster_label', 'preference_value', 'ranking'
        ).first()
        if top_laptop:
            top_laptop['image_url'] = get_laptop_image_url(top_laptop['brand'], top_laptop['category'])
        hasil[label] = top_laptop

    return JsonResponse({
        'status': 'success',
        'best_per_cluster': hasil
    })


@require_GET
def api_filter_options(request):
    brands = sorted({
        str(b).strip() for b in Laptop.objects.values_list('brand', flat=True)
        if b and str(b).strip()
    })

    ram_options = sorted(
        Laptop.objects.filter(ram_gb__gte=4)
        .values('ram_gb')
        .annotate(total=Count('id'))
        .filter(total__gte=15)
        .values_list('ram_gb', flat=True)
    )

    storage_options = sorted(
        Laptop.objects.filter(storage_gb__gte=128)
        .values('storage_gb')
        .annotate(total=Count('id'))
        .filter(total__gte=15)
        .values_list('storage_gb', flat=True)
    )

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_kebutuhan, nama_aktivitas, target_cluster_label,
                   rekomendasi_min_ram, rekomendasi_min_storage, deskripsi_profil
            FROM aturan_kebutuhan_survei
            ORDER BY id ASC
        """)
        columns = [col[0] for col in cursor.description]
        kebutuhan_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

    prioritas_options = [
        {'kode': 'seimbang', 'label': 'Seimbang (Harga 30% : Spesifikasi 70%)'},
        {'kode': 'performa', 'label': 'Prioritas Performa Tinggi (Harga 15% : Spesifikasi 85%)'},
        {'kode': 'hemat', 'label': 'Prioritas Hemat Anggaran (Harga 45% : Spesifikasi 55%)'},
    ]

    return JsonResponse({
        'status': 'success',
        'brands': brands,
        'ram_options': list(ram_options),
        'storage_options': list(storage_options),
        'kebutuhan_options': kebutuhan_list,
        'prioritas_options': prioritas_options,
    }, json_dumps_params={'ensure_ascii': False})