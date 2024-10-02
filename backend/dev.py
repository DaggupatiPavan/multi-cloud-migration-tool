from flask import Flask, request, jsonify, send_from_directory
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.storage.blob import BlobServiceClient
from google.cloud import storage, compute_v1
from google.oauth2 import service_account
import os
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
import time
from google.cloud import compute_v1
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
from google.oauth2 import service_account
from azure.identity import DefaultAzureCredential
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/list-instances', methods=['POST'])
def list_instances():
    data = request.json
    source = data.get('source')
    region = data.get('region')

    if source == 'aws':
        aws_access_key = data.get('awsAccessKey')
        aws_secret_key = data.get('awsSecretKey')

        # Create EC2 client
        ec2_client = boto3.client(
            'ec2',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # List EC2 instances
        instances = ec2_client.describe_instances()
        instance_info = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                # Get the instance ID
                instance_id = instance['InstanceId']
                
                # Get the instance name from tags
                instance_name = None
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                # If no name tag is found, use the instance ID as the name
                if not instance_name:
                    instance_name = instance_id
                
                instance_info.append(f"{instance_id} ({instance_name})")

        return jsonify({'instances': instance_info})

    # Placeholder for Azure and GCP logic
    return jsonify({'instances': []})

@app.route('/migrate-instances', methods=['POST'])
@app.route('/migrate-instances', methods=['POST'])
def migrate_instances():
    data = request.json
    instances = data.get('instances', [])
    source = data.get('source')
    destination = data.get('destination')
    
    # Log the instance migration request
    print(f"Migrating instances from {source} to {destination}: {instances}")

    if source == 'aws':
        if destination == 'azure':
            # Placeholder for AWS to Azure migration logic
            result = migrate_aws_to_azure(instances)
        elif destination == 'gcp':
            # Placeholder for AWS to GCP migration logic
            result = migrate_aws_to_gcp(instances)
    elif source == 'azure':
        if destination == 'aws':
            # Placeholder for Azure to AWS migration logic
            result = migrate_azure_to_aws(instances)
        elif destination == 'gcp':
            # Placeholder for Azure to GCP migration logic
            result = migrate_azure_to_gcp(instances)
    elif source == 'gcp':
        if destination == 'aws':
            # Placeholder for GCP to AWS migration logic
            result = migrate_gcp_to_aws(instances)
        elif destination == 'azure':
            # Placeholder for GCP to Azure migration logic
            result = migrate_gcp_to_azure(instances)

    return jsonify({'message': result})


def migrate_aws_to_azure(instances):
    aws_access_key = 'your_aws_access_key'
    aws_secret_key = 'your_aws_secret_key'
    aws_region = 'your_aws_region'
    
    azure_subscription_id = 'your_azure_subscription_id'
    azure_resource_group = 'your_azure_resource_group'
    azure_storage_account_name = 'your_azure_storage_account_name'
    azure_container_name = 'your_azure_container_name'
    
    # Step 1: Create an AMI of the instances
    ec2_client = boto3.client('ec2', 
                               aws_access_key_id=aws_access_key,
                               aws_secret_access_key=aws_secret_key,
                               region_name=aws_region)

    ami_ids = []
    for instance_id in instances:
        print(f"Creating AMI for instance {instance_id}...")
        response = ec2_client.create_image(InstanceId=instance_id, Name=f"{instance_id}-ami")
        ami_ids.append(response['ImageId'])

    # Step 2: Wait for AMIs to be available
    print("Waiting for AMIs to be available...")
    for ami_id in ami_ids:
        waiter = ec2_client.get_waiter('image_available')
        waiter.wait(ImageIds=[ami_id])
        print(f"AMI {ami_id} is available.")

    # Step 3: Export AMI to S3
    s3_bucket_name = 'your_s3_bucket_name'
    for ami_id in ami_ids:
        print(f"Exporting AMI {ami_id} to S3...")
        export_task = ec2_client.create_instance_export_task(
            InstanceId=ami_id,
            S3ExportLocation={
                'S3Bucket': s3_bucket_name,
                'S3Prefix': f"{ami_id}/"
            }
        )
        print(f"Export task for AMI {ami_id} started: {export_task['ExportToS3Task']['TaskId']}")

    # Step 4: Upload the image to Azure Blob Storage
    print("Uploading the image to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string('your_azure_blob_connection_string')
    blob_client = blob_service_client.get_blob_client(container=azure_container_name, blob='your_image_name')
    
    # Assuming you have downloaded the image from S3 to a local file path
    local_file_path = 'path_to_your_local_image_file'
    
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data)
    print("Image uploaded to Azure Blob Storage.")

    # Step 5: Create Azure VM from the uploaded image
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, azure_subscription_id)

    print("Creating Azure VM from the uploaded image...")
    # Define VM parameters
    vm_name = "YourVMName"
    vm_params = {
        'location': 'your_azure_region',
        'os_profile': {
            'computer_name': vm_name,
            'admin_username': 'your_admin_username',
            'admin_password': 'your_admin_password'
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'id': f"/subscriptions/{azure_subscription_id}/resourceGroups/{azure_resource_group}/providers/Microsoft.Compute/images/your_image_name"
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': 'your_network_interface_id',
                'properties': {
                    'primary': True
                }
            }]
        }
    }

    creation_result = compute_client.virtual_machines.begin_create_or_update(azure_resource_group, vm_name, vm_params)
    creation_result.wait()  # Wait for the VM creation to complete
    return f'Migrated AWS instances: {instances} to Azure VM {vm_name}'


