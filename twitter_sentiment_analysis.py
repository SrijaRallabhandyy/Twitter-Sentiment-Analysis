# -*- coding: utf-8 -*-
"""Twitter Sentiment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SprwsS8yIIZSZnjZvy45wBYvcORyQVao
"""

# Library to work with regular expressions, required during cleaning the data
import re
# Working with numpy arrays during data exploration, like count 
import numpy as np 
# Used to store the csv data in data frames and perform various operations like groupby etc
import pandas as pd 
# The below given libraries are used for plotting various graphs during data exploration
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# The below given library is used for stemminga dn lemmatization
from nltk.stem import WordNetLemmatizer
# Scikit Learn is the library used to apply various algorithms as shown below
# Import used for Support Vector Machine Library
from sklearn.svm import LinearSVC 
# Import to implement Beroulli Naive Bayes Algorithm for classification
from sklearn.naive_bayes import BernoulliNB 
# Logistic regresssion for classification
from sklearn.linear_model import LogisticRegression 
# Import to split the complete dataset into train and test data
from sklearn.model_selection import train_test_split 
 # Import used for working on Term Frequency and Inverse Docuemnt Frequency
from sklearn.feature_extraction.text import TfidfVectorizer
#Code used to asses the algorithm using Accuracy, F1Score etc, and also used to build the confusion matrix. To draw the AUC-ROC Curve
from sklearn.metrics import confusion_matrix, classification_report

# mounting the google drive. 
# Used to load the dataset in google drive and use it in the run time environment whenever necessary
from google.colab import drive
drive.mount('/content/drive')

# Importing the dataset
DATASET_COLUMNS=['target','ids','date','flag','user','text'] 
DATASET_ENCODING = "ISO-8859-1"
df = pd.read_csv('/content/drive/MyDrive/Explorytics_Dataset/Project_Data.csv', encoding=DATASET_ENCODING, names=DATASET_COLUMNS)
df.sample(5)

# Printing the column names of the dataframe
df.columns 
# Printing the dimensions and datatype details of the dataframe
df.info() 
# Displaying the number of rows contaning null values
np.sum(df.isnull().any(axis=1))

# Printing the number of unique values of the dataframe under the column named 'target'
df['target'].nunique()

# Plotting the distribution for dataset.
ax = df.groupby('target').count().plot(kind='bar', title='Distribution of data',legend=False)
ax.set_xticklabels(['Negative','Positive'], rotation=0)
# Storing data in lists.
text, sentiment = list(df['text']), list(df['target'])

import seaborn as sns
#  Printing the number of value/tweets under the postive/negative target category 
# Here 0 represents Negative sentiment and 4 represents Positive Sentiment
sns.countplot(x='target', data=df)

# Extracting the tweet text and target(Sentinment) columns data into a new dataframe
data=df[['text','target']]
# Under the target values replacing 4 by 1 which means, now,
# Here 0 represents Negative sentiment and 1 represents Positive Sentiment
data['target'] = data['target'].replace(4,1)
data['target'].unique()
# Storing the text of the tweets having positive sentiment in data_pos and negative sentiments in data_neg
data_pos = data[data['target'] == 1]
data_neg = data[data['target'] == 0]

# Concatenating the grouped negative and positive datasets to a single data set
# Currently, first 8 lakh rows would have positive sentiment and 8 lakh - 16 lakh rows represnt negative sentiment data
dataset = pd.concat([data_pos, data_neg])
# Coverting all the twitter text to lowercase
dataset['text']=dataset['text'].str.lower()
# Printing the last 50 lines of the dataset to see the sample
dataset['text'].tail(50)

import string
# Getting and Printing the list of all the punctuations under the library string
english_punctuations = string.punctuation
print(string.punctuation)
punctuations_list = english_punctuations
# A function to remove the punctuations from the collected tweets
def cleaning_punctuations(text):
    translator = str.maketrans('', '', punctuations_list)
    return text.translate(translator)
# Function call and storage of the cleaned data in the same column of the data frame 'dataset'
dataset['text']= dataset['text'].apply(lambda x: cleaning_punctuations(x))
dataset['text'].tail()

# A list which contains all the unnecessary words which are to be removed from the corpus during the data cleaning process
stopwordlist = ['a','u','r','about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and','any','are', 'as', 'at', 'be', 'because', 'been', 'before',"but","im","'",
             'being', 'below', 'between','both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each','few', 'for', 'from',
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into','is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most','my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours','ourselves', 'out', 'own', 're','s', 'same', 'she', "shes", 'should', "shouldve",'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
             'through', 'to', 'too','under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where','which','while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd","youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves',"now","day","want","going","day","today","go","work","guys"]

#  Converting the list to set so that the repeated values are not taken into consideration
STOPWORDS = set(stopwordlist)
# A function to clean the unnecessary words given in the list and combine the remaining words into a sentence
def cleaning_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])
# Function call and storage of the cleaned data in the same column of the data frame 'dataset'
dataset['text'] = dataset['text'].apply(lambda text: cleaning_stopwords(text))
dataset['text'].head()

# A function to clean the repeated charecters for example
# consider a tweet having the word "thankssss" which would be converted
# to thanks after running this function
def cleaning_repeating_char(text):
    return re.sub(r'(.)1+', r'1', text)
# Function call and storage of the cleaned data in the same column of the data frame 'dataset'
dataset['text'] = dataset['text'].apply(lambda x: cleaning_repeating_char(x))
dataset['text'].tail()

