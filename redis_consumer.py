import json, redis, logging
from datetime import datetime
from elasticsearch import Elasticsearch

K_VALUE = 5 # Lo "sweet spot" individuato nella tesi 
REDIS_QUEUE = "web_access_logs_queue"
# Puntamenti ai servizi Docker 
ES_CLIENT = Elasticsearch(["http://elasticsearch:9200"])
r = redis.Redis(host='redis', port=6379, db=0)

equivalence_classes = {}

def generalizza_ip(ip):
    parts = ip.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0" # Network Masking /24 [cite: 24]

def generalizza_timestamp(ts_str):
    try:
        dt = datetime.strptime(ts_str.split(' ')[0], "%d/%b/%Y:%H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:00:00") # Time Slotting orario [cite: 24]
    except: return "1970-01-01 00:00:00"

def process_and_anonymize(raw_event):
    global equivalence_classes
    qi_ip = generalizza_ip(raw_event.get('client_ip', ''))
    qi_ts = generalizza_timestamp(raw_event.get('timestamp', ''))
    ec_id = f"{qi_ip}|{qi_ts}"
    
    anon_record = {
        "gen_timestamp": qi_ts,
        "gen_ip": qi_ip,
        "verb": raw_event.get('verb'),
        "status": raw_event.get('status'),
        "category": raw_event.get('path', '/').split('/')[1] # Path Abstraction [cite: 24]
    }
    
    if ec_id not in equivalence_classes: equivalence_classes[ec_id] = []
    equivalence_classes[ec_id].append(anon_record)
    
    if len(equivalence_classes[ec_id]) >= K_VALUE:
        for record in equivalence_classes[ec_id]:
            ES_CLIENT.index(index="logs-anonimi", document=record)
        del equivalence_classes[ec_id] # Rilascio della classe anonimizzata [cite: 24]

def main():
    logging.info("Agent attivo. In attesa di log...")
    while True:
        msg = r.blpop(REDIS_QUEUE, timeout=5)
        if msg:
            process_and_anonymize(json.loads(msg[1]))

if __name__ == "__main__":
    main()