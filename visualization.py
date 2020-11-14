import pandas as pd
data=pd.read_csv('jobs.csv')
data['skills']=data['skills'].apply(eval)
top_25=pd.Series([s for skills in data['skills'] for s in skills]).value_counts().head(25)

from matplotlib import pyplot as plt
# plt.show(top_25['index'],top_25['counts'])
top_25.plot(kind='barh')
plt.show()