from models.isolation_forest_model import IsolationForestModel
from models.one_class_svm_model import OneClassSvmModel
from models.db_scan_model import DbScanModel

class TrainingPipeline:
    def __init__(self, model, dataset_path, save_path):
        self.model = model
        self.dataset_path = dataset_path
        self.save_path = save_path

    def run(self):
        data = self.model.load_data(self.dataset_path)
        X, y = self.model.preprocess_data(data)
        self.model.train(X)
        # self.model.evaluate(X, y)
        self.model.save_model(self.save_path)
