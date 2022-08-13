from fastapi import FastAPI
from hiveengine.nft import Nft
from hiveengine.tokenobject import Token
from nfts_config import config

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "FASTAPI Service is currently running."}


@app.get("/mints")
async def mints():
    data = []
    nft = Nft(symbol="Woo")

    mints = {}
    for k, v in config.items():
        nfts_0 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                  query={
                                      "properties.edition": 0,
                                      "properties.type": v["type"]
                                  })

        nfts_1 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                  query={
                                      "properties.edition": 1,
                                      "properties.type": v["type"]
                                  })

        foil_nfts_0 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                       query={
                                           "properties.edition": 0,
                                           "properties.type": v["type"],
                                           "properties.foil": 1
                                       })

        foil_nfts_1 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                       query={
                                           "properties.edition": 1,
                                           "properties.type": v["type"],
                                           "properties.foil": 1
                                       })

        # woo_nft = {
        #     k: {
        #         "Edition_0": len(nfts_0),
        #         "Edition_0_GF": len(foil_nfts_0),
        #         "Edition_1": len(nfts_1),
        #         "Edition_1_GF": len(foil_nfts_1)
        #     }
        # }
        mints[k] = {
            "Edition_0": len(nfts_0),
            "Edition_0_GF": len(foil_nfts_0),
            "Edition_1": len(nfts_1),
            "Edition_1_GF": len(foil_nfts_1)
        }

        #data.append(woo_nft)

    for i in range(2):
        nfts_2 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                  query={
                                      "properties.edition": 2,
                                      "properties.type": i
                                  })

        foil_nfts_2 = nft.api.find_all("nft", "%sinstances" % nft.symbol,
                                       query={
                                           "properties.edition": 2,
                                           "properties.type": i,
                                           "properties.foil": 1
                                       })

        if i == 0:
            # woo_nft = {
            #     "Raven": {
            #         "Edition_2": len(nfts_2),
            #         "Edition_2_GF": len(foil_nfts_2)
            #     }
            # }
            mints["Raven"] = {
                "Edition_2": len(nfts_2),
                "Edition_2_GF": len(foil_nfts_2)
            }
        else:
            # woo_nft = {
            #     "Raven lore": {
            #         "Edition_2": len(nfts_2),
            #         "Edition_2_GF": len(foil_nfts_2)
            #     }
            # }
            mints["Raven lore"] = {
                "Edition_2": len(nfts_2),
                "Edition_2_GF": len(foil_nfts_2)
            }

        #data.append(woo_nft)

    return mints


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
