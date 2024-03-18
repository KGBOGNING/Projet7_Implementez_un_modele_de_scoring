from tools import (plot_amount, post_treatment, pre_encoded_feature, impute_data, scaling_data, encode_data_2,
                   plot_local_water)
from flask import Flask, request, jsonify
from flask_caching import Cache
import pickle
import pandas as pd
import shap
from config import config


def create_app(config):
    app = Flask(__name__)
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = 'cache'  # path to your server cache folder
    app.config['CACHE_THRESHOLD'] = 100000  # number of 'files' before start auto-delete
    # app.config.from_object('config')
    app.config['TESTING'] = config.get('TESTING')
    app.config['CSV_DIR'] = config.get('CSV_DIR')
    app.config['SAVE_DIR'] = config.get('SAVE_DIR')
    app.config['PROJECT_DIR'] = config.get('PROJECT_DIR')
    cache = Cache(app)

    @app.route("/", methods=['GET'])
    def root_func():
        return "<p>Hello, World!</p>"

    # def graph_numeric(data, name, value):
    #     fig = plot_amount(data, col=name, val=value, bins=50, label_rotation=False)
    #     fig.savefig(f'{name}.png')

    def load_process():
        path = app.config.get('PROJECT_DIR') + app.config.get('CSV_DIR') + '/application_test_prepro.csv'
        save_dir = app.config.get('PROJECT_DIR') + app.config.get('SAVE_DIR')
        objects_to_save = ["data", "model", "_scaler", "_impute", "_le", "feature_le_encoded", "_ohe"]
        loaded_objects = {}

        if cache.get('load_data'):
            print('Inside the cache..... and we have data')
            return cache.get('load_data')
        else:
            for key in objects_to_save:
                if key != "data":
                    with open(save_dir + f"{key}.pkl", "rb") as file:
                        loaded_objects[key] = pickle.load(file)
                else:
                    print('frffrf', path)
                    loaded_objects[key] = pd.read_csv(path)
            cache.set('load_data', loaded_objects)
            return loaded_objects

    object_loaded = load_process()

    df = object_loaded["data"]
    model = object_loaded["model"]
    _scaler = object_loaded["_scaler"]
    _impute = object_loaded["_impute"]
    _le = object_loaded["_le"]
    _ohe = object_loaded["_ohe"]
    feature_le_encoded = object_loaded["feature_le_encoded"]

    def process_2(x, var=None):
        """
        Effectue un traitement sur les données en plusieurs étapes.

        """
        x = post_treatment(x)

        if var is None:
            x, feature, le_count = pre_encoded_feature(x)
        else:
            x, feature, le_count = pre_encoded_feature(x, var)

        # Utilisez l'encodage personnalisé si var est spécifié, sinon utilisez l'encodage par défaut
        x = encode_data_2(x, _le, _ohe)
        x = impute_data(x, _impute)
        x = scaling_data(x, _scaler)

        return x

    @app.route("/load_initial_data/v2", methods=['GET'])
    def load_initial_data():
        row_select = df.iloc[0, :]
        details = {
            'code_gender': row_select["CODE_GENDER"],
            'occupation_type': row_select['OCCUPATION_TYPE'],
            'name_income_type': row_select['NAME_INCOME_TYPE'],
            'education_type': row_select['NAME_EDUCATION_TYPE'],
            'housing_type': row_select['NAME_HOUSING_TYPE'],
            'amt_credit': row_select["AMT_CREDIT"],
            'amt_income_total': row_select["AMT_INCOME_TOTAL"],
            'amt_annuity': row_select["AMT_ANNUITY"],
            'days_employed': abs(int(row_select["DAYS_EMPLOYED"])),
            'days_birth': int(row_select["DAYS_BIRTH"])
        }

        # graph_numeric(df, name="AMT_CREDIT", value=details.get('amt_credit'))
        fig1 = plot_amount(df, col="AMT_CREDIT", val=details.get('amt_credit'), bins=50, label_rotation=False)
        fig1.savefig(f'{"AMT_CREDIT"}.png')

        # graph_numeric(df, name="AMT_INCOME_TOTAL", value=details.get('amt_income_total'))
        fig2 = plot_amount(df, col="AMT_INCOME_TOTAL", val=details.get('amt_income_total'), bins=50,
                           label_rotation=False)
        fig2.savefig(f'{"AMT_INCOME_TOTAL"}.png')

        # graph_numeric(df, name="AMT_ANNUITY", value=details.get('amt_annuity'))
        fig3 = plot_amount(df, col="AMT_ANNUITY", val=details.get('amt_annuity'), bins=50, label_rotation=False)
        fig3.savefig(f'{"AMT_ANNUITY"}.png')

        # graph_numeric(df, name="DAYS_EMPLOYED", value=details.get('days_employed'))
        fig4 = plot_amount(df, col="DAYS_EMPLOYED", val=details.get('days_employed'), bins=50, label_rotation=False)
        fig4.savefig(f'{"DAYS_EMPLOYED"}.png')

        # graph_numeric(df, name="DAYS_BIRTH", value=details.get('days_birth'))
        fig5 = plot_amount(df, col="DAYS_BIRTH", val=details.get('days_birth'), bins=50, label_rotation=False)
        fig5.savefig(f'{"DAYS_BIRTH"}.png')

        # Convertissez le DataFrame en un dictionnaire JSON compatible
        json_data = {'ids': df['SK_ID_CURR'].to_dict(), 'values': details}

        return jsonify(json_data)

    @app.route("/load_data/v2/<int:id>", methods=['GET'])
    def load_data(id):
        print('Inside load_data....')
        mask = df['SK_ID_CURR'] == id
        row_select = df[mask]
        details = {
            'code_gender': row_select["CODE_GENDER"].values[0],
            'occupation_type': row_select['OCCUPATION_TYPE'].values[0],
            'name_income_type': row_select['NAME_INCOME_TYPE'].values[0],
            'education_type': row_select['NAME_EDUCATION_TYPE'].values[0],
            'housing_type': row_select['NAME_HOUSING_TYPE'].values[0],
            'amt_credit': row_select["AMT_CREDIT"].values[0],
            'amt_income_total': row_select["AMT_INCOME_TOTAL"].values[0],
            'amt_annuity': row_select["AMT_ANNUITY"].values[0],
            'days_employed': abs(int(row_select["DAYS_EMPLOYED"].values[0])),
            'days_birth': int(row_select["DAYS_BIRTH"].values[0])
        }
        # graph_numeric(df, name="AMT_CREDIT", value=details.get('amt_credit'))
        fig1 = plot_amount(df, col="AMT_CREDIT", val=details.get('amt_credit'), bins=50, label_rotation=False)
        fig1.savefig(f'{"AMT_CREDIT"}.png')

        # graph_numeric(df, name="AMT_INCOME_TOTAL", value=details.get('amt_income_total'))
        fig2 = plot_amount(df, col="AMT_INCOME_TOTAL", val=details.get('amt_income_total'), bins=50,
                           label_rotation=False)
        fig2.savefig(f'{"AMT_INCOME_TOTAL"}.png')

        # graph_numeric(df, name="AMT_ANNUITY", value=details.get('amt_annuity'))
        fig3 = plot_amount(df, col="AMT_ANNUITY", val=details.get('amt_annuity'), bins=50, label_rotation=False)
        fig3.savefig(f'{"AMT_saveANNUITY"}.png')

        # graph_numeric(df, name="DAYS_EMPLOYED", value=details.get('days_employed'))
        fig4 = plot_amount(df, col="DAYS_EMPLOYED", val=details.get('days_employed'), bins=50, label_rotation=False)
        fig4.savefig(f'{"DAYS_EMPLOYED"}.png')

        # graph_numeric(df, name="DAYS_BIRTH", value=details.get('days_birth'))
        fig5 = plot_amount(df, col="DAYS_BIRTH", val=details.get('days_birth'), bins=50, label_rotation=False)
        fig5.savefig(f'{"DAYS_BIRTH"}.png')

        # Convertissez le DataFrame en un dictionnaire JSON compatible
        json_data = {'ids': df['SK_ID_CURR'].to_dict(), 'values': details}

        return jsonify(json_data)

    def get_shap(mymodel, data):
        explainer = shap.Explainer(mymodel)
        # Shap values of the customer
        shap_values_loc = explainer(data.iloc[0].drop(['SK_ID_CURR'], errors='ignore').to_numpy().reshape(1, -1))
        # Feature names
        shap_values_loc.feature_names = data.drop(['SK_ID_CURR'], axis=1).columns.tolist()
        plot_local_water(shap_values_loc, max_display=10)

    @app.route("/predict", methods=['GET'])
    def predict():

        if 'id' not in request.args:
            return 'Error: No id field provided. Please specify an id.'

        idx = int(request.args['id'])
        mask = df['SK_ID_CURR'] == idx
        data = df[mask]
        data = process_2(data, var=feature_le_encoded)

        if len(data) == 0:
            return f'Error: an id.{len(data)}'

        if len(data) >= 1:
            row_data = data.iloc[0]
            row_data_x = row_data.drop(['SK_ID_CURR'], errors='ignore')

            # Faites la prédiction (remplacez cela par votre propre logique)
            row_data_x_reshape = row_data_x.values.reshape(1, -1)
            proba_pre = model.predict_proba(row_data_x_reshape)
            y_pre = model.predict(row_data_x_reshape)

            # Convertissez le résultat de la prédiction en un dictionnaire JSON
            prediction_result = {'proba': proba_pre.tolist(),
                                 'prediction': y_pre.tolist()}  # Assurez-vous que y_pre est sérialisable
            get_shap(model, data)

            # Retournez le résultat sous forme de réponse JSON
            return jsonify(prediction_result)

    return app


app = create_app(config)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

    # app.run(host='localhost', port=3000, debug=True)

# http://localhost:3000/api/get_data_from_id/?id=1

# app.run(host='localhost', port=3000)