import boto3
from google.cloud import storage, compute_v1
from google.oauth2 import service_account
import os

def migrate_aws_to_gcp(instances):
    aws_access_key = 'your_aws_access_key'
    aws_secret_key = 'your_aws_secret_key'
    aws_region = 'your_aws_region'
    
    gcp_project_id = 'your_gcp_project_id'
    gcp_bucket_name = 'your_gcp_bucket_name'
    gcp_zone = 'your_gcp_zone'
    
    # Step 1: Create an AMI of the instances
    ec2_client = boto3.client('ec2', 
                               aws_access_key_id=aws_access_key,
                               aws_secret_access_key=aws_secret_key,
                               region_name=aws_region)

    ami_ids = []
    for instance_id in instances:
        print(f"Creating AMI for instance {instance_id}...")
        response = ec2_client.create_image(InstanceId=instance_id, Name=f"{instance_id}-ami")
        ami_ids.append(response['ImageId'])

    # Step 2: Wait for AMIs to be available
    print("Waiting for AMIs to be available...")
    for ami_id in ami_ids:
        waiter = ec2_client.get_waiter('image_available')
        waiter.wait(ImageIds=[ami_id])
        print(f"AMI {ami_id} is available.")

    # Step 3: Export AMI to S3
    s3_bucket_name = 'your_s3_bucket_name'
    for ami_id in ami_ids:
        print(f"Exporting AMI {ami_id} to S3...")
        export_task = ec2_client.create_instance_export_task(
            InstanceId=ami_id,
            S3ExportLocation={
                'S3Bucket': s3_bucket_name,
                'S3Prefix': f"{ami_id}/"
            }
        )
        print(f"Export task for AMI {ami_id} started: {export_task['ExportToS3Task']['TaskId']}")

    # Step 4: Download the exported image from S3 to local or GCP Storage
    # NOTE: This step assumes you already downloaded the image or you can directly download it to GCP Storage.

    # For local download example
    # This part of the code needs to be implemented based on your S3 setup.
    local_file_path = 'path_to_your_local_image_file'

    # Download the image from S3 (implement the logic to download the S3 object)

    # Step 5: Upload the image to GCP Cloud Storage
    print("Uploading the image to GCP Cloud Storage...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcp_bucket_name)
    
    blob = bucket.blob('your_image_name')
    blob.upload_from_filename(local_file_path)
    print("Image uploaded to GCP Cloud Storage.")

    # Step 6: Create a GCP VM from the uploaded image
    print("Creating GCP VM from the uploaded image...")
    credentials = service_account.Credentials.from_service_account_file('path_to_your_service_account_key.json')
    
    compute_client = compute_v1.InstancesClient(credentials=credentials)

    instance_name = "YourVMName"
    source_image = f"projects/{gcp_project_id}/global/images/your_image_name"

    operation = compute_client.insert(
        project=gcp_project_id,
        zone=gcp_zone,
        instance_resource={
            'name': instance_name,
            'machine_type': f"zones/{gcp_zone}/machineTypes/n1-standard-1",
            'disks': [{
                'boot': True,
                'auto_delete': True,
                'initialize_params': {
                    'source_image': source_image,
                }
            }],
            'network_interfaces': [{
                'network': 'global/networks/default',
                'access_configs': [{
                    'name': 'External NAT',
                    'type': 'ONE_TO_ONE_NAT',
                }]
            }]
        }
    )

    # Wait for the operation to complete
    print(f"Waiting for GCP VM creation to complete: {operation.name}")
    wait_for_operation(gcp_project_id, gcp_zone, operation.name)

    return f'Migrated AWS instances: {instances} to GCP VM {instance_name}'

def wait_for_operation(project_id, zone, operation_name):
    compute_client = compute_v1.GlobalOperationsClient()
    while True:
        operation = compute_client.get(project=project_id, operation=operation_name)
        if operation.status == 'DONE':
            if 'error' in operation:
                raise Exception(f"Error during operation: {operation.error}")
            print("Operation completed successfully.")
            return
        print("Waiting for operation to complete...")



def migrate_azure_to_aws(instances):
    azure_tenant_id = 'your_azure_tenant_id'
    azure_client_id = 'your_azure_client_id'
    azure_client_secret = 'your_azure_client_secret'
    aws_access_key = 'your_aws_access_key'
    aws_secret_key = 'your_aws_secret_key'
    aws_region = 'your_aws_region'
    aws_s3_bucket = 'your_aws_s3_bucket'
    
    # Initialize Azure clients
    credentials = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credentials, 'your_azure_subscription_id')
    resource_client = ResourceManagementClient(credentials, 'your_azure_subscription_id')
    
    # Step 1: Export Azure VM to VHD
    for instance_id in instances:
        resource_group = 'your_resource_group'  # Define your resource group
        vm_name = instance_id  # Assuming instance_id is the name of the VM

        print(f"Exporting Azure VM {vm_name} to VHD...")
        blob_container_name = 'your_blob_container'
        vhd_uri = f"https://{your_storage_account}.blob.core.windows.net/{blob_container_name}/{vm_name}.vhd"

        # Start the export process
        async_export = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
        async_export.wait()
        async_export = compute_client.virtual_machines.begin_generalize(resource_group, vm_name)
        async_export.wait()
        async_export = compute_client.virtual_machines.begin_export_image(resource_group, vm_name, {
            'target_vhd': vhd_uri,
            'os_type': 'Windows'  # Change based on your OS type
        })

        async_export.wait()
        print(f"VM {vm_name} exported to {vhd_uri}")

        # Step 2: Upload the VHD to AWS S3
        print(f"Uploading VHD to AWS S3 bucket {aws_s3_bucket}...")
        s3_client = boto3.client('s3', 
                                  aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=aws_secret_key,
                                  region_name=aws_region)

        s3_client.upload_file(vhd_uri, aws_s3_bucket, f"{vm_name}.vhd")
        print(f"Uploaded {vm_name}.vhd to S3 bucket {aws_s3_bucket}")

    # Step 3: Import the VHD to AWS as AMI
    for instance_id in instances:
        print(f"Importing {instance_id}.vhd to AWS...")
        import_task = {
            'Description': f'Imported from Azure: {instance_id}',
            'DiskContainers': [
                {
                    'Description': f'VHD of {instance_id}',
                    'Format': 'vhd',
                    'Url': f'https://{aws_s3_bucket}.s3.amazonaws.com/{instance_id}.vhd'
                }
            ]
        }
        
        ec2_client = boto3.client('ec2', 
                                   aws_access_key_id=aws_access_key,
                                   aws_secret_access_key=aws_secret_key,
                                   region_name=aws_region)

        response = ec2_client.import_image(**import_task)
        print(f"Import task started: {response['ImportTaskId']}")

        # Wait for import task to complete
        while True:
            task_status = ec2_client.describe_import_image_tasks(ImportTaskIds=[response['ImportTaskId']])
            status = task_status['ImportImageTasks'][0]['Status']
            print(f"Import status: {status}")

            if status == 'completed':
                print(f"Import of {instance_id} completed.")
                break
            elif status == 'failed':
                raise Exception("Import failed.")
            time.sleep(5)

    # Step 4: Launch new EC2 instance from imported AMI
    ami_id = response['ImportTaskId']  # Get the AMI ID from the import task
    instance_type = 't2.micro'  # Define your instance type
    instance_name = "MigratedFromAzure"

    ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName='your_key_pair',  # Specify your key pair
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': instance_name}]
        }]
    )

    return f'Migrated Azure instances: {instances} to AWS successfully!'



