import json

from dotenv import load_dotenv
from .gateways.here_to_help_api import HereToHelpGateway
from .gateways.pygsheets_gateway import PygsheetsGateway
from .gateways.google_drive_gateway import GoogleDriveGateway
from .usecase.create_help_requests import CreateHelpRequest
from .usecase.process_contact_tracing_calls import ProcessContactTracingCalls
from .usecase.process_cev_calls import ProcessCevCalls
from .usecase.add_cev_requests import AddCEVRequests
from .usecase.add_contact_tracing_requests import AddContactTracingRequests
from .usecase.add_spl_requests import AddSPLRequests
from .usecase.process_spl_calls import ProcessSPLCalls
from .usecase.process_multiple_sheets import ProcessMultipleSheets
from os import getenv
from os import path

load_dotenv()


def lambda_handler(event, context):

    print('- -start up - -')

    here_to_help_gateway = HereToHelpGateway()

    create_help_request = CreateHelpRequest(gateway=here_to_help_gateway)

    key_file_location = path.relpath('lib/key_file.json')

    google_drive_gateway = GoogleDriveGateway(key_file_location)

    pygsheets_gateway = PygsheetsGateway(
        key_file_location
    )

    add_contact_tracing_requests = AddContactTracingRequests(
        create_help_request)

    find_and_process_contact_tracing = ProcessContactTracingCalls(
        google_drive_gateway, pygsheets_gateway, add_contact_tracing_requests)

    ct_inbound_folder_id = getenv("CT_INBOUND_FOLDER_ID")
    ct_outbound_folder_id = getenv("CT_OUTBOUND_FOLDER_ID")

    response = find_and_process_contact_tracing.execute(
        ct_inbound_folder_id,
        ct_outbound_folder_id
    )

    return {
        "body": json.dumps([response])
    }

def spl_lambda_handler(event, context):
    print('- -spl_lambda_handler - -')

    here_to_help_gateway = HereToHelpGateway()

    create_help_request = CreateHelpRequest(gateway=here_to_help_gateway)

    key_file_location = path.relpath('lib/key_file.json')

    google_drive_gateway = GoogleDriveGateway(key_file_location)

    pygsheets_gateway = PygsheetsGateway(
        key_file_location
    )

    add_spl_requests = AddSPLRequests(
        create_help_request, here_to_help_gateway)

    process_spl_calls = ProcessSPLCalls(add_spl_requests)

    spl_inbound_folder_id = getenv("SPL_INBOUND_FOLDER_ID")
    spl_outbound_folder_id = getenv("SPL_OUTBOUND_FOLDER_ID")

    sheet_process = ProcessMultipleSheets(
        google_drive_gateway, pygsheets_gateway)

    spl_response = sheet_process.execute(
        spl_inbound_folder_id,
        spl_outbound_folder_id,
        process_spl_calls
    )

    return {
        "body": json.dumps([spl_response])
    }

def nsss_lambda_handler(event, context):
    print('- -nsss_lambda_handler - -')

    here_to_help_gateway = HereToHelpGateway()

    create_help_request = CreateHelpRequest(gateway=here_to_help_gateway)

    key_file_location = path.relpath('lib/key_file.json')

    google_drive_gateway = GoogleDriveGateway(key_file_location)

    pygsheets_gateway = PygsheetsGateway(
        key_file_location
    )

    add_cev_requests = AddCEVRequests(
        create_help_request, here_to_help_gateway)

    process_new_sheet_cev_calls = ProcessCevCalls(add_cev_requests)

    cev_inbound_folder_id = getenv("CEV_INBOUND_FOLDER_ID")
    cev_outbound_folder_id = getenv("CEV_OUTBOUND_FOLDER_ID")

    sheet_process = ProcessMultipleSheets(
        google_drive_gateway, pygsheets_gateway)

    cev_response = sheet_process.execute(
        cev_inbound_folder_id,
        cev_outbound_folder_id,
        process_new_sheet_cev_calls
    )

    return {
        "body": json.dumps([cev_response])
    }
