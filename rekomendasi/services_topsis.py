import numpy as np

KEBUTUHAN_CLUSTER_MAP = {
    'K01': 'Rendah',
    'K02': 'Menengah',
    'K03': 'Tinggi',
    'K04': 'Tinggi',
}

BOBOT_PRIORITAS = {
    'seimbang': np.array([0.30, 0.25, 0.15, 0.10, 0.20]),
    'performa': np.array([0.15, 0.30, 0.20, 0.10, 0.25]),
    'hemat':    np.array([0.45, 0.20, 0.15, 0.10, 0.10]),
}


def get_laptop_image_url(brand: str, category: str) -> str:
    b = str(brand).lower()
    c = str(category).lower()
    if 'apple' in b:
        # Apple MacBook Space Gray / Silver dengan background studio netral sejuk (laptop asli)
        return 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&q=80'
    if 'gaming' in c or any(k in b for k in ['msi', 'alienware', 'razer', 'gigabyte']):
        # Laptop gaming RGB (ASUS ROG / MSI) terbuka di ruangan gelap dengan keyboard RGB cyber blue/neon
        return 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&q=80'
    if 'ultrabook' in c or any(k in b for k in ['lg', 'dell', 'microsoft']):
        # Ultrabook ramping (Dell XPS) terbuka dengan layar tipis dan warna cool slate
        return 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80'
    # Notebook modern (Dell/HP/Lenovo) terbuka menghadap depan di atas meja putih bersih
    return 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80'


def hitung_topsis_dinamis(queryset, prioritas='seimbang', top_n=12):
    laptops = list(queryset)
    if not laptops:
        return []

    weights = BOBOT_PRIORITAS.get(prioritas, BOBOT_PRIORITAS['seimbang'])
    is_benefit = np.array([False, True, True, True, True])

    matrix = np.array([
        [l.price_idr, l.cpu_score, l.ram_gb, l.storage_gb, l.gpu_score]
        for l in laptops
    ], dtype=float)

    denom = np.sqrt((matrix ** 2).sum(axis=0))
    denom[denom == 0] = 1.0
    norm_matrix = matrix / denom
    weighted = norm_matrix * weights

    ideal_pos = np.where(is_benefit, weighted.max(axis=0), weighted.min(axis=0))
    ideal_neg = np.where(is_benefit, weighted.min(axis=0), weighted.max(axis=0))

    d_pos = np.sqrt(((weighted - ideal_pos) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_neg) ** 2).sum(axis=1))
    total_d = d_pos + d_neg
    total_d[total_d == 0] = 1.0
    scores = d_neg / total_d

    indexed = sorted(zip(laptops, scores), key=lambda x: x[1], reverse=True)[:top_n]

    hasil = []
    for rank, (l, score) in enumerate(indexed, start=1):
        hasil.append({
            'id': l.id,
            'full_name': l.full_name,
            'status': l.status,
            'brand': l.brand,
            'model_name': l.model_name,
            'category': l.category,
            'screen_size': l.screen_size,
            'touchscreen': l.touchscreen,
            'cpu': l.cpu,
            'ram_gb': l.ram_gb,
            'storage_gb': l.storage_gb,
            'storage_type': l.storage_type,
            'gpu': l.gpu,
            'price_idr': l.price_idr,
            'cpu_score': l.cpu_score,
            'gpu_score': l.gpu_score,
            'cluster_label': l.cluster_label,
            'preference_value': l.preference_value,
            'ranking': l.ranking,
            'dynamic_score': round(float(score), 4),
            'dynamic_rank': rank,
            'image_url': get_laptop_image_url(l.brand, l.category),
        })
    return hasil