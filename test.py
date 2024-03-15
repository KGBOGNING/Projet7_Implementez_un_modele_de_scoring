import numpy as np
import pandas as pd
import pytest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from tools import encode_data_2, impute_data, scaling_data, post_treatment

# Fixture pour fournir le chemin du fichier de données d'entrée


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'SK_ID_CURR': [1, 2, 3],
        'Numeric_Column': [10, np.nan, 30],
        'Another_Numeric_Column': [5, 15, np.nan],
        'DAYS_EMPLOYED': [365243, 1000, 2000],
        'DAYS_BIRTH': [-10000, -15000, -20000],
        'TARGET': [0, 1, 0],
        'Category_Column': ['A', 'B', 'A']
    })


@pytest.fixture
def encoders(sample_data):
    y_encoder = LabelEncoder()
    x_encoder = OneHotEncoder(sparse_output=False)

    if 'TARGET' in sample_data.columns:
        y_encoder.fit(sample_data['TARGET'])

    x_encoder.fit(sample_data[['Category_Column']])

    return y_encoder, x_encoder


def test_encode_data_2_with_target(sample_data, encoders):
    y_encoder, x_encoder = encoders
    result = encode_data_2(sample_data, y_encoder, x_encoder)

    # Assertions pour vérifier le résultat
    assert result.shape[0] == sample_data.shape[0]
    assert result.shape[1] == len(sample_data.columns) - 1 + len(x_encoder.get_feature_names_out(['Category_Column']))


def test_encode_data_2_without_target(sample_data, encoders):
    df_no_target = sample_data.drop('TARGET', axis=1)
    y_encoder, x_encoder = encoders

    result = encode_data_2(df_no_target, y_encoder, x_encoder)

    # Assertions pour vérifier le résultat
    assert result.shape[0] == df_no_target.shape[0]
    assert result.shape[1] == df_no_target.shape[1] - 1 + len(x_encoder.get_feature_names_out(['Category_Column']))


def test_impute_data(sample_data):
    columns = [name for name, dtype in sample_data.dtypes.items() if dtype != 'object' and name not in ['SK_ID_CURR',
                                                                                                 'TARGET']]
    # Créer une instance de SimpleImputer pour imputer les valeurs manquantes avec la médiane
    imputer = SimpleImputer(strategy='median').fit(sample_data[columns])

    # Appeler la fonction à tester avec le DataFrame d'exemple et l'imputer
    result = impute_data(sample_data[columns], imputer)

    # Vérifier que les valeurs manquantes ont été correctement imputées
    print(result.isna().sum().sum())
    assert result.isna().sum().sum() == 0


def test_scaling_data(sample_data):
    columns = [name for name, dtype in sample_data.dtypes.items() if dtype != 'object' and name not in ['SK_ID_CURR',
                                                                                                        'TARGET']]
    # Créer une instance de StandardScaler pour le test
    scaler = StandardScaler().fit(sample_data[columns])

    # Appeler la fonction à tester avec le DataFrame d'exemple et le scaler
    result = scaling_data(sample_data[columns], scaler)

    # Vérifier que les colonnes numériques ont été correctement mises à l'échelle
    assert isinstance(result['Numeric_Column'], pd.Series)
    assert isinstance(result['Another_Numeric_Column'], pd.Series)

    # Vérifier les types des colonnes numériques après mise à l'échelle
    assert isinstance(result['Numeric_Column'].dtype, np.dtype)
    assert isinstance(result['Another_Numeric_Column'].dtype, np.dtype)


def test_post_treatment(sample_data):
    # Appeler la fonction à tester avec le DataFrame d'exemple
    result = post_treatment(sample_data)

    # Vérifier que la colonne DAYS_EMPLOYED_ANOM a été ajoutée et contient les bons résultats
    assert 'DAYS_EMPLOYED_ANOM' in result.columns
    assert result['DAYS_EMPLOYED_ANOM'].equals(pd.Series([True, False, False]))

    # Vérifier que les valeurs 365243 dans la colonne DAYS_EMPLOYED ont été remplacées par NaN
    assert pd.isnull(result['DAYS_EMPLOYED']).sum() == 1

    # Vérifier que les valeurs négatives dans la colonne DAYS_BIRTH ont été transformées en valeurs positives
    assert (result['DAYS_BIRTH'] >= 0).all()






