import jbelib
import hashlib
import os
import datetime

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
                start_time = datetime.datetime.now()
                result = jbelib.encode(fullpath, tmp_path, 88)
                end_time = datetime.datetime.now()
                time_difference  = end_time - start_time
                print('encode time: '+str(divmod(time_difference.days * 86400 + time_difference.seconds, 60)))
                if result == 0:
                    # pass
                    tmp_name2 = replace_chars(filename)
                    tmp_path2 = os.path.join('dec_output',tmp_name2)
                    start_time = datetime.datetime.now()
                    jbelib.decode(tmp_path,tmp_path2)
                    end_time = datetime.datetime.now()
                    time_difference  = end_time - start_time
                    print('decode time: '+str(divmod(time_difference.days * 86400 + time_difference.seconds, 60)))
                    m = hashlib.sha1()
                    with open(fullpath, 'rb') as f:
                        for chunk in iter(lambda: f.read(8192), b''): 
                            m.update(chunk)
                    hash1 = m.hexdigest()
                    m = hashlib.sha1()
                    with open(tmp_path2, 'rb') as f:
                        for chunk in iter(lambda: f.read(8192), b''): 
                            m.update(chunk)
                    hash2 = m.hexdigest()
                    if (hash1 != hash2):
                        print(hash1+','+hash2+','+fullpath)
                else:
                    print("process failed for file: "+fullpath)
