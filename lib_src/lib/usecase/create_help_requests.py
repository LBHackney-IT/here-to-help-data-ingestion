from ..helpers import resident_is_identifiable


class CreateHelpRequest:

    def __init__(self, gateway):
        self.gateway = gateway

    def execute(self, help_requests):
        result = {"created_help_request_ids": [], "unsuccessful_help_requests": []}
        exceptions = []
        for help_request in help_requests:
            try:
                if not resident_is_identifiable(help_request):
                    result["unsuccessful_help_requests"].append(help_request)
                    print("INGEST_WARNING - Help request was not uniquely identifiable and was skipped.")
                    continue
                response = self.gateway.create_help_request(help_request=help_request)
                if "Error" in response:
                    print("Gateway error was found within [CreateHelpRequestUseCase] use case.")
                    help_request['Error'] = response["Error"]
                    result["unsuccessful_help_requests"].append(help_request)
                    # I question whether all this information ends up doing anything at all.
                    print("Gateway error was appended to UC result.")
                else:
                    result["created_help_request_ids"].append(response['Id'])
            except Exception as err:
                help_request['Error'] = str(err)
                exceptions.append(help_request)
                print("[CreateHelpRequestUseCase] Failed to create help request", str(err), help_request)
            
            if exceptions:
                result["exceptions"] = exceptions
                print("Exceptions list was appended to [CreateHelpRequestUseCase] result.")
        return result
