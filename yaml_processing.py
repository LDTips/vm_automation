import fabric
import ruamel.yaml as yaml
import logging
import copy
import os
import driver_functions_yaml


def read_yaml(file_path: str) -> dict:
    """
    Reads a yaml file specified in the file_path
    :param file_path: str
    :return: dict
    """
    with open(file_path, 'r') as text:
        try:
            yaml_parsed = yaml.safe_load(text)
        except yaml.YAMLError as e:
            logging.exception("Unable to process yaml stream:\n {}".format(e))
            return {}
        # print(yaml.dump(yaml_parsed))
    return yaml_parsed


def write_yaml(file_path: str, yaml_data: dict, *, overwrite: bool = False) -> None:
    """
    Writes yaml_data to the provided file in file_path.
    If overwrite flag is set, the destination file will be overwritten with the passed yaml_data
    If overwrite flag is not set and the file exists, FileExistsError is raised and yaml_data is not written
    Otherwise, overwrite flag has no effect
    :param file_path: str
    :param yaml_data: dict
    :param overwrite: bool
    :return: None
    """
    try:
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError("Overwrite file was not set, but file {} exists!".format(file_path))
        with open(file_path, 'w') as output:
            # Output compared with https://www.yamldiff.com/ - It is semantically the same
            yaml.dump(yaml_data, output, default_flow_style=False)
    except FileExistsError as e:
        logging.exception(e)


def modify_yaml(src_dict: dict, new_values_dict: dict, file_type: str) -> dict:
    """
    Function creates a modified deep copy of src_dict with values present in the new_values_dict
    Modification is done according to the passed file_type. Every config file of open5gs has different structure
    :param src_dict: dict
    :param new_values_dict: dict
    :param file_type: str
    :return: dict
    """
    function_name = "driver_" + "universal"
    # TODO - Rename 'function' into something more clever
    try:
        driver_fun = getattr(driver_functions_yaml, function_name)  # Raises AttributeError if function does not exist
    except AttributeError:
        logging.exception("Invalid file type passed. {} is not specified in driver functions".format(file_type))
        return src_dict

    diff_dict = copy.deepcopy(src_dict)  # By default, python does a shallow cpy, which results in modifying amf_dict
    for key in new_values_dict:
        #try:
        diff_dict = driver_fun(key.split("-"), diff_dict, file_type, new_values_dict[key])
        #except KeyError:
            #logging.exception("Key {} was not found in amf.yaml, but was passed in new_values dict".format(key))

    return diff_dict


def test_amf():
    yaml_data_amf = read_yaml("./transfers/all_open5gs/amf.yaml")
    # AMF testing section
    test_dict_amf = {'sbi-addr': "1.1.1.1", 'sbi-port': 111, 'ngap-addr': "1.1.1.1", 'metrics-addr': "1.1.1.1",
                     'metrics-port': 11, 'guami-plmn_id-mcc': 111, 'guami-plmn_id-mnc': 111, 'guami-amf_id-region': 111,
                     'guami-amf_id-set': 111, 'tai-plmn_id-mcc': 111, 'tai-plmn_id-mnc': 111, 'tai-tac': 111,
                     'plmn_support-plmn_id-mcc': 111, 'plmn_support-plmn_id-mnc': 111, 'plmn_support-s_nssai-sst': 111,
                     'security-integrity_order': [111, 111, 111], 'security-ciphering_order': [111, 111, 111],
                     'network_name-full': "111111", "amf_name": "111111"}
    new_yaml_data = modify_yaml(yaml_data_amf, test_dict_amf, "amf")
    #print(yaml.dump(new_yaml_data_amf))
    write_yaml("./transfers/some_folder/new_amf.yaml", new_yaml_data, overwrite=True)


