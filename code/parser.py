import xml.sax
import re
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import os
from heapq import heapify,heappush,heappop
from collections import OrderedDict



def createInvertedIndex(index,file_no):
    inverted_index_path="./Final1/imf"+str(file_no)+".txt"
    
    with open(inverted_index_path,'w') as f:
        for token in sorted(index):
            f.write(token+",")
            docids=list(index[token].keys())
            f.write(str(docids[0])+","+str(docids[-1])+":")
            prev=0
            for docid in docids:
                gap=docid-prev
                f.write(str(gap)+":")
                if 't' in index[token][docid]:
                    count=str(index[token][docid]['t'])
                    f.write(count+"t")
                if 'i' in index[token][docid]:
                    count=str(index[token][docid]['i'])
                    f.write(count+"i")
                if 'c' in index[token][docid]:
                    count=str(index[token][docid]['c'])
                    f.write(count+"c")
                if 'e' in index[token][docid]:
                    count=str(index[token][docid]['e'])
                    f.write(count+"e")
                if 'r' in index[token][docid]:
                    count=str(index[token][docid]['r'])
                    f.write(count+"r")
                if 'b' in index[token][docid]:
                    count=str(index[token][docid]['b'])
                    f.write(count+"b")
                f.write(",")
                prev=docid
            f.write("\n")
        
                
def write_merged(inv_index,file_no):
    f=open("./Final1/merged"+str(file_no)+".txt","w")
    keys=list(inv_index.keys())[:min(len(inv_index),50000)]
    for key in keys:
        f.write(key+","+inv_index[key]+"\n")

def merge_files(no_of_files):
    path="./Final1/imf"
    fps=[]
    postings=[]
    inv_index=OrderedDict()
    prev_docids={}
    cur_docids={}
    words=[]
    count=0
    last_added=""
    for i in range(1,no_of_files+1):
        file_name=path+str(i)+".txt"
        f=open(file_name,"r")
        s=f.readline()
        p=s.find(':')
        temp=s[:p]
        temp1=temp.split(',')
        words.append([temp1[0],int(temp1[1]),int(temp1[2]),i-1])
        postings.append(s[p+1:-1])
        fps.append(f)
    heapify(words)
    while(len(words)>0):
        word,start,end,index=heappop(words)
        if word not in inv_index:
            inv_index[word]=postings[index]
            prev_docids[word]=[start,end]
            last_added=word
        else:
            gap=int(start)-int(prev_docids[word][1])
            #print(word,index)
            p=postings[index].find(",")
            first_doc=postings[index][:p]
            details=first_doc.split(":")
            details[0]=str(gap)
            inv_index[word]+=details[0]+":"+details[1]+","
            if(p+1<len(postings[index])):
                inv_index[word]+=postings[index][p+1:]
            prev_docids[word]=[start,end]
            
        s=fps[index].readline()
        if(len(s)>0):
            p=s.find(':')
            temp=s[:p]
            temp1=temp.split(',')
            heappush(words,[temp1[0],int(temp1[1]),int(temp1[2]),index])
            postings[index]=s[p+1:-1]
        if(len(inv_index)>50000):
            count+=1
            write_merged(inv_index,count)
            last_posting=inv_index[last_added]
            inv_index=OrderedDict()
            inv_index[last_added]=last_posting
    
    if(len(inv_index)>0):
        count+=1
        write_merged(inv_index,count)
    for fp in fps:
        fp.close()
    for i in range(1,no_of_files+1):
        os.remove(path+str(i)+".txt")
            
    
    

        
        


def write_token_count(titles,tokenCounts,file_no):
    path="./Final1/file"+str(file_no)+".txt"
    with open(path,"w") as f:
        for title,count in zip(titles,tokenCounts):
            f.write(str(count)+","+title+"\n")
    

class PageHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.docID=0
        self.data=""
        self.index={}
        self.tokens=[]
        self.first_last={}
        self.count=0
        self.process_file=False
        self.titles=[]
        self.title=""
        
    def add_to_index(self,docid,flag,freq):
            for token in freq.keys():
                if token in self.index.keys():
                    if docid not in self.index[token]:
                        self.index[token][docid]={}
                else:
                    self.index[token]={}
                    self.index[token][docid]={}
                if(flag==1):
                    self.index[token][docid]['t']=freq[token]
                elif(flag==2):
                    self.index[token][docid]['i']=freq[token]
                elif(flag==4):
                    self.index[token][docid]['c']=freq[token]
                elif(flag==8):
                    self.index[token][docid]['e']=freq[token]
                elif(flag==16):
                    self.index[token][docid]['r']=freq[token]
                elif(flag==32):
                    self.index[token][docid]['b']=freq[token]
                        

    def processData(self,data,flag):
        data=re.sub(r'[^\x00-\x7f]+','',data)
        tokens=word_tokenize(data)
        new_tokens=[]
        for token in tokens:
            if token.isalnum() and token.lower() not in stop_words:
                if(token.isnumeric()):
                    if(len(token)<=6):
                        n=int(token)
                        new_tokens.append(str(n))
                else:
                    new_tokens.append(token)
        
        
        self.count+=len(new_tokens)
        freq={}
        for token in new_tokens:
            s=ps.stem(token)
            if s in freq:
                freq[s]+=1
            else:
                freq[s]=1
        self.add_to_index(self.docID,flag,freq)

    def startElement(self, name, attrs):
        self.current=name
    def characters(self, content):
        if(self.current=="title"):
            self.title+=content.lower()
            self.process_file=False
        elif(self.current=="text"):
            self.data+=content.lower()
            
            
            
    def endElement(self, name):

        if(self.current=="title"):
            if(self.title[:9]!="wikipedia" and self.title[:8]!="category" and self.title[:4]!="file" and self.title[:6]!="portal"):
                self.process_file=True
                self.docID+=1
                self.titles.append(self.title)
            if(self.process_file==True):
                self.processData(self.title,1)
            self.title=""
        elif(self.current=="text"):
            #remove comments
            if(self.process_file==True):
                self.data=re.sub('<!-- (.*?) -->',' ',self.data)
                infobox=re.findall('\{Infobox (.*?)\}',self.data,re.DOTALL)
                infobox_string=""
                for x in infobox:
                    infobox_values=re.findall('=.+$',x,re.MULTILINE)
                    for y in infobox_values:
                        infobox_string+=y[1:]+" "
                
                infobox_string=infobox_string[:-1]
                self.processData(infobox_string,2)
                
                categories=re.findall('^\[\[Category:.+\]\]$',self.data,re.MULTILINE)
                categories_string=""
                for x in categories:
                    categories_string+=x[11:-2]+" "
                self.processData(categories_string,4)

                m1=re.search("^==External links==$",self.data,re.MULTILINE)
                links=[]
                
                if not m1==None:
                    start=m1.start()
                    e=self.data.find('\n',m1.end())
                    while True:
                        s=e+1
                        if(self.data[s]=='*'):
                            e=self.data.find('\n',s)
                            link=self.data[s+2:e]
                            link=link.lstrip()
                            link=re.sub('https?://(.*?) ',' ',link)
                            link=re.sub('\[\[file:(.*?)\]\]',' ',link)
                            links.append(link)
                        else:
                            links=' '.join(links)
                            if(len(links)>0):
                                self.processData(links,8)
                            break
                            
                    self.data=self.data[:start]+self.data[s:]

                m1=re.search('^==References==$',self.data,re.MULTILINE)
                references=[]

                if not m1==None:
                    start=m1.start()
                    e=self.data.find('\n',m1.end())
                    while True:
                        s=e+1
                        if(self.data[s]=='*'):
                            e=self.data.find('\n',s)
                            ref=self.data[s+2:e]
                            ref=ref.lstrip()
                            ref=re.sub('https?://(.*?) ',' ',ref)
                            ref=re.sub('\[\[file:(.*?)\]\]',' ',ref)
                            references.append(ref)
                        else:
                            ref=' '.join(references)
                            if(len(references)>0):
                                self.processData(refs,16)
                            break
                    self.data=self.data[:start]+self.data[s+1:]
                self.data=re.sub('\{\{Infobox (.*?)\}\}',' ',self.data,re.DOTALL)
                self.data=re.sub('https?://(.*?) ',' ',self.data)
                self.data=re.sub('^\[\[Category:.+\]\]$',' ',self.data,re.MULTILINE)
                self.data=re.sub('^==(.*)==$',' ',self.data,re.MULTILINE)
                self.data=re.sub('\{|\}|\[|\]|\(|\)|[@_!#$%^&*()<>?/|}{~:]',' ',self.data)
                self.data=self.data.replace("\n"," ")
                self.processData(self.data,32)
                #body
                self.tokens.append(self.count)
                self.count=0
                self.process_file=False
                print(self.docID,end="\r")
                if(self.docID%7500==0):
                    file_no=self.docID//7500
                    write_token_count(self.titles,self.tokens,file_no)
                    createInvertedIndex(self.index,file_no)
                    self.tokens=[]
                    self.titles=[]
                    self.index={}
            self.data=""
        
        self.current=""
        
        
stop_words=set(stopwords.words('english'))
ps=SnowballStemmer(language='english')
handler=PageHandler()
parser=xml.sax.make_parser()
parser.setContentHandler(handler)
parser.parse("./wiki_dump.xml")


print(handler.docID)
print(len(handler.tokens))
no_of_files=handler.docID//7500
if(len(handler.index)>0):
    no_of_files=no_of_files+1
    createInvertedIndex(handler.index,no_of_files)
    write_token_count(handler.titles,handler.tokens,no_of_files)
print("merging_files.....")
merge_files(no_of_files)

