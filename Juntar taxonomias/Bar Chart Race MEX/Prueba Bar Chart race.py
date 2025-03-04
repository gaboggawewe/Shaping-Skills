import pandas as pd
import bar_chart_race as bcr

# Crear un DataFrame de ejemplo
data = {
    'A': [10, 20, 30, 50, 80],
    'B': [5, 15, 25, 40, 60],
    'C': [3, 10, 20, 35, 55],
    'D': [1, 5, 15, 30, 45]
}
df = pd.DataFrame(data, index=pd.date_range('2023-01-01', periods=5, freq='YE'))

# Crear la animación
bcr.bar_chart_race(
    df=df,
    filename='barchart_race.mp4',
    title='Evolución del Top 10 a lo largo del tiempo'
)