from src.ingestion.fastf1_loader import get_session
from src.ingestion.raw_writer import save_dataframe

session = get_session(2022, 1, "R")

save_dataframe(session.results, ...)
save_dataframe(session.laps, ...)
save_dataframe(session.laps.get_weather_data(), ...)
