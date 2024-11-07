"""Utility methods for Cisco Catalyst Add-On."""
import traceback
import urllib.parse

import consts
from solnlib import conf_manager


def get_sslconfig(session_key, helper):
    """Get the verify_ssl flag or ca_cert file to be used for network calls."""
    app = consts.APP_NAME
    conf_name = consts.CONF_NAME
    session_key = urllib.parse.unquote(session_key.encode("ascii").decode("ascii"))
    session_key = session_key.encode().decode("utf-8")
    verify_ssl = None
    try:
        ssl_config = True
        ca_certs_path = ""

        cfm = conf_manager.ConfManager(
            session_key,
            app,
            realm="__REST_CREDENTIAL__#{}#configs/conf-{}".format(app, conf_name),
        )
        stanza = cfm.get_conf(conf_name, refresh=True).get("additional_parameters")
        verify_ssl = is_true((stanza.get("verify_ssl") or "").strip().upper())
        ca_certs_path = (stanza.get("ca_certs_path") or "").strip()

    except Exception:
        msg = f"Error while fetching ca_certs_path from '{conf_name}' conf. Traceback: {traceback.format_exc()}"
        helper.log_error(msg)

    if not verify_ssl:
        helper.log_debug("SSL Verification is set to False.")
        ssl_config = False
    elif verify_ssl and ca_certs_path:
        helper.log_debug(
            f"SSL Verification is set to True and will use the cert from this path: {ca_certs_path}."
        )
        ssl_config = ca_certs_path
    else:
        helper.log_debug("SSL Verification is set to True.")
        ssl_config = True

    return ssl_config


def is_true(val):
    """
    Check truthy value of the given parameter.

    :param val: Parameter of which truthy value is to be checkeds

    :return: True / False
    """
    value = str(val).strip().upper()
    if value in ("1", "TRUE", "T", "Y", "YES"):
        return True
    return False
