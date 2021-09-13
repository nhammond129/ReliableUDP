import engine.server
import shelve

class GameServer(engine.server.Server):
	database_file = 'data.db'
	def __init__(self, *args, **kwargs):
		engine.server.Server.__init__(self, *args, **kwargs)

		self.db = shelve.open(self.database_file, writeback=True)

	def __del__(self):
		self.db.close()

	def on_attack(self, attack_position):
		# Check if the attack landed near enough to hit.
		if abs(attack_position - game_state.position) < 0.1:
			self.dispatch_event("info", "Hit!", target_client=client_address)
			# Subtract the attacks damage from the enemies health.
			return {"hp": game_state.hp - 10}
		self.dispatch_event("info", "Missed.", target_client=client_address)
		return {}

def main():
	server = GameServer('localhost', 8080)
	server.run()

if __name__ == "__main__":
	main()