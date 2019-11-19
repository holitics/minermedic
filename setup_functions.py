import boto3, os

def get_package_requirements():

    REQUIRED = []
    # Load the package's requirements from the TXT file
    with open('requirements.txt') as f:
        for line in f:
            line = line.partition('#')[0]
            line = line.rstrip()
            if line is not None and len(line) > 0 and line.startswith('--') is False:
                REQUIRED.append(line)

    return REQUIRED

def get_platform():

    # https://www.python.org/dev/peps/pep-0513/
    # https://www.python.org/dev/peps/pep-0425/#abi-tag

    from distutils import util

    PLATFORMS = util.get_platform()

    print("Distutils PLATFORM={}".format(PLATFORMS))

    return PLATFORMS

    # TODO - see if using raw platform is OK before we shorten

    if 'macosx' in PLATFORMS or 'darwin' in PLATFORMS:
        PLATFORMS = "darwin-x86_64"
    elif 'linux' in PLATFORMS:
        PLATFORMS = "linux-x86_64"

    print("Package PLATFORM={}".format(PLATFORMS))

    return PLATFORMS

def __get_version_from_file(version_file):

    import re

    verstr = 'unknown'

    try:
        print("Try to open version file {}".format(version_file))
        verfile = open(version_file, "rt")
        verstrline = verfile.read()
        verfile.close()
    except EnvironmentError:
        print("WARNING! There is no version file {}".format(version_file))
        from phenome_core.version import __version__
        if __version__ is not None:
            print("Using version module to get version {}".format(__version__))
            verstr = __version__
    else:
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            verstr = mo.group(1)
        else:
            print("unable to find version in %s" % (version_file,))
            raise RuntimeError("if %s exists, it is required to be well-formed" % (version_file,))

    return verstr

def get_package_version(package, root_dir, write_new_file):

    # Load the package's version.py module as a dictionary.
    # Then set a VERSION NUMBER for the build to be used by requirements and the SETUP

    import os, re

    VERSIONFILE = os.path.join(root_dir, package, "version.py")
    LASTBUILDFILE = os.path.join(root_dir, package, ".lastbuild.py")

    verstr = __get_version_from_file(VERSIONFILE)
    verstr_lastbuild = __get_version_from_file(LASTBUILDFILE)

    # set the version based on version + build_number
    if '%s' in verstr:

        # we need to insert the build number
        travis_build_no = os.environ.get('TRAVIS_BUILD_NUMBER', 0)
        print('travis-build:{}'.format(travis_build_no))

        if (travis_build_no == 0 or travis_build_no == '') and ('%s' not in verstr_lastbuild):

            # is there a prior build file? If so, use the version from that
            build_version = verstr_lastbuild
            print('using last build version: {}'.format(verstr_lastbuild))

        else:

            build_version = verstr % travis_build_no

            if write_new_file:

                # we need to rewrite the file with the new version in it
                print('writing new version file: {}'.format(VERSIONFILE))
                with open(VERSIONFILE, "w") as f:
                    f.write("__version__ = '{}'".format(build_version))

                print('writing last build version file: {}'.format(LASTBUILDFILE))
                with open(LASTBUILDFILE, "w") as f:
                    f.write("__version__ = '{}'".format(build_version))


    else:
        build_version = verstr

    print("Version for package is: {}".format(build_version))

    return build_version

def upload_build(package, build_prefix):

    # get root dir of where we are running the script
    rootdir = os.path.abspath(os.path.dirname(__file__))

    # get the build version
    build_version = get_package_version(package, rootdir, True)

    # set the access and secret keys
    access_key = os.environ.get('AMZ_ACCESS_KEY', 'key')
    secret_key = os.environ.get('AMZ_SECRET_KEY', 'secret')

    S3_OBJECT = boto3.client('s3', region_name='us-east-1',
                             aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key)

    # one bucket for this package - NOTE: cannot create buckets with __ in them for some reason
    build_bucket_name = 'phenome-builds-{}'.format(build_prefix.replace("_","-")).lower()

    # the alternate has no platform info attached to it
    tarball_name_alt = "{}-{}.tar.gz".format(build_prefix, build_version)
    tarball_path_alt = "{}/dist/{}".format(rootdir,tarball_name_alt)

    if (os.path.exists(tarball_path_alt)):
        print("uploading tarball '{}' to S3 bucket '{}'".format(tarball_name_alt, build_bucket_name))
        S3_OBJECT.upload_file(tarball_path_alt, build_bucket_name, tarball_name_alt)
    else:
        print ("File {} does not exist..".format(tarball_path))
        raise Exception


if __name__ == '__main__':

    import sys

    if "upload_core_s3" in sys.argv:
        upload_build('phenome', 'phenome-core')
    elif "upload_minermedic_s3" in sys.argv:
        upload_build('phenome', 'minermedic')
    elif "upload_sampleapp_s3" in sys.argv:
        upload_build('phenome', 'sample_app')

