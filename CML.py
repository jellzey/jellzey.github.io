import sys
import webbrowser
import bs4
import requests
import os
import math
import shutil
from PIL import Image
from pathlib import Path
from git import Repo

#Paths to different levels of the site
INDEX_PATH= 'C:\\Users\\jellz\\Desktop\\PythonCMS-Local\\jellzey.github.io\\'
SITE_PATH= INDEX_PATH + 'jellzey\\'
PROJ_PATH= SITE_PATH + 'projects\\'
PATH_OF_GIT_REPO = r'C:\Users\jellz\Desktop\PythonCMS-Local\jellzey.github.io'

#master HTML file to copy from
master= SITE_PATH + 'Master.html'

ENCODING='utf-8'

#global list used by trim function
imagesUsed=[]


def loadMaster():
    #load the master HTML file and turn it into a soup object with absolute paths for links
    global soup
    f=open(master,encoding=ENCODING)
    soup=bs4.BeautifulSoup(f,features="html.parser")
    f.close()
    #change links to absolute paths
    localsOnly=soup.find_all('a',id='local')
    localsOnly+=soup.find_all('link',id='local')
    origin=os.getcwd()#save working directory
    os.chdir(os.path.dirname(master))
    for i in range(len(localsOnly)):
        localsOnly[i]['href']=os.path.abspath(localsOnly[i]['href'])
    #change image sources to absolute path
    localsOnly=soup.find_all('img',id='local')
    for i in range(len(localsOnly)):
        localsOnly[i]['src']=os.path.abspath(localsOnly[i]['src'])
    os.chdir(origin)#return to working directory

def formatPage(name):
    #apply formatting from the master file to specified page
    
    if name==os.path.basename(master): #don't format the master
        return 0

    loadMaster();
    f=open(name,encoding=ENCODING) #load page into soup
    soup2=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    
    #replace main content and title
    soup.main.replace_with(soup2.main)
    soup.title.replace_with(soup2.title)
    
    #generate relative paths based on 'local' attribute
    localsOnly=soup.find_all('a',id='local')
    localsOnly+=soup.find_all('link',id='local')
    
    for i in range(len(localsOnly)): #generate relative paths for links
        localsOnly[i]['href']=os.path.relpath(localsOnly[i]['href'])
    localsOnly=soup.find_all('img',id='local') #generate relative paths for images
    for i in range(len(localsOnly)):
        localsOnly[i]['src']=os.path.relpath(localsOnly[i]['src'])

    #remove comments section for non-project pages
    if os.getcwd()+'\\' != PROJ_PATH:
        discuss=soup.find('div',id='disqus_thread')
        discuss.decompose()
        
    #format text and write file
    newHTML=soup.prettify(formatter='html')
    f=open(name,'w',encoding=ENCODING)
    f.write(newHTML)
    f.close()

        
def formatAll():
    #iterate through all .html files in the path and apply formatting from the master file
    for page in os.scandir():
        if page.name.endswith('.html'):
            formatPage(page.name)
            continue
        else:
            continue

def makeNew(name):
    #creates a new HTML file based on the master file
    #loads images from specified folder
    loadMaster()
    f=open(PROJ_PATH+name +'.html','w',encoding=ENCODING)
    f.write('<HTML><title>'+name.capitalize()+'</title></HTML>')
    f.close()
    f=open(PROJ_PATH+name +'.html',encoding=ENCODING)
    new=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    f=open(PROJ_PATH+name +'.html','w',encoding=ENCODING)
    soup.title.replace_with(new.title)
    newHTML=soup.prettify(formatter='html')
    f.write(newHTML)
    f.close()
    configureImages(name)
    populate(name+'.html')
    print('done')
    
def populate(name):
    #generates main content and loads the page with images from corresponding folder
    os.chdir(PROJ_PATH)
    imagesPath= 'images\\'+Path(name).stem+'\\'
    loadMaster();
    
    f=open(name,encoding=ENCODING) #load page into soup
    soup2=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    #replace main content with template from master
    soup2.main.replace_with(soup.main)
    #add intro photo and set title
    soup2.select('.intro')[0].img['src']= imagesPath + 'img0.jpg'
    soup2.select('.intro')[0].img['title']= 'intro image'
    #set first image
    main=soup2.main.find_all('div')[1]
    main.img['src']=imagesPath+ 'img0.jpg'
    main.img['title']='img0'
    i=0
    for filename in os.listdir(imagesPath):
        #iterate through all images and make placeholders in the html
        if i>0:
            #Because I already set the first image out of the loop, I need to start from i=1.
            #This keeps the img0 from showing up 3 times. (Couldn't come up with a better way to do this)
            loadMaster()
            temp=soup.main.find_all('div')[1].img
            temp['src']=imagesPath + filename
            temp['title']=Path(filename).stem
            #append is the easiest way to add content. This is why the first image is set out of the loop
            main.append(temp)
            main.append('\n \n')
        i+=1
    #change title 
    soup2.h1.string=soup2.title.string
    #save and write to file
    newHTML=soup2.prettify(formatter='html')
    f=open(name,'w',encoding=ENCODING)
    f.write(newHTML)
    f.close()
    
