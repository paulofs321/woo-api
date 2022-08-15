import time

import aiohttp
import json
import asyncio
from fastapi import FastAPI
from hiveengine.nft import Nft
from hiveengine.tokenobject import Token
from nfts_config import config

hiveengine_version = "0.2.2"

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "FASTAPI Service is currently running."}


@app.get("/mints/{edition}")
async def mints(edition: int):
    i = 1
    tasks = []
    gf_tasks = []
    start = time.time()
    nft = Nft(symbol="Woo")

    url = "https://api.hive-engine.com/rpc/contracts"
    headers = {'User-Agent': 'hiveengine v%s' % hiveengine_version,
               'content-type': 'application/json'}
    payload = {"method": "find", "jsonrpc": "2.0",
               "params": {"contract": "nft", "table": f"{nft.symbol}instances",
                          "limit": 1000, "offset": 0, "indexes": []},
               "id": i}

    async with aiohttp.ClientSession() as session:
        if edition == 2:
            for j in range(2):
                payload["params"]["query"] = {"properties.edition": edition,
                                              "properties.type": j}

                tasks.append(asyncio.create_task(query_mints(url, json.dumps(payload), headers, session)))

                gf_payload = payload
                gf_payload["params"]["query"]["properties.foil"] = 1

                gf_tasks.append(asyncio.create_task(query_mints(url, json.dumps(gf_payload),
                                                                headers, session)))

                i += 1
        else:
            for k, v in config.items():
                payload["params"]["query"] = {"properties.edition": edition,
                                              "properties.type": v["type"]}

                tasks.append(asyncio.create_task(query_mints(url, json.dumps(payload),
                                                             headers, session)))

                gf_payload = payload
                gf_payload["params"]["query"]["properties.foil"] = 1

                gf_tasks.append(asyncio.create_task(query_mints(url, json.dumps(gf_payload),
                                                                headers, session)))

                i += 1

        nft_data = [data for data in await asyncio.gather(*tasks)]
        gf_data = [data for data in await asyncio.gather(*gf_tasks)]

    mints_data = {}

    if edition == 2:
        for i in range(2):
            name = "Raven" if i == 0 else "Raven Lore"

            mints_data[name] = {
                "Edition_2": nft_data[i],
                "Edition_2_GF": gf_data[i]
            }
    else:
        i = 0
        for k in config.keys():
            mints_data[k] = {
                f"Edition_{edition}": nft_data[i],
                f"Edition_{edition}_GF": gf_data[i]
            }

            i += 1

    print(f"total time processed: {time.time() - start}")
    return mints_data


@app.get("/holders")
async def holders():
    woo_token = Token("WOOALPHA")
    saturn_token = Token("WOOSATURN")
    raven_token = Token("WOORAVEN")

    woo_holders = woo_token.api.find_all("tokens", "balances", query={"symbol": woo_token.symbol})
    saturn_holders = saturn_token.api.find_all("tokens", "balances", query={"symbol": saturn_token.symbol})
    raven_holders = raven_token.api.find_all("tokens", "balances", query={"symbol": raven_token.symbol})

    holders_dict = {}

    for i in woo_holders:
        if int(i["balance"]) > 0:
            holders_dict[i["account"]] = {"woo_balance": i["balance"]}

    for i in saturn_holders:
        if int(i["balance"]) > 0:
            if i["account"] in holders_dict.keys():
                holders_dict[i["account"]]["saturn_balance"] = i["balance"]
            else:
                holders_dict[i["account"]] = {"saturn_balance": i["balance"]}

    for i in raven_holders:
        if int(i["balance"]) > 0:
            if i["account"] in holders_dict.keys():
                holders_dict[i["account"]]["raven_balance"] = i["balance"]
            else:
                holders_dict[i["account"]] = {"raven_balance": i["balance"]}

    return holders_dict


async def async_query(url, payload, headers=None, session=None):
    flag = False
    result = []

    while not flag:
        async with session.post(url=url, data=payload, headers=headers, timeout=60, ssl=False) as resp:
            # print(resp.status)
            if resp.status != 200:
                continue

            last_result = await resp.json()

            return last_result["result"]
        # await asyncio.sleep(1)

        # last_result = last_result["result"]

        # if last_result is not None:
        #     print(json.loads(payload)["params"]["query"]["properties.type"], len(last_result))
        #     result += last_result
        #     offset += limit
        #     new_payload = json.loads(payload)
        #     new_payload["params"]["offset"] = offset
        #     payload = json.dumps(new_payload)

    # print(json.loads(payload)["params"]["query"]["properties.type"], len(result))
    return result


async def query_mints(url, payload, headers, session):
    limit = 1000
    offset = 0
    last_result = []
    cnt = 0
    result = 0

    while last_result is not None and len(last_result) == limit or cnt == 0:
        cnt += 1
        last_result = await async_query(url, payload, headers, session)

        if last_result is not None:
            # print(json.loads(payload)["params"]["query"]["properties.type"], len(last_result))
            result += len(last_result)
            offset += limit
            new_payload = json.loads(payload)
            new_payload["params"]["offset"] = offset
            payload = json.dumps(new_payload)

    return result
