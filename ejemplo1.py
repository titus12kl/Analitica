import pandas as pd
df=pd.read_csv('d:/tec/semanatec4/retoAnalitica/arteDeLaAnalitica/avocado_full.csv')

df_filtered = df[df['region'].isin(['California', 'NewYork', 'Charlotte'])]

total_bags_by_region = df_filtered.groupby('region')['Total Bags'].sum()

mean_totalbags = df_filtered.groupby('region')['Total Bags'].mean()

desviacion_estandar = df_filtered.groupby('region')['Total Bags'].std()


percentages_by_region = df_filtered.groupby('region')[['Small Bags', 'Large Bags', 'XLarge Bags']].sum() / total_bags_by_region.values[:, None] * 100

print("porcentajes de bolsas")
print(percentages_by_region)

print("El promedio de bolsas por region")
print(mean_totalbags)

print("produccion total de bolsas por region")
print(total_bags_by_region)

print("desviacion estandar del promedio por region")
print(desviacion_estandar)