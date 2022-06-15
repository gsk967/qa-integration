import json, logging
from db import db

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

COL_NAME = "test_stats"
TX_TYPE = "tx"
QUERY_TYPE = "query"


def insert_stat(data):
    _ = db[COL_NAME].insert_one(data)


def check_status(test_type, cmd_type, output, err):
    if err:
        stat = {
            "test_type": test_type,
            "cmd_type": cmd_type,
            "success": False,
            "code": "unknown",
            "error_type": "unknown",
            "error": err,
        }
        insert_stat(stat)
        return

    out = json.loads(output)
    if type(out) is dict and "code" in out:
        if out["code"] != 0:
            error_type = out["raw_log"]
            split_raw_log = error_type.split(":")
            if len(split_raw_log):
                error_type = split_raw_log[-1].strip()
            stat = {
                "test_type": test_type,
                "cmd_type": cmd_type,
                "success": False,
                "code": out["code"],
                "error_type": error_type,
                "error": out["raw_log"],
                "txhash": out["txhash"],
            }
        else:
            stat = {
                "test_type": test_type,
                "cmd_type": cmd_type,
                "success": True,
                "code": out["code"],
                "txhash": out["txhash"],
            }
    elif test_type is not None and cmd_type == "query":
        stat = {
            "test_type": test_type,
            "cmd_type": cmd_type,
            "success": True,
        }
    else:
        stat = None

    if stat:
        insert_stat(stat)


def clear_data_by_type(test_type):
    db[COL_NAME].delete_many({"test_type": test_type})


def print_stats(test_type, cmd_type=TX_TYPE):
    log_text = "transactions" if cmd_type == TX_TYPE else "queries"
    num_txs = db[COL_NAME].count_documents(
        {"test_type": test_type, "cmd_type": cmd_type}
    )
    num_success_txs = db[COL_NAME].count_documents(
        {"test_type": test_type, "cmd_type": cmd_type, "success": True}
    )
    num_failed_txs = db[COL_NAME].count_documents(
        {"test_type": test_type, "cmd_type": cmd_type, "success": False}
    )
    logging.info(
        f"""
Testing Stats:
-----------------------------
Number of {log_text} executed: {num_txs}
Number of successful {log_text}: {num_success_txs} ({(num_success_txs/num_txs)*100}%)
Number of failed {log_text}: {num_failed_txs} ({(num_failed_txs/num_txs)*100}%)
        """
    )
    if num_failed_txs and cmd_type == TX_TYPE:
        logging.info("Failures:")
        failures = list(
            db[COL_NAME].aggregate(
                [
                    {
                        "$match": {
                            "test_type": test_type,
                            "cmd_type": cmd_type,
                            "success": False,
                        }
                    },
                    {
                        "$group": {
                            "_id": "$code",
                            "count": {"$count": {}},
                            "items": {"$push": "$$ROOT"},
                        }
                    },
                ]
            )
        )
        for item in failures:
            if item["_id"] == "unknown":
                logging.info(f"Runtime errors: {item['count']}")
            else:
                logging.info(
                    f"Failed with code {item['_id']} ({item['items'][0]['error_type']}): {item['count']}"
                )

    logging.info("-----------------------------")