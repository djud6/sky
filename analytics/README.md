# Analytics Routes

## /ActiveVehicles

Accepts query parameter Location_IATA to filter by asset location

Returns JSON array of form [{Status,count}]

## /Locations

Returns JSON array of form [{Location_IATA, count}]

## /BusinessUnits

Returns JSON array of form [{Department, count}]

## /Accidents

URL Parameters: start (date YYYY-MM-DD), end (date YYYY-MM-DD), scale (one of day, week or month for resolution of data; defaults to month)

Returns JSON array of form [{month/week/date_created, count}]