def migrate_azure_to_gcp(instances):
    azure_tenant_id = 'your_azure_tenant_id'
    azure_client_id = 'your_azure_client_id'
    azure_client_secret = 'your_azure_client_secret'
    gcp_service_account_key = 'path/to/your/gcp_service_account_key.json'
    gcp_project_id = 'your_gcp_project_id'
    gcp_bucket_name = 'your_gcp_bucket_name'
    
    # Initialize Azure clients
    credentials = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credentials, 'your_azure_subscription_id')
    
    # Step 1: Export Azure VM to VHD
    for instance_id in instances:
        resource_group = 'your_resource_group'  # Define your resource group
        vm_name = instance_id  # Assuming instance_id is the name of the VM

        print(f"Exporting Azure VM {vm_name} to VHD...")
        blob_container_name = 'your_blob_container'
        vhd_uri = f"https://{your_storage_account}.blob.core.windows.net/{blob_container_name}/{vm_name}.vhd"

        # Start the export process
        async_export = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
        async_export.wait()
        async_export = compute_client.virtual_machines.begin_generalize(resource_group, vm_name)
        async_export.wait()
        async_export = compute_client.virtual_machines.begin_export_image(resource_group, vm_name, {
            'target_vhd': vhd_uri,
            'os_type': 'Windows'  # Change based on your OS type
        })

        async_export.wait()
        print(f"VM {vm_name} exported to {vhd_uri}")

        # Step 2: Upload the VHD to Google Cloud Storage
        print(f"Uploading VHD to Google Cloud Storage bucket {gcp_bucket_name}...")
        storage_client = storage.Client.from_service_account_json(gcp_service_account_key)
        bucket = storage_client.bucket(gcp_bucket_name)

        # Upload the VHD file to GCP
        blob = bucket.blob(f"{vm_name}.vhd")
        blob.upload_from_filename(vhd_uri)
        print(f"Uploaded {vm_name}.vhd to GCP bucket {gcp_bucket_name}")

    # Step 3: Create an image from the uploaded VHD in GCP
    for instance_id in instances:
        print(f"Creating GCP image from {instance_id}.vhd...")
        image_name = f"{instance_id}-image"
        
        # Create a new image from the VHD in GCP
        image = {
            'name': image_name,
            'source': f"gs://{gcp_bucket_name}/{instance_id}.vhd",
            'storage_locations': ['us-central1']  # Set to the desired region
        }
        
        from google.cloud import compute_v1
        images_client = compute_v1.ImagesClient()
        operation = images_client.insert(project=gcp_project_id, image_resource=image)
        operation.result()  # Wait for the operation to complete
        print(f"Created image {image_name} in GCP.")

    # Step 4: Launch new GCP instance from the image
    for instance_id in instances:
        print(f"Launching new GCP instance from image {image_name}...")
        instance_name = f"{instance_id}-instance"
        instance_body = {
            'name': instance_name,
            'machineType': f"zones/us-central1-a/machineTypes/n1-standard-1",  # Adjust machine type as needed
            'disks': [{
                'boot': True,
                'initializeParams': {
                    'sourceImage': f"projects/{gcp_project_id}/global/images/{image_name}"
                }
            }],
            'networkInterfaces': [{
                'network': 'global/networks/default',  # Adjust network as needed
                'accessConfigs': [{'type': 'ONE_TO_ONE_NAT'}]
            }]
        }
        
        instances_client = compute_v1.InstancesClient()
        operation = instances_client.insert(project=gcp_project_id, zone='us-central1-a', instance_resource=instance_body)
        operation.result()  # Wait for the operation to complete
        print(f"Launched new instance {instance_name} in GCP successfully.")

    return f'Migrated Azure instances: {instances} to GCP successfully!'


