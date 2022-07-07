# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for output modules."""

import logging
import socket
from datetime import datetime, timedelta
from socket import error as socket_error
from time import sleep

from mrack.utils import find_value_in_config_hierarchy

logger = logging.getLogger(__name__)


def resolve_hostname(ip_addr, timeout_minutes=2, sleep_seconds=10):
    """
    Resolve IP address to hostname.

    Try to resolve IP address to the hostname in the specified timeout.
    """
    timeout_time = datetime.now() + timedelta(minutes=timeout_minutes)
    res = None
    logger.info(
        f"Waiting up to {timeout_minutes} minute(s) for host "
        f" with ip {ip_addr} to have DNS entry."
    )

    # In some cases it takes time to create DNS record
    while datetime.now() < timeout_time:
        try:
            res = socket.gethostbyaddr(ip_addr)[0]
            if res:
                break

            sleep(sleep_seconds)

        except socket_error:
            pass

    logger.debug(f"Result of the DNS lookup: {res if res else 'Failed'}")
    return res


def get_external_id(host, meta_host, config):
    """
    Get host's external ID.

    That can be its resolvable DNS name (from IP) or the IP - based on provider or
    host configuration (key: resolve_host, default True).

    IP is used as fallback if the desired is not available.
    """
    resolve_ip = find_value_in_config_hierarchy(
        config, host.provider.name, host, meta_host, "resolve_host", None, None, True
    )

    external_id = host.ip_addr
    if resolve_ip:
        external_id = resolve_hostname(host.ip_addr) or host.ip_addr
    return external_id
