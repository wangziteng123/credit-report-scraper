import hashlib
import json
import multiprocessing
import os
import sys
import urllib.request
import tqdm

SIZE = 6 * 1024
dump_fname = ''
dump_json = []
DL_PATH = os.path.abspath('../downloads')


def download(job):
    try:
        link = job[1]['file_urls'][0]
        src = job[1]['source']
        cat = job[1]['category']
        fname = link.split('/')[-1]
        fpath = os.path.join(DL_PATH, src, cat, fname)
        res = urllib.request.urlopen(link)

        with open(fpath, 'wb') as file:
            for chunk in iter(lambda: res.read(SIZE), ''):
                if not chunk:
                    break
                file.write(chunk)
    except Exception as e:
        print('\nDownload %s failed: %s\n' % (link, e))
        try:
            os.remove(fpath)
        except OSError:
            pass
        return

    item = dump_json[job[0]]
    item['status'] = 'success'
    item.pop('file_urls', None)
    item['files'] = {
        'url': link,
        'path': fpath,
        'checksum': md5_checksum(fpath)
    }
    dump_json[job[0]] = item
    write_json()
    return


def get_jobs():
    return [(i, x) for i, x in enumerate(dump_json) if x['status'] == 'download_failed']


def read_json(fname):
    with open(fname, 'r') as f:
        return json.load(f)


def write_json():
    with open(dump_fname, 'w', encoding='utf-8') as f:
        json.dump(dump_json, f, ensure_ascii=False)


def md5_checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(SIZE)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def main():
    global dump_fname, dump_json
    try:
        dump_fname = sys.argv[1]
        dump_json = read_json(dump_fname)
    except IndexError:
        print('Did not provide path to json dump file. Usage: python3 retry.py <path>')
        exit()

    jobs = get_jobs()
    pool = multiprocessing.Pool(3)
    jobs_ct = len(jobs)
    with tqdm.tqdm(total=jobs_ct) as pbar:
        for i, _ in tqdm.tqdm(enumerate(pool.imap_unordered(download, jobs))):
            pbar.update()
    pool.close()
    print('\nall downloads complete\n')


if __name__ == '__main__':
    main()
