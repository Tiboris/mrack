Name:           mrack
Version:        1.6.0
Release:        1%{?dist}
Summary:        Multicloud use-case based multihost async provisioner

License:        Apache-2.0
URL:            https://github.com/neoave/mrack
Source0:        %{URL}/releases/download/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-click
BuildRequires:  python3-pyyaml
BuildRequires:  python3-setuptools

# coma separated list of provider plugins
%global provider_plugins aws,beaker,openstack,podman,virt

Requires:       %{name}-cli = %{version}-%{release}
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-%{name}-aws = %{version}-%{release}
Requires:       python3-%{name}-beaker = %{version}-%{release}
Requires:       python3-%{name}-openstack = %{version}-%{release}
Requires:       python3-%{name}-podman = %{version}-%{release}
Requires:       python3-%{name}-virt = %{version}-%{release}

# We filter out the asyncopenstackclient dependency of this package
# so it is not forcing installation of missing dependencies in Fedora
# Once python3-AsyncOpenStackClient is in fedora we can drop this line
%global __requires_exclude asyncopenstackclient
%{?python_disable_dependency_generator}

%description
mrack is a provisioning tool and a library for CI and local multi-host
testing supporting multiple provisioning providers (e.g. AWS, Beaker,
Openstack). But in comparison to other multi-cloud libraries,
the aim is to be able to describe host from application perspective.

%package        cli
Summary:        Command line interface for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-click

%package -n     python3-%{name}lib
Summary:        Core mrack libraries
Requires:       python3-pyyaml
Recommends:     python3-gssapi
Requires:       sshpass

%{?python_provide:%python_provide python3-%{name}lib}

%package -n     python3-%{name}-aws
Summary:        AWS provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-boto3
Requires:       python3-botocore

%{?python_provide:%python_provide python3-%{name}-aws}


%package -n     python3-%{name}-beaker
Summary:        Beaker provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
%if 0%{?rhel} == 8
# c8s has missing beaker-client package
Recommends:     beaker-client
%else
Requires:       beaker-client
%endif

%{?python_provide:%python_provide python3-%{name}-beaker}


%package -n     python3-%{name}-openstack
Summary:        Openstack provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Recommends:       python3-aiofiles
Recommends:       python3-os-client-config
Recommends:     python3-AsyncOpenStackClient

%{?python_provide:%python_provide python3-%{name}-openstack}


%package -n     python3-%{name}-podman
Summary:        Podman provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       podman

%{?python_provide:%python_provide python3-%{name}-podman}

%package -n     python3-%{name}-virt
Summary:        Virtualization provider plugin for mrack using testcloud
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       testcloud

%{?python_provide:%python_provide python3-%{name}-virt}

%description        cli
%{name}-cli contains mrack command which functionality
can be extended by installing mrack plugins

%description -n     python3-%{name}lib
python3-%{name}lib contains core mrack functionalities
and static provider which can be used as a library

%description -n     python3-%{name}-aws
%{name}-aws is an additional plugin with AWS provisioning
library extending mrack package

%description -n     python3-%{name}-beaker
%{name}-beaker is an additional plugin with Beaker provisioning
library extending mrack package

%description -n     python3-%{name}-openstack
%{name}-openstack is an additional plugin with OpenStack provisioning
library extending mrack package

%description -n     python3-%{name}-podman
%{name}-podman is an additional plugin with Podman provisioning
library extending mrack package

%description -n     python3-%{name}-virt
%{name}-virt is an additional plugin with Virualization provisioning
library extending mrack package using testcloud

%prep
%autosetup -p1 -n %{name}-%{version}
# Remove bundled egg-info
rm -r src/%{name}.egg-info

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%doc CHANGELOG.md

%files cli
# the mrack man page RFE: https://github.com/neoave/mrack/issues/197
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%{_bindir}/%{name}
%{python3_sitelib}/%{name}/{,__pycache__/}run.*

