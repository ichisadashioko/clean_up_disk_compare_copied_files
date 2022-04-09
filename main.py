import os
import io
import hashlib
import math
import stat
import traceback
import pickle
import argparse
import time

from tqdm import tqdm


def compute_filehash(
    fpath,
    filesize=None,
    chunksize=16777216,
):
    md5_obj = hashlib.md5()

    if filesize is None:
        filesize = os.path.getsize(fpath)

    number_of_chunks = int(math.ceil(filesize / chunksize))
    if os.path.getsize(fpath) != 0:
        with open(fpath, mode='rb') as infile:
            pbar = tqdm(range(number_of_chunks))
            for i in pbar:
                pbar.set_description(f'MD5 {i}/{number_of_chunks} {fpath}')
                chunk = infile.read(chunksize)
                md5_obj.update(chunk)

    return md5_obj.digest()


def get_file_info(
    fpath,
    compute_hash=False,
):
    filename = os.path.basename(fpath)

    try:
        filestat = os.stat(fpath)

        if stat.S_ISREG(filestat.st_mode):
            filesize = filestat.st_size
            filehash = compute_filehash(fpath, filesize)

            if compute_hash:
                filehash = compute_filehash(fpath, filesize)

                return {
                    'filename': filename,
                    'filemode': filestat.st_mode,
                    'filesize': filesize,
                    'filehash': filehash,
                    'modified': filestat.st_mtime,
                }
            else:
                return {
                    'filename': filename,
                    'filemode': filestat.st_mode,
                    'filesize': filesize,
                    'modified': filestat.st_mtime,
                }
        elif stat.S_ISDIR(filestat.st_mode):
            # TODO
            filelist = []
            filename_list = os.listdir(fpath)
            for filename in filename_list:
                child_fpath = os.path.join(fpath, filename)
                filelist.append(get_file_info(
                    fpath=child_fpath,
                    compute_hash=compute_hash,
                ))
            return {
                'filename': filename,
                'filemode': filestat.st_mode,
                'filelist': filelist,
            }
        else:
            return {
                'filename': filename,
                'filemode': filestat.st_mode,
            }
    except Exception as ex:
        stack_trace_str = traceback.format_exc()
        return {
            'filename': filename,
            'stacktrace': stack_trace_str,
            'exception': ex,
        }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--path',
        dest='path',
        type=str,
        help='file path to scan',
        required=True,
    )

    args = parser.parse_args()

    start_time_ns = time.time_ns()
    file_info = get_file_info(args.path)
    end_time_ns = time.time_ns()
    result = {
        'abspath': os.path.abspath(args.path),
        'start_time_ns': start_time_ns,
        'end_time_ns': end_time_ns,
        'file_info': file_info,
    }

    log_filename = f'{start_time_ns}.pickle'

    with open(log_filename, 'wb') as outfile:
        pickle.dump(result, outfile)


if __name__ == '__main__':
    main()
