import datetime
from ..helpers import parse_date_of_birth, concatenate_address


class AddSelfIsolationRequests:
    def __init__(self, create_help_request, here_to_help_api):
        self.create_help_request = create_help_request
        self.here_to_help_api = here_to_help_api

    def execute(self, data_frame):
        data_frame.insert(0, 'help_request_id', '')
        data_frame.insert(0, 'resident_id', '')
        data_frame.insert(0, 'cev_case_added_id', '')

        for index, row in data_frame.iterrows():
            if not self.is_self_isolation_request(row):
                continue

            dob_day, dob_month, dob_year = parse_date_of_birth(
                row['Date of Birth'])

            address_line_1 = concatenate_address(row['Address Line 1'], row['House Number'])

            metadata = {
                "LA_support_required": row["LA Support Required"],
                "LA_support_letter_received": row["LA Support Letter Received"]
            }

            help_request = [
                {
                    "Metadata": metadata,
                    "Uprn": row.UPRN,
                    "Postcode": row.Postcode.upper(),
                    "AddressFirstLine": address_line_1,
                    "AddressSecondLine": row['Address Line 2'],
                    "AddressThirdLine": row.Town,
                    "FirstName": row.Forename.capitalize() if row.Forename else '',
                    "LastName": row.Surname.capitalize() if row.Surname else '',
                    "DobDay": f'{dob_day}',
                    "DobMonth": f'{dob_month}',
                    "DobYear": f'{dob_year}',
                    "ContactTelephoneNumber": row.Phone2,
                    "ContactMobileNumber": row.Phone,
                    "EmailAddress": row.Email,
                    "CallbackRequired": True,
                    "HelpNeeded": "Welfare Call",
                    "NhsNumber": row['NHS Number'],
                    "NhsCtasId": row.ID
                }]

            response = self.create_help_request.execute(
                help_requests=help_request)

            if response['created_help_request_ids']:
                help_request_id = response['created_help_request_ids'][0]

                request = self.here_to_help_api.get_help_request(
                    help_request_id)

                resident_id = request["ResidentId"]

                data_frame.at[index, 'help_request_id'] = help_request_id
                data_frame.at[index, 'resident_id'] = resident_id

                print(
                    f'Added CEV {index + 1} of {len(data_frame)}: resident_id: {resident_id} help_request_id: {help_request_id}')

                # update case notes here
                if row["LA Support Letter Received"] == '1':
                    resident_help_requests = self.here_to_help_api.get_resident_help_requests(
                        resident_id)
                    if not any(res_help_request['HelpNeeded'] == 'Shielding' for res_help_request in resident_help_requests):
                        cev_help_request = {
                                    "CallbackRequired": False,
                                    "HelpNeeded": "Shielding"}
                        cev_case_id = self.here_to_help_api.create_resident_help_request(
                            resident_id, cev_help_request)['Id']

                        data_frame.at[index, 'cev_case_added_id'] = cev_case_id

                        if cev_case_id:
                            self.here_to_help_api.create_case_note(
                                resident_id, cev_case_id, {
                                    "author": "Self Isolation data ingestion pipeline",
                                    "note": "--- self-reported CEV resident identified through self-isolation support "
                                            "process ---"})

        return data_frame

    def is_self_isolation_request(self, row):
        return row["LA Support Required"] == '1' or row["LA Support Letter Received"] == "1"
