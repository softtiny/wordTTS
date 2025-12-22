import os

TMPWORDS = [
        'um',
        'uh',
        ]

GAPS = [
        " ",
        "\n",
        ]
def txt2lines(source):
    realp = os.path.realpath(source)
    position,name = os.path.split(realp)
    print(position)
    print(name)
    usename,ext = os.path.splitext(name)
    tmpname = usename+'.tmp'
    txtname = usename+'.lines'
    tmppath = os.path.join(position,tmpname)
    txtpath = os.path.join(position,txtname)
    with open(realp) as real_file,open(tmppath,'w+') as tmp_file, open(txtpath,'w+') as txt_file:
        real_content = real_file.read()
        word = ""
        line = ""
        idx = 0
        length = len(real_content)
        while idx < length:
            code = real_content[idx]
            if code in GAPS:
                if word in TMPWORDS:
                    tmp_file.write(word+"\n")
                else:
                    line += (word + " ")
                    if len(line) > 46:
                        if line.endswith(". ") or line.endswith("? "):
                            line=line.replace(" [ __ ]","")
                            line=line.replace("[ __ ] ","")
                            txt_file.write(line+"\n")
                            line = ""
                word=""
            else:
                word += code
            idx+=1
        txt_file.write(line+"\n")

