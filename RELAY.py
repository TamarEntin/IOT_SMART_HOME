import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
from mqtt_init import *

# Creating Client name - should be unique
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id-"+str(r)
relay_topic = 'pr/home/AquaAlert/relay/'+str(r)
global ON
ON = False

class Mqtt_client():

    def __init__(self):
        # broker IP adress:
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self,value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self,value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self,value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self,value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self,value):
        self.password = value

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self,value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self,value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self,value):
        self.publishMessage = value


    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))

    def is_valid_temperature(self, temperature_value):
        if temperature_value < temperature_threshold_min or temperature_value > temperature_threshold_max:
            return False
        return True

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)

        if m_decode.startswith("ALERT"):
            # Check if the temperature is out of range
            temperature_range_str = "Temperature value"
            if temperature_range_str in m_decode:
                temp_value_str = m_decode.split(temperature_range_str)[1].split()[0].strip("()°C")
                try:
                    temperature_value = float(temp_value_str)
                except ValueError:
                    print(f"Error: Unable to convert '{temp_value_str}' to float")
                    return

                print(f"Temperature value: {temperature_value}")  # Debugging print statement

                if not self.is_valid_temperature(temperature_value):
                    print("Updating button state: temperature_alert=True")  # Debugging print statement
                    mainwin.connectionDock.update_btn_state(temperature_alert=True)
                else:
                    print("Updating button state: temperature_alert=False")  # Debugging print statement
                    mainwin.connectionDock.update_btn_state(temperature_alert=False)
            else:
                print("Updating button state: temperature_alert=False")  # Debugging print statement
                mainwin.connectionDock.update_btn_state(temperature_alert=False)

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance
        self.client.on_connect = self.on_connect  #bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)     #connect to broker

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        self.client.subscribe(topic)

    def publish_to(self, topic, message):
        self.client.publish(topic,message)

class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)

        self.connected = False

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName=QLineEdit()
        self.eUserName.setText(username)

        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL=QCheckBox()

        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn=QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.eSubscribeTopic=QLineEdit()
        self.eSubscribeTopic.setText(relay_topic)

        self.ePushtbtn=QPushButton("", self)
        self.ePushtbtn.setToolTip("Push me")
        self.ePushtbtn.setStyleSheet("background-color: gray")

        formLayot=QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Sub topic", self.eSubscribeTopic)
        formLayot.addRow("Status", self.ePushtbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Relay for temperature")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        if not self.connected:
            self.mc.set_broker(self.eHostInput.text())
            self.mc.set_port(int(self.ePort.text()))
            self.mc.set_clientName(self.eClientID.text())
            self.mc.set_username(self.eUserName.text())
            self.mc.set_password(self.ePassword.text())
            self.mc.connect_to()
            self.mc.start_listening()
            self.mc.subscribe_to(self.eSubscribeTopic.text())
            self.mc.subscribe_to(warning_topic)

            self.connected = True
            self.eConnectbtn.setText("Disable/Disconnect")
            self.eConnectbtn.setStyleSheet("background-color: green")

        else:
            self.mc.stop_listening()
            self.mc.disconnect_from()

            self.connected = False
            self.eConnectbtn.setText("Enable/Connect")
            self.eConnectbtn.setStyleSheet("background-color: red")

    def update_btn_state(self, temperature_alert=False):
        if temperature_alert:
            self.ePushtbtn.setStyleSheet("background-color: red")

        else:
            self.ePushtbtn.setStyleSheet("background-color: gray")


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc=Mqtt_client()

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 300, 370, 150)
        self.setWindowTitle('RELAY')

        # Init QDockWidget objects
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

app = QApplication(sys.argv)

stylesheet = """
    QMainWindow {
        background-color: #DFFDFF;
    }
    QLineEdit {
        border: 1px solid #C0C0C0;
        padding: 5px;
    }
    QPushButton {
        background-color: #6E9FEC;
        color: white;
        padding: 6px 12px;
        text-align: center;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5683D3;
    }
    QLabel {
        font-size: 14px;
        font-family: "Segoe UI";
    }

"""
app.setStyleSheet(stylesheet)

mainwin = MainWindow()
mainwin.show()
app.exec_()
