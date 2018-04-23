from pytube import YouTube
import boto3

# Add your credentials below and uncomment.
# Warning: DO NOT CHECK ANY CODE WHICH CONTAINS CREDENTIALS INTO GITHUB
#access_key=
#secret_key=

#Your bucket containing the video or audio you want to transcribe.
# Add your bucket name on the next line and uncomment.
#bucket_name=


transcribe = boto3.client(service_name='transcribe', region_name='us-west-2', aws_access_key_id=access_key,
    aws_secret_access_key=secret_key)

s3 = boto3.resource(service_name='s3', region_name='us-west-2', aws_access_key_id=access_key,
    aws_secret_access_key=secret_key)

yt = YouTube('https://www.youtube.com/watch?v=MaP5Dgg7tBA')
yt.streams.first().download()

s3.Bucket(bucket).upload_file('Amazon Alexa Moments Hide and Seek (Amazon Echo Commercial).mp4'
                                    ,'video/demo.mp4')


#Go into the AWS Console and look at the Transcribe service page to see your job and output.
response = transcribe.start_transcription_job(
    TranscriptionJobName='YourDemoJob',
    LanguageCode='en-US',
    MediaFormat='mp4',
    Media={
        'MediaFileUri': 'https://s3-us-west-2.amazonaws.com/debrosse-transcribe-demo/video/demo.mp4'
    },
    Settings={
        'ShowSpeakerLabels': True,
        'MaxSpeakerLabels': 10
    }
)

print(response)