def test_ausf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1111}
    yaml_data = read_yaml("./transfers/all_open5gs/ausf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "ausf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_ausf.yaml", new_yaml_data, overwrite=True)


def test_bsf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1111, 'db_uri': "mongodb://remotehost/closed2gd"}
    yaml_data = read_yaml("./transfers/all_open5gs/bsf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "bsf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_bsf.yaml", new_yaml_data, overwrite=True)


def test_hss():
    test_dict = {'db_uri': "mongodb://", "freeDiameter": "/etc/hasd"}
    yaml_data = read_yaml("./transfers/all_open5gs/hss.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "hss")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_hss.yaml", new_yaml_data, overwrite=True)


def test_mme():
    test_dict = {'freeDiameter': "/ctf", "s1ap-addr": "11.11.11.11", "gtpc-addr": "11.11.11.11",
                 "metrics-addr": "11.11.11.11", "metrics-port": 11, 'gummei-plmn_id-mcc': 11, 'gummei-plmn_id-mnc': 11,
                 'gummei-mme_gid': 11, 'gummei-mme_code': 11, 'tai-plmn_id-mcc': 11, 'tai-plmn_id-mnc': 11,
                 'tai-tac': 11, 'security-integrity_order': [11, 11, 11], 'security-ciphering_order': [11, 11, 11],
                 'network_name-full': "111111", "mme_name": "111111"}
    yaml_data = read_yaml("./transfers/all_open5gs/mme.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "mme")
    print(new_yaml_data['mme']['gummei']['plmn_id']['mcc'])
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_mme.yaml", new_yaml_data, overwrite=True)


def test_nrf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234}
    yaml_data = read_yaml("./transfers/all_open5gs/nrf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "nrf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_nrf.yaml", new_yaml_data, overwrite=True)


def test_nssf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 11, 'nsi-addr': "11.11.11.11", "nsi-port": 11,
                 'nsi-s_nssai-sst': 11}
    yaml_data = read_yaml("./transfers/all_open5gs/nssf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "nssf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_nssf.yaml", new_yaml_data, overwrite=True)


def test_pcf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234, "metrics-addr": "11.11.11.11", "metrics-port": 11}
    yaml_data = read_yaml("./transfers/all_open5gs/pcf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "pcf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_pcf.yaml", new_yaml_data, overwrite=True)


def test_pcrf():
    test_dict = {'db_uri': r'mongodb://', 'freeDiameter': r"/etc"}
    yaml_data = read_yaml("./transfers/all_open5gs/pcrf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "pcrf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_pcrf.yaml", new_yaml_data, overwrite=True)


def test_scp():
    # Most likely not needed, do not test!
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234}
    yaml_data = read_yaml("./transfers/all_open5gs/scp.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "scp")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_scp.yaml", new_yaml_data, overwrite=True)


def test_sgwc():
    test_dict = {'gtpc-addr': "11.11.11.11", 'pfcp-addr': "11.11.11.11"}
    yaml_data = read_yaml("./transfers/all_open5gs/sgwc.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "sgwc")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_sgwc.yaml", new_yaml_data, overwrite=True)


def test_sgwu():
    test_dict = {'gtpu-addr': "11.11.11.11", 'pfcp-addr': "11.11.11.11"}
    yaml_data = read_yaml("./transfers/all_open5gs/sgwu.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "sgwu")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_sgwu.yaml", new_yaml_data, overwrite=True)


def test_smf():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234, 'pfcp-addr': "11.11.11.11", 'gtpc-addr': "11.11.11.11",
                 'gtpu-addr': "11.11.11.11", 'metrics-addr': "11.11.11.11", 'metrics-port': 1234, 'dns': "11.11.11.11",
                 'mtu': 1111, 'ctf-enabled': "aaaa", 'freeDiameter': "/etc", 'subnet-addr': "11.11.11.11/11"}
    yaml_data = read_yaml("./transfers/all_open5gs/smf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "smf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_smf.yaml", new_yaml_data, overwrite=True)


def test_udm():
    # Not implemented due to complexity; we will not need it most likely any way
    pass


def test_udr():
    test_dict = {'sbi-addr': "11.11.11.11", 'sbi-port': 1234}
    yaml_data = read_yaml("./transfers/all_open5gs/udr.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "udr")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_udr.yaml", new_yaml_data, overwrite=True)


def test_upf():
    test_dict = {'pfcp-addr': "11.11.11.11", 'metrics-addr': "11.11.11.11", 'metrics-port': 1234,
                 'gtpu-addr': "11.11.11.11", 'subnet-addr': "11.11.11.11"}
    yaml_data = read_yaml("./transfers/all_open5gs/upf.yaml")
    new_yaml_data = modify_yaml(yaml_data, test_dict, "upf")
    #print(yaml.dump(new_yaml_data))
    write_yaml("./transfers/some_folder/new_upf.yaml", new_yaml_data, overwrite=True)


def main():
    # TODO - Is the lack of ability to rename standalone values in yaml files ok?
    # e.g. BSF.yaml has db_uri value as bsf: db_uri (nested), but also db_uri: (standalone)
    # Currently the way new_value dictionaries are formatted does not allow to modify db_uri standalone if there exists
    # A different version of the same value name nested. Only the nested will be updated
    # If only one exists (only nested or only standalone), there is no issue

    logging.basicConfig(filename="processing_yaml.log", level=logging.INFO)
    # All tests work
    test_amf()
    test_ausf()
    test_bsf()
    test_hss()
    test_mme()
    test_nrf()
    test_nssf()
    test_pcf()
    test_pcrf()
    test_sgwc()
    test_sgwu()
    test_smf()
    test_udr()
    test_upf()


if __name__ == "__main__":
    main()
