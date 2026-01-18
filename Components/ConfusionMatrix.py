from sklearn.metrics import ConfusionMatrixDisplay
import numpy as np
import streamlit as st
import matplotlib.pylab as plt

class ConfusionMatrix:
    def __init__(self,metrics):
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