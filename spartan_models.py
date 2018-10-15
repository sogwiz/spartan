class Race:
    subevent_id = 0
    race_id = 0
    event_id = 0

    def __init__(self, race_id, event_id, subevent_id):
        self.race_id = race_id
        self.event_id = event_id
        self.subevent_id = subevent_id

    def __str__(self):
        return str(self.event_id) + "_" + str(self.subevent_id) + "_" + str(self.race_id)