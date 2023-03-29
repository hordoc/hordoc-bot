import numpy as np
from hordoc.embeddings.embeddings_search import encode, decode


def test_encode_decode():
    vector = [
        0.02574840560555458,
        -0.005180681589990854,
        -0.0024430365301668644,
        -0.02745029889047146,
        0.07963452488183975,
    ]
    blob = encode(vector)
    assert len(blob) == len(vector) * 4
    np.testing.assert_almost_equal(decode(blob), vector)
