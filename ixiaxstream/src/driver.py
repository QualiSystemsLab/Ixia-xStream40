from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource,  AutoLoadAttribute, AutoLoadDetails
from cloudshell.api.cloudshell_api import CloudShellAPISession
import json

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
        # # Add sub resources details
        # sub_resources = [ AutoLoadResource(model ='Generic Chassis',name= 'Chassis 1', relative_address='1'),
        # AutoLoadResource(model='Generic Module',name= 'Module 1',relative_address= '1/1'),
        # AutoLoadResource(model='Generic Port',name= 'Port 1', relative_address='1/1/1'),
        # AutoLoadResource(model='Generic Port', name='Port 2', relative_address='1/1/2'),
        # AutoLoadResource(model='Generic Power Port', name='Power Port', relative_address='1/PP1')]
        #
        #
        # attributes = [ AutoLoadAttribute(relative_address='', attribute_name='Location', attribute_value='Santa Clara Lab'),
        #                AutoLoadAttribute('', 'Model', 'Catalyst 3850'),
        #                AutoLoadAttribute('', 'Vendor', 'Cisco'),
        #                AutoLoadAttribute('1', 'Serial Number', 'JAE053002JD'),
        #                AutoLoadAttribute('1', 'Model', 'WS-X4232-GB-RJ'),
        #                AutoLoadAttribute('1/1', 'Model', 'WS-X4233-GB-EJ'),
        #                AutoLoadAttribute('1/1', 'Serial Number', 'RVE056702UD'),
        #                AutoLoadAttribute('1/1/1', 'MAC Address', 'fe80::e10c:f055:f7f1:bb7t16'),
        #                AutoLoadAttribute('1/1/1', 'IPv4 Address', '192.168.10.7'),
        #                AutoLoadAttribute('1/1/2', 'MAC Address', 'te67::e40c:g755:f55y:gh7w36'),
        #                AutoLoadAttribute('1/1/2', 'IPv4 Address', '192.168.10.9'),
        #                AutoLoadAttribute('1/PP1', 'Model', 'WS-X4232-GB-RJ'),
        #                AutoLoadAttribute('1/PP1', 'Port Description', 'Power'),
        #                AutoLoadAttribute('1/PP1', 'Serial Number', 'RVE056702UD')]
        #
        # return AutoLoadDetails(sub_resources,attributes)
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


        for actionResult in requestJson['driverRequest']['actions']:
            actionResultTemplate = {"actionId":None, "type":None, "infoMessage":"", "errorMessage":"", "success":"True", "updatedInterface":"None"}
            actionResultTemplate['type'] = str(actionResult['type'])
            actionResultTemplate['actionId'] = str(actionResult['actionId'])
            response["driverResponse"]["actionResults"].append(actionResultTemplate)



        return 'command_json_result=' + str(response) + '=command_json_result_end'

        pass