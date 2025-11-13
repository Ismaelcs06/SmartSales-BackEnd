# catalog/recommendation.py
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import os
import pickle
from .models import Producto

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'recommender_model.pkl')

class ProductRecommender:
    def __init__(self):
        # Intentamos cargar modelo entrenado
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model_data = pickle.load(f)
        else:
            self.model_data = None

    def get_similar(self, product_id, n=5):
        """
        Devuelve los IDs de productos similares
        """
        if self.model_data is None:
            return []

        product_idx_map = self.model_data['product_idx_map']
        matrix = self.model_data['matrix']
        knn = self.model_data['model']

        if product_id not in product_idx_map:
            return []

        idx = product_idx_map[product_id]
        distances, indices = knn.kneighbors([matrix[idx]], n_neighbors=n+1)
        neighbors = [self.model_data['id_list'][i] for i in indices[0] if self.model_data['id_list'][i] != product_id]
        return neighbors[:n]

# Función para entrenar y guardar el modelo
def train_recommender():
    # Simular ratings desde la base de datos
    # Debes tener un modelo Rating o usar ventas/visitas como proxy
    # Por simplicidad: usuario_id, producto_id, rating
    data = [
        # user_id, product_id, rating
        [1, 1, 5],
        [1, 2, 3],
        [2, 1, 4],
        [2, 3, 5],
        [3, 2, 4],
        [3, 3, 2],
        # Agrega más datos reales de tu DB
    ]
    df = pd.DataFrame(data, columns=['user_id', 'product_id', 'rating'])

    matrix = df.pivot(index='user_id', columns='product_id', values='rating').fillna(0).values
    id_list = list(df['product_id'].unique())
    product_idx_map = {pid: idx for idx, pid in enumerate(id_list)}

    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(matrix.T)  # Transponer: product-product similarity

    model_data = {
        'matrix': matrix.T,
        'id_list': id_list,
        'product_idx_map': product_idx_map,
        'model': knn
    }

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
