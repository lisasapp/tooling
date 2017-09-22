
class ProcessTagsThatClientReturns:

    def __init__(self, config):
        self._config = config['tagging']
        self._client = self._config['client']
        self._start_date = self._config['start_date']
        self._end_date = self._config['end_date']
        self._output_directory = os.path.join(ASAPP_ROOT, 'data', self._client, self._start_date)

    def _print_instructions_to_merge_client_tags(self):
        print(
f"""
The client will return the {self._client}{self._start_date}.xslx. file we had
sent. This file will contain several tabs.

> One of these tabs will be named "AutoTags". These will contains
updates/corrections to the auto-tag we had previously applied. This tab will
typically contain the columns "TEXT", "tag", "New Tag", and "Notes".
> In this tab, review the changes made in the "New Tag" column. Once
comfortable with these changes, merge the results into the "tag".
"""
        )