%files -n python3-%{name}lib
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info
%exclude %{python3_sitelib}/%{name}/{,__pycache__/}run.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}testcloud.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}podman.*
%exclude %{python3_sitelib}/%{name}/providers/{,__pycache__/}{%{provider_plugins}}.*
%exclude %{python3_sitelib}/%{name}/transformers/{,__pycache__/}{%{provider_plugins}}.*

%files -n python3-%{name}-aws
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}aws.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}aws.*

%files -n python3-%{name}-beaker
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}beaker.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}beaker.*

%files -n python3-%{name}-openstack
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}openstack.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}openstack.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.*

%files -n python3-%{name}-podman
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}podman.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}podman.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}podman.*

%files -n python3-%{name}-virt
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}virt.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}virt.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}testcloud.*

%changelog
* Tue Sep 19 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.6.0-1
- 8b33ac0 chore: tmp (Tibor Dudlák)
- c8ec1df chore: tmp (Tibor Dudlák)
- 91831cc chore: tmp (Tibor Dudlák)
- 8f54dc7 chore: tmp (Tibor Dudlák)
- 7967e24 chore(release): Add PyPI action & extract copr step (Tibor Dudlák)
- 9bbd987 chore: Bump python-semantic-release to v7.34.4 (Tibor Dudlák)
- d6b7298 feat: Add new dependecies to mrack.spec file (David Pascual)
- 7bbda34 feat(OpenStack): Add clouds.yaml as an authentication method (David Pascual)
- a5b32e3 feat(OpenStack): Import publick key on provision (David Pascual)
- 1a29d86 test: fix pylint issues and use isinstance (Tibor Dudlák)
- db74ae0 fix(Beaker): Exception has been thrown as raise missed argument (Tibor Dudlák)
- de027fa docs(Beaker): Add hostRequires documentation section to guides (David Pascual)
- 0135d46 chore: Release version 1.15.1 (github-actions)
- 608c763 chore(Packit): Use yaml magic to run same internal tests for PRs and commits to main (Tibor Dudlák)
- 8062a20 refactor: more verbose output when (re)provisioning (Tibor Dudlák)
- 19b52f8 test(OpenStack): Add reprovision with dynamic result tests (Tibor Dudlák)
- fd111f5 fix: Do not reprovision all hosts when server error is detected (Tibor Dudlák)
- 6e499f6 fix: Use lower cooldown time to not be too slow in re-provisioning (Tibor Dudlák)
- e03793c chore(Packit): Add internalt tests per pull request (Tibor Dudlák)
- 44023eb chore(Packit): add missing build job(s) to Packit config (Tibor Dudlák)
- 5903fb9 chore: Release version 1.15.0 (github-actions)
- f9f0e33 test: Add missing strategy_retry test (Tibor Dudlák)
- 121c5db refactor(provider): take max_utilization out to method to ease mocking (Tibor Dudlák)
- dc74ced test: Add missing tests for fixed code from https://github.com/neoave/mrack/pull/245 (Tibor Dudlák)
- 86393ab feat(outputs): preset username and password for windows host in pytest-mh (Tibor Dudlák)
- 4c26b5f feat(outputs): merge nested dictionary instead of overriding it (Tibor Dudlák)
- 4dde2e5 feat(utils): add merge_dict (Tibor Dudlák)
- 5440be1 refactor: fixes _openstack_gather_responses test warnings and exec time (David Pascual)
- e29031b fix: Handle 403 AuthError (out of quota) in openstack provisioning (David Pascual)
- a4e5075 feat: configurable ssh options (Petr Vobornik)
- e9d716e chore: fix docs dependencies in tox run (Petr Vobornik)
- 6f1943b chore: add Markdown support to docs and add design section (Petr Vobornik)
- 88458e1 docs: SSH options design (Petr Vobornik)
- af38b70 chore: Release version 1.14.1 (github-actions)
- a9c4e62 fix: mrack not re-provisioning hosts which were destroyed (Tibor Dudlák)
- 17b45e4 fix: Replace coroutines with tasks to avoid RuntimeError (David Pascual)
- c209923 chore: Release version 1.14.0 (github-actions)
- e319b73 refactor(AWS): change variable name typo in get_ip_addresses (Tibor Dudlák)
- d95e65f fix(OpenStack): Add missing await for self._load_limits() method call (Tibor Dudlák)
- d0c2d8f refactor: Update supported providers (Tibor Dudlák)
- 13ad3df fix(outputs): remove config section from pytest-multihost (Tibor Dudlák)
- d3da251 feat(outputs): allow to overwrite ansible layout (Tibor Dudlák)
- d3ac20d feat(outputs): allow to choose which outputs should be generated (Tibor Dudlák)
- 66f2877 feat(outputs): add support for pytest-mh (Tibor Dudlák)
- db633b7 feat(utils): relax condition in get_fqdn (Tibor Dudlák)
- 0735e36 fix(outputs): add host to correct group in layout (Tibor Dudlák)
- b1f5318 feat(utils): add get_os_type (Tibor Dudlák)
- 0ab88e6 refactor(black): reformat code (Tibor Dudlák)
- acf943e chore: Release version 1.13.3 (github-actions)
- 0f62237 fix(OpenStack): await loading limits to not break provisioning (Tibor Dudlák)
- 13e2635 chore: Release version 1.13.2 (github-actions)
- 06f18d1 fix: Use get method when host error object is a dictionary (Tibor Dudlák)
- fd33d68 fix(Beaker): rerurn common dictionary when validation fails (Tibor Dudlák)
- b6c5ef4 fix(OpenStack): Add exception parameter when validation fails (Tibor Dudlák)
- fa2c779 fix(OpenStack): load limits properly by one method (Tibor Dudlák)
- 61e515f chore: change back mrack dist release to 1 (Tibor Dudlák)
- 469298d chore: Release version 1.13.1 (github-actions)
- 1421b37 fix(MrackConfig): Fix MrackConfig class properties (Tibor Dudlák)
- 38313f8 chore: Release version 1.13.0 (github-actions)
- 72cc2f3 test: add extra dnf options when dealing with rhel/epel 8 (Tibor Dudlák)
- 32a754b chore: set packit to sync changelog as well (Tibor Dudlák)
- b0512b4 chore: sync fedora spec to upstream to maintain changelog history for fedora (Tibor Dudlák)
- be7b50a chore: Generate proper changelog from commit history when releasing (Tibor Dudlák)
- 98f4035 chore: Bump python-semantic-release to latest (Tibor Dudlák)
- a0e76dd test(OpenStack): Fixup the network spread tests (Tibor Dudlák)
- 88b9332 test(OpenStack): rewrite network alloaction tests (Tibor Dudlák)
- 777862f feat(OpenStack): Provide a way to disable network spreading (Tibor Dudlák)
- ff7331d fix(OpenStack): fix condition for network to get in interval (Tibor Dudlák)
- 943316d fix: fqdn in name is ignored and mrack guesses the name instead #237 (Tibor Dudlák)
- 46141dc feat(AWS): Add utilization check method (Tibor Dudlák)
- bb80060 feat(OpenStack): Add utilization check method (Tibor Dudlák)
- 55f9c2c feat: Do not use same sleep for every mrack run (Tibor Dudlák)
- 6ce3927 test(AnsibleInventory): global level output values override (Tibor Dudlák)
- a7a896a feat(AnsibleInventory): Allow additional global level values (Tibor Dudlák)
- 91c562c feat(AnsibleInventory): Allow additional domain level ansible inventory values (Tibor Dudlák)
- 109b03c test(OpenStack): Update calls in openststack tests (Tibor Dudlák)
- 4467cc2 refactor(OpenStack): make private openstack methods truly private (Tibor Dudlák)
- 72b9b9c chore: use custom release_suffix for PR testing via packit (Petr Vobornik)
- f3f734a chore: disable pylint pre-commit hook (Petr Vobornik)
- 4aa9b0a chore(Packit): Add synchronization of tmt plans and tests (Tibor Dudlák)
- 02c3e01 chore(Packit): Configure users on whose actions packit is allowed to be run (Tibor Dudlák)
- cf14ed9 chore(Packit): Add missing ci.fmf to synced files (Tibor Dudlák)
- 6bd9e17 chore: Release version 1.12.3 (github-actions)
- 52bb87e chore(Packit): Enable copr build for commit to main only. (Tibor Dudlák)
- 635d008 chore(Packit): Enable TF tests job to run on pull request. (Tibor Dudlák)
- 9c83b5d chore(Packit): Add fedora gating.yaml to synced files. (Tibor Dudlák)
- a07785c chore(TestingFarm): Add gating for fedora workflow (Tibor Dudlák)
- c4c1a67 fix: Add cache decorator for older python versions. (Tibor Dudlák)
- aac3ed4 fix(mrack.spec): Missing dependency in c8s for beaker-client (Tibor Dudlák)
- 5a726db chore(Packit): enable epel-8 and epel-9 updates and tests (Tibor Dudlák)
- cd0335a fix(AWS): refactor sources to be py3.6 compatible (Tibor Dudlák)
- 497e95b chore: Release version 1.12.2 (github-actions)
- 3397948 chore: Use python 3.10 in GH actions (Tibor Dudlák)
- 71abf31 refactor: pylint fixes related to Python 3.10 (Tibor Dudlák)
- 6e3563b test: Fix test_utils.py to be included in pytest run (Tibor Dudlák)
- 9303259 chore(pytest): add missing python_path when using pytest >=7.0.0 (Tibor Dudlák)
- de0986f test: Add test for value_to_bool util function (Tibor Dudlák)
- 592f364 fix: Owner requirement boolean parsing from string (Tibor Dudlák)
- a7bf366 chore(Packit): Add upstream_tag_template to .packit.yaml (Tibor Dudlák)
- cd95a01 chore: Release version 1.12.1 (github-actions)
- 378ec61 chore: Add packit service configuration (Tibor Dudlák)
- 9449082 fix: make db file and provisioning file optional (Tibor Dudlák)
- 80ade20 chore: bump commit message checker version (Tibor Dudlák)
- e281c32 chore: Set persist credentials to false at checkout (Tibor Dudlák)
- 40345f0 refactor: Use MrackError in run.py (Tibor Dudlák)
- 1c9a75e test(OpenStack): update test according to new changes in error handling (Tibor Dudlák)
- 990224b fix: Use MrackError in action Up to catch all possible mrack errors at once (Tibor Dudlák)
- 883dd81 refactor: Add MrackError as Parent exception class (Tibor Dudlák)
- 1b87ce5 refactor(OpenStack): raise Validation error when validation fails (Tibor Dudlák)
- 111d481 fix: validate ownership and lifetime only for AWS and OpenStack (kaleemsiddiqu)
- bd3a08a chore: Use personal GH token to release mrack (Tibor Dudlák)
- 81db5bf chore: Release version 1.12.0 (github-actions)
- fd4e0db chore: include optional dependency of gssapi (Tibor Dudlák)
- 07682c1 fix: integration test_actions test fixes (Tibor Dudlák)
- ed9e977 feat(aws): Add owner/lifetime info in VM's metadata (Tibor Dudlák)
- e33038e feat(openstack): Add owner/lifetime info in VM's metadata (Tibor Dudlák)
- e11c9a7 chore: disable automatic runtime deps discovery for rpm build (Petr Vobornik)
- c66fef7 fix: Do not use deprecated asyncio.coroutine wrapper (Tibor Dudlák)
- 30f1d5d chore: rpm and clean-rpms targets in Makefile (Petr Vobornik)
- 84e055e chore: Release version 1.11.0 (github-actions)
- 9a998bc fix(mrack.spec): fix the location for mrack.egg-info (Tibor Dudlák)
- f76c31a fix(mrack.spec): cli package files and deps (Tibor Dudlák)
- 87c397e fix(Podman): Fix action ssh import failing if podman provider not found (Tibor Dudlák)
- 22993be chore: bump python version in tox.ini (Tibor Dudlák)
- dbb43f3 fix(mrack.spec): remove unecessary statement (Tibor Dudlák)
- d00dbe5 test(Beaker): add tests for non-default keys (Tibor Dudlák)
- 9c6869f test(Beaker): add check for additional keys (Tibor Dudlák)
- b58f717 refactor(Beaker): transformer test to use dictionary (Tibor Dudlák)
- 742ed9c feat(AWS): Add multiple subnet support & IPs availability check (David Pascual)
- 7ff67e2 chore: Release version 1.10.0 (github-actions)
- 5262bca fix: Update paths in specfile and python_provide (Tibor Dudlák)
- e28e044 fix(utils): add encoding to open functions (Tibor Dudlák)
- 84cd4dc fix(Podman): add encoding to open function (Tibor Dudlák)
- 71ef2f1 fix(Beaker): Add encoding to open when opening ssh key (Tibor Dudlák)
- 1ca449d chore: bump versions of GitHub actions (Tibor Dudlák)
- e7646b8 test(OpenStack): network picker check (Tibor Dudlák)
- 317c2ac feat(OpenStack): Pick from all networks based on load (Tibor Dudlák)
- 887a13e refactor: create more verbose output when listing reqs (Tibor Dudlák)
- ab4c1c6 chore: Release version 1.9.1 (github-actions)
- 64fa546 fix: add CHANGELOG.md to MANIFEST.in (Tibor Dudlák)
- 91726d7 fix: Update spec to match fedora community standard (Tibor Dudlák)
- 221ea15 chore: Use branch main instead of master (Tibor Dudlák)
- 18f6b78 fix(Beaker): traceback when hub is not accessible at session creation (Tibor Dudlák)
- 9c258d8 fix(Beaker): connection to hub timing out (Tibor Dudlák)
- c42e4e2 chore: Release version 1.9.0 (github-actions)
- 48b16f4 docs: Update installation steps based on mrack package division (Tibor Dudlák)
- 1709af0 feat: Split mrack spec to multiple packages (Tibor Dudlák)
- 40cd839 chore: Release version 1.8.1 (github-actions)
- 957f8c5 refactor: fix the typos in aws provider (Tibor Dudlák)
- d22d360 fix: add missing split support for transformer (Tibor Dudlák)
- aaa611d chore: Release version 1.8.0 (github-actions)
- 607c99c feat: Add support to dynamically load providers (Tibor Dudlák)
- 3ef4b92 fix: Use encoding when opening files in setup.py (Tibor Dudlák)
- 2e76b4f chore: Release version 1.7.0 (github-actions)
- d1b794b fix(Beaker): Do not throw an Exception when not authenticated (Tibor Dudlák)
- 98255c7 fix: issue when searching for value when dict_name == attr (Tibor Dudlák)
- 7a8bd24 refactor(beaker): move distro_tags and hostRequires to transformer (Tibor Dudlák)
- 64cfa3a test(Beaker): check transformation for all supported reqs (Tibor Dudlák)
- 0617fdf test(Beaker): Do not use pubkey in mocked config (Tibor Dudlák)
- 59ba489 feat(Beaker): Specify ks_append per host or config (Tibor Dudlák)
- e9b6fa7 feat(Beaker): support configurable jobxml specs (Tibor Dudlák)
- 161a145 test(Beaker): check the ks_meta translation (Tibor Dudlák)
- 7a690a0 test(Beaker): Update beaker test to mock global context provisioning config (Tibor Dudlák)
- e167443 feat(Beaker): Support custom configurable ks_meta values (Tibor Dudlák)
- aa938e3 refactor(Beaker): fix the typo in the comment message (Tibor Dudlák)
- be560d9 fix: Beaker log polling to logfile instead of console (Tibor Dudlák)
- 4852af9 chore: Add ksiddiqu as release actor (Tibor Dudlák)
- 9c0b89b chore: Release version 1.6.0 (github-actions)
- 3d97bcc chore: Use python 3.9 and new python-semantic-release (Tibor Dudlák)
- d0c28f6 feat(pytest-multihost): arbitrary attributes for hosts (Petr Vobornik)
- d337a7b fix(pytest-multihost): crash when group is not defined (Petr Vobornik)
- d6e3483 fix(pytest-multihost): crash when mhcfg is missing in prov. config (Petr Vobornik)
- 65057e7 feat(ansible-inventory): host arbitrary attributes (Petr Vobornik)
- 3da517c feat: copyign meta_ attributes from host to ansible inventory (Petr Vobornik)

