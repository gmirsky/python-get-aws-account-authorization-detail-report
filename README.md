# Generate the AWS account authorization details report

Python script to get the AWS account authorization details report.

## Requirements

You need AWS Systems Administrator or AWS IAM Administrator level access to run this report.

## Parameters

`-r` or `--region`: The AWS region you wish to execute this script in. The acceptable regions are:

- af-south-1
- ap-east-1
- ap-northeast-1
- ap-northeast-2
- ap-south-1
- ap-south-2
- ap-southeast-1
- ap-southeast-2
- ap-southeast-3
- ap-southeast-4
- ca-central-1
- cn-north-1
- cn-northwest-1
- eu-central-1
- eu-central-2
- eu-north-1
- eu-south-1
- eu-west-1
- eu-west-2
- eu-west-3
- me-south-1
- me-central-1
- sa-east-1
- us-east-1
- us-east-2
- us-gov-east-1
- us-gov-west-1
- us-west-1
- us-west-2

`-p` or `--profile`: The AWS profile to pull the AWS credentials from.

`-i` or `--include-non-default-policy-versions`: When downloading AWS managed policy documents, also include the non-default policy versions. Note that this will dramatically increase the size of the downloaded file. 'This can be useful when you want to see the full history of a policy. 'This option is ignored when downloading customer-managed policies.

`-u` or `--include-unattached`: When downloading AWS managed policy documents, also include the unattached policies.

`-o` or `--output`: The output directory and file to save the JSON files to. Defaults to `./accountAuthorizationDetailsReport.json`

`-l` or `--log-level`: The logging level to use. Defaults to `ERROR`. Acceptable choices are: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`

`-x` or `--open-in-excel`: When included this will trigger the script to open the report in Excel (Windows, Mac) or LibreOffice (Linux)

`-f` or `--flatten`: Flatten the report in Excel/LibreOffice. Note: This will exponentially expand the output.

## Usage

To run the report, you need to have the AWS CLI installed and configured. You can find more information on how to do that here: <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html>

Once you have the AWS CLI installed and configured, you can run the report by running the following command:

```shell
python3 ./generateAccountAuthorizationDetailReport.py --region='us-east-1' --profile='default' --output ./accountAuthorizationDetailsReport1.json --open-in-excel 
```

You should expect the following output:

```sh


-------------------------------------------------------------------------------------------------------------

💻  Platform: macOS-13.2.1-arm64-arm-64bit
🐍  Python version: 3.11.2 (main, Feb 16 2023, 02:55:59) [Clang 14.0.0 (clang-1400.0.29.202)]
Python version is OK ✅
AWS CLI is installed ✅
🆗  AWS CLI version: 2.11.6
📦  Boto3 version: 1.26.93
📦  Requests version: 2.28.2
📦  Emoji version: 2.2.0
📦  Argparse version: 1.1
📦  Logging version: 0.5.1.2
📦  Platform version: 1.0.8
➡️  AWS Region: us-east-1
➡️  AWS Profile: default
➡️  Include non-default policy versions: False
➡️  Include unattached policies: False
➡️  Output directory and file: ./accountAuthorizationDetailsReport.json
➡️  Logging level: ERROR

❗  Starting report generation.
✅  JSON Report generation complete.
✅  Report written to ./accountAuthorizationDetailsReport.json.
✅  Converting JSON to Excel.
✅  Excel report written to ./accountAuthorizationDetailsReport.xlsx.
📂 Opening ./accountAuthorizationDetailsReport6.xlsx in Excel in Mac

🏁  Done!
-------------------------------------------------------------------------------------------------------------


```