def configureImages(folder):
    #scales down raw images and adds them to the project folder of the same name. If the folder exists,
    #adds the images and indexes the new filenames to continue from the highest in the folder
    initialPath = INDEX_PATH+'..\\raw-images\\' + folder
    folderPath = PROJ_PATH+'images\\'+folder
    fileSequence = 0
    newWidth=1296 #defines the width of all photos, height is scaled proportionally
    newHeight=0

    print('Configuring '+ folderPath )
    try:
        os.mkdir(folderPath) #if the folder exists, the images are added with higher index #s
    except FileExistsError:
        pass
    
    while os.path.isfile(folderPath + '\\' 'img' + str(fileSequence) + '.jpg'):
        fileSequence+=1 #increment index # to continue numbering scheme in file

    for filename in os.listdir(initialPath):
            
            imgTemp=Image.open(initialPath + '\\' + filename)
            initialWidth=imgTemp.getbbox()[2]
            initialHeight=imgTemp.getbbox()[3]
            
            if initialWidth>newWidth:
                r=initialHeight/initialWidth #find ratio of dimensions
                newHeight=math.floor(newWidth*r) #scale width to find new height
                imgTemp=imgTemp.resize((newWidth,newHeight))

            
            imgTemp.save(folderPath + '\\' + filename)
            
            os.rename(folderPath + '\\' + filename, folderPath + '\\' 'img' + str(fileSequence) + '.jpg')

            print('img' + str(fileSequence)) # print progress
            fileSequence +=1

def clearImages(folder):
    #deletes image folder
    folderPath = PROJ_PATH + 'images\\'+folder
    print('Cleaning '+ folderPath )
    try:
        shutil.rmtree(folderPath)
    except OSError as e:
        print("Error: %s : %s" % (folderPath, e.strerror))

def removePage(name):
    #deletes a page and its associated image folder
    #the raw image folder is not deleted
    clearImages(name)
    print('deleting ' + name + '.html')
    os.remove(PROJ_PATH + name + '.html')
            
def makeTile(image):
    #takes a path to an image and makes a tile sized for the index stored to the tile folder
    os.chdir(INDEX_PATH)
    folderPath = 'tiles\\'
    newWidth=432 #defines the width of all photos, height is scaled proportionally
    newHeight=0

    print('Tilizing '+ image )
    try:
        os.mkdir(folderPath) #if the folder exists, the images are added with higher index #s
    except FileExistsError:
        pass
        
    imgTemp=Image.open(image)
    initialWidth=imgTemp.getbbox()[2]
    initialHeight=imgTemp.getbbox()[3]
        
    if initialWidth>newWidth:
        r=initialHeight/initialWidth #find ratio of dimensions
        newHeight=math.floor(newWidth*r) #scale width to find new height
        imgTemp=imgTemp.resize((newWidth,newHeight))
    #get project name from path
    prefix=os.path.relpath(os.path.dirname(image),PROJ_PATH+'\\images')
    newName=prefix+'_'+ os.path.basename(image)
    try:
        imgTemp.save(folderPath + newName) #if the file exists, ignore
    except FileExistsError:
        pass
    return folderPath+newName

def tileize(name,imgNum):
    #takes a page name and an image number and generates an index tile
    imgPath=PROJ_PATH+'images\\'+name+'\\img'+imgNum+'.jpg'
    tilePath='Path not'
    try:
        tilePath=makeTile(imgPath)
    except:
        print('Image not found')
    return tilePath

