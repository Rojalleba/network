import streamlit as st
import numpy as np
from scapy.all import *
import logging
from Model.UnsupervisedModel import Model
import matplotlib.pylab as plt
from sklearn.metrics import ConfusionMatrixDisplay


# ==================
# Configure logging
# ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Evaluation:
    
    def get_metrics(model):
        
        # Algorithm options
        algorithms = {
            "Isolation Forest": model.isolation_forest,
            "One-Class SVM": model.one_class_svm,
            "DBSCAN": model.dbscan,
        }

        choice = st.selectbox("Select Algorithm", list(algorithms.keys()))

        if st.button("Run Model"):
            # Run selected algorithm
            y_pred = algorithms[choice]()  # predictions from algorithm
            metrics = model.get_metrics(y_pred)  # returns tp, tn, fp, fn, fpr, tpr, roc_auc

            # --- Confusion Matrix ---
            st.write("### ✅ Confusion Matrix")
            tn = int(metrics.get("tn", 0))
            fp = int(metrics.get("fp", 0))
            fn = int(metrics.get("fn", 0))
            tp = int(metrics.get("tp", 0))

            cm = np.array([[tn, fp], [fn, tp]])
            fig_cm, ax_cm = plt.subplots()
            cm_display = ConfusionMatrixDisplay(confusion_matrix=cm)
            cm_display.plot(ax=ax_cm, cmap="Blues", colorbar=False)
            st.pyplot(fig_cm)

            # --- ROC Curve ---
            st.write("### 📈 ROC Curve")
            fpr = metrics.get("fpr", [0, 1])
            tpr = metrics.get("tpr", [0, 1])
            roc_auc = metrics.get("roc_auc", 0)

            fig_roc, ax_roc = plt.subplots()
            ax_roc.plot(fpr, tpr, label=f"AUC = {roc_auc:.2f}")
            ax_roc.plot([0, 1], [0, 1], linestyle="--", color="gray")
            ax_roc.set_xlabel("False Positive Rate")
            ax_roc.set_ylabel("True Positive Rate")
            ax_roc.set_title(f"ROC Curve - {choice}")
            ax_roc.legend()
            st.pyplot(fig_roc)

            # --- Metrics Summary ---
            st.success(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    
# Dashboard()
