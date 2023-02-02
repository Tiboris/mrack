from mrack.outputs.pytest_multihost import PytestMultihostOutput

from .mock_data import get_db_from_metadata, metadata_extra, provisioning_config


class TestPytestMultihostOutput:
    def test_arbitrary_attrs(self):
        """
        Test that values defined in `pytest_multihost` dictionary in host part
        of job metadata file gets into host attributes in generated pytest-multihost
        output.
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        m_srv1["pytest_multihost"] = {
            "readonly_dc": "yes",
            "something_else": "for_fun",
        }
        m_srv2["pytest_multihost"] = {
            "no_ca": "yes",
            "something_else": "for_fun",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "for_fun"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "for_fun"

    def test_domain_arbitrary_attrs(self):
        """
        Test that values defined in `pytest_multihost` dictionary in domain part
        of job metadata file gets into host attributes in generated pytest-multihost
        output and host `pytest_multihost` dictionary can override domain section.
        """
        metadata = metadata_extra()
        metadata["domains"][0]["pytest_multihost"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" not in srv1
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "no"
        assert srv2["something_else"] == "not_funny"

    def test_domain_arbitrary_attrs_override(self):
        """
        Test that values defined in `pytest_multihost` dictionary in domain part
        of job metadata file gets into host attributes in generated pytest-multihost
        output and host `pytest_multihost` dictionary can override domain section.
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        metadata["domains"][0]["pytest_multihost"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        m_srv1["pytest_multihost"] = {
            "readonly_dc": "yes",
            "something_else": "for_fun",
        }
        m_srv2["pytest_multihost"] = {
            "no_ca": "yes",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "for_fun"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "not_funny"

    def test_global_arbitrary_attrs(self):
        """
        Test that values defined in `pytest_multihost` dictionary in the
        job metadata file gets into host attributes in generated pytest-multihost
        output and host `pytest_multihost` dictionary can override values using
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        metadata["pytest_multihost"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" not in srv1
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "no"
        assert srv2["something_else"] == "not_funny"

    def test_global_arbitrary_attrs_domain_override(self):
        """
        Test that values defined in `pytest_multihost` dictionary in the
        job metadata file gets into host attributes in generated pytest-multihost
        output and host `pytest_multihost` dictionary can override values using
        host section.
        """
        metadata = metadata_extra()
        metadata["pytest_multihost"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        metadata["domains"][0]["pytest_multihost"] = {
            "no_ca": "yes",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" not in srv1
        assert "something_else" in srv1
        assert srv1["something_else"] == "not_funny"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "yes"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "not_funny"

    def test_global_arbitrary_attrs_host_override(self):
        """
        Test that values defined in `pytest_multihost` dictionary in the
        job metadata file gets into host attributes in generated pytest-multihost
        output and host `pytest_multihost` dictionary can override values using
        domain section.
        """
        metadata = metadata_extra()
        m_srv1 = metadata["domains"][0]["hosts"][0]
        m_srv2 = metadata["domains"][0]["hosts"][1]
        metadata["domains"][0]["pytest_multihost"] = {
            "no_ca": "no",
            "something_else": "not_funny",
        }

        m_srv1["pytest_multihost"] = {
            "readonly_dc": "yes",
            "something_else": "for_fun",
        }
        m_srv2["pytest_multihost"] = {
            "no_ca": "yes",
        }

        config = provisioning_config()
        db = get_db_from_metadata(metadata)
        mhcfg_output = PytestMultihostOutput(config, db, metadata)
        mhcfg = mhcfg_output.create_multihost_config()

        srv1 = mhcfg["domains"][0]["hosts"][0]

        assert "readonly_dc" in srv1
        assert srv1["readonly_dc"] == "yes"
        assert "something_else" in srv1
        assert srv1["something_else"] == "for_fun"
        assert "no_ca" in srv1
        assert srv1["no_ca"] == "no"

        srv2 = mhcfg["domains"][0]["hosts"][1]
        assert "no_ca" in srv2
        assert "something_else" in srv2
        assert srv2["no_ca"] == "yes"
        assert srv2["something_else"] == "not_funny"
