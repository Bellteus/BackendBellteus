from fastapi import APIRouter,HTTPException
from typing import List
from models.call_data_records import CallDataRecord
from service.CallService import ObtenerMetadata

router =APIRouter()


@router.get("/v1/call_data_records",response_model=List[CallDataRecord])
def get_call_data_records(limit : int=30):
    try:
        """Endopoint to retrieve call data records with a limit on the number of records."""
        records = ObtenerMetadata(limit)
        if not records:
            raise HTTPException(status_code=404, detail="No call data records found")
        return records
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in get_call_data_records: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving call data records")