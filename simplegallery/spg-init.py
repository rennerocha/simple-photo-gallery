import argparse
import logging
import os
import sys
import pkg_resources
import glob
import shutil
import json
from distutils.dir_util import copy_tree


logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)-6s %(message)s')


def parse_args():
    """
    Configures the argument parser
    :return: Parsed arguments
    """

    description = '''Initializes a new Simple Photo Gallery in the specified folder (default is the current folder). 

    This script creates config files, copies the required templates for the gallery and moves the photos to the correct 
    subfolder in the newly created structure.'''

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-p', '--path',
                        dest='path',
                        action='store',
                        default='.',
                        help='Path to the folder which will be turned into a gallery')

    parser.add_argument('--force',
                        dest='force',
                        action='store_true',
                        help='Overrides existing config and template files files')

    return parser.parse_args()


def check_if_gallery_creation_possible(gallery_root):
    """
    Checks if a gallery can be created in the specified folder
    :param gallery_root: Root of the new gallery
    :return: True if a new gallery can be created and false otherwise
    """

    # Check if the path exists
    if not os.path.exists(gallery_root):
        logging.error(f'The specified gallery path does not exist ({gallery_root}).')
        return False

    return True


def check_if_gallery_already_exists(gallery_root):
    """
    Checks if a gallery already exists in the specified folder
    :param gallery_root: Root of the new gallery
    :return: True if a gallery exists and false otherwise
    """

    paths_to_check = [
        os.path.join(gallery_root, 'gallery.json'),
        os.path.join(gallery_root, 'images_data.json'),
        os.path.join(gallery_root, 'index_template.html'),
        os.path.join(gallery_root, 'public'),
    ]

    # Check if any of the paths exists
    for path in paths_to_check:
        if os.path.exists(path):
            return True

    return False


def create_gallery_folder_structure(gallery_root):
    """
    Creates the gallery folder structure by copying all the gallery templates and moving all images and videos to the
    photos subfolder
    :param gallery_root: Path to the gallery root
    """

    # Copy the public folder
    copy_tree(pkg_resources.resource_filename('simplegallery', 'templates/public'), os.path.join(gallery_root, 'public'))

    # Move all images and videos to the correct subfolder under public
    photos_dir = os.path.join(gallery_root, 'public', 'images', 'photos')
    for path in glob.glob(os.path.join(gallery_root, '*')):
        basename_lower = os.path.basename(path).lower()
        if basename_lower.endswith('.jpg') or basename_lower.endswith('.jpeg') or basename_lower.endswith('.gif') or basename_lower.endswith('.mp4'):
            shutil.move(path, os.path.join(photos_dir, os.path.basename(path)))

    # Copy the HTML template
    copy_tree(pkg_resources.resource_filename('simplegallery', 'templates/html'), gallery_root)


def create_gallery_json(gallery_root):
    """
    Creates a new gallery.json file, based on settings specified by the user
    :param gallery_root: Path to the gallery root
    """

    # Initialize the gallery config with the main gallery paths
    gallery_config = dict(
        images_data_file=os.path.join(gallery_root, 'images_data.json'),
        public_path=os.path.join(gallery_root, 'public'),
        images_path=os.path.join(gallery_root, 'public', 'images', 'photos'),
        thumbnails_path=os.path.join(gallery_root, 'public', 'images', 'thumbnails'),
    )

    # Set configuration defaults
    DEFAULT_TITLE = 'My Gallery'
    DEFAULT_DESCRIPTION = 'Default description of my gallery'
    DEFAULT_THUMBNAIL_HEIGHT = '320'

    # Ask the user for the title
    gallery_config['title'] = input(f'What is the title of your gallery? (default: "{DEFAULT_TITLE}")\n') or DEFAULT_TITLE

    # Ask the user for the description
    gallery_config['description'] = input(f'What is the description of your gallery? (default: "{DEFAULT_DESCRIPTION}")\n') or DEFAULT_DESCRIPTION

    # Ask the user for the thumbnail size
    while True:
        thumbnail_size = input(f'What should be the height of your thumbnails (between 32 and 1024)? (default: {DEFAULT_THUMBNAIL_HEIGHT})\n') or DEFAULT_THUMBNAIL_HEIGHT
        if thumbnail_size.isdigit():
            thumbnail_size = int(thumbnail_size)
            if 32 <= thumbnail_size <= 1024:
                break
    gallery_config['thumbnail_height'] = thumbnail_size

    # Save the configuration to a file
    gallery_config_path = os.path.join(gallery_root, 'gallery.json')
    with open(gallery_config_path, 'w') as out:
        json.dump(gallery_config, out, indent=4, separators=(',', ': '))


def main():
    """
    Initializes a new Simple Photo Gallery in a specified folder
    """
    # Parse the arguments
    args = parse_args()

    # Get the gallery root from the arguments
    gallery_root = args.path

    # Check if a gallery can be created at this location
    if not check_if_gallery_creation_possible(gallery_root):
        sys.exit(1)

    # Check if the specified gallery root already contains a gallery
    if check_if_gallery_already_exists(gallery_root):
        if not args.force:
            logging.info('A Simple Photo Gallery already exists at the specified location. Set the --force parameter '
                         'if you want to overwrite it.')
            sys.exit(0)
        else:
            logging.info('A Simple Photo Gallery already exists at the specified location, but will be overwritten.')

    # Copy the template files to the gallery root
    create_gallery_folder_structure(gallery_root)

    # Create the gallery json file
    create_gallery_json(gallery_root)


if __name__ == "__main__":
    main()
