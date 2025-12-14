import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

print("1. Descargando datos (esto puede tardar un poco si el internet es lento)...")
url_train = 'https://raw.githubusercontent.com/Jehuty4949/NSL_KDD/refs/heads/master/KDDTest%2B.txt'
col_names = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","class","difficulty"]

df = pd.read_csv(url_train, header=None, names=col_names)

print("2. Procesando datos...")
df['target'] = df['class'].apply(lambda x: 0 if x == 'normal' else 1)
codificador = LabelEncoder()
columns_to_encode = ['protocol_type', 'service', 'flag']
for col in columns_to_encode:
    df[col] = codificador.fit_transform(df[col])

df = df.drop(['class', 'difficulty'], axis=1)

X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print("3. Entrenando la IA (Paciencia, tu CPU está trabajando)...")
# Reduje n_estimators a 50 para que sea más liviano para tu CPU
modelo = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
modelo.fit(X_train, y_train)

print("4. Guardando los nuevos archivos compatibles...")
joblib.dump(modelo, 'modelo_ia_nids.pkl')
joblib.dump(codificador, 'codificador_datos.pkl')
print("¡LISTO! Ya puedes ejecutar app.py")