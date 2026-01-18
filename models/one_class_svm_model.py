from models.base_model import BaseModel
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler


class OneClassSvmModel(BaseModel):
    def __init__(self):
        self.model = OneClassSVM(nu=0.05, kernel="rbf", gamma="scale")
        self.scaler = StandardScaler()
        self.data = None
        
    
    def load_data(self, filepath):
        return super().load_data(filepath)
    def preprocess_data(self, data):
        return super().preprocess_data(data)
    def train(self, X):
        return super().train(X)
    def save_model(self, filepath):
        return super().save_model(filepath)