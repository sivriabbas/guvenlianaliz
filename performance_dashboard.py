"""
Phase 7.D3: Performans Dashboard
=================================
Streamlit ile interaktif model performans dashboard'u.

Özellikler:
- Gerçek zamanlı performans izleme
- Model karşılaştırma grafikleri
- Son tahminler ve sonuçları
- Doğruluk trendi
- Güven skoru analizi
- Lig ve maç tipi bazlı performans
- Export/Download fonksiyonları

Kullanım:
    streamlit run performance_dashboard.py
    
    # Özel port
    streamlit run performance_dashboard.py --server.port 8501
    
    # Farklı veritabanı
    streamlit run performance_dashboard.py -- --db-path custom.db

Bileşenler:
- 📊 Genel İstatistikler
- 📈 Doğruluk Trendi
- 🎯 Model Karşılaştırma
- 📋 Son Tahminler
- 🏆 En İyi Performanslar
- 📉 Detaylı Analiz
"""

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    print("⚠️ Streamlit not installed. This dashboard requires Streamlit to run.")
    print("Install it with: pip install streamlit")
    exit(1)
    
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import json
from prediction_logger import PredictionLogger


# Sayfa ayarları
st.set_page_config(
    page_title="⚽ Model Performance Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


class PerformanceDashboard:
    """Streamlit performans dashboard'u."""
    
    def __init__(self, db_path: str = "predictions.db"):
        """
        Args:
            db_path: Predictions veritabanı yolu
        """
        self.db_path = db_path
        self.logger = PredictionLogger(db_path)
        
        # Cache
        if 'refresh_trigger' not in st.session_state:
            st.session_state.refresh_trigger = 0
    
    def load_data(self) -> pd.DataFrame:
        """Tüm tahminleri yükle."""
        query = '''
            SELECT 
                id, timestamp, home_team, away_team, league,
                prediction, confidence, model_name, model_version,
                actual_result, is_correct, created_at
            FROM predictions
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, self.logger.conn)
        
        # Datetime dönüşümü
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        return df
    
    def get_model_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Model özet istatistikleri."""
        summary = df[df['actual_result'].notna()].groupby('model_name').agg({
            'id': 'count',
            'is_correct': 'sum',
            'confidence': 'mean'
        }).reset_index()
        
        summary.columns = ['Model', 'Total', 'Correct', 'Avg Confidence']
        summary['Accuracy'] = (summary['Correct'] / summary['Total'] * 100).round(2)
        summary['Wrong'] = summary['Total'] - summary['Correct']
        
        return summary.sort_values('Accuracy', ascending=False)
    
    def get_daily_accuracy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Günlük doğruluk trendi."""
        daily = df[df['actual_result'].notna()].groupby(['date', 'model_name']).agg({
            'id': 'count',
            'is_correct': 'sum'
        }).reset_index()
        
        daily.columns = ['Date', 'Model', 'Total', 'Correct']
        daily['Accuracy'] = (daily['Correct'] / daily['Total'] * 100).round(2)
        
        return daily
    
    def plot_model_comparison(self, summary: pd.DataFrame):
        """Model karşılaştırma grafiği."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Accuracy Comparison', 'Prediction Volume'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Accuracy
        fig.add_trace(
            go.Bar(
                x=summary['Model'],
                y=summary['Accuracy'],
                name='Accuracy',
                marker_color='lightblue',
                text=summary['Accuracy'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=summary['Model'],
                y=summary['Total'],
                name='Total Predictions',
                marker_color='lightgreen',
                text=summary['Total'],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            title_text="Model Performance Comparison"
        )
        
        fig.update_yaxes(title_text="Accuracy (%)", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        
        return fig
    
    def plot_accuracy_trend(self, daily: pd.DataFrame):
        """Doğruluk trendi grafiği."""
        fig = px.line(
            daily,
            x='Date',
            y='Accuracy',
            color='Model',
            title='Daily Accuracy Trend',
            markers=True
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Date',
            yaxis_title='Accuracy (%)',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_confidence_distribution(self, df: pd.DataFrame):
        """Güven skoru dağılımı."""
        fig = px.histogram(
            df,
            x='confidence',
            color='model_name',
            nbins=20,
            title='Confidence Score Distribution',
            labels={'confidence': 'Confidence', 'model_name': 'Model'},
            barmode='overlay',
            opacity=0.7
        )
        
        fig.update_layout(height=400)
        
        return fig
    
    def plot_confusion_heatmap(self, df: pd.DataFrame, model_name: str):
        """Confusion matrix heatmap."""
        model_df = df[(df['model_name'] == model_name) & (df['actual_result'].notna())]
        
        if model_df.empty:
            return None
        
        # Confusion matrix
        cm = pd.crosstab(
            model_df['actual_result'],
            model_df['prediction'],
            rownames=['Actual'],
            colnames=['Predicted']
        )
        
        # Normalize
        cm_normalized = cm.div(cm.sum(axis=1), axis=0) * 100
        
        fig = go.Figure(data=go.Heatmap(
            z=cm_normalized.values,
            x=['Away Win', 'Draw', 'Home Win'],
            y=['Away Win', 'Draw', 'Home Win'],
            colorscale='Blues',
            text=cm_normalized.values.round(1),
            texttemplate='%{text}%',
            textfont={"size": 14},
            colorbar=dict(title="Percentage")
        ))
        
        fig.update_layout(
            title=f'Confusion Matrix - {model_name}',
            xaxis_title='Predicted',
            yaxis_title='Actual',
            height=400
        )
        
        return fig
    
    def render_header(self):
        """Dashboard başlığı."""
        st.title("⚽ Football Prediction Dashboard")
        st.markdown("---")
        
        # Refresh butonu
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("🔄 Refresh Data"):
                st.session_state.refresh_trigger += 1
                st.rerun()
        
        with col2:
            st.metric("Database", self.db_path)
    
    def render_overview(self, df: pd.DataFrame, summary: pd.DataFrame):
        """Genel bakış."""
        st.header("📊 Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_predictions = len(df)
        verified = df['actual_result'].notna().sum()
        pending = total_predictions - verified
        
        if verified > 0:
            overall_accuracy = (df['is_correct'].sum() / verified * 100)
        else:
            overall_accuracy = 0
        
        avg_confidence = df['confidence'].mean() * 100
        
        with col1:
            st.metric("Total Predictions", f"{total_predictions:,}")
        
        with col2:
            st.metric("Verified", f"{verified:,}")
        
        with col3:
            st.metric("Pending", f"{pending:,}")
        
        with col4:
            st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
        
        with col5:
            st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
        
        st.markdown("---")
    
    def render_model_comparison(self, summary: pd.DataFrame):
        """Model karşılaştırması."""
        st.header("🎯 Model Comparison")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig = self.plot_model_comparison(summary)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Model Statistics")
            st.dataframe(
                summary[['Model', 'Total', 'Correct', 'Wrong', 'Accuracy', 'Avg Confidence']],
                hide_index=True,
                use_container_width=True
            )
        
        st.markdown("---")
    
    def render_trends(self, daily: pd.DataFrame, df: pd.DataFrame):
        """Trendler."""
        st.header("📈 Trends")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = self.plot_accuracy_trend(daily)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = self.plot_confidence_distribution(df)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    def render_recent_predictions(self, df: pd.DataFrame):
        """Son tahminler."""
        st.header("📋 Recent Predictions")
        
        # Filtreler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_model = st.selectbox(
                "Model",
                ["All"] + list(df['model_name'].unique())
            )
        
        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Verified", "Pending"]
            )
        
        with col3:
            limit = st.slider("Show", 10, 100, 20)
        
        # Filtreleme
        filtered_df = df.copy()
        
        if selected_model != "All":
            filtered_df = filtered_df[filtered_df['model_name'] == selected_model]
        
        if status_filter == "Verified":
            filtered_df = filtered_df[filtered_df['actual_result'].notna()]
        elif status_filter == "Pending":
            filtered_df = filtered_df[filtered_df['actual_result'].isna()]
        
        # Göster
        display_df = filtered_df.head(limit)[
            ['timestamp', 'home_team', 'away_team', 'league', 
             'prediction', 'confidence', 'model_name', 'actual_result', 'is_correct']
        ].copy()
        
        # Tahmin metni
        display_df['prediction'] = display_df['prediction'].map({
            0: 'Away Win', 1: 'Draw', 2: 'Home Win'
        })
        
        # Actual metni
        display_df['actual_result'] = display_df['actual_result'].map({
            0.0: 'Away Win', 1.0: 'Draw', 2.0: 'Home Win', np.nan: '-'
        })
        
        # Confidence percentage
        display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
        
        # Is correct
        display_df['is_correct'] = display_df['is_correct'].map({
            1.0: '✅', 0.0: '❌', np.nan: '-'
        })
        
        st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
    
    def render_detailed_analysis(self, df: pd.DataFrame):
        """Detaylı analiz."""
        st.header("📉 Detailed Analysis")
        
        # Model seçimi
        selected_model = st.selectbox(
            "Select Model for Analysis",
            df['model_name'].unique()
        )
        
        model_df = df[df['model_name'] == selected_model]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Confusion matrix
            fig = self.plot_confusion_heatmap(df, selected_model)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No verified predictions for confusion matrix")
        
        with col2:
            # League performance
            if 'league' in model_df.columns:
                league_perf = model_df[model_df['actual_result'].notna()].groupby('league').agg({
                    'id': 'count',
                    'is_correct': 'sum'
                }).reset_index()
                
                league_perf.columns = ['League', 'Total', 'Correct']
                league_perf['Accuracy'] = (league_perf['Correct'] / league_perf['Total'] * 100).round(1)
                
                st.subheader("League Performance")
                st.dataframe(
                    league_perf[['League', 'Total', 'Accuracy']],
                    hide_index=True,
                    use_container_width=True
                )
        
        st.markdown("---")
    
    def render_export(self, df: pd.DataFrame):
        """Export bölümü."""
        st.header("💾 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON export
            json_data = df.to_json(orient='records', date_format='iso')
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        with col3:
            # Summary report
            summary = self.get_model_summary(df)
            summary_json = summary.to_json(orient='records')
            st.download_button(
                label="📥 Download Summary",
                data=summary_json,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    def run(self):
        """Dashboard'u çalıştır."""
        # Header
        self.render_header()
        
        # Veri yükle
        df = self.load_data()
        
        if df.empty:
            st.warning("⚠️ No predictions found in database!")
            st.info("Make some predictions first to see the dashboard.")
            return
        
        # Özet
        summary = self.get_model_summary(df)
        daily = self.get_daily_accuracy(df)
        
        # Bölümler
        self.render_overview(df, summary)
        self.render_model_comparison(summary)
        self.render_trends(daily, df)
        self.render_recent_predictions(df)
        self.render_detailed_analysis(df)
        self.render_export(df)
        
        # Footer
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Ana fonksiyon."""
    import sys
    
    # CLI args
    db_path = "predictions.db"
    
    if len(sys.argv) > 1:
        if '--db-path' in sys.argv:
            idx = sys.argv.index('--db-path')
            if idx + 1 < len(sys.argv):
                db_path = sys.argv[idx + 1]
    
    # Dashboard
    dashboard = PerformanceDashboard(db_path=db_path)
    dashboard.run()


if __name__ == "__main__":
    main()
