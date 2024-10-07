# Multi-Cloud Migration Tool

![AWS Logo]([https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_Web_Services_Logo.svg](https://www.google.com/url?sa=i&url=https%3A%2F%2Flogos-world.net%2Famazon-web-services-logo%2F&psig=AOvVaw0vDLsK33KgdT_AzfSnc1hj&ust=1728368472325000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCIj3s7nQ-4gDFQAAAAAdAAAAABAE)) ![Azure Logo](https://upload.wikimedia.org/wikipedia/commons/4/4f/Microsoft_Azure_Logo.svg) ![GCP Logo](https://upload.wikimedia.org/wikipedia/commons/4/4e/Google_Cloud_Platform_Logo.svg)

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
