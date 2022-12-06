from sktime.forecasting.arima import AutoARIMA
from sktime.datasets import load_airline
from sktime.utils.plotting import plot_series
#from sktime.utils.plotting.forecasting import plot_ys
from sktime.forecasting.model_selection import temporal_train_test_split
import matplotlib.pyplot as plt
import pandas as pd

rd = pd.DataFrame
ser = pd.Series.from_csv("BTCUSDT-1d-data.csv", header=None, index_col=0)

airline = load_airline()
plot_series(airline)
y_train, y_test = temporal_train_test_split(airline, test_size=36)
fh = list(range(1, 37))
forecaster = AutoARIMA()
forecaster.fit(y_train)
y_pred = forecaster.predict(fh)
plot_series(y_train, y_test, y_pred, labels = ["Train", "Test", "Pred"])