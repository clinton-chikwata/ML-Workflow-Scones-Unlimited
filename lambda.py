"""serializeImageData function below will 
   1 . copy an object from S3, 
   2 . base64 encode it,
   3 and then return it to the step function as `image_data` in an event.
"""

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']   
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




""" Image Classification function is responsible for the classification part - 
1. we're going to take the image output from the previous function,
2.decode it, 
3.and then pass inferences back to the the Step Function."""

import json
import base64
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor 


# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-02-07-15-40-05-854'

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    predictor = Predictor(endpoint_name=ENDPOINT)

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    inferences = json.loads(response['Body'].read())
    
    # We return the data back to the Step Function    
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': event
    }


"""
Lambda Function 3: Filter-Low-Confidence-Inferences
A lambda function that takes the inferences from the Lambda 2 function output and filters low-confidence inferences
(above a certain threshold indicating success)
"""

import json


THRESHOLD = .70


def lambda_handler(event, context):
    
    # Grab the inferences from the event
  
    inferences = event['body']['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(list(inferences))>THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }