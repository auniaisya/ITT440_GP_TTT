import socket
from sys import argv

class TTTClient:
	def __init__(self):
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

	def connect(self, address, port_number):
		while True:
			try:
				print("Connecting to the game server...");
				self.client_socket.settimeout(10);
				self.client_socket.connect((address, int(port_number)));
				return True;
			except:
				print("There is an error when trying to connect to " + 
					str(address) + "::" + str(port_number));
				self.__connect_failed__();
		return False;

	def __connect_failed__(self):
		choice = input("[A]bort, [C]hange address and port, or [R]etry?");
		if(choice.lower() == "a"):
			exit();
		elif(choice.lower() == "c"):
			address = input("Please enter the address:");
			port_number = input("Please enter the port:");

	def s_send(self, command_type, msg):
		try:
			self.client_socket.send((command_type + msg).encode());
		except:
			# If any error occurred, the connection might be lost
			self.__connection_lost();

	def s_recv(self, size, expected_type):
		try:
			msg = self.client_socket.recv(size).decode();
			if(msg[0] == "Q"):
				why_quit = "";
				try:
					why_quit = self.client_socket.recv(1024).decode();
				except:
					pass;
				print(msg[1:] + why_quit);
				raise Exception;
			elif(msg[0] == "E"):
				self.s_send("e", msg[1:]);
				return self.s_recv(size, expected_type);
			elif(msg[0] != expected_type):
				print("The received command type \"" + msg[0] + "\" does not " + 
					"match the expected type \"" + expected_type + "\".");
				self.__connection_lost();
			elif(msg[0] == "I"):
				return int(msg[1:]);
			else:
				return msg[1:];
			return msg;
		except:
			self.__connection_lost();
		return None;

	def __connection_lost(self):
		print("Error: connection lost.");
		try:
			self.client_socket.send("q".encode());
		except:
			pass;
		raise Exception;

	def close(self):	
		self.client_socket.shutdown(socket.SHUT_RDWR);
		self.client_socket.close();

class TTTClientGame(TTTClient):
	def __init__(self):
		TTTClient.__init__(self);

	def start_game(self):
		self.player_id = int(self.s_recv(128, "A"));
		self.s_send("c","1");

		self.__connected__();

		self.role = str(self.s_recv(2, "R"));
		self.s_send("c","2");

		self.match_id = int(self.s_recv(128, "I"));
		self.s_send("c","3");

		print(("You are now matched with player " + str(self.match_id) 
			+ "\nYou are the \"" + self.role + "\""));
		self.__game_started__();
		self.__main_loop();

	def __connected__(self):
		print("Welcome to Tic Tac Toe online, player " + str(self.player_id) 
			+ "\nPlease wait for another player to join the game...");

	def __game_started__(self):
		return;

	def __main_loop(self):
		while True:
			board_content = self.s_recv(10, "B");
			command = self.s_recv(2, "C");
			self.__update_board__(command, board_content);

			if(command == "Y"):
				self.__player_move__(board_content);
			elif(command == "N"):
				self.__player_wait__();
				move = self.s_recv(2, "I");
				self.__opponent_move_made__(move);
			elif(command == "D"):
				print("It's a draw.");
				break;
			elif(command == "W"):
				print("You WIN!");
				self.__draw_winning_path__(self.s_recv(4, "P"));
				break;
			elif(command == "L"):
				print("You lose.");
				self.__draw_winning_path__(self.s_recv(4, "P"));
				break;
			else:
				print("Error: unknown message was sent from the server");
				break;

	def __update_board__(self, command, board_string):
		if(command == "Y"):
			print("Current board:\n" + TTTClientGame.format_board(
				TTTClientGame.show_board_pos(board_string)));
		else:
			print("Current board:\n" + TTTClientGame.format_board(
				board_string));

	def __player_move__(self, board_string):
		while True:
			try:
				position = int(input('Please enter the position (1~9):'));
			except:
				print("Invalid input.");
				continue;

			if(position >= 1 and position <= 9):
				if(board_string[position - 1] != " "):
					print("That position has already been taken." + 
						"Please choose another one.");
				else:
					break;
			else:
				print("Please enter a value between 1 and 9 that" + 
					"corresponds to the position on the grid board.");
		self.s_send("i", str(position));

	def __player_wait__(self):
		print("Waiting for the other player to make a move...");

	def __opponent_move_made__(self, move):
		print("Your opponent took up number " + str(move));

	def __draw_winning_path__(self, winning_path):
		readable_path = "";
		for c in winning_path:
			readable_path += str(int(c) + 1) + ", "
		print("The path is: " + readable_path[:-2]);


	def show_board_pos(s):
		new_s = list("123456789");
		for i in range(0, 8):
			if(s[i] != " "):
				new_s[i] = s[i];
		return "".join(new_s);

	def format_board(s):
		if(len(s) != 9):
			print("Error: there should be 9 symbols.");
			raise Exception;

		#print("|1|2|3|");
		#print("|4|5|6|");
		#print("|7|8|9|");
		return("|" + s[0] + "|" + s[1]  + "|" + s[2] + "|\n" 
			+ "|" + s[3] + "|" + s[4]  + "|" + s[5] + "|\n" 
			+ "|" + s[6] + "|" + s[7]  + "|" + s[8] + "|\n");

def main():
	if(len(argv) >= 3):
		address = argv[1];
		port_number = argv[2];
	else:
		address = input("Please enter the address:");
		port_number = input("Please enter the port:");

	client = TTTClientGame();
	client.connect(address, port_number);
	try:
		client.start_game();
	except:
		print(("Game finished unexpectedly!"));
	finally:
		client.close();

if __name__ == "__main__":
	main();
 
