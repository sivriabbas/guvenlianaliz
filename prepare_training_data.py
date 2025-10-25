"""
📊 DATASET HAZIRLAMA - PHASE 7.B1
==================================
training_dataset.csv'yi ML model eğitimi için hazırla
Train/Test split, normalization, feature engineering
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils import class_weight
import joblib
import json
from datetime import datetime


class DatasetPreparator:
    """Training dataset'i hazırla"""
    
    def __init__(self, csv_path='training_dataset.csv'):
        self.csv_path = csv_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        print(f"✅ Dataset Preparator başlatıldı")
    
    def load_data(self):
        """CSV'den veriyi yükle"""
        print(f"\n📂 Veri yükleniyor: {self.csv_path}")
        
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"✅ {len(self.df)} satır, {len(self.df.columns)} sütun yüklendi")
            return True
        except FileNotFoundError:
            print(f"❌ Dosya bulunamadı: {self.csv_path}")
            print("⚠️  Önce calculate_historical_factors.py çalıştırın!")
            return False
        except Exception as e:
            print(f"❌ Yükleme hatası: {str(e)}")
            return False
    
    def explore_data(self):
        """Veri keşfi"""
        print("\n" + "="*80)
        print("🔍 VERİ KEŞFİ")
        print("="*80)
        
        # Temel bilgiler
        print(f"\n📊 Dataset Boyutu:")
        print(f"   Satırlar: {len(self.df)}")
        print(f"   Sütunlar: {len(self.df.columns)}")
        
        # İlk 5 satır
        print(f"\n📋 İlk 5 Satır:")
        print(self.df.head().to_string())
        
        # Veri tipleri
        print(f"\n🔢 Veri Tipleri:")
        print(self.df.dtypes.value_counts())
        
        # Eksik değerler
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(f"\n⚠️  Eksik Değerler:")
            print(missing[missing > 0])
        else:
            print(f"\n✅ Eksik değer yok")
        
        # Hedef değişken dağılımı
        if 'result' in self.df.columns:
            print(f"\n🎯 Hedef Değişken Dağılımı (result):")
            result_counts = self.df['result'].value_counts()
            for result, count in result_counts.items():
                label = {'H': 'Ev Sahibi Galibiyet', 'A': 'Deplasman Galibiyet', 'D': 'Beraberlik'}[result]
                pct = (count / len(self.df)) * 100
                print(f"   {label:25}: {count:4} ({pct:5.1f}%)")
        
        # Temel istatistikler
        print(f"\n📈 Temel İstatistikler:")
        print(self.df.describe().to_string())
    
    def feature_engineering(self):
        """Özellik mühendisliği"""
        print("\n" + "="*80)
        print("⚙️ ÖZELLİK MÜHENDİSLİĞİ")
        print("="*80)
        
        initial_features = len(self.df.columns)
        
        # 1. ELO tabanlı özellikler
        if 'home_elo' in self.df.columns and 'away_elo' in self.df.columns:
            self.df['elo_ratio'] = self.df['home_elo'] / (self.df['away_elo'] + 1)
            self.df['elo_sum'] = self.df['home_elo'] + self.df['away_elo']
            print("   ✅ ELO ratio ve sum eklendi")
        
        # 2. Form tabanlı özellikler
        if 'home_form' in self.df.columns and 'away_form' in self.df.columns:
            self.df['form_ratio'] = self.df['home_form'] / (self.df['away_form'] + 1)
            self.df['form_sum'] = self.df['home_form'] + self.df['away_form']
            print("   ✅ Form ratio ve sum eklendi")
        
        # 3. Pozisyon tabanlı özellikler
        if 'home_position' in self.df.columns and 'away_position' in self.df.columns:
            self.df['position_sum'] = self.df['home_position'] + self.df['away_position']
            self.df['top_clash'] = ((self.df['home_position'] <= 5) & 
                                   (self.df['away_position'] <= 5)).astype(int)
            self.df['relegation_battle'] = ((self.df['home_position'] >= 15) | 
                                           (self.df['away_position'] >= 15)).astype(int)
            print("   ✅ Pozisyon özellikler eklendi")
        
        # 4. H2H tabanlı özellikler
        if 'h2h_win_rate' in self.df.columns:
            self.df['h2h_advantage'] = (self.df['h2h_win_rate'] - 0.5) * 2  # -1 ile 1 arası
            print("   ✅ H2H advantage eklendi")
        
        # 5. Ev avantajı composite
        if 'home_advantage' in self.df.columns and 'away_disadvantage' in self.df.columns:
            self.df['total_home_edge'] = self.df['home_advantage'] + self.df['away_disadvantage']
            print("   ✅ Total home edge eklendi")
        
        # 6. Lig bazlı encoding
        if 'league' in self.df.columns:
            league_dummies = pd.get_dummies(self.df['league'], prefix='league')
            self.df = pd.concat([self.df, league_dummies], axis=1)
            print(f"   ✅ Lig one-hot encoding ({len(league_dummies.columns)} özellik)")
        
        # 7. Sezon bazlı encoding
        if 'season' in self.df.columns:
            season_dummies = pd.get_dummies(self.df['season'], prefix='season')
            self.df = pd.concat([self.df, season_dummies], axis=1)
            print(f"   ✅ Sezon one-hot encoding ({len(season_dummies.columns)} özellik)")
        
        final_features = len(self.df.columns)
        added = final_features - initial_features
        
        print(f"\n   📊 {initial_features} → {final_features} özellik (+{added})")
    
    def prepare_features(self):
        """Model için özellik ve hedef değişkenleri hazırla"""
        print("\n" + "="*80)
        print("🎯 ÖZELLİK HAZIRLAMA")
        print("="*80)
        
        # Meta bilgileri kaldır
        meta_columns = ['match_id', 'date', 'home_team', 'away_team', 'league', 'season',
                       'home_goals', 'away_goals', 'result']
        
        # Özellik sütunları
        feature_columns = [col for col in self.df.columns if col not in meta_columns]
        
        print(f"\n   📋 Toplam {len(feature_columns)} özellik kullanılacak:")
        for i, col in enumerate(feature_columns, 1):
            if i <= 10 or i > len(feature_columns) - 5:
                print(f"      {i:2}. {col}")
            elif i == 11:
                print(f"      ... ({len(feature_columns) - 15} özellik daha)")
        
        # X (features) ve y (target)
        X = self.df[feature_columns]
        
        # Hedef değişkeni encode et: H=2, D=1, A=0
        y = self.df['result'].map({'H': 2, 'D': 1, 'A': 0})
        
        print(f"\n   ✅ X shape: {X.shape}")
        print(f"   ✅ y shape: {y.shape}")
        
        # Eksik değerleri doldur
        if X.isnull().sum().sum() > 0:
            print(f"\n   ⚠️  Eksik değerler dolduruluyor...")
            X = X.fillna(X.mean())
        
        # Sonsuz değerleri kontrol et
        X = X.replace([np.inf, -np.inf], 0)
        
        return X, y, feature_columns
    
    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Train/Test split"""
        print("\n" + "="*80)
        print("✂️ TRAIN/TEST SPLIT")
        print("="*80)
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\n   📊 Train Set: {len(self.X_train)} samples ({(1-test_size)*100:.0f}%)")
        print(f"   📊 Test Set:  {len(self.X_test)} samples ({test_size*100:.0f}%)")
        
        # Sınıf dağılımı
        print(f"\n   🎯 Train Set Dağılımı:")
        train_dist = self.y_train.value_counts().sort_index()
        for class_id, count in train_dist.items():
            label = {2: 'Ev Galibiyet', 1: 'Beraberlik', 0: 'Deplasman Galibiyet'}[class_id]
            pct = (count / len(self.y_train)) * 100
            print(f"      {label:20}: {count:4} ({pct:5.1f}%)")
        
        print(f"\n   🎯 Test Set Dağılımı:")
        test_dist = self.y_test.value_counts().sort_index()
        for class_id, count in test_dist.items():
            label = {2: 'Ev Galibiyet', 1: 'Beraberlik', 0: 'Deplasman Galibiyet'}[class_id]
            pct = (count / len(self.y_test)) * 100
            print(f"      {label:20}: {count:4} ({pct:5.1f}%)")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def normalize_data(self):
        """Veriyi normalize et (StandardScaler)"""
        print("\n" + "="*80)
        print("📏 NORMALİZASYON")
        print("="*80)
        
        # Train set üzerinde fit et
        self.scaler.fit(self.X_train)
        
        # Her iki seti de transform et
        self.X_train_scaled = self.scaler.transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        # DataFrame'e çevir
        self.X_train_scaled = pd.DataFrame(
            self.X_train_scaled, 
            columns=self.X_train.columns,
            index=self.X_train.index
        )
        self.X_test_scaled = pd.DataFrame(
            self.X_test_scaled,
            columns=self.X_test.columns,
            index=self.X_test.index
        )
        
        print(f"\n   ✅ Train set normalize edildi: {self.X_train_scaled.shape}")
        print(f"   ✅ Test set normalize edildi: {self.X_test_scaled.shape}")
        
        # Örnek istatistikler
        print(f"\n   📊 Normalize Edilmiş Veri Özeti (ilk 5 özellik):")
        print(self.X_train_scaled.iloc[:, :5].describe().to_string())
    
    def calculate_class_weights(self):
        """Dengesiz sınıflar için ağırlıklar hesapla"""
        print("\n" + "="*80)
        print("⚖️ SINIF AĞIRLIKLARI")
        print("="*80)
        
        # Sklearn class_weight hesapla
        classes = np.unique(self.y_train)
        weights = class_weight.compute_class_weight(
            'balanced',
            classes=classes,
            y=self.y_train
        )
        
        class_weights_dict = dict(zip(classes, weights))
        
        print(f"\n   📊 Hesaplanan Ağırlıklar:")
        for class_id, weight in class_weights_dict.items():
            label = {2: 'Ev Galibiyet', 1: 'Beraberlik', 0: 'Deplasman Galibiyet'}[class_id]
            print(f"      {label:20}: {weight:.3f}")
        
        return class_weights_dict
    
    def save_datasets(self, output_dir='prepared_data'):
        """Hazırlanan datasetleri kaydet"""
        print("\n" + "="*80)
        print("💾 KAYDETME")
        print("="*80)
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # NumPy arrays olarak kaydet (hızlı yükleme için)
        np.save(f'{output_dir}/X_train.npy', self.X_train_scaled.values)
        np.save(f'{output_dir}/X_test.npy', self.X_test_scaled.values)
        np.save(f'{output_dir}/y_train.npy', self.y_train.values)
        np.save(f'{output_dir}/y_test.npy', self.y_test.values)
        
        # Scaler'ı kaydet
        joblib.dump(self.scaler, f'{output_dir}/scaler.pkl')
        
        # Feature names kaydet
        feature_names = self.X_train.columns.tolist()
        with open(f'{output_dir}/feature_names.json', 'w') as f:
            json.dump(feature_names, f, indent=2)
        
        # Metadata kaydet
        metadata = {
            'created_at': datetime.now().isoformat(),
            'total_samples': len(self.df),
            'train_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'n_features': len(feature_names),
            'test_size': 0.2,
            'random_state': 42,
            'class_distribution': {
                'train': self.y_train.value_counts().to_dict(),
                'test': self.y_test.value_counts().to_dict()
            }
        }
        
        with open(f'{output_dir}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n   ✅ X_train.npy ({self.X_train_scaled.shape})")
        print(f"   ✅ X_test.npy ({self.X_test_scaled.shape})")
        print(f"   ✅ y_train.npy ({self.y_train.shape})")
        print(f"   ✅ y_test.npy ({self.y_test.shape})")
        print(f"   ✅ scaler.pkl")
        print(f"   ✅ feature_names.json ({len(feature_names)} features)")
        print(f"   ✅ metadata.json")
        
        print(f"\n   📁 Klasör: {output_dir}/")
    
    def process(self):
        """Tam işlem pipeline'ı"""
        print("\n" + "="*80)
        print("🚀 DATASET HAZIRLAMA BAŞLADI")
        print("="*80)
        
        # 1. Veri yükle
        if not self.load_data():
            return False
        
        # 2. Veri keşfi
        self.explore_data()
        
        # 3. Feature engineering
        self.feature_engineering()
        
        # 4. Özellik hazırlama
        X, y, feature_columns = self.prepare_features()
        
        # 5. Train/Test split
        self.split_data(X, y)
        
        # 6. Normalizasyon
        self.normalize_data()
        
        # 7. Sınıf ağırlıkları
        class_weights = self.calculate_class_weights()
        
        # 8. Kaydet
        self.save_datasets()
        
        print("\n" + "="*80)
        print("✅ DATASET HAZIRLAMA TAMAMLANDI!")
        print("="*80)
        
        return True


# Test & Run
if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 DATASET HAZIRLAMA - PHASE 7.B1")
    print("="*80)
    
    # Dataset hazırlayıcı oluştur
    preparator = DatasetPreparator('training_dataset.csv')
    
    # Tam işlemi çalıştır
    success = preparator.process()
    
    if success:
        print("\n" + "="*80)
        print("🎯 SONRAKİ ADIMLAR")
        print("="*80)
        print("\n   1. prepared_data/ klasörünü kontrol edin")
        print("   2. tune_xgboost.py ile XGBoost model eğitimi yapın")
        print("   3. tune_lightgbm.py ile LightGBM model eğitimi yapın")
        print("   4. evaluate_models.py ile modelleri karşılaştırın")
        print("\n" + "="*80)
    else:
        print("\n❌ Dataset hazırlama başarısız!")
        print("⚠️  Önce historical_data_collector.py ve calculate_historical_factors.py çalıştırın")
