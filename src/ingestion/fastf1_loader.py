import fastf1


def get_season_schedule(year):
    return fastf1.get_event_schedule(year, include_testing=False)


def get_event(year, round_number):
    return fastf1.get_event(year, round_number)


def get_session(year, round_number, session_type):
    session = fastf1.get_session(year, round_number, session_type)
    session.load(weather=True, messages=False)
    return session


def get_laps(session):
    return session.laps


def get_telemetry(lap):
    return lap.get_telemetry()


def get_weather(session):
    return session.laps.get_weather_data()
