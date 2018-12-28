import os
import struct
import shutil
import functools

"""
This is a Python 3 implementation of J-Bit Encoding (JBE), with sightly differences in I/O processing.
All credit goes to author I Made Agus Dwi Suarjaya.
Reference: https://arxiv.org/ftp/arxiv/papers/1209/1209.1045.pdf
"""
CONST_4K = 4096
CONST_DEBUG = False

def log(msg):
    if CONST_DEBUG:
        print(msg)


def encode(source, target):
    temp = 0
    statinfo = os.stat(source)
    file_size = statinfo.st_size
    bit_cnt = 0
    cnt = 0

    tmp_data1 = os.path.basename(source).replace(':', '_').replace(' ', '_').replace('.', '_')+'_data1.bin'
    tmp_data2 = os.path.basename(source).replace(':', '_').replace(' ', '_').replace('.', '_')+'_data2.bin'
    tmp_data1 = os.path.join("temp", tmp_data1)
    tmp_data2 = os.path.join("temp", tmp_data2)

    try:
        with open(source, "rb") as file_in:
            with open(tmp_data1, "wb") as data1_file:
                with open(tmp_data2, "wb") as data2_file:
                    copy_buf = True
                    while copy_buf:
                        bytes_to_read = CONST_4K

                        if file_size % CONST_4K == 0:
                            pass
                        elif file_size - (cnt * CONST_4K) > CONST_4K:
                            pass
                        else:
                            bytes_to_read = file_size % CONST_4K

                        copy_buf = file_in.read(bytes_to_read)

                        if not copy_buf:
                            break

                        for c in copy_buf:

                            if temp > 0:
                                temp = temp << 1

                            if c > 0:
                                temp = temp | 1
                                data1_file.write(bytes([c]))

                            bit_cnt = bit_cnt + 1

                            if bit_cnt % 8 == 0:
                                data2_file.write(bytes([temp]))
                                temp = 0

                        cnt = cnt + 1

                        if bit_cnt == file_size:
                            break

                    remain_bit = bit_cnt % 8
                    if remain_bit > 0:
                        bit_to_shift = 8 - remain_bit
                        log('encode.bit_to_shift = '+str(bit_to_shift))
                        log('temp before '+str(temp))
                        temp = temp << bit_to_shift
                        log('temp after '+str(temp))
                        data2_file.write(bytes([temp]))
                        temp = 0

        with open(target, "wb") as file_out:
            log(str(file_size))
            file_out.write(struct.pack(">Q", file_size))

            with open(tmp_data1, "rb") as data1_file:
                shutil.copyfileobj(data1_file, file_out)
            # os.remove(tmp_data1)

            with open(tmp_data2, "rb") as data2_file:
                shutil.copyfileobj(data2_file, file_out)
            # os.remove(tmp_data2)

            file_out.flush()
    except PermissionError as identifier:
        return 1
    else:
        return 0


def decode(source, target):
    statinfo = os.stat(source)
    file_size = statinfo.st_size

    # tmp_data1 = r'r:\data3.bin'
    # tmp_data2 = r'r:\data4.bin'
    # tmp_data1 = os.path.basename(source).replace(':', '_').replace(' ', '_').replace('.', '_')+'_data3.bin'
    tmp_data2 = os.path.basename(source).replace(':', '_').replace(' ', '_').replace('.', '_')+'_data4.bin'
    # tmp_data1 = os.path.join("temp", tmp_data1)
    tmp_data2 = os.path.join("temp", tmp_data2)

    with open(source, "rb") as file_in:
        with open(target, "wb") as file_out:
            # with open(tmp_data1, "wb+") as data1_file:
            with open(tmp_data2, "wb+") as data2_file:
                # first four bytes are the file size
                file_size_bytes = struct.unpack(">Q", file_in.read(8))
                file_size_bytes = file_size_bytes[0]

                # determine the size of data 2
                data2_size = file_size_bytes // 8
                if file_size_bytes % 8 > 0:
                    data2_size += 1

                data2_start = file_size - data2_size

                file_in.seek(data2_start)

                # read data2
                shutil.copyfileobj(file_in, data2_file)
                data2_file.flush()

                data2_file.seek(0)
                # data1_file.seek(0)
                file_in.seek(8,0)
                # file_in.read(8)

                byte_written = 0

                max_bit = 8
                bit_shift = 7

                while True:
                    one_byte = data2_file.read(1)
                    if one_byte:
                        one_byte = ord(one_byte)
                    else:
                        one_byte = 0

                    if (byte_written + 8 > file_size_bytes):
                        log('file_size_bytes = '+str(file_size_bytes))
                        max_bit = (file_size_bytes % 8)
                        log('209, max_bit: '+str(max_bit))

                        # becoz original file size is not a multiple of 8 bits
                        # need to trim unncessary bits
                        one_byte = one_byte >> (8-max_bit)
                        
                        bit_shift = max_bit - 1
                        log('218, bit_shift: '+str(bit_shift))

                    for j in reversed(range(max_bit)):
                        try:
                            if one_byte >> (j) & 1 == 1:
                                tmp = file_in.read(1)
                                if tmp:
                                    file_out.write(tmp)
                                    byte_written += 1
                                else:
                                    log(str(one_byte >> (bit_shift - j)))
                                    log('file_size_bytes = ' + str(file_size_bytes))
                                    log('tmp = '+str(tmp))
                                    log('max_bit = '+str(max_bit))
                                    log('one_byte = '+str(one_byte))
                                    log('bit_shift = '+str(bit_shift))
                                    log('j = '+str(j))
                                    log('byte_written = ' + str(byte_written))
                            else:
                                file_out.write(b"\0")
                                byte_written += 1
                        except Exception as identifier:
                            log('Ex: '+str(bit_shift))
                            log('Ex: '+str(j))
                            log('Ex: '+identifier)
                            raise
                            # pass

                    if byte_written >= file_size_bytes:
                        break

        file_out.flush()
