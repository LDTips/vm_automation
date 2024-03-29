import fabric
import test_VM_commands as vm
import yaml_processing as config
import logging
from datetime import datetime


def update_configs(c: [fabric.Connection], ip_addr: [str]) -> None:
    # Perform config file modification - Open5gs
    # Read default configs
    upf = config.read_yaml("./transfers/all_open5gs/upf.yaml")
    amf = config.read_yaml("./transfers/all_open5gs/amf.yaml")
    # Prepare modifications dicts
    upf_diff_dict = {'upf-gtpu0-addr': ip_addr[0]}
    amf_diff_dict = {'amf-ngap0-addr': ip_addr[0], 'amf-guami-plmn_id-mcc': 999, 'amf-guami-plmn_id-mnc': 99,
                     'amf-tai-plmn_id-mcc': 999, 'amf-tai-plmn_id-mnc': 99,
                     'amf-plmn_support-plmn_id-mcc': 999, 'amf-plmn_support-plmn_id-mnc': 99}
    # Modify the yaml dict
    new_upf = config.modify_yaml(upf, upf_diff_dict)
    new_amf = config.modify_yaml(amf, amf_diff_dict)
    # Write out the modified version
    config.write_yaml("./transfers/basic_test/upf.yaml", new_upf, overwrite=True)
    config.write_yaml("./transfers/basic_test/amf.yaml", new_amf, overwrite=True)

    # Perform config file modification - UERANSIM
    # Read default configs
    gnb = config.read_yaml("transfers/all_ueransim/open5gs-gnb.yaml")
    ue = config.read_yaml("transfers/all_ueransim/open5gs-ue.yaml")
    # Prepare modification dicts
    gnb_diff_dict = {'mcc': 999, 'mnc': 99, 'ngapIp': ip_addr[1], 'gtpIp': ip_addr[1], 'amfConfigs-address': ip_addr[0]}
    ue_diff_dict = {'supi': 'imsi-999990000000001', 'mcc': 999, 'mnc': 99}
    # Write out the modified version
    new_gnb = config.modify_yaml(gnb, gnb_diff_dict)
    new_ue = config.modify_yaml(ue, ue_diff_dict)
    # Write out the modified version
    config.write_yaml("./transfers/basic_test/open5gs-gnb.yaml", new_gnb, overwrite=True)
    config.write_yaml("./transfers/basic_test/open5gs-ue.yaml", new_ue, overwrite=True)

    # Transfer new configs - Open5gs
    # Open5gs configs are root only
    vm.put_file(
        c[0],
        "./transfers/basic_test/upf.yaml",
        "/etc/open5gs/upf.yaml",
        permissions="644",
        overwrite=True,
        sudo=True
    )
    vm.put_file(
        c[0],
        "./transfers/basic_test/amf.yaml",
        "/etc/open5gs/amf.yaml",
        permissions="644",
        overwrite=True,
        sudo=True
    )
    # Restart daemons to update the configuration
    vm.execute(c[0], command="systemctl restart open5gs-upfd", sudo=True)
    vm.execute(c[0], command="systemctl restart open5gs-amfd", sudo=True)
    # Transfer new configs - UERANSIM
    vm.put_file(
        c[1],
        "./transfers/basic_test/open5gs-gnb.yaml",
        f"/home/{c[1].user}/UERANSIM/config/open5gs-gnb.yaml",
        permissions="644",
        overwrite=True,
        sudo=False
    )
    vm.put_file(
        c[1],
        "./transfers/basic_test/open5gs-ue.yaml",
        f"/home/{c[1].user}/UERANSIM/config/open5gs-ue.yaml",
        permissions="644",
        overwrite=True,
        sudo=False
    )


def main():
    logging.basicConfig(filename="driver_script.log", level=logging.INFO)
    logging.info("\n--------------------------------------\n"
                 "Start log {}"
                 "\n--------------------------------------"
                 .format(datetime.now()))
    # Define connection information
    ip_addr = ["192.168.111.105", "192.168.111.110"]
    key_path_all = r"C:\Users\batru\Desktop\Keys\private_clean_ubuntu_20_clone"
    conn_dict = {ip_addr[0]: key_path_all, ip_addr[1]: key_path_all}
    # conn_dict = {"192.168.111.101": key_path_all}
    # Initialise connections to the machines
    c = []
    try:
        c = vm.init_connections(conn_dict, username="open5gs")
    except ConnectionError:
        logging.error("Received timeout error from init_connections. Driver script aborted!")
        exit(1)
    # Run install scripts
    # vm.install_sim(c[0], "open5gs")
    # vm.install_sim(c[1], "ueransim")
    # time.sleep(30)
    update_configs(c, ip_addr)


if __name__ == "__main__":
    main()
