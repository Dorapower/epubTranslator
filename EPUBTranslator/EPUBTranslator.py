from googletrans import Translator
from bs4 import BeautifulSoup as bs, element
import os,zipfile,shutil
import json
import time,retrying

maxLen=5e3
maxtrial=3

# @retry(wait_fixed=3000,stop_max_attemp_time=3,retry_on_exception=lambda exception:isinstance(exception,json.decoder.JSONDecodeError))
def paraTrans(s:str,lang='zh-CN') -> str:
    paraTrans.called+=1
    print('translating for the %dth time'%paraTrans.called)
    trans=Translator()
    success = False
    trytime=0
    while not success:
        try:
            transed=trans.translate(s,dest=lang).text
        except json.decoder.JSONDecodeError:
            trytime+=1
            if trytime<=maxtrial:
                print('Nothing get from google...Retrying %d/%d'%(trytime,maxtrial))
                time.sleep(3)
            else:
                print('It seems nothing will change for a long time. I hope you can change your ip now.')
                str=input('Enter y to continue, or you can exit now')
                trytime=0
        else:
            success=True
    return transed
def titleTrans(src:str,lang='zh-CN') -> str:
    nl=src.split('.')
    if(nl[-1].lower()!='epub'):
        print('not a epub file?!')
        raise Exception("Unexpected filetype",nl[-1])
    for i in range(len(nl)-1):
        nl[i]=paraTrans(nl[i])
    return '.'.join(nl)
def htmlTrans(src:str, dest:str,lang='zh-CN'):
    raw_str_join,ted_str_join='',''
    soup=bs(open(src,encoding='utf8'),'xml')
    eles=list(soup.descendants)
    strCount=0
    for ele in eles:
        if isinstance(ele,element.NavigableString) and str(ele).strip()!='':
            elestr=str(ele)
            if len(raw_str_join)+len(elestr)<maxLen:
                raw_str_join+='\n-----\n'
                raw_str_join+=elestr
            else:
                ted_str_join+=paraTrans(raw_str_join)
                raw_str_join='\n-----\n'+elestr
    ted_str_join+=paraTrans(raw_str_join)
    ted_str_list=ted_str_join.split('-----')
    nextpos=0
    for ele in eles:
        if isinstance(ele,element.NavigableString) and str(ele).strip()!='':
            nextpos+=1
            if nextpos<len(ted_str_list):
                ele.replace_with(element.NavigableString(ted_str_list[nextpos]))
            else:
                print("something strange has occur. I will try to prevent the program from interruption.")
                break
    with open(dest,'w',encoding='utf8') as f:
        f.write(soup.prettify())
def dirTrans(path:str,src:str,dest=None,lang='zh-CN'):
    filename=' '.join(src.split('.')[:-1])
    transname=paraTrans(filename)

    # unzip
    os.chdir(path)
    if os.path.isdir('tmp'):
        pass
    else:
        os.mkdir('tmp')
    epub=zipfile.ZipFile(src)
    os.chdir('tmp')
    os.mkdir(filename)
    os.mkdir(transname)
    for name in epub.namelist():
        epub.extract(name,filename)

    fileCount=0
    for root, dirs, files in os.walk(filename):
        for dir in dirs:
            os.mkdir(os.path.join(root.replace(filename,transname),dir))
        for file in files:
            total=len(files)
            if file.split('.')[-1] in ('html','htm'):
                htmlTrans(os.path.join(root,file),os.path.join(root.replace(filename,transname),file))
                fileCount+=1
                print('%s tranlate done. %d/%d'%(file,fileCount,total))
            else:
                shutil.copyfile(os.path.join(root,file),os.path.join(root.replace(filename,transname),file))
                fileCount+=1
                print('%s copied. %d/%d'%(file,fileCount,total))

    # zip
    os.chdir(path)
    if dest==None:
        dest=transname+'.epub'
    z = zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) 
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir,'') 
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    print ('done')
    z.close()

if __name__=='__main__':
    paraTrans.called=0
    #dirTrans(r'E:\course\English',r'Iris Chang - The Chinese in America-Penguin Group US (1980).epub')
    htmlTrans('test/test.html','t.html')