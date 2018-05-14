# -*- coding: utf-8 -*-
"""fab_support
"""


import boto3
import datetime as dt
from distutils.dir_util import copy_tree
import mimetypes
import os
import shutil
import sys
import socketserver

from fabric.api import run, local, env, settings, cd, task, put, execute
from fabric.operations import require
from unipath import Path, DIRS

from pelican.server import ComplexHTTPRequestHandler


@task
def build(stage):
    """Build version of site ready for use locally or deployment to main site eg fab local build"""
    copy_images(stage)
    local(f"pelican -s {env['stages'][stage]['config_file']}")


@task
def copy_images(stage, alias='ci'):
    """Copy files in all images directories"""
    src = Path(env['stages'][stage].deploy_path).ancestor(2).child('content')
    dst = src.ancestor(2).child('images')
    for my_dir in src.walk(filter=DIRS):  # os.walk('./..'):
        if my_dir.name == 'images':
            copy_tree(my_dir, dst)


@task
def rebuild(stage):
    """`build` with the delete switch"""
    local(f"pelican -d -s {env['stages'][stage]['config_file']}")


@task
def regenerate():
    """Automatically regenerate site upon file modification"""
    local("pelican -r -s {env['stages'][stage]['config_file']}")


@task
def serve(stage):
    """Serve site at eg http://localhost:8000/"""
    os.chdir(env['stages'][stage]['deploy_path'])

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', env['stages'][stage]['PORT']), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(env['stages'][stage]['PORT']))
    server.serve_forever()


@task
def reserve(stage):
    """`build`, then `serve`"""
    build(stage)
    serve(stage)


@task
def deploy(stage):
    """Publish to stage. includes build."""
    build(stage)
    deploy_path = env['stages'][stage]['deploy_path']
    destination = env['stages'][stage]['destination']
    copy_method = env['stages'][stage]['copy_method']
    print(f'Using copy from {deploy_path} to {destination}')
    copy_method(deploy_path, destination)
    # ? clean()
    # copy_tree(DEPLOY_PATH, LOCAL_SITE_PATH)
    # copy_tree(DEPLOY_PATH.ancestor(2).child(
    #     'Pelican').child('pelican-bootstrap3').child('static'),
    #                 LOCAL_SITE_PATH.child('static'))
    # copy_tree(DEPLOY_PATH.ancestor(1).child(
    #     'content').child('images'),
    #                 LOCAL_SITE_PATH.child('images'))


@task
def clean(stage):
    """Remove newly generated files from remote environment"""
    destination = env['stages'][stage]['destination']
    if os.path.isdir(destination):
        shutil.rmtree(destination)
        os.makedirs(destination)

        # ?try:
        #    shutil.rmtree(LOCAL_SITE_PATH)
        # except FileNotFoundError:
        #    pass  # doesn't exist


@task
def s3_upload(stage):
    """Publish to S3"""
    rebuild(stage)
    # get an access token, local (from) directory, and S3 (to) directory
    # from the command-line
    #local_directory = Path(normpath('./output'))
    local_directory = Path('./output').norm()
    print('Local directory = {}',format(local_directory))
    bucket = env['stages'][stage]['S3_BUCKET']

    client = boto3.client('s3')

    # enumerate local files recursively
    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = Path(root, filename).norm()
            print('Local path = {}', format(local_path))
            # construct the full S3 path
            s3_path = '/'.join(local_directory.rel_path_to(local_path).components())[1:]
            print('Searching for path "{}" in "{}" for {}'.format(s3_path, bucket, local_path))
            try:
                file = client.head_object(Bucket=bucket, Key=s3_path)
                lt = dt.datetime.utcfromtimestamp(local_path.mtime())
                #print('Local time {} and external time {}'.format(lt,file['LastModified']))
                print("Path found on S3! Skipping {} which has {}...".format(s3_path, file['LastModified']))

                try:
                    client.delete_object(Bucket=bucket, Key=s3_path)
                    print("Uploading %s..." % s3_path)
                    mime_type = mimetypes.guess_type(local_path)
                    client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                               'ACL': 'public-read'})
                except:
                    print("Unable to delete %s..." % s3_path)
            except:
                print("Uploading %s..." % s3_path)
                mime_type = mimetypes.guess_type(local_path)
                client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                           'ACL': 'public-read'})
    # s3cmd sync $(OUTPUTDIR)/ s3://$(S3_BUCKET) --acl-public --delete-removed --guess-mime-type --no-mime-magic --no-preserve




@task
def gh_pages(stage):
    """Publish to GitHub Pages"""
    rebuild(stage)
    local(f"ghp-import -b {env['stages'][stage]['github_pages_branch']} {env['stages'][stage]['deploy_path']} -p")