* Tue Jun 13 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.15.1-1
- 608c763 chore(Packit): Use yaml magic to run same internal tests for PRs and commits to main (Tibor Dudlák)
- 8062a20 refactor: more verbose output when (re)provisioning (Tibor Dudlák)
- 19b52f8 test(OpenStack): Add reprovision with dynamic result tests (Tibor Dudlák)
- fd111f5 fix: Do not reprovision all hosts when server error is detected (Tibor Dudlák)
- 6e499f6 fix: Use lower cooldown time to not be too slow in re-provisioning (Tibor Dudlák)
- e03793c chore(Packit): Add internalt tests per pull request (Tibor Dudlák)
- 44023eb chore(Packit): add missing build job(s) to Packit config (Tibor Dudlák)

* Tue Apr 18 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.15.0-1
- f9f0e33 test: Add missing strategy_retry test (Tibor Dudlák)
- 121c5db refactor(provider): take max_utilization out to method to ease mocking (Tibor Dudlák)
- dc74ced test: Add missing tests for fixed code from https://github.com/neoave/mrack/pull/245 (Tibor Dudlák)
- 86393ab feat(outputs): preset username and password for windows host in pytest-mh (Tibor Dudlák)
- 4c26b5f feat(outputs): merge nested dictionary instead of overriding it (Tibor Dudlák)
- 4dde2e5 feat(utils): add merge_dict (Tibor Dudlák)
- 5440be1 refactor: fixes _openstack_gather_responses test warnings and exec time (David Pascual)
- e29031b fix: Handle 403 AuthError (out of quota) in openstack provisioning (David Pascual)
- a4e5075 feat: configurable ssh options (Petr Vobornik)
- e9d716e chore: fix docs dependencies in tox run (Petr Vobornik)
- 6f1943b chore: add Markdown support to docs and add design section (Petr Vobornik)
- 88458e1 docs: SSH options design (Petr Vobornik)

