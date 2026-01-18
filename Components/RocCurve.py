import streamlit as st
import matplotlib.pylab as plt

class RocCurve:
    def __init__(self,metrics,choice):
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