import jbelib
import hashlib
import os

def replace_chars(s):
    return s.replace(':','_').replace('\\','_').replace('.','_')

if __name__ == '__main__':
    directory = r"test"
    for dirpath, dnames, fnames in os.walk(directory):
        for filename in fnames:
            fullpath = os.path.join(dirpath,filename)
            if os.path.isfile(fullpath):
                tmp_name = replace_chars(filename) + '.enc'
                tmp_path = os.path.join('enc_output',tmp_name)
                result = jbelib.encode(fullpath, tmp_path)
                if result == 0:
                    tmp_name2 = replace_chars(filename)
                    tmp_path2 = os.path.join('dec_output',tmp_name2)
                    jbelib.decode(tmp_path,tmp_path2)
                    m = hashlib.sha1()
                    for line in open(fullpath,'rb'):
                        m.update(line)
                    hash1 = m.hexdigest()
                    m = hashlib.sha1()
                    for line in open(tmp_path2,'rb'):
                        m.update(line)
                    hash2 = m.hexdigest()
                    if (hash1 != hash2):
                        print(hash1+','+hash2+','+fullpath)
