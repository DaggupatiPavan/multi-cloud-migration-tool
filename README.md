# Multi-Cloud Migration Tool

![AWS Logo](https://logos-world.net/wp-content/uploads/2021/08/Amazon-Web-Services-AWS-Logo-700x394.png) ![Azure Logo]([https://upload.wikimedia.org/wikipedia/commons/4/4f/Microsoft_Azure_Logo.svg](https://swimburger.net/media/ppnn3pcl/azure.png)) ![GCP Logo]([https://upload.wikimedia.org/wikipedia/commons/4/4e/Google_Cloud_Platform_Logo.svg](https://1000logos.net/wp-content/uploads/2020/05/Logo-Google-Cloud.jpg))

## Overview

The **Multi-Cloud Migration Tool** allows users to seamlessly migrate virtual machine instances across major cloud platforms: **AWS**, **Azure**, and **Google Cloud Platform (GCP)**. With an intuitive user interface and powerful backend integration, users can select source and destination clouds, manage regions, and initiate migrations with ease.

## Features

- **Cross-Cloud Migration**: Migrate instances between AWS, Azure, and GCP effortlessly.
- **User-Friendly Interface**: Simple web interface to select clouds, regions, and instances.
- **Multi-Region Support**: Specify regions for both source and destination clouds.
- **Real-Time Notifications**: Get notified about the migration status.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Cloud Providers**: AWS, Azure, Google Cloud
- **Dependencies**:
    - Flask
    - Boto3 (AWS SDK)
    - Google Cloud Libraries
    - Azure SDKs

## Installation

### Prerequisites

- **Python 3.x**: Ensure Python is installed on your machine.
- **Git**: For cloning the repository.

### Clone the Repository

```bash
git clone https://github.com/yourusername/multi-cloud-migration-tool.git
cd multi-cloud-migration-tool/backend/
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Start Application
```bash
python app.py
```
