

from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import bisect
import math
import timeit

stop_words=set(stopwords.words('english'))
ps=SnowballStemmer(language='english')
scores={'t':4,'i':3.5,'c':2,'b':3,'e':1.5,'r':1.5}

with open("stats.txt","r") as f:
    size=f.readline()
    docs=int(f.readline())
    inv_tokens=int(f.readline())
first_words=[]
for i in range(1,docs+1):
    f=open("../Final1/merged"+str(i)+".txt","r")
    s=f.readline()
    p=s.find(",")
    first_words.append(s[:p])
docid=0
freq_docs={}
for i in range(1,2260):
    f=open("../Final1/file"+str(i)+".txt","r")
    line=f.readline()
    while(len(line)>0):
        docid+=1
        freq_docs[docid]=line
        line=f.readline()
        
docid=0

def intersect(A,B):
    ans=[]
    i=j=0
    while(i<len(A) and j<len(B)):
        if(A[i]==B[j]):
            ans.append(A[i])
        else:
            if(A[i]<B[j]):
                i+=1
            else:
                j+=1
    return ans 

def process_plain_queries(plain_query):
    tokens=word_tokenize(plain_query.lower())
    new_tokens=set()
    mydict={}
    for token in tokens:
        if token.isalnum() and token not in stop_words:
            if(token.isnumeric() and len(token)==4):
                s=ps.stem(token)
            else:
                s=ps.stem(token)
            new_tokens.add(s)
    for token in new_tokens:
        index_id=bisect.bisect(first_words,token,0,len(first_words))
        with open("../Final1/merged"+str(index_id)+".txt","r") as f:
            count=0
            s=f.readline()
            while(len(s)>0):
                p=s.find(",")
                if(s[:p]==token):
                    mydict[token]=s[p+1:-2].split(",")
                    break
                s=f.readline()
    tf_idf={}
    for key in mydict.keys():
        
        docid=0
        idf=16936277/len(mydict[key])
        print(key,len(mydict[key]))
        postings_calc=0
        for posting in mydict[key]:
            postings_calc+=1
            print(len(mydict[key])-postings_calc,end='\r')
            temp=posting.split(":")
            docid=docid+int(temp[0])
            p=temp[1].find('t')
            freq=0
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['t']
                temp[1]=temp[1][p+1:]
            p=temp[1].find('i')
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['i']
                temp[1]=temp[1][p+1:]
            p=temp[1].find('c')
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['c']
                temp[1]=temp[1][p+1:]
            p=temp[1].find('e')
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['e']
                temp[1]=temp[1][p+1:]
            p=temp[1].find('r')
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['r']
                temp[1]=temp[1][p+1:]
            p=temp[1].find('b')
            if(p!=-1):
                freq+=int(temp[1][:p])*scores['b']
            details=freq_docs[docid].split(",")
            if docid in tf_idf:
                tf_idf[docid][1]+=math.log(1+freq/int(details[0]))*math.log(idf)
            else:
                tf_idf[docid]=[details[1],math.log(1+freq/int(details[0]))*math.log(idf)]
            
    sorted_tfidf=sorted(tf_idf.items(),key=lambda item:item[1][1])[-10:]
    sorted_tfidf.reverse()
    return sorted_tfidf
    
def process_field_queries(field_query):
    if(field_query[-1]=='\n'):
        field_query=field_query[:-1]
    queries=field_query.split(":")
    queries1=[queries[0]]
    for i in range(1,len(queries)-1):
        queries1.append(queries[i][:-1])
        queries1.append(queries[i][-1])
    queries1.append(queries[-1])
    final_tfidfs=[]
    for i in range(1,len(queries1),2):
        c=queries1[i-1]
        field=queries1[i]
        tokens=word_tokenize(field)
        new_tokens=set()
        mydict={}
        idf={}
        for token in tokens:
            if token not in stop_words:
                s=ps.stem(token)
                new_tokens.add(s)
        for token in new_tokens:
            index_id=bisect.bisect(first_words,token,0,len(first_words))
            with open("../Final1/merged"+str(index_id)+".txt","r") as f:
                s=f.readline()
                while(len(s)>0):
                    p=s.find(",")
                    if(s[:p]==token):
                        mydict[token]=s[p+1:-2].split(",")
                        idf[token]=16936277/len(mydict[token])
                        break
                    s=f.readline()
        
        tf={}
        docs=set()
        for key in mydict.keys():
            docid=0
            if key not in tf:
                tf[key]={}
            for posting in mydict[key]:
                temp=posting.split(":")
                docid=docid+int(temp[0])
                p=temp[1].find(c)
                if(p!=-1):
                    j=p-1
                    while(j>=0 and temp[1][j].isdigit()):
                        j-=1
                    freq=int(temp[1][j+1:p])*scores[c]
                    if docid in tf:
                        tf[key][docid]+=freq
                    else:
                        tf[key][docid]=freq
                    docs.add(docid)
            
        
        tfidf={}
        for docid in docs:
            for token in new_tokens:
                if token in tf and docid in tf[token]:
                    s=freq_docs[docid]
                    p=s.find(",")
                    N=int(s[:p])
                    title=s[p+1:]
                    tfidf[docid]=[title,math.log(1+tf[token][docid]/N)*math.log(idf[token])]
        sorted_tfidf=sorted(tfidf.items(),key=lambda item:item[1][1],reverse=True)[:10]
        final_tfidfs.extend(sorted_tfidf)                   
    return final_tfidfs                   
        
fo=open("2020201011_queries_op.txt","w")
queries_resolved=0
with open("2020201011_queries.txt","r") as q:
    query=q.readline()
    while(len(query)>0):
        p=query.find(":")
        if(p!=-1):
            plain_query=query[:p-1].lower()
            field_query=query[p-1:].lower()
        else:
            plain_query=query.lower()
            field_query=""            
        
        start=timeit.default_timer()
        l1=[]
        if(len(plain_query)>0):
            l1=process_plain_queries(plain_query)
        l2=[]
        if(len(field_query)>0):
            l2=process_field_queries(field_query)
        if(len(l1)>0):
            l2.extend(l1)
        final_tfidfs=sorted(l2,key=lambda item:item[1][1],reverse=True)[:10]
        for x in final_tfidfs:
            fo.write(str(x[0])+", "+x[1][0][:-1]+"\n")
        fo.write(str(timeit.default_timer()-start)+"\n\n")
        queries_resolved+=1
        print(queries_resolved)
        query=q.readline()
        
fo.close()
        
