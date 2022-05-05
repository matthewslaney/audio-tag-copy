import argparse
import os
import shutil
from datetime import datetime

import mutagen

def arg_pair(value):
    rv = value.split(',')
    if len(rv) != 2:
        raise argparse.ArgumentParser()
    return rv

def copy_tags(source_file, destination_file, edit_tag):
    source_file_object = mutagen.File(source_file)
    destination_file_object = mutagen.File(destination_file)
    source_tags = source_file_object.tags
    if edit_tag:
        source_file_type = source_file_object.mime[0].split(sep='/')[1]
        if source_file_type == 'mp3':
            source_tags.add(mutagen.id3.TXXX(desc=edit_tag[0],text=edit_tag[1]))
        else:
            try:
                source_tags[edit_tag[0]] = edit_tag[1]
            except:
                print('Unsupported file type when trying to add new tags. Error:\n')
                raise
    destination_file_object.tags = source_tags
    destination_file_object.save()

def backup_source_file(source_file, backup_location):
    shutil.copy(source_file, backup_location)

def backup_asd(source_file, backup_location):
    shutil.copy(str(source_file) + '.asd', str(backup_location) + '.asd')

def overwrite_file(source_file, destination_file):
    shutil.move(destination_file, source_file)
    try:
        os.remove(source_file + '.asd')
    except FileNotFoundError:
        pass
    if os.path.exists(destination_file + '.asd'):
        shutil.move(destination_file + '.asd', source_file + '.asd')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy metadata tags from the source file to the destination file.')
    parser.add_argument('source_file')
    parser.add_argument('destination_file')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Move the destination file to the location of the source file. (A backup is made of the source unless using -D)')
    parser.add_argument(
        '-b','--backup-location',
        help='When using -o, sets location to create backup of the source file. Accepts full file name or only a folder. When given only a folder, will use original file name. Default: ./source_file.bak',
        metavar='backup_location'
        )
    parser.add_argument('-D', '--disable-backup', action='store_true', help='When using -o, this option disables backup of source file before it is overwritten by the destination file.')
    parser.add_argument('--no-backup-asd', action='store_true', help='Disables backup of the asd file when using -o.')
    parser.add_argument(
        '-e', '--edit-tag',
        nargs='?', type=arg_pair, const=['edited_retagged', datetime.now().isoformat()],
        help='Adds a new tag to the destination file to indicate that it is an edited version. Requires two arguments tag_name,tag_value or zero arguments which defaults to the name "edited_retagged" and the value of the current time.',
        metavar='tag_name,tag_value'
        )
    args = parser.parse_args()
    source_file = os.path.realpath(args.source_file)
    destination_file = os.path.realpath(args.destination_file)
    copy_tags(source_file, destination_file, args.edit_tag)
    if args.overwrite:
        if not args.disable_backup:
            if args.backup_location:
                backup_location = os.path.realpath(args.backup_location)
                if os.path.isdir(backup_location):
                    backup_location = os.path.join(backup_location, os.path.basename(os.path.realpath(source_file)))
            else:
                backup_location = source_file + '.bak'
            try:
                backup_source_file(source_file, backup_location)
            except:
                print('Unable to backup source file. Aborting remaining actions. Error:\n')
                raise
            if not args.no_backup_asd:
                try:
                    backup_asd(source_file, backup_location)
                except FileNotFoundError:
                    pass
                except:
                    print('Unable to backup asd file. Aborting remaining actions. Error:\n')
                    raise
        overwrite_file(source_file, destination_file)