import CML


################### MAIN LOOP #########################################

print("Content Manager 9000\n")

while True:
    print('Enter command (new, pub, hid, del, img, end)\n')
    cmd=input()
    if cmd=='new':
        print('Create a new page from image folder\n')
        CML.printImageFiles('C:\\Users\\jellz\\Desktop\\PythonCMS-Local\\raw-images\\')
        print('Enter image folder name')
        answer=input()
        print('Making '+ answer +'.html \n')
        CML.makeNew(answer)
        CML.printActivePages(CML.PROJ_PATH)
        
    elif cmd=='pub':
        print('Publish page to index\n')
        CML.printActivePages(CML.PROJ_PATH)
        print('Enter page name')
        page=input()
        CML.printImageFiles(CML.PROJ_PATH+'images\\'+page)
        print('Enter image number to use for index tile')
        imgNum=input()
        tilePath=CML.tileize(page,imgNum)
        print(tilePath +' created \n')
        print('Enter a title for this page')
        title=input()
        print('Enter a description')
        desc=input()
        print('Enter a category (d) Design, (r) Repair, (m) Misc)')
        cat=input()
        CML.publishPage(page,title,cat,desc,tilePath)
    elif cmd=='del':
        print('Delete page and all its content\n')
        CML.printActivePages(CML.PROJ_PATH)
        print('Enter page name')
        answer=input()
        print('Delete '+ answer + '? (y/any char)')
        ans=input()
        if ans=='y':
            print('\n')
            CML.removePage(answer)
        else:
            print('Action cancelled')
    elif cmd=='hid':
        print('Hide page from index\n')
        CML.printActivePages(CML.PROJ_PATH)
        print('Enter page name')
        answer=input()
        print('Hide '+ answer + '? (y/any char)')
        ans=input()
        if ans=='y':
            CML.hidePage(answer)
        else:
            print('Action cancelled')
    elif cmd=='img':
        print('Update images\n')
        CML.printActivePages(CML.PROJ_PATH)
        print('Enter page name')
        answer=input()
        print('Update images in '+ answer + '? (y/any char)')
        ans=input()
        if ans=='y':
            CML.clearImages(answer)
            CML.configureImages(answer)
        else:
            print('Action cancelled')
    elif cmd=='end':
        print('Clean files and push site to github? (y/any char)')
        ans=input()
        if ans=='y':
            CML.theWorks()
            print('Enter commit message')
            answer=input()
            CML.git_push(answer);
            print('Site pushed')
            break
        else:
            print('Site not pushed')
            break
    else:
        print('Not a valid command\n')
        

