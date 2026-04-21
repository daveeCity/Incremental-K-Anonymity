import re, sqlite3, json, os, logging, hashlib
import redis

# Configurazione tramite variabili d'ambiente per Docker
LOG_DIRECTORY = "./logs_kaggle/" 
REDIS_HOST = os.getenv("REDIS_HOST", "redis") # Puntamento al servizio Docker 
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_QUEUE_NAME = "web_access_logs_queue"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

LOG_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<ts>.*?)\] "(?P<verb>\w+) (?P<path>.*?) HTTP/\d\.\d" (?P<status>\d{3}) (?P<size>\d+|-)'
    r'(?: "(?P<referer>.*?)" "(?P<ua>.*?)")?'
)

def parse_log_line(line):
    m = LOG_PATTERN.search(line)
    if not m: return None
    data = m.groupdict()
    return {
        "timestamp": data.get('ts'),
        "client_ip": data.get('ip'),
        "verb": data.get('verb'),
        "path": data.get('path'),
        "status": int(data.get('status', 200)),
        "size": int(data['size']) if data['size'] != '-' else 0,
        "raw_message": line.rstrip("\n")
    }

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    # Esempio di processamento file singolo
    log_file = os.path.join(LOG_DIRECTORY, "access_test.log")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                entry = parse_log_line(line)
                if entry:
                    r.rpush(REDIS_QUEUE_NAME, json.dumps(entry))
        logging.info("Logs inviati a Redis con successo.")

if __name__ == "__main__":
    main()