* Thu Mar 16 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.14.1-1
- a9c4e62 fix: mrack not re-provisioning hosts which were destroyed (Tibor Dudlák)
- 17b45e4 fix: Replace coroutines with tasks to avoid RuntimeError (David Pascual)

* Wed Mar 08 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.14.0-1
- e319b73 refactor(AWS): change variable name typo in get_ip_addresses (Tibor Dudlák)
- d95e65f fix(OpenStack): Add missing await for self._load_limits() method call (Tibor Dudlák)
- d0c2d8f refactor: Update supported providers (Tibor Dudlák)
- 13ad3df fix(outputs): remove config section from pytest-multihost (Tibor Dudlák)
- d3da251 feat(outputs): allow to overwrite ansible layout (Tibor Dudlák)
- d3ac20d feat(outputs): allow to choose which outputs should be generated (Tibor Dudlák)
- 66f2877 feat(outputs): add support for pytest-mh (Tibor Dudlák)
- db633b7 feat(utils): relax condition in get_fqdn (Tibor Dudlák)
- 0735e36 fix(outputs): add host to correct group in layout (Tibor Dudlák)
- b1f5318 feat(utils): add get_os_type (Tibor Dudlák)
- 0ab88e6 refactor(black): reformat code (Tibor Dudlák)