def formatTiles():
    #ensures all index tiles are sized and sourced from the tile folder
    os.chdir(INDEX_PATH)
    f=open('index.html',encoding=ENCODING)
    index=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    nugs=index.select('.nav-nugget')#select all project tile elements
    for i in range(len(nugs)):#iterate through list, generate tile image and change source path to new image
        if os.path.dirname(nugs[i].img['src'])!='tiles':        
            nugs[i].img['src']=makeTile(nugs[i].img['src'])
            print(nugs[i].img['src']) #print new source path
        
    #format text and write file
    newHTML=index.prettify(formatter='html')
    f=open('index.html','w',encoding=ENCODING)
    f.write(newHTML)
    f.close()

def publishPage(name,title,cat,desc,tile):
    
    os.chdir(INDEX_PATH)
    f=open('index.html',encoding=ENCODING)
    index=bs4.BeautifulSoup(f,features='html.parser')
    f.close()

    newPage=index.new_tag("li")
    newPage['class']='nav-nugget'
    
    if cat=='d':
        block=index.find('nav', class_='design')
    elif  cat== 'r':
        block=index.find('nav', class_='repair')
    elif cat=='m':
        block=index.find('nav', class_='misc')
    else:
        print('Not a valid category')
        return
        
    block.ul.append(newPage)
    link=index.new_tag('a', href='jellzey\\projects\\'+name+'.html')
    newPage.append(link)
    header=index.new_tag('h3')
    link.append(header)
    header.append(title)
    image=index.new_tag('img', src=tile)
    link.append(image)
    link.append(desc)
    
    newHTML=index.prettify(formatter='html')
    f=open('index.html','w',encoding=ENCODING)
    f.write(newHTML)
    f.close()
    print(name+ ' published to index')

def hidePage(name):
    #Removes a page from the index
    global soup
    os.chdir(INDEX_PATH)
    f=open('index.html',encoding=ENCODING)
    soup=bs4.BeautifulSoup(f,features='html.parser')
    f.close()

    listItem=soup.find('a',href='jellzey\\projects\\'+name+'.html').findParent()
    listItem.decompose()
    
    newHTML=soup.prettify(formatter='html')
    f=open('index.html','w',encoding=ENCODING)
    f.write(newHTML)
    f.close()
    print(name+ ' removed from index')

    
def findUsedImages(name):#input is image FOLDER name (no '.html' extension in argument) 
    #compares HTML to the matching image folder and finds which images were used
    #sets the global variable imagesUsed to an array of relative paths from the project folder
    global imagesUsed
    f=open(name + '.html', encoding=ENCODING)
    soup=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    images=soup.main.find_all('img')
    paths=[]
    for i in range(len(images)):
        paths.append(images[i]['src'])
    imagesUsed=paths
    return paths
    
def trimImageFolder(name):#input is image FOLDER name (no '.html' extension in argument) 
    #removes unused images from the image folder for a page specified by 'name'
    findUsedImages(name);
    global imagesUsed
    folderPath = os.getcwd() + '\\images\\'+name

    print('Trimming '+ folderPath )
    os.mkdir(name)
    for i in range (len(imagesUsed)):
        shutil.copy(imagesUsed[i], name)
        print('.',end=' ')
    try:
        shutil.rmtree(folderPath)
    except OSError as e:
        print("Error: %s : %s" % (folderPath, e.strerror))
    shutil.move(name,'images')
    print('Done')
    
def trimAll():
    #iterate through all .html files in the path and remove unused images from the image folder
    for entry in os.scandir('images'):
        trimImageFolder(entry.name)

def printList(istlay):
    for i in range(len(istlay)):
        print(istlay[i])
    print('\n');
    
def printImageFiles(path):
    os.chdir(path)
    names=os.listdir()
    printList(names)
    
def printActivePages(path):
    os.chdir(path)
    files=os.listdir()
    pages=[]
    for i in range(len(files)):
        if files[i].endswith('.html'):
            pages.append(files[i])
    printList(pages)

def git_push(message):
    try:
        repo = Repo(os.path.relpath(PATH_OF_GIT_REPO))
        repo.git.add(all=True)
        repo.index.commit(message)
        origin = repo.remote(name='origin')
        origin.push()
        print('done')
    except:
        print('Some error occured while pushing to github')
        
###############################################

def theWorks():
    #runs through all of the clean up functions to tidy the entire site at one time

    #index page
    os.chdir(INDEX_PATH)
    formatPage('index.html')
    formatTiles()

    #site pages
    os.chdir(SITE_PATH)
    formatAll()
    trimAll()

    #project pages
    os.chdir(PROJ_PATH)
    formatAll()
    trimAll()





    
