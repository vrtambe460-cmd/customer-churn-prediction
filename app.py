"""Customer Churn Prediction Dashboard - Streamlit App"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from agents import DataPrepAgent, PredictionAgent, RecommendationAgent
from utils.helpers import load_data

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="",
    layout="wide"
)

@st.cache_resource
def load_agents():
    data_prep = DataPrepAgent()
    prediction = PredictionAgent()
    recommendation = RecommendationAgent()
    data_prep.initialize()
    prediction.initialize()
    recommendation.initialize()
    return data_prep, prediction, recommendation

def train_model(data_prep, prediction):
    df = load_data('data/telco_churn.csv')
    prep_result = data_prep.execute({'dataframe': df, 'fit_scaler': True})
    pred_result = prediction.execute({'dataframe': prep_result['dataframe']})
    return prep_result, pred_result

def main():
    st.title("Customer Churn Prediction System")
    st.markdown("Predict which customers will leave and get retention recommendations.")

    data_prep, prediction, recommendation = load_agents()

    tab1, tab2, tab3, tab4 = st.tabs(["Predict", "Analytics", "Models", "Bulk Analysis"])

    with tab1:
        st.header("Customer Information")
        col1, col2, col3 = st.columns(3)

        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            senior = st.selectbox("Senior Citizen", ["No", "Yes"])
            partner = st.selectbox("Partner", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["Yes", "No"])

        with col2:
            tenure = st.slider("Tenure (months)", 0, 72, 12)
            phone = st.selectbox("Phone Service", ["Yes", "No"])
            multiple = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
            internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])

        with col3:
            contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
            paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
            payment = st.selectbox("Payment Method", [
                "Electronic check", "Mailed check",
                "Bank transfer (automatic)", "Credit card (automatic)"
            ])
            monthly = st.number_input("Monthly Charges ($)", 18.0, 120.0, 70.0)
            total = st.number_input("Total Charges ($)", 0.0, 10000.0, monthly * tenure)

        online_sec = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_back = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_prot = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
        tech_sup = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        stream_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        stream_mov = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

        if st.button("Predict Churn", type="primary"):
            customer_data = {
                'gender': gender,
                'SeniorCitizen': 1 if senior == "Yes" else 0,
                'Partner': partner,
                'Dependents': dependents,
                'tenure': tenure,
                'PhoneService': phone,
                'MultipleLines': multiple,
                'InternetService': internet,
                'OnlineSecurity': online_sec,
                'OnlineBackup': online_back,
                'DeviceProtection': device_prot,
                'TechSupport': tech_sup,
                'StreamingTV': stream_tv,
                'StreamingMovies': stream_mov,
                'Contract': contract,
                'PaperlessBilling': paperless,
                'PaymentMethod': payment,
                'MonthlyCharges': monthly,
                'TotalCharges': total
            }

            df = pd.DataFrame([customer_data])
            prep_result = data_prep.execute({'dataframe': df, 'fit_scaler': False})
            predictions, probabilities = prediction.predict(prep_result['dataframe'])
            prob = probabilities[0]
            pred = predictions[0]

            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Prediction Result")
                if prob >= 0.7:
                    st.error(f"HIGH RISK - Churn Probability: {prob:.1%}")
                elif prob >= 0.4:
                    st.warning(f"MEDIUM RISK - Churn Probability: {prob:.1%}")
                else:
                    st.success(f"LOW RISK - Churn Probability: {prob:.1%}")

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    title={'text': "Churn Risk Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "green"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': prob * 100
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Retention Recommendations")
                risk_level = "HIGH" if prob >= 0.7 else ("MEDIUM" if prob >= 0.4 else "LOW")
                recs = recommendation._get_customer_recommendations(prob, None, None)
                for i, rec in enumerate(recs, 1):
                    st.write(f"{i}. {rec}")

    with tab2:
        st.header("Data Analytics")
        df = load_data('data/telco_churn.csv')

        churn_map = {'True': 'Churn', 'False': 'No Churn', 'Yes': 'Churn', 'No': 'No Churn'}
        df['Churn_Label'] = df['Churn'].map(churn_map).fillna('No Churn')

        col1, col2 = st.columns(2)
        with col1:
            churn_counts = df['Churn_Label'].value_counts()
            fig = px.pie(values=churn_counts.values, names=churn_counts.index,
                        title='Churn Distribution')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.histogram(df, x='MonthlyCharges', color='Churn_Label',
                              title='Monthly Charges by Churn', nbins=30)
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x='tenure', color='Churn_Label',
                              title='Tenure by Churn', nbins=20)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            contract_churn = df.groupby(['Contract', 'Churn_Label']).size().reset_index(name='Count')
            fig = px.bar(contract_churn, x='Contract', y='Count', color='Churn_Label',
                        title='Churn by Contract Type')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Customer Data Sample")
        st.dataframe(df.head(20))

    with tab3:
        st.header("Model Performance")

        with st.spinner("Training models..."):
            prep_result, pred_result = train_model(data_prep, prediction)

        metrics = pred_result['metrics']
        best_model = pred_result['best_model_name']

        st.success(f"Best Model: {best_model}")

        metrics_df = pd.DataFrame(metrics).T
        metrics_df = metrics_df.round(4)
        st.dataframe(metrics_df)

        fig = px.bar(x=list(metrics.keys()),
                    y=[m['accuracy'] for m in metrics.values()],
                    title='Model Accuracy Comparison',
                    labels={'x': 'Model', 'y': 'Accuracy'})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("All Model Metrics")
        for model_name, m in metrics.items():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Accuracy", f"{m['accuracy']:.2%}")
            col2.metric("Precision", f"{m['precision']:.2%}")
            col3.metric("Recall", f"{m['recall']:.2%}")
            col4.metric("F1 Score", f"{m['f1']:.2%}")
            st.divider()

    with tab4:
        st.header("Bulk Customer Analysis")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

        if uploaded_file is not None:
            bulk_df = pd.read_csv(uploaded_file)
            st.write(f"Uploaded {len(bulk_df)} customers")

            if st.button("Analyze All Customers"):
                with st.spinner("Analyzing..."):
                    bulk_df_clean = bulk_df.copy()
                    if 'customerID' in bulk_df_clean.columns:
                        bulk_df_clean = bulk_df_clean.drop('customerID', axis=1)
                    if 'Unnamed: 0' in bulk_df_clean.columns:
                        bulk_df_clean = bulk_df_clean.drop('Unnamed: 0', axis=1)
                    if 'Churn' in bulk_df_clean.columns:
                        bulk_df_clean = bulk_df_clean.drop('Churn', axis=1)

                    prep_result = data_prep.execute({'dataframe': bulk_df_clean, 'fit_scaler': False})
                    predictions, probabilities = prediction.predict(prep_result['dataframe'])

                    results_df = bulk_df.copy()
                    results_df['Churn_Probability'] = probabilities
                    results_df['Risk_Level'] = ['High' if p >= 0.7 else ('Medium' if p >= 0.4 else 'Low') for p in probabilities]
                    results_df['Prediction'] = ['Will Churn' if p == 1 else 'Will Stay' for p in predictions]

                st.success("Analysis complete!")
                st.dataframe(results_df)

                fig = px.histogram(results_df, x='Churn_Probability', nbins=30,
                                  title='Churn Probability Distribution')
                st.plotly_chart(fig, use_container_width=True)

                risk_counts = results_df['Risk_Level'].value_counts()
                fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                            title='Risk Level Distribution')
                st.plotly_chart(fig, use_container_width=True)

                csv = results_df.to_csv(index=False)
                st.download_button("Download Results", csv, "churn_results.csv", "text/csv")

if __name__ == "__main__":
    main()
