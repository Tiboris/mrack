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

"""OpenStack provider."""

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta
from asyncopenstackclient import GlanceClient, AuthPassword
from simple_rest_client.exceptions import NotFoundError
from urllib.parse import urlparse, parse_qs
from aiohabit.providers.utils.osapi import ExtraNovaClient, NeutronClient
from aiohabit.providers.provider import Provider
from aiohabit.host import (
    Host,
    STATUS_ACTIVE,
    STATUS_PROVISIONING,
    STATUS_DELETED,
    STATUS_ERROR,
    STATUS_OTHER,
)
from aiohabit.errors import ServerNotFoundError, ValidationError, ProvisioningError

# Docs
# https://github.com/DreamLab/AsyncOpenStackClient
# https://docs.openstack.org/queens/api/


KEY = "openstack"


STATUS_MAP = {
    "ACTIVE": STATUS_ACTIVE,
    "BUILD": STATUS_PROVISIONING,
    "DELETED": STATUS_DELETED,
    "ERROR": STATUS_ERROR,
    # there is much more we can treat it as STATUS_OTHER, see:
    # https://docs.openstack.org/api-guide/compute/server_concepts.html
}


class OpenStackProvider(Provider):
    """
    OpenStack Provider.

    Provisions servers in OpenStack with added logic to check if requested
    resources are available.
    """

    def __init__(self):
        """Object initialization."""
        self._name = KEY
        self.flavors = {}
        self.flavors_by_ref = {}
        self.images = {}
        self.images_by_ref = {}
        self.limits = {}
        self.networks = {}
        self.networks_by_ref = {}
        self.ips = {}
        self.ips_by_ref = {}
        self.timeout = 60  # minutes
        self.poll_sleep_initial = 15  # seconds
        self.poll_sleep = 7  # seconds

    async def init(self, image_names=None):
        """Initialize provider with data from OpenStack.

        Load:
        * available flavors
        * networks
        * network availabilities (number of available IPs for networks)
        * images which were defined in `image_names` option
        * account limits (max and current usage of vCPUs, memory, ...)
        """
        # session expects that credentials will be set via env variables
        self.session = AuthPassword()
        self.nova = ExtraNovaClient(session=self.session)
        self.glance = GlanceClient(session=self.session)
        self.neutron = NeutronClient(session=self.session)

        login_start = datetime.now()
        await asyncio.gather(
            self.nova.init_api(), self.glance.init_api(), self.neutron.init_api()
        )
        login_end = datetime.now()
        login_duration = login_end - login_start
        print(f"Login duration {login_duration}")

        object_start = datetime.now()
        flavors, images, limits, networks, ips = await asyncio.gather(
            self.load_flavors(),
            self.load_images(image_names),
            self.nova.limits.show(),
            self.load_networks(),
            self.load_ip_availabilities(),
        )
        self.limits = limits
        object_end = datetime.now()
        object_duration = object_end - object_start
        print(f"Open Stack environment objects " f"load duration: {object_duration}")

    def set_flavors(self, flavors):
        """Extend provider configuration with list of flavors."""
        for flavor in flavors:
            self.flavors[flavor["name"]] = flavor
            self.flavors_by_ref[flavor["id"]] = flavor

    def set_images(self, images):
        """Extend provider configuration with list of images."""
        for image in images:
            self.images[image["name"]] = image
            self.images_by_ref[image["id"]] = image

    def set_networks(self, networks):
        """Extend provider configuration with list of networks."""
        for network in networks:
            self.networks[network["name"]] = network
            self.networks_by_ref[network["id"]] = network

    def get_flavor(self, name=None, ref=None):
        """Get flavor by name or UUID."""
        flavor = self.flavors.get(name)
        if not flavor:
            flavor = self.flavors_by_ref.get(ref)
        return flavor

    def get_image(self, name=None, ref=None):
        """Get image by name or UUID."""
        image = self.images.get(name)
        if not image:
            image = self.images_by_ref.get(ref)
        return image

    def get_network(self, name=None, ref=None):
        """Get network by name or UUID."""
        network = self.networks.get(name)
        if not network:
            network = self.networks_by_ref.get(ref)
        return network

    def get_ips(self, name=None, ref=None):
        """Get network availability by network name or network UUID."""
        aval = self.ips.get(name)
        if not aval:
            aval = self.ips_by_ref.get(ref)
        return aval

    async def load_flavors(self):
        """Extend provider configuration by loading all flavors from OpenStack."""
        resp = await self.nova.flavors.list()
        flavors = resp["flavors"]
        self.set_flavors(flavors)
        return flavors

    async def load_images(self, image_names=None):
        """
        Extend provider configuration by loading information about images.

        Load everything if image_names list is not specified.

        Specifying list of images to load might improve performance if the
        OpenStack instance contains a lot of images.
        """
        params = {"limit": 1000}

        if image_names:
            image_filter = ",".join(image_names)
            image_filter = "in:" + image_filter
            params["name"] = image_filter

        images = []
        response = await self.glance.images.list(**params)
        images.extend(response["images"])

        while response.get("next"):
            p_result = urlparse(response.get("next"))
            query = p_result.query
            next_params = parse_qs(query)
            for key, val in next_params.items():
                if type(val) == list and len(val):
                    next_params[key] = val[0]
            response = await self.glance.images.list(**next_params)
            images.extend(response["images"])

        self.set_images(images)

        return images

    async def load_networks(self):
        """Extend provider configuration by loading all networks from OpenStack."""
        resp = await self.neutron.network.list()
        networks = resp["networks"]
        self.set_networks(networks)
        return networks

    async def load_ip_availabilities(self):
        """Extend provider configuration by loading networks availabilities."""
        resp = await self.neutron.ip.list()
        availabilities = resp["network_ip_availabilities"]
        for availability in availabilities:
            self.ips[availability["network_name"]] = availability
            self.ips_by_ref[availability["network_id"]] = availability
        return availabilities

    def _translate_flavor(self, req):
        flavor_spec = req.get("flavor")
        flavor_ref = req.get("flavorRef")
        flavor = None
        if flavor_ref:
            flavor = self.get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self.get_flavor(flavor_spec, flavor_spec)

        if not flavor:
            specs = f"flavor: {flavor_spec}, ref: {flavor_ref}"
            raise ValidationError(f"Flavor not found: {specs}")
        return flavor

    def _translate_image(self, req):
        image_spec = req.get("image")
        image_ref = req.get("imageRef")
        image = None
        if image_ref:
            image = self.get_image(ref=image_ref)
        if image_spec:
            image = self.get_image(image_spec, image_spec)
        if not image:
            specs = f"image: {image_spec}, ref: {image_ref}"
            raise ValidationError(f"Image not found {specs}")
        return image

    def _translate_networks(self, req, spec=False):
        network_req = req.get("network")
        network_specs = req.get("networks", [])
        network_specs = deepcopy(network_specs)
        networks = []
        if type(network_specs) != list:
            network_specs = []
        for network_spec in network_specs:
            uuid = network_spec.get("uuid")
            network = self.get_network(ref=uuid)
            if not network:
                raise ValidationError(f"Network not found: {network_spec}")
            networks.append(network)
        if network_req:
            network = self.get_network(name=network_req, ref=network_req)
            if not network:
                raise ValidationError(f"Network not found: {network_req}")
            network_specs.append({"uuid": network["id"]})
            networks.append(network)

        if spec:
            return network_specs
        return networks

    def validate_host(self, req):
        """Validate that host requirements contains existing required objects."""
        self._translate_flavor(req)
        self._translate_image(req)
        self._translate_networks(req)

        return True

    async def validate_hosts(self, reqs):
        """Validate that all hosts requirements contains existing required objects."""
        for req in reqs:
            self.validate_host(req)

    def get_host_requirements(self, req):
        """Get vCPU and memory requirements for host requirement."""
        flavor_spec = req.get("flavor")
        flavor_ref = req.get("flavorRef")
        if flavor_ref:
            flavor = self.get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self.get_flavor(flavor_spec, flavor_spec)
        return {"ram": flavor["ram"], "vcpus": flavor["vcpus"]}

    async def can_provision(self, reqs):
        """Check that all host can be provisioned.

        Checks:
        * available vCPUs and memory based on account limits
        * that all host contain available flavors, images, networks
        """
        vcpus = 0
        ram = 0

        for req in reqs:
            needs = self.get_host_requirements(req)
            vcpus += needs["vcpus"]
            ram += needs["ram"]

        limits = self.limits["limits"]["absolute"]
        used_vcpus = limits["totalCoresUsed"]
        used_memory = limits["totalRAMUsed"]
        limit_vcpus = limits["maxTotalCores"]
        limit_memory = limits["maxTotalRAMSize"]

        req_vcpus = used_vcpus + vcpus
        req_memory = used_memory + ram

        print(f"Required vcpus: {vcpus}, " f"used: {used_vcpus}, max: {limit_vcpus}")
        print(f"Required ram: {ram}, used: {used_memory}, max: {limit_memory}")

        return req_vcpus <= limit_vcpus and req_memory <= limit_memory

    async def create_server(self, req):
        """Issue creation of a server.

        req - dict of server requirements - can contains values defined in
              POST /servers official OpenStack API
              https://docs.openstack.org/api-ref/compute/?expanded=create-server-detail#create-server

        The req object can contain following additional attributes:
        * 'flavor': uuid or name of flavor to use
        * 'network': uuid or name of network to use. Will be added to networks
                     list if present
        """
        specs = deepcopy(req)  # work with own copy, do not modify the input

        flavor = self._translate_flavor(req)
        specs["flavorRef"] = flavor["id"]
        if specs.get("flavor"):
            del specs["flavor"]

        image = self._translate_image(req)
        specs["imageRef"] = image["id"]
        if specs.get("image"):
            del specs["image"]

        network_specs = self._translate_networks(req, spec=True)
        specs["networks"] = network_specs
        if specs.get("network"):
            del specs["network"]

        response = await self.nova.servers.create(server=specs)
        return response.get("server")

    async def delete_server(self, uuid):
        """Issue deletion of server.

        Doesn't wait for the deletion to happen.
        """
        try:
            await self.nova.servers.force_delete(uuid)
        except NotFoundError:
            print("Server not found, probably already deleted")
            pass

    async def wait_till_provisioned(
        self, uuid, timeout=None, poll_sleep=None, poll_sleep_initial=None
    ):
        """
        Wait till server is provisioned.

        Provisioned means that server is in ACTIVE or ERROR state

        State is checked by polling. Polling can be controller via `poll_sleep` and
        `poll_sleep_initial` options. This is useful when provisioning a lot of
        machines as it is better to increase initial poll to not ask to often as
        provisioning resources takes some time.

        Waits till timeout happens. Timeout can be either specified or default provider
        timeout is used.

        Return information about provisioned server.
        """
        if not poll_sleep_initial:
            poll_sleep_initial = self.poll_sleep_initial
        if not poll_sleep:
            poll_sleep = self.poll_sleep
        if not timeout:
            timeout = self.timeout

        start = datetime.now()
        timeout_time = start + timedelta(minutes=timeout)
        done_states = ["ACTIVE", "ERROR"]

        # do not check the state immediately, it will take some time
        await asyncio.sleep(poll_sleep_initial)

        while datetime.now() < timeout_time:
            try:
                resp = await self.nova.servers.get(uuid)
            except NotFoundError:
                raise ServerNotFoundError(uuid)
            server = resp["server"]
            if server["status"] in done_states:
                break

            await asyncio.sleep(poll_sleep)

        done_time = datetime.now()
        prov_duration = (done_time - start).total_seconds()

        if datetime.now() >= timeout_time:
            print(f"{uuid} was not provisioned within a timeout of" f" {timeout} mins")
        else:
            print(f"{uuid} was provisioned in {prov_duration:.1f}s")

        return server

    def get_poll_sleep_times(self, hosts):
        """Compute polling sleep times based on number of hosts.

        So that we don't create unnecessary load on server while checking state of
        provisioning.

        returns (initial_sleep, sleep)
        """
        count = len(hosts)

        init_poll = self.poll_sleep_initial
        poll = self.poll_sleep

        # initial poll is the biggest performance saver it should be around
        # time when more than half of host is in ACTIVE state
        init_poll = init_poll + 0.65 * count

        # poll time should ask often enough, to not create unnecessary delays
        # while not that many to not load the server much
        poll = poll + 0.22 * count

        return init_poll, poll

    async def provision_hosts(self, hosts):
        """Provision hosts based on list of host requirements.

        Main provider method for provisioning.

        First it validates that host requirements are valid and that OpenStack tenant
        has enough resources(quota).

        Then issues provisioning and waits for it succeed. Raises exception if any of
        the servers was not successfully provisioned. If that happens it issues deletion
        of all already provisioned resources.

        Return list of information about provisioned servers.
        """
        print("Validating hosts definitions")
        await self.validate_hosts(hosts)
        print("Host definitions valid")

        print("Checking available resources")
        can = await self.can_provision(hosts)
        if not can:
            raise ValidationError("Not enough resources to provision")
        print("Resource availability: OK")

        started = datetime.now()

        count = len(hosts)
        print(f"Issuing provisioning of {count} hosts")
        create_aws = []
        for req in hosts:
            aws = self.create_server(req)
            create_aws.append(aws)
        create_resps = await asyncio.gather(*create_aws)
        print("Provisioning issued")

        print("Waiting for all hosts to be available")
        init_poll_sleep, poll_sleep = self.get_poll_sleep_times(hosts)
        wait_aws = []
        for create_resp in create_resps:
            aws = self.wait_till_provisioned(
                create_resp.get("id"),
                poll_sleep=poll_sleep,
                poll_sleep_initial=init_poll_sleep,
            )
            wait_aws.append(aws)

        server_results = await asyncio.gather(*wait_aws)
        provisioned = datetime.now()
        provi_duration = provisioned - started

        print("All hosts reached provisioning final state (ACTIVE or ERROR)")
        print(f"Provisioning duration: {provi_duration}")

        errors = [res for res in server_results if res["status"] == "ERROR"]
        if errors:
            print("Some host did not start properly")
            for err in errors:
                self.print_basic_info(err)
            print("Given the error, will delete all hosts")
            await self.delete_hosts(server_results)
            raise ProvisioningError(errors)

        hosts = [self.to_host(srv) for srv in server_results]
        for host in hosts:
            print(host)
        return hosts

    async def delete_host(self, host):
        """Issue deletion of host(server) from OpenStack."""
        await self.delete_server(host._id)
        return True

    async def delete_hosts(self, hosts):
        """Issue deletion of all servers based on previous results from provisioning."""
        print("Issuing deletion")
        delete_aws = []
        for host in hosts:
            aws = self.delete_host(host)
            delete_aws.append(aws)
        results = await asyncio.gather(*delete_aws)
        print("All servers issued to be deleted")
        return results

    def to_host(self, provisioning_result):
        """Transform provisioning result into Host object."""
        networks = provisioning_result.get("addresses", {})
        addresses = [ip.get("addr") for n in networks.values() for ip in n]
        fault = provisioning_result.get("fault")
        status = STATUS_MAP.get(provisioning_result.get("status"), STATUS_OTHER)

        host = Host(
            self,
            provisioning_result.get("id"),
            provisioning_result.get("name"),
            addresses,
            status,
            provisioning_result,
            error_obj=fault,
        )
        return host
