import os, csv, codecs

os.chdir("C:\Python27\SMMProject2\paulwalker\classifiedlivetweets")

def get_information(directory):
    file_list = []
    for i in os.listdir(directory):
        a = os.stat(os.path.join(directory,i))
        file_list.append([i]) #[file,most_recent_access,created]
    return file_list

filenames = get_information("C:\Python27\SMMProject2\paulwalker\classifiedlivetweets")
f = codecs.open("ExcelInfo.csv",'w','utf-8')
writer = csv.writer(f)
count = 0
while True:
        with open(filenames[count][0],'rb') as inputfile:
##            lines = sum(1 for line in inputfile)
            for line1 in inputfile:
                pass
            last = line1
            s=last.split(',')
            print s
            writer.writerow((filenames[count][0],s[1]))
            print count
            count=count+1
##while True:
##        with open(filenames[count][0],'rb') as inputfile:
##            lines = sum(1 for line in inputfile)
####            for line1 in inputfile:
####                pass
####            last = line1
####            s=last.split(',')
####            print s
##            writer.writerow((filenames[count][0],lines-1))
##            print count
##            count=count+1
