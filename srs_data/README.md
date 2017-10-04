# srs-data tools
Tools to automate various SRS-data workflows and client-asks.

## `ProcessTagsThatClientReturns`
Before instantiating this class, we must *manually* perform the following:

### 1. Correct autotags
The client will return the `.xlsx` tags file we had sent. This file will contain several tabs.

- One of these tabs will be named `AutoTags`. These will contains updates/corrections to the auto-tag we had previously applied. This tab will typically contain the columns `TEXT`, `tag`, `New Tag`, `Notes`.
- In this tab, review the changes made in the `New Tag` column. Once comfortable with these changes, merge the results into the `tag` column.

### 2. Append the results of the previous step onto the columns in the `Final` tab

### 3. Save the `.xlsx` file
- Ensure that the file contains 3 columns: `text`, `tag`, and `notes`. Rename the existing columns if this is not the case.
- Save the `Final` tab as a CSV UTF-8 (comma-delimited) file.
- Name the file `<client_name>-tagsource<start_date>.csv`. This is the `input_file` that `ProcessTagsThatClientReturns` is expecting to exist.
    - `<start_date>`, for example, might be: `20170907`.
