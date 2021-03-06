'''
Breast Cancer Breast-Cancer-Classi-cation-With-Machine-Learning

'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score,confusion_matrix
from sklearn.neighbors import KNeighborsClassifier,NeighborhoodComponentsAnalysis, LocalOutlierFactor
from sklearn.decomposition import PCA

# warning library
import warnings
warnings.filterwarnings('ignore')


# data read
data= pd.read_csv('data.csv')
yol = data
data.drop(['Unnamed: 32','id'],inplace = True, axis=1)
#0 benign cells 
#1 malignant cells
data=data.rename(columns={"diagnosis":"target"})
plt.figure()
sns.countplot(data["target"])
print(data.target.value_counts())
plt.show()
plt.savefig('plot0.png')
data["target"]=[1 if i.strip() == "M" else 0 for i in data.target]


print(data.head())

print("Data Shape",data.shape)

data.info()

describe=data.describe()
data=data.iloc[:,0:31]

#%% EDA

# Correlation
plt.figure()
corr_matrix = data.corr()
sns.clustermap(corr_matrix,annot=True, fmt='.2f')
plt.title('correlation between features')
plt.show()

plt.figure()
threshold=0.50
filtre =np.abs(corr_matrix["target"])>threshold
corr_features=corr_matrix.columns[filtre].tolist()
sns.clustermap(data[corr_features].corr(),annot=True, fmt='.2f')
plt.title('correlation between features with threshold 0.75')
plt.tight_layout()
plt.show()
plt.savefig('plot1.png')

"""
there some correlated features
"""
# box plot
plt.figure()
data_melted= pd.melt(data,id_vars="target",var_name="Features",value_name="value")

plt.figure()
sns.boxplot(x="Features",y="value",hue="target",data=data_melted)
plt.xticks(rotation=90)
plt.show()



"""
Standardization- normalization

"""
plt.figure()
# pair plot
sns.pairplot(data[corr_features],diag_kind='kde',markers="+",hue="target")
plt.show()

#%%
y= data.target
x=data.drop(['target'],axis=1)
columns=x.columns.tolist()
# outlier detection
clf=LocalOutlierFactor(n_neighbors=2)
y_pred=clf.fit_predict(x)
X_score = clf.negative_outlier_factor_
outlier_score=pd.DataFrame()
outlier_score["score"]=X_score
#threshold
threshold=-2.5
filter1 =outlier_score["score"]<threshold
outlier_index=outlier_score[filter1].index.tolist()




# plt scatter 
plt.figure()
plt.scatter(x.iloc[outlier_index,0],x.iloc[outlier_index,1],color="blue",s=50,label="Outliers")
plt.scatter(x.iloc[:,0],x.iloc[:,1],color="k",s=3,label="Data Points")
plt.show()
#normalization
radius=(X_score.max()- X_score)-(X_score.max() - X_score.min())
outlier_score["radius"]=radius
plt.scatter(x.iloc[:,0],x.iloc[:,1],s =1000*radius, edgecolors="r",facecolors="none",label="Outlier Scores")
plt.legend()
plt.show()
plt.savefig('plot2.png')
# drop outliers

x=x.drop(outlier_index)
y=y.drop(outlier_index).values


# %%
# train test split
test_size=0.3
X_train,X_test,Y_train,Y_test=train_test_split(x,y,test_size=test_size,random_state=42)

#%% standization

sc = StandardScaler()
X_train=sc.fit_transform(X_train)
X_test =sc.transform(X_test)

x_train_df=pd.DataFrame(X_train,columns=columns)


# %%
# KNN method

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train,Y_train)
y_pred=knn.predict((X_test))
cm=confusion_matrix(Y_test,y_pred)
acc=accuracy_score(Y_test,y_pred)
# score= knn.score(X_test,Y_test)
# print("Score: ", score)
print("Accuary: ",acc)
print("confusion: ",cm)

# %%
# choose best parameters for knn

def KNN_Best_Params(x_train,x_test,y_train,y_test):
    k_range=list(range(1,31))
    weight_options=["uniform","distance"]
    print()
    param_grid=dict(n_neighbors=k_range,weights=weight_options)
    
    knn=KNeighborsClassifier()
    grid=GridSearchCV(knn,param_grid,cv=10,scoring= "accuracy")
    grid.fit(x_train,y_train)
    
    print("Best Training Score: {} with parameters: {}".format(grid.best_score_,grid.best_params_))
    print()
    
    
    knn = KNeighborsClassifier(**grid.best_params_)
    knn.fit(x_train,y_train)
    
    y_pred_test =knn.predict(x_test)
    y_pred_train =knn.predict(x_train)
    
    cm_test =confusion_matrix(y_test,y_pred_test)
    cm_train = confusion_matrix(y_train,y_pred_train)
    
    acc_test =accuracy_score(y_test,y_pred_test)
    acc_train = accuracy_score(y_train,y_pred_train)
    print("Test score: {}, Train Score : {}".format(acc_test,acc_train))
    print()
    
    print("Cm test")
    print(cm_test)
    print("CM train")
    print(cm_train)
    group_names = ['True Neg','False Pos','False Neg','True Pos']
    group_counts = ["{0:0.0f}".format(value) for value in
                cm_train.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in
                      cm_train.flatten()/np.sum(cm_train)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    plt.figure()
    sns.heatmap(cm_train, annot=labels, fmt='', cmap='Blues')
    plt.title("confusion matrix train")
    plt.xlabel("predicted")
    plt.ylabel("true")
    plt.show()
    plt.savefig('plot3.png')
    
    group_names = ['True Neg','False Pos','False Neg','True Pos']
    group_counts = ["{0:0.0f}".format(value) for value in
                cm_test.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in
                      cm_test.flatten()/np.sum(cm_test)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    plt.figure()
    sns.heatmap(cm_test, annot=labels, fmt='', cmap='Blues')
    plt.title("confusion matrix test")
    plt.xlabel("predicted")
    plt.ylabel("true")
    plt.show()
    plt.savefig('plot4.png')
    return grid
    
grid = KNN_Best_Params(X_train,X_test,Y_train,Y_test)



#%%
# # PCA
# reduced the data to two dimensions
scaler =StandardScaler()
x_scaled = scaler.fit_transform(x)
pca =PCA(n_components=2)
pca.fit(x_scaled)
X_reduced_pca =pca.transform(x_scaled)
pca_data = pd.DataFrame(X_reduced_pca,columns =["p1","p2"])
pca_data["target"]=y
plt.figure()
sns.scatterplot(x= "p1", y= "p2",hue= "target",data= pca_data)
plt.title("PCA: p1 vs p2")
plt.show()
plt.savefig('plot5.png')

X_train_pca,X_test_pca,Y_train_pca,Y_test_pca=train_test_split(X_reduced_pca,
                                                               y,test_size=test_size,
                                                               random_state=42)

grid_pca = KNN_Best_Params(X_train_pca,X_test_pca,Y_train_pca,Y_test_pca)

# visualize
cmap_light =ListedColormap(['orange','cornflowerblue'])
cmap_bold = ListedColormap(['darkorange','darkblue'])

h = .05 # step size in the mesh
X = X_reduced_pca

x_min , x_max = X[:,0].min()-1,X[:,0].max()+1
y_min , y_max = X[:,0].min()-1,X[:,0].max()+1
xx,yy = np.meshgrid(np.arange(x_min,x_max,h),np.arange(y_min,y_max,h))

Z = grid_pca.predict(np.c_[xx.ravel(),yy.ravel()])

# put the result into a color plot
Z =Z.reshape(xx.shape)

plt.pcolormesh(xx,yy,Z, cmap = cmap_light)
# plot also the training  points
plt.figure()
plt.scatter(X[:,0],X[:,1],c=y,cmap =cmap_bold,edgecolor ='k',s=20)
plt.xlim(xx.min(),xx.max())
plt.ylim(yy.min(),yy.max())
plt.title("%i-Class classification(k = %i, weights ='%s')".format((len(np.unique(y))),
                                                                   grid_pca.best_estimator_.n_neighbors,
                                                                   grid_pca.best_estimator_.weights))
plt.show()
plt.savefig('plot6.png')


#%%
# NCA neighborhood componenet analysis
nca =NeighborhoodComponentsAnalysis(n_components=2,random_state=42)
nca.fit(x_scaled,y)
X_reduced_nca = nca.transform(x_scaled)
nca_data = pd.DataFrame(X_reduced_nca,columns = ["p1","p2"])
nca_data["target"] = y
plt.figure()
sns.scatterplot(x ="p1",y="p2",hue = "target",data = nca_data)
plt.title("NCA: 0 benign cells 1 malignant cells")
plt.show()
plt.savefig('plot7.png')

X_train_nca,X_test_nca,Y_train_nca,Y_test_nca=train_test_split(X_reduced_nca,
                                                                y,test_size=test_size,
                                                                random_state=42)

grid_nca = KNN_Best_Params(X_train_nca,X_test_nca,Y_train_nca,Y_test_nca)




