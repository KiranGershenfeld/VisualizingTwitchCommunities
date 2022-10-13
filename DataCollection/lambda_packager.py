import shutil
import sys
import os 
from dotenv import load_dotenv

load_dotenv()

#SIMPLE UTILITY SCRIPT TO PACKAGE AND UPLOAD LAMBDAS 

def create_lambda_package(directory, upload_to_lambda):
    function_path = f'{directory}/lambda_function.py'
    site_packages_path = f'{directory}/env/lib/python3.8/site-packages'
    shutil.copyfile(function_path, f'{site_packages_path}/lambda_function.py')
    shutil.make_archive(f'{directory}/lambda_package', 'zip', site_packages_path)

    if(upload_to_lambda):
        import boto3

        arn = os.environ.get(directory)

        with open(f'{directory}/lambda_package.zip', 'rb') as f:
            zipped_code = f.read()

        client = boto3.client(
            'lambda',
            region_name = 'us-east-2',
            aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        
        response = client.update_function_code(
            FunctionName=arn,
            ZipFile=zipped_code,
        )

        


if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    directory_cmd = sys.argv[1]
    upload_to_lambda = sys.argv[2]

    if(directory_cmd == 'all'):
        directories = ['Lambda1', 'Lambda2', 'Lambda3', 'Lambda4']
        for directory in directories:
            create_lambda_package(directory, upload_to_lambda)
    else:
        create_lambda_package(directory_cmd, upload_to_lambda)

        


