#!/usr/bin/env python
import os
import shutil
'''
This script gets called by the TravisCI build process
after tests pass on a tagged release. It is used to zip
the binary (linux) that travis generated so it can be copied
to the git hub repo
'''

def __get_file_path(relpath):
    '''
    workaround so that TravisCI can discover the files
    :param relpath: path to file relative to this file
    :return: full path to file
    '''

    root_folder = os.path.join(os.path.dirname(__file__))
    full_file_path = os.path.join(root_folder, relpath)
    print(full_file_path)
    return full_file_path


if __name__ == '__main__':
    # todo: get version number from setup.py file settings...
    shutil.make_archive(__get_file_path("data_diff_linux"), "zip",
                            __get_file_path("./dist/"))
    print("zipping file...")
    print("done")
