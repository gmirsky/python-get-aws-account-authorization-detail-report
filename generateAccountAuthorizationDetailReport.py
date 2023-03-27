import argparse as argparse
import boto3 as boto3
import configparser as configparser
import datetime as datetime
import emoji as emoji
import json as json
import logging as logging
import openpyxl as openpyxl
import pandas as pd
import platform as platform
import requests as requests
import subprocess as subprocess
import sys as sys
import os as os
from botocore.config import Config
from botocore.exceptions import ClientError
from shutil import get_terminal_size as get_terminal_size
from shutil import which as which

logger = logging.getLogger(__name__)


def get_account_authorization_details(
    profile,
    output,
    region,
    include_non_default_policy_versions=False,
    include_unattached=False,
    open_in_excel=False
):
    """
    Run aws iam get-account-authorization-details and store locally.
    :param profile: Name of the profile in the AWS Credentials file
    :param output: The path of a directory to store the results.
    :param include_non_default_policy_versions: When downloading AWS managed policy documents,
      also include the non-default policy versions. Note that this will dramatically increase 
      the size of the downloaded file.
    :return:
    """
    print()
    print(emoji.emojize(
        ":heavy_exclamation_mark:  Starting report generation.",
        language='alias'))

    config = Config(connect_timeout=5,
                    retries={"max_attempts": 10})

    session = boto3.Session(profile_name=profile,
                            region_name=region)

    iam_client = session.client("iam",
                                config=config,
                                use_ssl=True,
                                verify=True
                                )

    results = {
        "UserDetailList": [],
        "GroupDetailList": [],
        "RoleDetailList": [],
        "Policies": [],
    }

    # Get the account authorization details report
    paginator = iam_client.get_paginator("get_account_authorization_details")

    # Iterate over the pages of results for users
    for page in paginator.paginate(Filter=["User"]):
        # Always add inline user policies
        results["UserDetailList"].extend(page["UserDetailList"])
    # Iterate over the pages of results for groups
    for page in paginator.paginate(Filter=["Group"]):
        results["GroupDetailList"].extend(page["GroupDetailList"])
    # Iterate over the pages of results for roles
    for page in paginator.paginate(Filter=["Role"]):
        results["RoleDetailList"].extend(page["RoleDetailList"])
        for policy in page["Policies"]:
            # Ignore Service Linked Roles which cannot be modified and will create messy results.
            results["RoleDetailList"].append(policy)
    # Iterate over the pages of results for local managed policies
    for page in paginator.paginate(Filter=["LocalManagedPolicy"]):
        # Add customer-managed policies IF they are attached to IAM principals
        for policy in page["Policies"]:
            if policy["AttachmentCount"] > 0 or include_unattached:
                results["Policies"].append(policy)
    for page in paginator.paginate(Filter=["AWSManagedPolicy"]):
        for policy in page["Policies"]:
            # Add customer-managed policies if they are attached to IAM principals or if `--include-unattached` is specified
            if policy["AttachmentCount"] > 0 or include_unattached:
                if include_non_default_policy_versions:
                    results["Policies"].append(policy)
                else:
                    policy_version_list = []
                    for policy_version in policy.get("PolicyVersionList"):
                        if policy_version.get("VersionId") == policy.get(
                            "DefaultVersionId"
                        ):
                            policy_version_list.append(policy_version)
                            break
                    # Create a new entry with only the default policy version
                    entry = {
                        "PolicyName": policy.get("PolicyName"),
                        "PolicyId": policy.get("PolicyId"),
                        "Arn": policy.get("Arn"),
                        "Path": policy.get("Path"),
                        "DefaultVersionId": policy.get("DefaultVersionId"),
                        "AttachmentCount": policy.get("AttachmentCount"),
                        "PermissionsBoundaryUsageCount": policy.get(
                            "PermissionsBoundaryUsageCount"
                        ),
                        "IsAttachable": policy.get("IsAttachable"),
                        "CreateDate": policy.get("CreateDate"),
                        "UpdateDate": policy.get("UpdateDate"),
                        "PolicyVersionList": policy_version_list,
                    }
                    results["Policies"].append(entry)

    # Let the user know that the report is complete.
    print(emoji.emojize(":white_check_mark:  JSON Report generation complete.",
                        language='alias'))

    # Write the results to a file.
    with open(output, 'w') as f:
        json.dump(results, f, indent=4, default=str)
        print(emoji.emojize(":white_check_mark:  Report written to {}.".format(output),
                            language='alias'))

    # use pandas to read the json file and convert it to an excel file
    print(emoji.emojize(
        ":white_check_mark:  Converting JSON to Excel.", language='alias'))
    # write the json file to an excel file
    with open(output) as f:
        data = json.load(f)
        df = pd.json_normalize(data, record_path=['UserDetailList'],
                               errors='ignore'
                               )
        df.to_excel(output.replace('.json', '.xlsx'),
                    sheet_name='Users', index=False)
        print(emoji.emojize(":white_check_mark:  Excel report written to {}.".format(output.replace('.json', '.xlsx')),
                            language='alias'))

    # open the excel file
    if open_in_excel:
        # determine if platform is Windows, Linux or Mac
        if platform.system() == 'Windows':
            # check if Excel is installed
            # if which('excel.exe') is None:
            #     print(emoji.emojize(
            #         'Excel is not installed :cross_mark:',
            #         language='alias'))
            #     raise Exception("Excel is not installed")
            # else:
            print(emoji.emojize(
                ":open_file_folder: Opening {} in Excel in Windows").format(output.replace('.json', '.xlsx')))
            # nosec B605: start is used to open a file with excel.exe
            os.system('start excel.exe {}'.format(
                output.replace('.json', '.xlsx')))
        elif platform.system() == 'Linux':
            # check if LibreOffice is installed
            # if which('libreoffice') is None:
            #     print(emoji.emojize(
            #         'LibreOffice is not installed :cross_mark:',
            #         language='alias'))
            #     raise Exception("LibreOffice is not installed")
            # else:
            print(emoji.emojize(
                ":open_file_folder: Opening {} in LibreOffice in Linux").format(output.replace('.json', '.xlsx')))
            # nosec B605: libreoffice is used to open a file with LibreOffice
            os.system('libreoffice {}'.format(
                output.replace('.json', '.xlsx')))
        elif platform.system() == 'Darwin':
            # Check if Excel is installed in Mac
            # if which('Microsoft Excel.app') is None:
            #     print(emoji.emojize(
            #         'Excel is not installed :cross_mark:',
            #         language='alias'))
            #     raise Exception("Excel is not installed")
            # else:
            print(emoji.emojize(
                ":open_file_folder: Opening {} in Excel in Mac").format(output.replace('.json', '.xlsx')))
            # nosec B605: open is used to open a file with Microsoft Excel
            os.system(
                'open -a "Microsoft Excel" {}'.format(output.replace('.json', '.xlsx')))
        return 0