* Wed Mar 01 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.3-1
- 0f62237 fix(OpenStack): await loading limits to not break provisioning (Tibor Dudlák)

* Wed Mar 01 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.2-1
- 06f18d1 fix: Use get method when host error object is a dictionary (Tibor Dudlák)
- fd33d68 fix(Beaker): rerurn common dictionary when validation fails (Tibor Dudlák)
- b6c5ef4 fix(OpenStack): Add exception parameter when validation fails (Tibor Dudlák)
- fa2c779 fix(OpenStack): load limits properly by one method (Tibor Dudlák)
- 61e515f chore: change back mrack dist release to 1 (Tibor Dudlák)

* Tue Feb 21 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.1-1
- 1421b37 fix(MrackConfig): Fix MrackConfig class properties (Tibor Dudlák)

* Fri Feb 17 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.0-1
- 72cc2f3 test: add extra dnf options when dealing with rhel/epel 8 (Tibor Dudlák)
- 32a754b chore: set packit to sync changelog as well (Tibor Dudlák)
- b0512b4 chore: sync fedora spec to upstream to maintain changelog history for fedora (Tibor Dudlák)
- be7b50a chore: Generate proper changelog from commit history when releasing (Tibor Dudlák)
- 98f4035 chore: Bump python-semantic-release to latest (Tibor Dudlák)
- a0e76dd test(OpenStack): Fixup the network spread tests (Tibor Dudlák)
- 88b9332 test(OpenStack): rewrite network alloaction tests (Tibor Dudlák)
- 777862f feat(OpenStack): Provide a way to disable network spreading (Tibor Dudlák)
- ff7331d fix(OpenStack): fix condition for network to get in interval (Tibor Dudlák)
- 943316d fix: fqdn in name is ignored and mrack guesses the name instead #237 (Tibor Dudlák)
- 46141dc feat(AWS): Add utilization check method (Tibor Dudlák)
- bb80060 feat(OpenStack): Add utilization check method (Tibor Dudlák)
- 55f9c2c feat: Do not use same sleep for every mrack run (Tibor Dudlák)
- 6ce3927 test(AnsibleInventory): global level output values override (Tibor Dudlák)
- a7a896a feat(AnsibleInventory): Allow additional global level values (Tibor Dudlák)
- 91c562c feat(AnsibleInventory): Allow additional domain level ansible inventory values (Tibor Dudlák)
- 109b03c test(OpenStack): Update calls in openststack tests (Tibor Dudlák)
- 4467cc2 refactor(OpenStack): make private openstack methods truly private (Tibor Dudlák)
- 72b9b9c chore: use custom release_suffix for PR testing via packit (Petr Vobornik)
- f3f734a chore: disable pylint pre-commit hook (Petr Vobornik)
- 4aa9b0a chore(Packit): Add synchronization of tmt plans and tests (Tibor Dudlák)
- 02c3e01 chore(Packit): Configure users on whose actions packit is allowed to be run (Tibor Dudlák)
- cf14ed9 chore(Packit): Add missing ci.fmf to synced files (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-4
- chore: Add add tmt tests and plans and add them to sync (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-3
- chore: Add fmf/version and allowed users to run packit (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-2
- chore: Add ci.fmf to the repo (Tibor Dudlák)

* Tue Dec 13 2022 Packit <hello@packit.dev> - 1.12.3-1
- chore: Release version 1.12.3 (github-actions)
- chore(Packit): Enable copr build for commit to main only. (Tibor Dudlák)
- chore(Packit): Enable TF tests job to run on pull request. (Tibor Dudlák)
- chore(Packit): Add fedora gating.yaml to synced files. (Tibor Dudlák)
- chore(TestingFarm): Add gating for fedora workflow (Tibor Dudlák)
- fix: Add cache decorator for older python versions. (Tibor Dudlák)
- fix(mrack.spec): Missing dependency in c8s for beaker-client (Tibor Dudlák)
- chore(Packit): enable epel-8 and epel-9 updates and tests (Tibor Dudlák)
- fix(AWS): refactor sources to be py3.6 compatible (Tibor Dudlák)

* Fri Dec 02 2022 Packit <hello@packit.dev> - 1.12.2-1
- chore: Release version 1.12.2 (github-actions)
- chore: Use python 3.10 in GH actions (Tibor Dudlák)
- refactor: pylint fixes related to Python 3.10 (Tibor Dudlák)
- test: Fix test_utils.py to be included in pytest run (Tibor Dudlák)
- chore(pytest): add missing python_path when using pytest >=7.0.0 (Tibor Dudlák)
- test: Add test for value_to_bool util function (Tibor Dudlák)
- fix: Owner requirement boolean parsing from string (Tibor Dudlák)
- chore(Packit): Add upstream_tag_template to .packit.yaml (Tibor Dudlák)

* Thu Nov 24 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.1-1
- Released upstream version 1.12.1

* Mon Nov 14 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.0-1
- Released upstream version 1.12.0

* Thu Nov 03 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.11.0-1
- Released upstream version 1.11.0

* Wed Oct 26 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.10.0-1
- Released upstream version 1.10.0

* Thu Oct 20 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.9.1-1
- Released upstream version 1.9.1

* Wed Oct 12 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.9.0-1
- Released upstream version 1.9.0

* Mon Oct 10 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.8.1-1
- Released upstream version 1.8.1

* Mon Oct 10 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.8.0-1
- Released upstream version 1.8.0

* Tue Sep 20 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.7.0-1
- Released upstream version 1.7.0

* Wed Jul 27 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.6.0-1
- Released upstream version 1.6.0

* Fri Jul 08 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.5.0-1
- Released upstream version 1.5.0

* Fri Jun 17 2022 David Pascual Hernandez <davherna@redhat.com> - 1.4.1-1
- Released upstream version 1.4.1

* Thu May 05 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.4.0-1
- Released upstream version 1.4.0

* Tue Apr 05 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.3.1-1
- Released upstream version 1.3.1

* Fri Apr 01 2022 David Pascual Hernandez <davherna@redhat.com> - 1.3.0-1
- Released upstream version 1.3.0

* Wed Dec 15 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.2.0-1
- Released upstream version 1.2.0

* Thu Nov 25 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.1.1-1
- Released upstream version 1.1.1

* Tue Nov 23 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.1.0-1
- Released upstream version 1.1.0

* Fri Sep 03 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.0.0-1
- Released upstream version 1.0.0

* Thu Jul 01 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.14.0-1
- Released upstream version 0.14.0

* Tue Jun 08 2021 Francisco Triviño <ftrivino@redhat.com> - 0.13.0-1
- Released upstream version 0.13.0

* Thu May 13 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.12.0-1
- Released upstream version 0.12.0

* Fri May 07 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.11.0-1
- Released upstream version 0.11.0

* Fri Apr 30 2021 Bhavik Bhavsar <bbhavsar@redhat.com> - 0.10.0-1
- Released upstream version 0.10.0

* Mon Apr 19 2021 Armando Neto <abiagion@redhat.com> - 0.9.0-1
- Released upstream version 0.9.0

* Thu Apr 15 2021 Armando Neto <abiagion@redhat.com> - 0.8.0-1
- Released upstream version 0.8.0

* Tue Mar 23 2021 Armando Neto <abiagion@redhat.com> - 0.7.1-1
- Released upstream version 0.7.1

* Mon Mar 22 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.7.0-1
- Released upstream version 0.7.0

* Thu Feb 04 2021 Armando Neto <abiagion@redhat.com> - 0.6.0-1
- Initial package.
