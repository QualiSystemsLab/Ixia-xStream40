from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource,  AutoLoadAttribute, AutoLoadDetails
from cloudshell.api.cloudshell_api import CloudShellAPISession
import paramiko
import re
import json
import sys

class IxiaxstreamDriver (ResourceDriverInterface):

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def restore(self, context, config, config_type, restore_method, vrf):
        """
        Restores a configuration file
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str configfile: The path to the configuration file, including the configuration file name.
        :param str config_type: Specify whether the file should update the startup or running config.
        :param str restore_method: Determines whether the restore should append or override the current configuration.
        :param str vrf: Optional. Virtual routing and Forwarding management name
        """
        pass

    def save(self, context, configfolder, config_type, vrf):
        """
        Creates a configuration file and saves it to the provided destination
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str config_type: Specify whether the file should update the startup or running config. Value can one
        :param str configfolder: The path to the folder in which the configuration file will be saved.
        :param str vrf: Optional. Virtual routing and Forwarding management name
        :return The configuration file name.
        :rtype: str
        """
        pass

    def load_firmware(self, context, remote_host, file_path):
        """
        Upload and updates firmware on the resource
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str remote_host: path to tftp server where firmware file is stored
        :param str file_path: firmware file name
        """
        pass

    def send_custom_command(self, context, command):
        """
        Executes a custom command on the device
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str command: The command to run. Note that commands that require a response are not supported.
        :return: result
        :rtype: str
        """
        pass

    def send_custom_config_command(self, context, command):
        """
        Executes a custom command on the device in configuration mode
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str command: The command to run. Note that commands that require a response are not supported.
        :return: result
        :rtype: str
        """
        pass

    def shutdown(self, context):
        """
        Sends a graceful shutdown to the device
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        """
        pass

    # The ApplyConnectivityChanges function is intended to be used for using switches as connectivity providers
    # for other devices. If the Switch shell is intended to be used a DUT only there is no need to implement it

    # def ApplyConnectivityChanges(self, context, request):
    #     """
    #     Configures VLANs on multiple ports or port-channels
    #     :param ResourceCommandContext context: The context object for the command with resource and reservation info
    #     :param str request: A JSON object with the list of requested connectivity changes
    #     :return: a json object with the list of connectivity changes which were carried out by the switch
    #     :rtype: str
    #     """
    #
    #     pass


    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource
        :rtype: AutoLoadDetails
        """

        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain="Global")

        pw = session.DecryptPassword(context.resource.attributes['Password']).Value
        un = context.resource.attributes["User"]

        sub_resources = []
        attributes = [AutoLoadAttribute('', 'Model', 'xStream40'),AutoLoadAttribute('', 'Vendor', 'Ixia')]

        cmd = "show port"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(context.resource.address, username=un, password=pw,allow_agent=False,look_for_keys=False)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

        lines = ssh_stdout.readlines()
        p = re.compile(ur'^\s*[0-9]*\s*P')

        for l in lines:
            # check if it is a line with port
            if re.search(p, l) is not None:
                cols = re.split('\s{2,}', l.strip())
                if re.search(p, l) is not None:
                    cols = re.split('\s{2,}', l.strip())
                    if (cols[0] != "Port Name"):
                        speed = cols[5]
                        if speed == "keep":
                            speed = cols[4]
                        sub_resources.append(AutoLoadResource(model='Packet Broker Port Port', name=cols[1], relative_address=str(cols[0])))
                        attributes.append(AutoLoadAttribute(str(cols[0]), 'Port Speed', speed))


        ssh.close()
        return AutoLoadDetails(sub_resources,attributes)
        pass

    def ApplyConnectivityChanges(self, context, request):
        """
        Configures VLANs on multiple ports or port-channels
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str request: A JSON object with the list of requested connectivity changes
        :return: a json object with the list of connectivity changes which were carried out by the switch
        :rtype: str
        """
        """
        :type context: drivercontext.ResourceCommandContext
        :type json: str
        """
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain="Global")

        requestJson = json.loads(request)


        #Build Response
        response = {"driverResponse":{"actionResults":[]}}

        pair = []
        previousCid = ""

        for actionResult in requestJson['driverRequest']['actions']:
            actionResultTemplate = {"actionId":None, "type":None, "infoMessage":"", "errorMessage":"", "success":"True", "updatedInterface":"None"}
            actionResultTemplate['type'] = str(actionResult['type'])
            actionResultTemplate['actionId'] = str(actionResult['actionId'])
            response["driverResponse"]["actionResults"].append(actionResultTemplate)

            # now for the crazy... the actions array is in pairs of endpoints, not a line/connection. so pack them up together
            cid = actionResult["connectionId"]

            #if its the same cid, add to the pair list
            # if not the same, must be a new connector
            if previousCid != cid:

                previousCid = cid
                pair = [actionResult["actionTarget"]["fullName"]]

            else:
                pair.append(actionResult["actionTarget"]["fullName"])
                # check if not first run
                if len(pair) == 2:
                    src = str(pair[0])
                    dst = str(pair[1])

                # make connector
                if (str(actionResult['type']) == "setVlan"):
                    # add
                    pw = session.DecryptPassword(context.resource.attributes['Password']).Value
                    un = context.resource.attributes["User"]
                    cmd = "config"

                    session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Adding " + src + " to " + dst)

                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(context.resource.address, username=un, password=pw,allow_agent=False,look_for_keys=False)

                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                        cmd = "map add in_ports "+src+" out_ports " + dst
                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                        session.WriteMessageToReservationOutput(context.reservation.reservation_id, ssh_stdout.readlines())
                    except:
                       session.WriteMessageToReservationOutput(context.reservation.reservation_id,"Unexpected error: " + str(sys.exc_info()[0]))
                elif (str(actionResult['type']) == "removeVlan"):
                    # remove
                    session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Removing " + src + " to " + dst)
                else:
                    session.WriteMessageToReservationOutput(context.reservation.reservation_id, "huh?")

        ssh.close()
        return 'command_json_result=' + str(response) + '=command_json_result_end'

        pass