def main():
    """
    Take in the arguments and generate a presigned URL.
    """

    # Configure logging.
    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)s: %(message)s')

    # Add arguments to the parser.
    parser = argparse.ArgumentParser(exit_on_error=False)

    # The AWS region argument
    parser.add_argument('-r', '--region',
                        help='The AWS region you wish to execute the script in.'
                             'Defaults to us-east-1.',
                        default='us-east-1',
                        choices=(
                            'af-south-1',
                            'ap-east-1',
                            'ap-northeast-1',
                            'ap-northeast-2',
                            'ap-south-1',
                            'ap-south-2',
                            'ap-southeast-1',
                            'ap-southeast-2',
                            'ap-southeast-3',
                            'ap-southeast-4',
                            'ca-central-1',
                            'cn-north-1',
                            'cn-northwest-1',
                            'eu-central-1',
                            'eu-central-2',
                            'eu-north-1'
                            'eu-south-1',
                            'eu-west-1',
                            'eu-west-2',
                            'eu-west-3',
                            'me-south-1',
                            'me-central-1',
                            'sa-east-1',
                            'us-east-1',
                            'us-east-2',
                            'us-gov-east-1',
                            'us-gov-west-1',
                            'us-west-1',
                            'us-west-2'
                        )
                        )
    # The AWS CLI profile argument
    parser.add_argument('-p', '--profile',
                        help='AWS profile'
                             'Default: default'
                             'Example: --profile default',
                        default='default')

    # The include-non-default-policy-versions argument
    parser.add_argument('-i', '--include-non-default-policy-versions',
                        help='When downloading AWS managed policy documents, also include the non-default policy versions.'
                             'Note that this will dramatically increase the size of the downloaded file.'
                             'This can be useful when you want to see the full history of a policy.'
                             'This option is ignored when downloading customer-managed policies.'
                             'Default: False'
                             'Example: --include-non-default-policy-versions',
                        action='store_true')

    # The include-unattached argument
    parser.add_argument('-u', '--include-unattached',
                        help='When downloading AWS managed policy documents, also include the unattached policies.'
                             'Default: False'
                             'Example: --include-unattached',
                        action='store_true')

    # The file output argument
    parser.add_argument('-o', '--output',
                        help='The output directory to save the JSON files to.'
                        'Default: ./accountAuthorizationDetailsReport.json'
                        'Example: --output ./accountAuthorizationDetailsReport.json',
                        default='./accountAuthorizationDetailsReport.json')

    # The logging level argument
    parser.add_argument('-l', '--log-level',
                        help='The logging level to use.'
                             'Default: ERROR'
                             'Example: --log-level INFO',
                        default='ERROR',
                        choices=('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'))

    # The open in excel argument
    parser.add_argument('-x', '--open-in-excel',
                        help='Open the file in Excel.',
                        action='store_true')

    args = parser.parse_args()

    """ 
    The below outputs are for making the end user support staff lives easier;
    especially when dealing with end user PEBKAC & PICNIC issues.
    """

    # Set the logging level.
    logging.getLogger().setLevel(args.log_level)

    print('-' * get_terminal_size()[0])
    # Display the computer platform that this script is running on.
    print(emoji.emojize(":computer:  Platform: {}",
          language='alias').format(platform.platform()))
    # Display the version of Python that this script is running with
    print(emoji.emojize(":snake:  Python version: {}",
          language='alias').format(sys.version))

    # Check that the Python version is 3 or higher.
    if sys.version_info[0] < 3:
        print(emoji.emojize(
            'You must use Python 3 or higher :cross_mark:',
            language='alias'))
        raise Exception("You must use Python 3 or higher")
    else:
        print(emoji.emojize(
            'Python version is OK :check_mark_button:',
            language='alias'))

    # Check that the AWS CLI is installed.
    if which('aws') is None:
        print(emoji.emojize(
            'AWS CLI is not installed :cross_mark:',
            language='alias'))
        raise Exception("AWS CLI is not installed")
    else:
        print(emoji.emojize(
            'AWS CLI is installed :check_mark_button:',
            language='alias'))
        # Get the version of the AWS CLI.
        aws_cli_version = subprocess.check_output(
            ['aws', '--version']).decode('utf-8').split(' ')[0]
        # Check that the AWS CLI version is less than verson 2.
        if int(aws_cli_version.split('/')[1].split('.')[0]) < 2:
            # Print an error message and raise an exception.
            print(emoji.emojize(
                'You must use AWS CLI version 2 or higher :heavy_exclamation_mark:',
                language='alias'))
            raise Exception("You must use AWS CLI version 2 or higher")
        else:
            # Display the version of the AWS CLI.
            print(emoji.emojize(":ok:  AWS CLI version: {}", language='alias').format(
                aws_cli_version.split('/')[1]))

    # Display the version of the Boto3 library.
    print(emoji.emojize(":package:  Boto3 version: {}",
          language='alias').format(boto3.__version__))
    # Display the version of the Requests library.
    print(emoji.emojize(":package:  Requests version: {}",
          language='alias').format(requests.__version__))
    # Display the version of the Emoji library.
    print(emoji.emojize(":package:  Emoji version: {}",
          language='alias').format(emoji.__version__))
    # Display the version of the Argparse library.
    print(emoji.emojize(":package:  Argparse version: {}",
          language='alias').format(argparse.__version__))
    # Display the version of the Logging library.
    print(emoji.emojize(":package:  Logging version: {}",
          language='alias').format(logging.__version__))
    # Display the version of the Platform library.
    print(emoji.emojize(":package:  Platform version: {}",
          language='alias').format(platform.__version__))

    # Display the values of the command-line arguments.
    print(emoji.emojize(":arrow_right:  AWS Region: {}",
          language='alias').format(args.region))
    # Display the AWS profile.
    print(emoji.emojize(":arrow_right:  AWS Profile: {}",
          language='alias').format(args.profile))
    # Display the include-non-default-policy-versions argument.
    print(emoji.emojize(":arrow_right:  Include non-default policy versions: {}", language='alias').format(
        args.include_non_default_policy_versions))
    # Display the include-unattached argument.
    print(emoji.emojize(":arrow_right:  Include unattached policies: {}", language='alias').format(
        args.include_unattached))
    # check to see if the output value ends with .json
    if args.output.endswith('.json'):
        # Display the output directory.
        print(emoji.emojize(":arrow_right:  Output directory and file: {}",
              language='alias').format(args.output))
    else:
        print(emoji.emojize(":bangbang:  Output file does not end with .json, replacing extension with .json at the end of the file name",
                            language='alias'))
        #  remove file extension if it exists
        args.output = args.output.split('.')[0]
        #  add .json file extension
        args.output = args.output + '.json'
        print(emoji.emojize(":arrow_right:  Output directory and file: {}",
              language='alias').format(args.output))
    # Display the logging level.
    print(emoji.emojize(":arrow_right:  Logging level: {}",
          language='alias').format(args.log_level))

    # Get account authorization details.
    account_authorization_details = get_account_authorization_details(
        region=args.region,
        profile=args.profile,
        include_non_default_policy_versions=args.include_non_default_policy_versions,
        include_unattached=args.include_unattached,
        output=args.output,
        open_in_excel=args.open_in_excel)

    # Let the user know that the script is done.
    print(emoji.emojize(":checkered_flag:  Done!",))
    print('-' * get_terminal_size()[0])


# The main function.
if __name__ == "__main__":
    main()
