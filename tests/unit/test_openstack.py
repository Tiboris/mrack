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
from copy import deepcopy
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from mrack.providers.openstack import OpenStackProvider

from .utils import get_data  # FIXME do not use relative import

predefined_hosts = [
    {
        "name": "f-latest-0.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
    {
        "name": "f-latest-1.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
    {
        "name": "f-latest-2.mrack.test",
        "os": "fedora-latest",
        "group": "ipaclient",
        "flavor": "ci.standard.xs",
        "image": "idm-Fedora-Cloud-Base-37-latest",
        "key_name": "idm-jenkins",
        "network": "IPv4",
        "config_drive": True,
    },
]

amended_nets = {
    "net_1": {
        "network_id": "9b42e096-7517-11ea-824f-e470b821142a",
        "network_name": "net_1",
        "project_id": "6ecd972c751711ea824fe470b821142a",
        "subnet_ip_availability": [
            {
                "cidr": "10.0.10.0/22",
                "ip_version": 4,
                "subnet_id": "a4b9e214-7517-11ea-824f-e470b821142a",
                "subnet_name": "provider_net_subnet_net_1",
                "total_ips": 1000,
                "used_ips": 100,
            }
        ],
        "tenant_id": "6ecd972c751711ea824fe470b821142a",
        "total_ips": 1010,
        "used_ips": 462,
    },
    "net_2": {
        "network_id": "a50332fc-7517-11ea-824f-e470b821142a",
        "network_name": "net_2",
        "project_id": "6ecd972c751711ea824fe470b821142a",
        "subnet_ip_availability": [
            {
                "cidr": "10.0.20.0/22",
                "ip_version": 4,
                "subnet_id": "3389431e-d528-4dfe-a42e-f21d2ec25ac0",
                "subnet_name": "provider_net_subnet_net_2",
                "total_ips": 1000,
                "used_ips": 500,
            }
        ],
        "tenant_id": "6ecd972c751711ea824fe470b821142a",
        "total_ips": 18446744073709552623,
        "used_ips": 1060,
    },
    "net_3": {
        "network_id": "daf913c9-cc06-4755-83fc-ece66d628d2d",
        "network_name": "net_3",
        "project_id": "6ecd972c751711ea824fe470b821142a",
        "subnet_ip_availability": [
            {
                "cidr": "10.0.30.0/22",
                "ip_version": 4,
                "subnet_id": "ebf607e0-63c0-491d-988f-d9829c1efcf3",
                "subnet_name": "provider_net_subnet_net_3",
                "total_ips": 1010,
                "used_ips": 990,
            }
        ],
        "tenant_id": "6ecd972c751711ea824fe470b821142a",
        "total_ips": 1010,
        "used_ips": 379,
    },
}

net1_usable = deepcopy(amended_nets)
net1_usable["net_3"]["subnet_ip_availability"][0]["used_ips"] = 990


net_pools = get_data("network_pools.json")
network_data = [
    (
        "empty-hosts",  # test name
        [],  # hosts
        {},  # network pools
        {},  # networks
        [],  # result
    ),
    (
        "test1-host",
        [predefined_hosts[0]],
        net_pools,
        net1_usable,
        ["net_1", "net_3"],
    ),
]


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestOpenStackProvider:
    def setup(self):
        self.limits = get_data("limits.json")
        self.flavors = get_data("flavors.json")
        self.images = get_data("images.json")
        self.availabilities = get_data("network_availabilities.json")
        self.network_pools = get_data("network_pools.json")
        self.networks = get_data("networks.json")

        self.auth_patcher = patch("mrack.providers.openstack.AuthPassword")
        self.mock_auth = self.auth_patcher.start()

        self.mock_nova = Mock()
        self.mock_nova.init_api = AsyncMock(return_value=True)
        self.mock_nova.limits.show = AsyncMock(return_value=self.limits)
        self.mock_nova.flavors.list = AsyncMock(return_value=self.flavors)

        self.mock_nova_class = Mock(return_value=self.mock_nova)
        self.nova_patcher = patch(
            "mrack.providers.openstack.ExtraNovaClient", new=self.mock_nova_class
        )
        self.nova_patcher.start()

        self.mock_neutron = Mock()
        self.mock_neutron.init_api = AsyncMock(return_value=True)
        self.mock_neutron.network.list = AsyncMock(return_value=self.networks)
        self.mock_neutron.ip.list = AsyncMock(return_value=self.availabilities)

        self.mock_neutron_class = Mock(return_value=self.mock_neutron)
        self.neutron_patcher = patch(
            "mrack.providers.openstack.NeutronClient", new=self.mock_neutron_class
        )
        self.neutron_patcher.start()

        self.mock_glance = Mock()
        self.mock_glance.init_api = AsyncMock(return_value=True)
        self.mock_glance.images.list = AsyncMock(return_value=self.images)

        self.mock_glance_class = Mock(return_value=self.mock_glance)
        self.glance_patcher = patch(
            "mrack.providers.openstack.GlanceClient", new=self.mock_glance_class
        )
        self.glance_patcher.start()

    def teardown(self):
        mock.patch.stopall()

    @pytest.mark.asyncio
    async def test_init_provider(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])

        # Provider loaded networks
        for network in self.networks["networks"]:
            name = network["name"]
            uuid = network["id"]
            net = provider.get_network(name)
            assert net["id"] == uuid
            net = provider.get_network(ref=uuid)
            assert net["name"] == name

        # Provider loaded images
        for image in self.images["images"]:
            name = image["name"]
            uuid = image["id"]
            im = provider.get_image(name)
            assert im["id"] == uuid
            im = provider.get_image(ref=uuid)
            assert im["name"] == name

        # Provider loaded flavors
        for flavor in self.flavors["flavors"]:
            name = flavor["name"]
            uuid = flavor["id"]
            fla = provider.get_flavor(name)
            assert fla["id"] == uuid
            fla = provider.get_flavor(ref=uuid)
            assert fla["name"] == name

        # Provider loaded limits
        limits = provider.limits
        for key in self.limits:
            assert self.limits[key] == limits[key]

        # Provider loaded IP availabilities
        for net_ava in self.availabilities["network_ip_availabilities"]:
            name = net_ava["network_name"]
            uuid = net_ava["network_id"]
            net = provider.get_ips(name)
            assert net["network_id"] == uuid
            net = provider.get_ips(ref=uuid)
            assert net["network_name"] == name

    @pytest.mark.asyncio
    async def test_provision(self):
        provider = OpenStackProvider()
        await provider.init(image_names=[])

    @pytest.mark.asyncio
    @pytest.mark.parametrize("x", network_data, ids=[x[0] for x in network_data])
    async def test_network_picking_validation(self, x):
        _, hosts, pools, networks, exp_nets = x
        reqs = deepcopy(hosts)
        provider = OpenStackProvider()
        provider.networks = provider.networks | networks
        await provider.init(image_names=[], networks=pools)  # why but OK FIXME
        provider.translate_network_types(hosts)
        assert len(hosts) == len(reqs)
        for i in range(len(hosts)):
            assert hosts[i] != reqs[i]
            assert hosts[i]["network"] in pools.get(reqs[i]["network"])
            assert hosts[i]["network"] in exp_nets