def migrate_gcp_to_aws(instances):
    gcp_project_id = 'your_gcp_project_id'
    gcp_region = 'us-central1'  # Set your GCP region
    aws_access_key = 'your_aws_access_key'
    aws_secret_key = 'your_aws_secret_key'
    s3_bucket_name = 'your_s3_bucket_name'

    # Initialize GCP Storage client
    storage_client = storage.Client()
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    for instance_id in instances:
        print(f"Migrating GCP instance {instance_id} to AWS...")

        # Step 1: Export GCP VM to image
        image_name = f"{instance_id}-image"
        print(f"Creating image from GCP instance {instance_id}...")
        compute_client = compute_v1.ImagesClient()

        operation = compute_client.insert(
            project=gcp_project_id,
            image_resource={
                'name': image_name,
                'sourceDisk': f"projects/{gcp_project_id}/zones/{gcp_region}/disks/{instance_id}",
                'sourceDiskZone': gcp_region
            }
        )
        operation.result()  # Wait for the operation to complete
        print(f"Created image {image_name} in GCP.")

        # Step 2: Download the image to local storage (if needed)
        # This would usually involve exporting the image to GCS and then downloading
        # For simplicity, we assume the image is accessible via GCP
        gcs_image_uri = f"gs://{your_gcs_bucket}/{image_name}.img"

        # Step 3: Transfer the image to AWS S3
        try:
            print(f"Transferring image from GCP to AWS S3 bucket {s3_bucket_name}...")
            blob = storage.Blob(f"{image_name}.img", storage_client.bucket(your_gcs_bucket))
            blob.download_to_filename(f"/tmp/{image_name}.img")  # Download to local path
            
            # Upload to S3
            s3_client.upload_file(f"/tmp/{image_name}.img", s3_bucket_name, f"{image_name}.img")
            print(f"Uploaded {image_name}.img to AWS S3 bucket {s3_bucket_name}.")
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error with AWS credentials: {str(e)}")
            return f"Failed to migrate GCP instances: {instances} to AWS due to credential issues."

        # Step 4: Launch new EC2 instance from the uploaded image
        print(f"Launching new EC2 instance from {image_name}.img...")
        ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

        try:
            response = ec2_client.run_instances(
                ImageId=image_name,  # Use the correct AMI ID here
                InstanceType='t2.micro',  # Adjust as needed
                MinCount=1,
                MaxCount=1,
                KeyName='your_aws_key_pair',  # Your AWS key pair for SSH access
                SecurityGroupIds=['your_security_group'],  # Your security group
                SubnetId='your_subnet_id'  # Your VPC subnet
            )
            print(f"Launched new EC2 instance: {response['Instances'][0]['InstanceId']}.")
        except Exception as e:
            print(f"Failed to launch EC2 instance: {str(e)}")

    return f'Migrated GCP instances: {instances} to AWS successfully!'


