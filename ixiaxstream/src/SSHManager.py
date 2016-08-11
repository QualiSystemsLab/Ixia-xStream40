import paramiko
import re
import time
import traceback

class SSHManager:
    def __init__(self, username, password, host, port=22,
                 timeout=60, newline='\r', buffer_size=1024):
        self._handler = paramiko.SSHClient()
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._newline = newline
        self._timeout = timeout

        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self._username = username
        self._password = password

        self._host = host
        self._port = port

        self._timeout = timeout
        self._newline = newline
        self._buffer_size = buffer_size

        self._current_channel = None

        more_line_re_str = '-- {0,1}more {0,1}--'
        self._more_line_pattern = re.compile(more_line_re_str, re.IGNORECASE)

    def __del__(self):
        self.disconnect()

    def connect(self, re_string=''):
        self._current_channel = None

        try:
            self._handler.connect(self._host, self._port,
                                  self._username, self._password, banner_timeout=self._timeout,
								  allow_agent=False,look_for_keys=False)

            self._current_channel = self._handler.invoke_shell()
            output = self._readOutBuffer(re_string)

        except Exception, err:
            error_str = "Exception: " + str(err) + '\n'

            error_str += '-' * 60 + '\n'
            error_str += traceback.format_exc()
            error_str += '-' * 60

            raise Exception('SSH Manager', error_str)

        return output

    def disconnect(self):
        self._current_channel = None

        self._handler.close()

    @staticmethod
    def hasEscapeChars(str_data):
        return re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', str_data)

    @staticmethod
    def replaceEscapeChars(str_data):
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', str_data)

    def sendCommand(self, command, re_string='', timeout=None):
        """
        Method for sending data to ssl socket connection
        command - string value of command in command line (if command == '' than not send data)
        end_string - string value of ending of out stream (if end_string == '' than not read data)
        timeout - float value (if default value - than used self._timeout) of seconds
        """

        if (self._current_channel == None):
            self._reconnect()

        timeout = timeout if timeout else self._timeout
        self._current_channel.settimeout(timeout)

        for retry in range(3):
            out_buffer=''
            if command != None:
                try:
                    self._current_channel.send(command + self._newline)
                except socket_error as serr:
                    self._reconnect()

                    self._current_channel.send(command + self._newline)

            out_buffer = self._readOutBuffer(re_string)

            if not SSHManager.hasEscapeChars(out_buffer):
                break

        return SSHManager.replaceEscapeChars(out_buffer)

    def _readOutBuffer(self, re_string=''):
        input_buffer = ''
        if re_string != '':
            try:
                if isinstance(re_string, unicode):
                    re_string = self._shieldString(re_string)

                pattern = re.compile(re_string)
                while not pattern.search(input_buffer):
                    response = self._current_channel.recv(self._buffer_size)
                    if len(response) == 0:
                        break

                    more_match = self._more_line_pattern.search(response)
                    if more_match is not None:
                        self._current_channel.send(self._newline)
                        more_pos = more_match.span()
                        response = response[0:more_pos[0]] + response[more_pos[1]:]
                    input_buffer += response

            except Exception, err:
                error_str = "Exception: " + str(err) + '\n'
                import traceback, sys
                error_str += '-' * 60 + '\n'
                error_str += traceback.format_exc()
                error_str += '-' * 60

        else:
            response_tuple = self._readRecvData()

            input_buffer += response_tuple[0]
            while len(response_tuple[0]) == self._buffer_size or response_tuple[1] != None:
                response_tuple = self._readRecvData()
                input_buffer += response_tuple[0]
        return self._clearColors(input_buffer)

    def _readRecvData(self):
        response = self._current_channel.recv(self._buffer_size)

        more_match = self._more_line_pattern.search(response)
        if more_match is not None:
            self._current_channel.send(self._newline)
            more_pos = more_match.span()
            response = response[0:more_pos[0]] + response[more_pos[1]:]

        return (response, more_match)

    def _reconnect(self):
        retries_count = 5
        self._current_channel = None
        while retries_count > 0 and self._current_channel is None:
            try:
                hkeys = self._handler.get_host_keys()
                hkeys.clear()

                self._handler.load_system_host_keys()
                self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self.connect()
            except Exception, err:
                pass

            retries_count -= 1
            if self._current_channel is None:
                time.sleep(3)

        if self._current_channel is None:
            raise Exception('SSH Manager', "Can't connect to server!")

    def _shieldString(self, data_str):
        iter_object = re.finditer('[\{\}\(\)\[\]\|]', data_str)

        list_iter = list(iter_object)
        iter_size = len(list_iter)
        iter_object = iter(list_iter)

        new_data_str = ''
        current_index = 0

        if iter_size == 0:
            new_data_str = data_str

        for match in iter_object:
            is_found = True
            match_range = match.span()

            new_data_str += data_str[current_index:match_range[0]] + '\\'
            new_data_str += data_str[match_range[0]:match_range[0] + 1]

            current_index = match_range[0] + 1

        return new_data_str

    def _clearColors(self, input_buffer):
        color_pattern = re.compile('\[([0-9]+;)*[0-9]+m|\[[0-9]+m|\[[A-Z]{0,1}m*|\b|' + chr(27))

        result_buffer = ''
        match_iter = color_pattern.finditer(input_buffer)

        current_index = 0
        for match_color in match_iter:
            match_range = match_color.span()
            result_buffer += input_buffer[current_index:match_range[0]]
            current_index = match_range[1]

        result_buffer += input_buffer[current_index:]

        return result_buffer.replace('\n',"")
