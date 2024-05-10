import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

df = pd.read_csv('reto/arteDeLaAnalitica/covid19_tweets.csv')

#numeric_columns = df.select_dtypes(include=['float64', 'int64'])
df['user_created_year'] = pd.to_datetime(df['user_created']).dt.year
df['user_verified_numeric'] = df['user_verified'].astype(int)
covid_keywords = ['COVID19', 'Covid19', 'coronavirus']
df['has_covid_hashtag'] = df['hashtags'].apply(lambda x: 1 if any(keyword.lower() in str(x).lower() for keyword in covid_keywords) else 0)
correlation_matrix = df[["user_created_year","user_followers","user_friends","user_favourites","user_verified_numeric","has_covid_hashtag"]].corr()
print(correlation_matrix)
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
plt.show()


X=df[['user_followers','user_verified_numeric']]
m = KMeans(n_clusters=2, random_state=5)
m.fit(X)
X["cl"] = m.labels_

plt.figure(figsize=(8, 6))
scatter = plt.scatter(x='user_followers', y='user_verified_numeric', c='cl', data=X, cmap='gist_rainbow')
plt.title('KMeans Clustering')
plt.xlabel('user followers')
plt.ylabel('user verified')
plt.colorbar(scatter, label='Cluster')
plt.grid(True)
plt.show()