from google.cloud import compute_v1
from azure.storage.blob import BlobServiceClient
import os

def migrate_gcp_to_azure(instances):
    gcp_project_id = 'your_gcp_project_id'
    gcp_region = 'us-central1'  # Set your GCP region
    azure_storage_connection_string = 'your_azure_storage_connection_string'
    azure_container_name = 'your_azure_container_name'

    # Initialize GCP client
    compute_client = compute_v1.ImagesClient()

    for instance_id in instances:
        print(f"Migrating GCP instance {instance_id} to Azure...")

        # Step 1: Export GCP VM to image
        image_name = f"{instance_id}-image"
        print(f"Creating image from GCP instance {instance_id}...")
        operation = compute_client.insert(
            project=gcp_project_id,
            image_resource={
                'name': image_name,
                'sourceDisk': f"projects/{gcp_project_id}/zones/{gcp_region}/disks/{instance_id}",
                'sourceDiskZone': gcp_region
            }
        )
        operation.result()  # Wait for the operation to complete
        print(f"Created image {image_name} in GCP.")

        # Step 2: Download the image to local storage (if needed)
        gcs_image_uri = f"gs://{your_gcs_bucket}/{image_name}.img"

        # Step 3: Transfer the image to Azure Blob Storage
        try:
            print(f"Transferring image from GCP to Azure Blob Storage container {azure_container_name}...")
            blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)
            blob_client = blob_service_client.get_blob_client(container=azure_container_name, blob=f"{image_name}.img")
            
            # Download the image from GCP (assuming it's stored in GCS)
            os.system(f"gsutil cp {gcs_image_uri} /tmp/{image_name}.img")  # Download to local path

            # Upload to Azure Blob Storage
            with open(f"/tmp/{image_name}.img", "rb") as data:
                blob_client.upload_blob(data)
                print(f"Uploaded {image_name}.img to Azure Blob Storage.")
        except Exception as e:
            print(f"Failed to transfer image to Azure: {str(e)}")
            return f"Failed to migrate GCP instances: {instances} to Azure."

        # Step 4: Create a new Azure VM from the uploaded image
        print(f"Creating new Azure VM from {image_name}.img...")
        # Implement Azure VM creation logic using Azure SDK
        # For example:
        # from azure.mgmt.compute import ComputeManagementClient
        # from azure.common.credentials import ServicePrincipalCredentials
        
        credentials = ServicePrincipalCredentials(
            client_id='your_azure_client_id',
            secret='your_azure_client_secret',
            tenant='your_azure_tenant_id'
        )
        compute_client = ComputeManagementClient(credentials, 'your_azure_subscription_id')

        # Create the VM from the uploaded image
        async_vm_creation = compute_client.virtual_machines.create_or_update(
            'your_resource_group_name',
            f'vm-{instance_id}',
            {
                'location': 'your_azure_region',
                'os_profile': {
                    'computer_name': f'vm-{instance_id}',
                    'admin_username': 'azure_user',
                    'admin_password': 'your_password'
                },
                'hardware_profile': {
                    'vm_size': 'Standard_DS1_v2'
                },
                'storage_profile': {
                    'image_reference': {
                        'id': f"/subscriptions/{your_azure_subscription_id}/resourceGroups/{your_resource_group_name}/providers/Microsoft.Compute/images/{image_name}"
                    },
                    'os_disk': {
                        'name': f'disk-{instance_id}',
                        'create_option': 'FromImage'
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': 'your_network_interface_id'
                    }]
                }
            }
        )
        async_vm_creation.wait()  # Wait for the VM to be created
        print(f"Created Azure VM from GCP instance {instance_id}.")

    return f'Migrated GCP instances: {instances} to Azure successfully!'



if __name__ == '__main__':
    app.run(debug=True)
	
