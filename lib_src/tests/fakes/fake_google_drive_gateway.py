class FakeGoogleDriveGateway:
    def __init__(
            self,
            return_inbound=True,
            return_outbound=True,
            return_inbound_files=[],
            return_outbound_files=[]):
        self.count = 1
        self.return_inbound = return_inbound
        self.return_outbound = return_outbound
        self.search_folder_calls = []
        self.created_spreadsheets = []
        self.get_list_of_files_called_with = []
        self.return_inbound_files = return_inbound_files
        self.return_outbound_files = return_outbound_files

    def search_folder(self, folder_id, file_type):
        self.search_folder_calls.append([folder_id, file_type])

        if self.return_outbound & (folder_id == 'outbound_folder_id'):
            return folder_id
        if self.return_inbound & (folder_id == 'inbound_folder_id'):
            return folder_id
        return False

    def create_spreadsheet(self, folder_id, spreadsheet_name):
        self.created_spreadsheets.append({
            'folder_id': folder_id,
            'spreadsheet_name': spreadsheet_name
        })
        return spreadsheet_name + folder_id

    def get_list_of_files(self, folder_id):
        self.get_list_of_files_called_with.append(folder_id)

        if folder_id == 'inbound_folder_id':
            return self.return_inbound_files
        if folder_id == 'outbound_folder_id':
            return self.return_outbound_files
