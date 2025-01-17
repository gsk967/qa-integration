"""
This module contains all util functions.
"""
import argparse
import os
import json
import logging
import subprocess
from shutil import which

from stats import record_stat, TX_TYPE, QUERY_TYPE


logging.basicConfig(format="%(message)s", level=logging.DEBUG)

DAEMON = os.getenv("DAEMON")
HOME = os.getenv("HOME")


def print_balance_deductions(wallet, diff):
    """
    The function `print_balance_deductions` will print information about the
    balance deductions after transactions for a wallet or account.
    Args:
        wallet (_str_): wallet name
        diff (_uint_): balance difference.
    """
    if diff > 0:
        logging.error("Some of the transactions failed")
        logging.info("Balance in the %s increased by %s", wallet, diff)
    elif diff < 0:
        logging.error("Some of the transactions failed")
        logging.info("Balance in the %s decreased by %s", wallet, (-1 * diff))
    else:
        logging.info(
            "All transaction went successfully, No deduction from %s balance", wallet
        )


def exec_command(command):
    """
    The utility function `exec_command` is used to execute the cosmos-sdk based commands.
    Args:
        command (_str_): Command to be executed.

    Returns:
        _tuple_: str, str
    """
    try:
        test_type = os.getenv("TEST_TYPE") if os.getenv("TEST_TYPE") else None
        # getting command type
        sub_commands = command.split()
        cmd_type = None
        if len(sub_commands) > 1 and (
            sub_commands[1] == "q"  # pylint: disable=C0330
            or sub_commands[1] == "query"  # pylint: disable=C0330
        ):
            cmd_type = QUERY_TYPE
        elif len(sub_commands) > 1 and (sub_commands[1] == "tx"):
            cmd_type = TX_TYPE

        stdout, stderr = subprocess.Popen(  # pylint: disable=R1732
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).communicate()
        out, error = stdout.strip().decode(), stderr.strip().decode()
        if test_type and cmd_type:
            record_stat(test_type, cmd_type, out, error)
        if len(error) != 0:
            return False, error
        json_out = json.loads(out)
        if cmd_type == TX_TYPE and "code" in json_out and json_out["code"] != 0:
            return False, json_out
        return True, json_out
    except Exception as error:  # pylint: disable=W0703
        if test_type and cmd_type:
            record_stat(test_type, cmd_type, "", error)
        return False, error


def is_tool(binary):
    """
    The utility function `is_tool` is used to verify the package or binary installation.
    """
    return which(binary) is not None


def is_positive_int(num_x):
    """
    is_positive_int will validate num_txs value
    Args:
        num_x (_int_)

    Raises:
        argparse.ArgumentTypeError

    Returns:
        _int_: _int_
    """
    if int(num_x) < 1:
        raise argparse.ArgumentTypeError(
            "The argument NUM_TXS should be positive integer"
        )
    return int(num_x)


def create_multi_messages(num_msgs, file_name):
    """
    The function `create_multi_messages` is used to duplicate the messages in a single transaction.
    Args:
        num_msgs (_uint_): uint
        file_name (_str_): file path to modify messages.
    """
    messages = []
    with open(HOME + "/" + file_name, "r+", encoding="utf8") as file:
        file_data = json.load(file)
        messages.append(file_data["body"]["messages"][-1])
    for _i in range(num_msgs):
        messages.append(messages[-1])

    with open(HOME + "/" + file_name, "r+", encoding="utf8") as file:
        file_data = json.load(file)
        file_data["body"]["messages"] = messages
        file.seek(0)
        json.dump(file_data, file, indent=4)
