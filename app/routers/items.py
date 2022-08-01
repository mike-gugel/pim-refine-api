from fastapi import (APIRouter, Depends, HTTPException, status)
from typing import List, Union

from app.core.config import settings
from app.models.user import UserRead as UserDB
from app.utils.dependencies import get_current_user, get_eans
from app.datasources.internal.bdx_am import BdxAm
from app.datasources.external.crawlab import Crawlab
from app.datasources.external.icecat import Icecat
from app.datasources.external.p_info import PInfo
from app.datasources.external.paw import Paw
from app.datasources.external.eprel import EPREL


router = APIRouter()


@router.get('/items/search')
async def search(
    user: UserDB = Depends(get_current_user()),
    query: str = Depends(get_eans),
    response_model=None,
    status_code=200
    ):
    pim_client = BdxAm()
    response = list()
    for ean in query:
        p_info_results = await PInfo(
            api_url = settings.P_INFO_API_URL,
            api_key = settings.P_INFO_API_KEY
            ).search(query=ean)
        pim_results = await pim_client.search(query=ean)
        icecat_results = await Icecat().search(query=ean)
        eprel_id = icecat_results and icecat_results.get('EprelID')
        eprel_results = eprel_id and await EPREL().search(query=eprel_id) or None
        async with Crawlab(
            settings.CRAWLAB_API_URL,
            settings.CRAWLAB_API_KEY
            ) as crawlab_client:
            crawlab_results = await crawlab_client.search(query=ean)
        paw_results = await Paw().search(query=ean)
        response.append({
            'EAN': ean,
            'results': {
                **{'internal_pim': pim_results},
                **{'p_info': p_info_results},
                **{'icecat': icecat_results},
                **{'crawlab': crawlab_results},
                **{'paw': paw_results},
                **{'eprel': eprel_results}
                }
            })
    
    return response


@router.get('/icecat/search')
async def search(
    query: str,
    user: UserDB = Depends(get_current_user()),
    response_model=None,
    status_code=200
    ):
   
    response = list()

    for ean in (item.strip() for item in query.split(',')):
        icecat_results = await Icecat().search_full_icecat(
            ean,
            username=settings.ICECAT_USER,
            icecat_api_key=settings.ICECAT_API_KEY,
            requested_by=user.id
            )
        response.append(icecat_results)
    return response


@router.get('/eprel/search')
async def search(
    query: str,
    user: UserDB = Depends(get_current_user()),
    response_model=None,
    status_code=200
    ):
   
    response = list()

    for eprel_id in (item.strip() for item in query.split(',')):
        eprel_results = await EPREL().search(eprel_id)
        response.append(eprel_results)
    return response
