#!/usr/bin/env python3
from flask import Flask, request, render_template
import pandas as pd
import joblib
import traceback
import os

app = Flask(__name__)

# Charger le modèle
model = joblib.load("rf_model.pkl")

# Colonnes utilisées pour l'entraînement
expected_features = [
    'Gender', 'Age', 'HouseTypeID', 'ContactAvaliabilityID', 'HomeCountry',
    'AccountNo', 'CardExpiryDate', 'TransactionAmount', 'TransactionCountry',
    'LargePurchase', 'ProductID', 'CIF', 'TransactionCurrencyCode'
]

@app.route('/')
def home():
    return render_template('index.html')


# ------------- PREDICTION MANUELLE -------------
@app.route('/predict_manual', methods=['POST'])
def predict_manual():
    try:
        input_data = {}

        # Récupération des entrées du formulaire
        for col in expected_features:
            value = request.form.get(col, "")
            # Si nombre -> convertir en float sinon garder tel quel
            try:
                value = float(value)
            except:
                pass
            input_data[col] = value

        # Convertir en DataFrame
        df_input = pd.DataFrame([input_data])

        # Faire la prédiction
        prediction = model.predict(df_input)[0]
        proba = model.predict_proba(df_input)[0][1] * 100

        if prediction == 1:
            message = f"⚠️ Transaction suspecte détectée ({proba:.2f}% de probabilité de fraude)"
        else:
            message = f"✅ Transaction normale ({proba:.2f}% de probabilité de fraude)"

        return render_template('index.html', message=message)

    except Exception as e:
        traceback.print_exc()
        return render_template('index.html', message=f"❌ Erreur lors de la prédiction : {e}")


# ------------- PREDICTION VIA FICHIER CSV -------------
@app.route('/predict_file', methods=['POST'])
def predict_file():
    try:
        if 'file' not in request.files:
            return render_template('index.html', message="❌ Aucun fichier reçu")

        file = request.files['file']
        df = pd.read_csv(file)
        original_df = df.copy()

        if 'PotentialFraud' in df.columns:
            df = df.drop(columns=['PotentialFraud'])

        missing_cols = [col for col in expected_features if col not in df.columns]
        if missing_cols:
            return render_template('index.html', message=f"❌ Colonnes manquantes : {missing_cols}")

        extra_cols = [col for col in df.columns if col not in expected_features]
        if extra_cols:
            df = df.drop(columns=extra_cols)

        df = df[expected_features]

        predictions = model.predict(df)
        df['PredictedFraud'] = predictions

        output_path = "static/predictions_result.csv"
        df.to_csv(output_path, index=False)

        total_transactions = len(df)
        total_frauds = int(df['PredictedFraud'].sum())
        total_non_frauds = total_transactions - total_frauds
        fraud_ratio = round(total_frauds / total_transactions * 100, 2)
        non_fraud_ratio = round(100 - fraud_ratio, 2)

        if 'PotentialFraud' in original_df.columns:
            original_total_frauds = int(original_df['PotentialFraud'].sum())
            original_ratio = round(original_total_frauds / total_transactions * 100, 2)
        else:
            original_total_frauds = None
            original_ratio = None

        def highlight_fraud(row):
            return [
                'background-color: rgba(255, 77, 77, 0.4); color: white; font-weight: bold;'
                if row['PredictedFraud'] == 1 else '' for _ in row
            ]

        df_preview = df.head(10).style.apply(highlight_fraud, axis=1).to_html()
        original_preview = original_df.head(10).to_html(classes='table table-striped', index=False)

        return render_template(
            'index.html',
            message=(
                f"✅ Prédiction terminée — {total_frauds} fraudes détectées sur {total_transactions} transactions "
                f"({fraud_ratio}%) — Non-fraudes : {total_non_frauds} ({non_fraud_ratio}%) "
                + (
                    f"| Avant prédiction : {original_total_frauds} fraudes ({original_ratio}%)"
                    if original_total_frauds is not None else ""
                )
            ),
            download_link=output_path,
            preview=df_preview,
            original_preview=original_preview
        )

    except Exception as e:
        traceback.print_exc()
        return render_template('index.html', message=f"❌ Erreur : {e}")


if __name__ == '__main__':
    app.run(debug=True)
