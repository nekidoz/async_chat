import socket as sock

import settings as sett
import jim

socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket.connect((sett.DEFAULT_SERVER_ADDRESS, sett.DEFAULT_PORT))
message = jim.Message(action=jim.Actions.PRESENCE, type="status",
                      user={
                          "account_name": "test",
                          "status": "Online"
                      }
                      )
socket.send(message.json.encode(sett.DEFAULT_ENCODING))
response = jim.Response.from_str(socket.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING))
print(f'Сообщение от сервера: ', response.json)
if response.response == jim.Responses.OK:
    print("Message acknowledged")
else:
    print(f"Unexpected return code: {response.response}")
socket.close()
