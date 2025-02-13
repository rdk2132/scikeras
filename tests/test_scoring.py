import numpy as np

from sklearn.metrics import r2_score as sklearn_r2_score
from tensorflow import convert_to_tensor

from scikeras.wrappers import KerasRegressor

from .mlp_models import dynamic_regressor


def test_kerasregressor_r2_correctness():
    """Test custom R^2 implementation against scikit-learn's."""
    n_samples = 50

    datasets = []
    y_true = np.arange(n_samples, dtype=float)
    y_pred = y_true + 1
    datasets.append((y_true.reshape(-1, 1), y_pred.reshape(-1, 1)))
    y_true = np.random.random_sample(size=y_true.shape)
    y_pred = np.random.random_sample(size=y_true.shape)
    datasets.append((y_true.reshape(-1, 1), y_pred.reshape(-1, 1)))

    def keras_backend_r2(y_true, y_pred):
        """Wrap Keras operations to numpy."""
        y_true = convert_to_tensor(y_true)
        y_pred = convert_to_tensor(y_pred)
        return KerasRegressor.r_squared(y_true, y_pred).numpy()

    for (y_true, y_pred) in datasets:
        np.testing.assert_almost_equal(
            keras_backend_r2(y_true, y_pred),
            sklearn_r2_score(y_true, y_pred),
            decimal=5,
        )


def test_kerasregressor_r2_as_metric():
    """Test custom R^2 implementation against scikit-learn's."""
    est = KerasRegressor(
        dynamic_regressor, metrics=[KerasRegressor.r_squared], epochs=10, random_state=0
    )

    y = np.random.randint(low=0, high=2, size=(1000,))
    X = y.reshape((-1, 1))

    est.fit(X, y)

    current_score = est.score(X, y)
    last_hist = est.history_["r_squared"][-1]
    np.testing.assert_almost_equal(current_score, last_hist, decimal=3)

    current_eval = est.model_.evaluate(X, y, return_dict=True)["r_squared"]
    np.testing.assert_almost_equal(current_score, current_eval, decimal=3)
