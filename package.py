#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, os, shutil, glob, tarfile
from setup_functions import get_package_version, get_package_requirements

NAME = 'minermedic'
SOURCE_DIRECTORY = 'phenome'
APPS = ['minermedic']

# get the root dir
rootdir = os.path.abspath(os.path.dirname(__file__))

# get the build version
build_version = get_package_version(SOURCE_DIRECTORY, rootdir, True)

# generate the tarball name
tarball_name = NAME + "-" + build_version + ".tar.gz"

# remove the version from the name so we can work more easily
new_tarball_path = "./build/" + NAME + ".tar.gz"

os.mkdir("./build")

print("{} tarball=./dist/{}".format(NAME, tarball_name))

# move/rename the tarball
os.rename("./dist/" + tarball_name, new_tarball_path)

# unpack into the build dir so we can work with contents 
shutil.unpack_archive(new_tarball_path, "./build/")

versioned_pathname = "./build/" + NAME + "-" + build_version
working_pathname = "./build/" + NAME

os.rename(versioned_pathname, working_pathname)

# clean up the working directory
shutil.rmtree(working_pathname + "/" + NAME + ".egg-info")
os.remove(working_pathname + "/setup.cfg")

# iterate through APPs and do app specific things to create each package
for app in APPS:
	
	app_name = app + "-" + build_version
	target_app_folder = "./build/" + app_name
	print("processing {}".format(app_name))

	# copy the main tree
	shutil.copytree(working_pathname, target_app_folder)

	# copy the apps static images to the main static image dir
	target_img_dir = target_app_folder + "/phenome/static/images"
	source_img_dir = target_app_folder + "/phenome/static/apps/{}/lib/img".format(app)
	for img_file in glob.glob(source_img_dir+"\\*.*"):
		shutil.copy2(img_file, target_img_dir)
		
	# move the ini sample file to the root of the distribution
	source_ini_file = target_app_folder + "/{}/{}.ini.dist".format(app,app)
	dest_init_file = target_app_folder + "/{}.ini.sample".format(app)
	shutil.move(source_ini_file, dest_init_file)

	# finally TAR into the resulting distribution tarball
	output_filename = "./dist/" + app_name + ".tar.gz"
	tar = tarfile.open(output_filename, "w:gz")
	tar.add(target_app_folder, arcname=os.path.basename(target_app_folder))

	print("Created new app package {}".format(output_filename))
	

    