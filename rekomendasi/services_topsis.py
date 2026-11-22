import numpy as np
import pandas as pd

KEBUTUHAN_CLUSTER_MAP = {
    'ringan': 'Rendah',       # Tugas kuliah, MS Office, Browsing
    'menengah': 'Menengah',   # Programming / Pemrograman
    'berat': 'Tinggi',        # Gaming, Data Science / AI, Desain Grafis
}

PRIORITAS_WEIGHTS = {
    'seimbang': {'price_idr': 0.30, 'cpu_score': 0.25, 'gpu_score': 0.20, 'ram_gb': 0.15, 'storage_gb': 0.10},
    'performa': {'price_idr': 0.15, 'cpu_score': 0.30, 'gpu_score': 0.25, 'ram_gb': 0.15, 'storage_gb': 0.15},
    'hemat':    {'price_idr': 0.45, 'cpu_score': 0.20, 'gpu_score': 0.10, 'ram_gb': 0.15, 'storage_gb': 0.10},
}

CATEGORY_IMAGE_MAP = {
    'Gaming': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&q=80',
    'Ultrabook': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80',
    '2 in 1 Convertible': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=600&q=80',
    'Workstation': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&q=80',
    'Netbook': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600&q=80',
    'Notebook': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&q=80',
}
APPLE_IMAGE_URL = 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&q=80'


def get_laptop_image_url(brand, category):
    if str(brand).strip().lower() == 'apple':
        return APPLE_IMAGE_URL
    return CATEGORY_IMAGE_MAP.get(category, CATEGORY_IMAGE_MAP['Notebook'])


def hitung_topsis_dinamis(queryset, prioritas='seimbang', top_n=10):
    data = list(queryset.values(
        'id', 'brand', 'model_name', 'category', 'screen_size', 'cpu',
        'ram_gb', 'storage_gb', 'storage_type', 'gpu', 'weight_kg',
        'price_idr', 'cpu_score', 'gpu_score', 'cluster_label', 'preference_value', 'ranking'
    ))

    if not data:
        return []

    df = pd.DataFrame(data)

    if len(df) == 1:
        df['dynamic_score'] = 1.0
        df['dynamic_rank'] = 1
        df['image_url'] = df.apply(lambda r: get_laptop_image_url(r['brand'], r['category']), axis=1)
        return df.to_dict(orient='records')

    weights = PRIORITAS_WEIGHTS.get(prioritas, PRIORITAS_WEIGHTS['seimbang'])
    criteria = ['price_idr', 'cpu_score', 'gpu_score', 'ram_gb', 'storage_gb']
    matrix = df[criteria].astype(float).values

    # 1. Normalisasi Vektor
    denom = np.sqrt((matrix ** 2).sum(axis=0))
    denom[denom == 0] = 1
    norm_matrix = matrix / denom

    # 2. Normalisasi Terbobot
    w_array = np.array([weights[c] for c in criteria])
    weighted_matrix = norm_matrix * w_array

    # 3. Solusi Ideal Positif (A+) & Negatif (A-)
    ideal_pos = np.zeros(len(criteria))
    ideal_neg = np.zeros(len(criteria))

    ideal_pos[0] = weighted_matrix[:, 0].min()  # Price = Cost
    ideal_neg[0] = weighted_matrix[:, 0].max()

    for i in range(1, len(criteria)):
        ideal_pos[i] = weighted_matrix[:, i].max()  # Spek = Benefit
        ideal_neg[i] = weighted_matrix[:, i].min()

    # 4. Jarak Euclidean & Nilai Preferensi
    d_plus = np.sqrt(((weighted_matrix - ideal_pos) ** 2).sum(axis=1))
    d_minus = np.sqrt(((weighted_matrix - ideal_neg) ** 2).sum(axis=1))

    total_d = d_plus + d_minus
    total_d[total_d == 0] = 1
    v_score = d_minus / total_d

    df['dynamic_score'] = np.round(v_score, 4)
    df = df.sort_values(by='dynamic_score', ascending=False).reset_index(drop=True)
    df['dynamic_rank'] = df.index + 1

    hasil_top = df.head(top_n).copy()
    hasil_top['image_url'] = hasil_top.apply(
        lambda r: get_laptop_image_url(r['brand'], r['category']), axis=1
    )

    return hasil_top.to_dict(orient='records')