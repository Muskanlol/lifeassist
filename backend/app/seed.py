from sqlalchemy.orm import Session

from app.models import PeakHoursRule

RULES = [
    ("Western Line", "weekday", "07:30", "10:45", "Churchgate-bound locals are packed. Mira Road, Borivali and Bandra get crushed between 8:30 and 10:00."),
    ("Western Line", "weekday", "17:00", "20:30", "Evening peak towards the suburbs. Virar/Dahanu trains fill up by Andheri."),
    ("Western Line", "weekend", "10:00", "13:30", "Late-morning leisure crowd, lighter than weekdays but still busy around Bandra."),
    ("Western Line", "weekend", "17:00", "20:00", "Return-from-town weekend peak. Still better than a weekday 9am local."),
    ("Central Line", "weekday", "07:30", "10:45", "Kalyan/Kasara locals towards CST are standing-room only."),
    ("Central Line", "weekday", "17:00", "20:30", "Evening crush out of CST and Dadar towards Thane and Kalyan."),
    ("Central Line", "weekend", "10:00", "13:30", "Weekend market and travel rush, milder than weekdays."),
    ("Harbour Line", "weekday", "07:45", "10:30", "Panvel–CST corridor is busiest through Wadala and Dockyard Road."),
    ("Harbour Line", "weekday", "17:15", "20:15", "Evening peak towards Navi Mumbai."),
    ("Mumbai Metro Line 1", "weekday", "08:00", "10:30", "Versova–Ghatkopar is packed at Andheri and WEH."),
    ("Mumbai Metro Line 1", "weekday", "17:30", "20:30", "Evening peak both ways, worst at Andheri."),
    ("Mumbai Metro Line 2A", "weekday", "08:00", "10:30", "Dahisar–DN Nagar morning peak."),
    ("Mumbai Metro Line 2A", "weekday", "17:30", "20:30", "Evening peak towards Dahisar and Borivali."),
    ("Mumbai Metro Line 3", "weekday", "08:00", "10:30", "Aqua Line Bandra–Kurla–BKC stretch fills fast."),
    ("Mumbai Metro Line 3", "weekday", "17:30", "20:30", "Office return peak through BKC and Worli."),
    ("Mumbai Metro Line 7", "weekday", "08:00", "10:30", "Gundavali–Dahisar East morning peak."),
    ("Mumbai Metro Line 7", "weekday", "17:30", "20:30", "Evening peak towards Dahisar East."),
    ("Delhi Metro", "weekday", "08:00", "10:30", "Yellow, Blue and Red lines are the most crowded."),
    ("Delhi Metro", "weekday", "17:30", "20:30", "Evening office peak across the network."),
    ("Namma Metro", "weekday", "08:00", "10:30", "Purple and Green lines peak through MG Road and Majestic."),
    ("Namma Metro", "weekday", "17:30", "20:30", "Evening peak towards Whitefield and Nagasandra."),
    ("Hyderabad Metro", "weekday", "08:00", "10:30", "Red and Blue lines busy through Ameerpet."),
    ("Hyderabad Metro", "weekday", "17:30", "20:30", "Evening peak towards Hitec City and Nagole."),
    ("Chennai Metro", "weekday", "08:00", "10:30", "Morning peak on both corridors."),
    ("Chennai Metro", "weekday", "17:30", "20:30", "Evening office peak."),
    ("Kolkata Metro", "weekday", "08:00", "10:30", "North–South line is the most crowded."),
    ("Kolkata Metro", "weekday", "17:00", "20:00", "Evening peak, especially Esplanade–Kalighat."),
    ("Pune Metro", "weekday", "08:30", "10:30", "Purple and Aqua lines morning peak."),
    ("Pune Metro", "weekday", "17:30", "20:00", "Evening peak towards Pimpri and Vanaz."),
    ("Ahmedabad Metro", "weekday", "08:30", "10:30", "Morning peak on both corridors."),
    ("Ahmedabad Metro", "weekday", "17:30", "20:00", "Evening peak."),
    ("Lucknow Metro", "weekday", "08:30", "10:30", "Red Line morning peak."),
    ("Lucknow Metro", "weekday", "17:30", "20:00", "Evening peak."),
    ("Jaipur Metro", "weekday", "08:30", "10:30", "Pink Line morning peak."),
    ("Jaipur Metro", "weekday", "17:30", "20:00", "Evening peak."),
    ("Kochi Metro", "weekday", "08:30", "10:30", "Aluva–Thrippunithura morning peak."),
    ("Kochi Metro", "weekday", "17:30", "20:00", "Evening peak."),
    ("Rapid Metro Gurgaon", "weekday", "08:30", "10:30", "Cyber City feeder peak."),
    ("Rapid Metro Gurgaon", "weekday", "17:30", "20:30", "Evening office outflow."),
    ("Indian Metro", "weekday", "08:00", "10:30", "Typical Indian metro morning peak. Leave before 8:00 or after 10:30."),
    ("Indian Metro", "weekday", "17:30", "20:30", "Typical evening office peak."),
    ("Indian Metro", "weekend", "11:00", "14:00", "Weekend leisure peak, usually milder."),
    ("Suburban Railway", "weekday", "07:30", "10:45", "Suburban locals across Indian metros are most crowded in this window."),
    ("Suburban Railway", "weekday", "17:00", "20:30", "Evening suburban peak."),
    ("City Bus", "weekday", "08:00", "10:30", "City buses fill on office corridors."),
    ("City Bus", "weekday", "17:30", "20:30", "Evening bus peak. AC routes are still crowded but more predictable."),
]


def seed_peak_hours(db: Session) -> None:
    if db.query(PeakHoursRule).count() > 0:
        return
    for line_name, day_type, start_time, end_time, note in RULES:
        db.add(
            PeakHoursRule(
                line_name=line_name,
                day_type=day_type,
                start_time=start_time,
                end_time=end_time,
                note=note,
            )
        )
    db.commit()
