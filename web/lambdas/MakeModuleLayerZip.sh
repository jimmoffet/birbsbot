#!/bin/bash

# MAKE SURE YOU ARE INSIDE AN (ENV)

# clean any existing files
echo "Cleaning existing temp files/folders"
rm -r ./env/python
rm ./env/python_layer.zip

echo "Upgrading pip"
python -m pip install --upgrade pip

# install some packages
echo "Installing specified packages"
pip install requests

# copy site-packages to root of env and compress to zip
echo "Copying site-packages to root of env and compressing to zip"
cp -r ./env/lib/python3.8/site-packages ./env
mv ./env/site-packages ./env/python
cd env
zip -r ./python_layer.zip ./python
rm -r ./python

NOTE: max size of zip file is 50MB compressed, 250mb uncompressed
https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html

TODO: send the zip file to S3 and point lambda layer to it

# arn:aws:lambda:us-west-2:296153684168:function:BirbsBotHelloWorld
FUNCTION_NAME=BirbsBotHelloWorld
FUNCTION_ARN_ID=296153684168
FUNCTION_REGION=us-west-2
MODULES_LAYER_NAME=birbsbot-helloworld-common-app-modules
MODULES_LAYER_DESC="BirbsBot Hello World dependencies for Python application modules"
MODULES_LAYER_VERSION=2

# push zip to aws and make available as layer
echo "Pushing zip to aws and making available as layer"
aws lambda publish-layer-version \
--layer-name $MODULES_LAYER_NAME \
--description "$MODULES_LAYER_DESC" \
--compatible-runtimes python3.6 python3.7 python3.8 python3.9 \
--zip-file fileb://python_layer.zip

# update existing function to tell it to use the new layer
# echo "Updating existing function to use the new layer"
# aws lambda update-function-configuration \
# --function-name $FUNCTION_NAME \
# --layers arn:aws:lambda:$FUNCTION_REGION:$FUNCTION_ARN_ID:layer:$MODULES_LAYER_NAME:$MODULES_LAYER_VERSION

cd ..
rm ./env/python_layer.zip