# A function used to cleaned the urls in the tweets using the regular expression
# In the regular expression we used a conceept of checking words
# starting with https or www, which would actually cover all the URLS
def cleaning_URLs(data):
    return re.sub('((www.[^s]+)|(https?://[^s]+))',' ',data)
# Function call and storage of the cleaned data in the same column of the data frame 'dataset'
dataset['text'] = dataset['text'].apply(lambda x: cleaning_URLs(x))
dataset['text'].tail()

# A function to remove numeric charecters from the tweets
def cleaning_numbers(data):
    return re.sub('[0-9]+', '', data)
dataset['text'] = dataset['text'].apply(lambda x: cleaning_numbers(x))
dataset['text'].tail()

# A tokenizer function to convert our complete sentence into tokens
from nltk.tokenize import TweetTokenizer
tokenizer = TweetTokenizer()
dataset['text'] = dataset['text'].apply(tokenizer.tokenize)
dataset['text'].head()

# A process where stemming is applied to each and every word in the sentence

# Stemming is basically removing the suffix from a word and reduce it to its root word.
# For example: ???Flying??? is a word and its suffix is ???ing???, 
# if we remove ???ing??? from ???Flying??? then we will get base word or root word which is ???Fly???. 
# We uses these suffix to create a new word from original stem word.
import nltk
st = nltk.PorterStemmer()
def stemming_on_text(data):
    text = [st.stem(word) for word in data]
    return text
dataset['text']= dataset['text'].apply(lambda x: stemming_on_text(x))
dataset['text'].head()

# Lemmatization usually refers to doing things properly with the use of a vocabulary and morphological analysis of words, 
# normally aiming to remove inflectional endings only and to return the base 
# or dictionary form of a word, which is known as the lemma .
import nltk
nltk.download('wordnet')
lm = nltk.WordNetLemmatizer()
def lemmatizer_on_text(data):
    text = [lm.lemmatize(word) for word in data]
    final_text=" ".join([word for word in text])
    return final_text
dataset['text'] = dataset['text'].apply(lambda x: lemmatizer_on_text(x))
dataset['text'].head()

# Taking the text and target into 2 variables required for application of algorithms
X=dataset.text
y=dataset.target

#  Taking the last 8lakh tweets to postive variable and plotting the word cloud
data_pos = dataset['text'][:800000]
plt.figure(figsize = (20,20))
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,collocations=False).generate(" ".join(str(v) for v in data_pos))
plt.imshow(wc)

#  Taking the first 8lakh tweets to negative variable and plotting the word cloud
data_neg = dataset['text'][800000:]
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
              collocations=False).generate(" ".join(str(v) for v in data_neg))
plt.figure(figsize = (20,20))
plt.imshow(wc)

# Taking 95% of the dataset into training data and 5% to test data
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.4, random_state =26105111)
print(X_train)

# Refer the following for TfidfVectorizer function 
# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=500000)
vectoriser.fit(X_train)
print('No. of feature_words: ', len(vectoriser.get_feature_names()))

X_train = vectoriser.transform(X_train)
X_test  = vectoriser.transform(X_test)

def model_Evaluate(model):
  # Predict values for Test dataset
  y_pred = model.predict(X_test)
  # Print the evaluation metrics for the dataset.
  print(classification_report(y_test, y_pred))
  # Compute and plot the Confusion matrix
  cf_matrix = confusion_matrix(y_test, y_pred)
  categories = ['Negative','Positive']
  group_names = ['True Neg','False Pos', 'False Neg','True Pos']
  group_percentages = ['{0:.2%}'.format(value) for value in cf_matrix.flatten() / np.sum(cf_matrix)]
  labels = [f'{v1}n{v2}' for v1, v2 in zip(group_names,group_percentages)]
  labels = np.asarray(labels).reshape(2,2)
  sns.heatmap(cf_matrix, annot = labels, cmap = 'Blues',fmt = '',
  xticklabels = categories, yticklabels = categories)
  plt.xlabel("Predicted values", fontdict = {'size':14}, labelpad = 10)
  plt.ylabel("Actual values" , fontdict = {'size':14}, labelpad = 10)
  plt.title ("Confusion Matrix", fontdict = {'size':18}, pad = 20)

# Bernoulli Naive Byes Classification and model evaluation
BNBmodel = BernoulliNB()
BNBmodel.fit(X_train, y_train)
model_Evaluate(BNBmodel)
y_pred1 = BNBmodel.predict(X_test)

# ROC-AUC Curve
from sklearn.metrics import roc_curve, auc
fpr, tpr, thresholds = roc_curve(y_test, y_pred1)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()

# Support Vector Machine Classification and model evaluation

SVCmodel = LinearSVC()
SVCmodel.fit(X_train, y_train)
model_Evaluate(SVCmodel)
y_pred2 = SVCmodel.predict(X_test)

# ROC-AUC Curve
from sklearn.metrics import roc_curve, auc
fpr, tpr, thresholds = roc_curve(y_test, y_pred2)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()

# Logistic Regression Classification and model evaluation

LRmodel = LogisticRegression(C = 2, max_iter = 1000, n_jobs=-1)
LRmodel.fit(X_train, y_train)
model_Evaluate(LRmodel)
y_pred3 = LRmodel.predict(X_test)

# ROC-AUC Curve
from sklearn.metrics import roc_curve, auc
fpr, tpr, thresholds = roc_curve(y_test, y_pred3)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()