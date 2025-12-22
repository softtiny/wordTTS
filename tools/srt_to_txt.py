import os

def srt2txt(source):
    realp = os.path.realpath(source)
    position,name = os.path.split(realp)
    print(position)
    print(name)
    usename,ext = os.path.splitext(name)
    tmpname = usename+'.tmp'
    txtname = usename+'.txt'
    tmppath = os.path.join(position,tmpname)
    txtpath = os.path.join(position,txtname)
    with open(realp) as real_file,open(tmppath,'w+') as tmp_file, open(txtpath,'w+') as txt_file:
        real_content= real_file.readlines()
        print(real_content)
        counter = 1
        idx = 0
        length = len(real_content)
        while idx < length:
            pointer = str(counter)
            next_pointer = str(counter+1)
            line_cont=real_content[idx].strip()
            if line_cont == "":
                idx+=1
            elif line_cont == pointer:
                tmp_file.write(real_content[idx])
                tmp_file.write(real_content[idx+1])
                idx+=2
            elif line_cont == next_pointer:
                counter+=1
            else:
                txt_file.write(real_content[idx])
                idx+=1
