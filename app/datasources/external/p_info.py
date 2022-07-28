from json import JSONDecodeError
from typing import Union, List

from fastapi.exceptions import HTTPException
from httpx import AsyncClient
import httpx

from app.datasources.generic import DataSource
from app.utils.cache import cached
from app.utils.misc import HTMLTextExtractor


class PInfo(DataSource):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = AsyncClient(verify=False)
        self.session.headers.update({'pinfo-product-api-key': api_key})
        self._txt_cleaner = HTMLTextExtractor()

    @cached
    async def search(self, query: str) -> dict:
        async with self.session as client:
            try:
                response = await client.get(f'{self.api_url}?gtin={query}')
                try:
                    json_body = response.json()
                    resp_code = int(json_body['response']['code'])
                    if resp_code not in (200, ):
                        return []
                        # raise HTTPException(status_code=resp_code)
                except JSONDecodeError:
                    return []
            except httpx.ReadTimeout:
                return 'Unable to get data.'
            
            articles = json_body['articles']
            result_set = [
                src for src in articles if (src.get('specs_raw') \
                    and len([item for item in articles if item and item.get('specs_raw')]) > 1) \
                        or src.get('description')
                    ]
            flat_result_set = []
            for shop in result_set:
                dict_temp = {}
                for shop_att in shop:
                    if shop_att=="specs_raw":
                        for specs in shop["specs_raw"]:
                            dict_temp.update({specs["spec"]: specs["value"]})
                    elif shop_att=="specs_raw" or shop_att=="cross":
                        pass
                    elif type(shop.get(shop_att))==list:
                        try:
                            dict_temp.update({shop_att:  ", ".join(shop.get(shop_att))})
                        except TypeError:
                            pass
                    else:
                        att_val = shop.get(shop_att)
                        if att_val:
                            dict_temp.update({shop_att: self._txt_cleaner.html_to_text(att_val)})
                flat_result_set.append(dict_temp)
            return flat_result_set
