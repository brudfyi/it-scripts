# snipe-importer
## Import computers from JAMF and Google to Snipe-IT. Import users from Okta.
```
Usage: snipe-importer [-h] [-v] [--dryrun] [-d] [--do_not_verify_ssl] [-r] [-m | -c]

Optional arguments:
-h, --help            show this help message and exit
-v, --verbose         Sets the logging level to INFO and gives you a better
                      idea of what the script is doing.
--dryrun              This checks your config and tries to contact both the
                      JAMFPro and Snipe-it instances, but exits before
                      updating or syncing any assets.
-d, --debug           Sets logging to include additional DEBUG messages.
--do_not_verify_ssl   Skips SSL verification for all requests. Helpful when
                      you use self-signed certificate.
-r, --ratelimited     Puts a half second delay between Snipe IT API calls to
                      adhere to the standard 120/minute rate limit
-f, --force           Updates the Snipe asset with information from Jamf
                      every time, despite what the timestamps indicate.
-m, --mobiles         Runs against the Jamf mobiles endpoint only.
-c, --computers       Runs against the Jamf computers endpoint only.
```

## Acknowledgement

This script is heavily modified from the the original jamf2snipe script found at [https://github.com/ParadoxGuitarist/jamf2snipe](https://github.com/ParadoxGuitarist/jamf2snipe).

## Overview:
This tool will import assets from a JAMF Pro instance to a Snipe-IT instance. The tool searches for assets based on the serial number, not the existing asset tag. If assets exist in JAMF and are not in Snipe-IT, the tool will create an asset and try to match it with an existing Snipe model. This match is based on the Mac's model identifier (ex. MacBookAir7,1) being entered as the model number in Snipe, rather than the model name. If a matching model isn't found, it will create one.


## Requirements:

- Python3 is installed on your system with the requests, json, time, and configparser python libs installed.
- Network access to both your JAMF and Snipe-IT environments.
- A JAMF username and password that has read permissions for computer assets.
- Snipe API key for a user that has edit/create permissions for assets and models. Snipe-IT documentation instructions for creating API keys: [https://snipe-it.readme.io/reference#generating-api-tokens](https://snipe-it.readme.io/reference#generating-api-tokens)

## Snipe-IT Configuration:

### Categories

- `Software` of type `License`
- `Laptop` of type `Asset`
- `Phone` of type `Asset`
- `Peripheral` of type `Accessory`
- `Monitor` of type `Accessory`

Category ID's will be used in `settings.conf`

### Custom Fields

- `Year` of format `regex:/^\d{4}$/` and element `text`
- `CPU` of format `ANY` and element `text`
- `RAM` of format `ANY` and element `text`
- `Storage` of format `ANY` and element `text`
- `IMEI Number` of format `ANY` and element `text`

### Fieldsets (contain custom fields)

- `Laptop`
- `Phone`

Fieldset ID's will be used in `settings.conf`

## Configuration - settings.conf:

All of the settings that are listed in the settings.conf are required except for the api-mapping section. It's recommended that you install these files to /opt/jamf2snipe/ and run them from there. You will need valid subsets from [JAMF's API](https://developer.jamf.com/apis/classic-api/index) to associate fields into Snipe.

### Required

Note: do not add `""` or `''` around any values.

**[jamf]**

- `url`: https://*your_jamf_instance*.com:*port*
- `username`: Jamf API user username
- `password`: Jamf API user password

**[okta]**

- `url`: https://*example*.okta.com
- `apiKey`: Okta API key
- `filter`: Filter applied to the 'Department' (only users that contain this filter will be imported)

**[snipe-it]**

- `url`: http://*your_snipe_instance*.com
- `apikey`: API key generated via [these steps](https://snipe-it.readme.io/reference#generating-api-tokens)
- `defaultStatus`: The status database field id to assign to any assets created in Snipe-IT from JAMF.
- `computer_model_category_id`: The category id for the computer model
- `mobile_model_category_id`: The category id for the mobile model
- `peripheral_category_id`: The category id for peripherals
- `software_category_id`: The category id for licenses
- `computer_custom_fieldset_id`: The fieldset id for custom computer fields
- `mobile_custom_fieldset_id`: The fieldset id for custome mobile fields

### API Mapping

To get the database fields for Snipe-IT Custom Fields, go to Custom Fields, scroll down past Fieldsets to Custom Fields, click the column selection and button and select the unchecked 'DB Field' checkbox. Copy and paste the DB Field name for the Snipe under api-mapping in settings.conf.

To get the database fields for Jamf, refer to Jamf's ["Classic" API documentation](https://developer.jamf.com/apis/classic-api/index).


Some example API mappings can be found below:

- Computer Name:		`name = general name`
- MAC Address:		`_snipeit_mac_address_1 = general mac_address`
- IPv4 Address:		`_snipeit_<your_IPv4_custom_field_id> = general ip_address`
- Purchase Cost:		`purchase_cost = purchasing purchase_price`
- Purchase Date:		`purchase_date = purchasing po_date`
- OS Version:			`_snipeit_<your_OS_version_custom_field_id> = hardware os_version`
- Extension Attribute:    `_snipe_it_<your_custom_field_id> = extension_attributes <attribute id from jamf>`

## Testing

It is *always* a good idea to create a test environment to ensure everything works as expected before running anything in production.
