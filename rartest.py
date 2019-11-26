import sys
def read_vint(stream, offset):
    v = 0
    s = 0
    i = 0
    continue_flag = True
    while continue_flag:
        v += (stream[offset + i] & 0b01111111) << s
        if stream[offset + i] & 0x80 == 0:
            continue_flag = False
        s += 7
        i += 1
    return (v, i)
path = sys.argv[1]
with open(path, 'rb') as f:
    content = f.read()
    if content[6] == 0x00:
        version = 3
    elif content[6] == 0x01:
        version = 5
    if version == 3:
        print("Rar Version: 3")
        for i in range(len(content)):
            if content[i] == 0x73:
                print("MAIN_HEAD")
                flags = (content[i+1] << 8) + content[i+2]
                print("FLAGS: {:016b}".format(flags))
                print("Looking for: {:016b}".format(0x0200))
                encrypted = flags & 0x0200
                if encrypted != 0:
                    print("Encrypted!")
                    sys.exit(1)
                else:
                    print("Not Encrypted.")
                    sys.exit(0)
    elif version == 5:
        print("Rar Version: 5")
        i = 12
        s = 0
        header_size = read_vint(content, i)
        i += header_size[1]
        header_type = read_vint(content, i)
        i += header_type[1]
        if header_type[0] == 4:
            print("Encrypted Header!")
            sys.exit(1)
        elif header_type[0] == 1:
            header_flags = read_vint(content, i)
            i += header_flags[1]
            extra_area_size = 0
            if header_flags[0] & 0x0001 != 0:
                print("Extra Area Size present.")
                extra_area_size = read_vint(content, i)
                i += extra_area_size[1]
            archive_flags = read_vint(content, i)
            i += archive_flags[1]
            if archive_flags[0] & 0x0002 != 0:
                print("Volume Number present.")
                volume_number = read_vint(content, i)
                i += volume_number[1]
            if extra_area_size != 0:
                i += extra_area_size[0]
            # n File Headers
            while True:                
                i += 4 # Skip CRC
                header_size = read_vint(content, i)
                i += header_size[1]
                start = i
                header_type = read_vint(content, i)
                i += header_type[1]
                if header_type[0] == 2:
                    print("File Header found.")
                    header_flags = read_vint(content, i)
                    i += header_flags[1]
                    if header_flags[0] & 0x0001 != 0:
                        print("Extra Area present.")
                        extra_area_size = read_vint(content, i)
                        i += extra_area_size[1]
                        if header_flags[0] & 0x0002:
                            data_size = read_vint(content, i)
                            i += data_size[1]                       
                        file_flags = read_vint(content, i)
                        i += file_flags[1]
                        unpacked_size = read_vint(content, i)
                        i += unpacked_size[1]
                        attributes = read_vint(content, i)
                        i += attributes[1]
                        if file_flags[0] & 0x0002:
                            i += 4                       
                        if file_flags[0] & 0x0004:
                            i += 4
                        compression_information = read_vint(content, i)
                        i += compression_information[1]
                        host_os = read_vint(content, i)
                        i += host_os[1]
                        name_length = read_vint(content, i)
                        i += name_length[1]
                        i += name_length[0] # Skip Name
                        ## Extra Area ##
                        extra_header_size = read_vint(content, i)
                        i += extra_header_size[1]
                        extra_header_type = read_vint(content, i)
                        if extra_header_type[0] == 1:
                            print("Encrypted File!")
                            sys.exit(1)
                        else:
                            i = start + header_size[0]
                            continue
                    else:
                        "File not encrypted."
                        i = start + header_size
                        continue
                else:
                    print("No Encrypted File found.")
                    break
