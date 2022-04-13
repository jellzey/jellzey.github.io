import sys
import webbrowser
import bs4
import requests
import os
import math
import shutil
from PIL import Image
from pathlib import Path

#Paths to different levels of the site
INDEX_PATH= 'C:\\Users\\jellz\\Desktop\\PythonCMS-Local\\jellzey.github.io\\'
SITE_PATH= INDEX_PATH + 'jellzey\\'
PROJ_PATH= SITE_PATH + 'projects\\'

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
    loadMaster()
    f=open(PROJ_PATH+name +'.html','w',encoding=ENCODING)
    f.write('<HTML><title>'+name+'</title></HTML>')
    f.close()
    f=open(PROJ_PATH+name +'.html',encoding=ENCODING)
    new=bs4.BeautifulSoup(f,features='html.parser')
    f.close()
    f=open(PROJ_PATH+name +'.html','w',encoding=ENCODING)
    soup.title.replace_with(new.title)
    newHTML=soup.prettify(formatter='html')
    f.write(newHTML)
    f.close()

def configureImages(folder):
    #scales down raw images and adds them to the project folder of the same name. If the folder exists,
    #it adds the images and indexes the new filenames to continue from the highest in the folder
    initialPath = '../raw-images/' + folder
    folderPath = './jellzey/projects/images/'+folder
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
    print('Clearing '+ folderPath )
    try:
        shutil.rmtree(folderPath)
    except OSError as e:
        print("Error: %s : %s" % (folderPath, e.strerror))
            
def makeTile(image):
    #takes a path to an image and makes a tile sized for the index stored to the tile folder
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





    
