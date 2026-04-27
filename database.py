import sqlite3
import os

DB_PATH = 'defense_platform.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            fake_score INTEGER,
            bot_score INTEGER,
            spam_score INTEGER,
            viral_score INTEGER,
            max_threat INTEGER,
            classification TEXT,
            bot_type TEXT,
            cluster_id TEXT,
            severity TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS learned_signatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            weight INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS takedowns (
            cluster_id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_submission(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO submissions 
        (text, fake_score, bot_score, spam_score, viral_score, max_threat, classification, bot_type, cluster_id, severity, action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['text'], data['fakeScore'], data['botScore'], data['spamScore'], 
        data['viralScore'], data['maxThreat'], data['classification'], 
        data.get('botType'), data['clusterId'], data['severity'], data['actionClass']
    ))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_recent_submissions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM submissions ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def find_similar_cluster(text, threshold=0.5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, text, cluster_id FROM submissions WHERE max_threat > 50 ORDER BY timestamp DESC LIMIT 100')
    rows = c.fetchall()
    conn.close()
    
    words1 = set(text.lower().split())
    if not words1: return None
    
    for row in rows:
        db_text = row[1]
        words2 = set(db_text.lower().split())
        if not words2: continue
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        if len(union) == 0: continue
        jaccard = len(intersection) / len(union)
        if jaccard > threshold:
            return row[2] 
    return None

def add_learned_signature(keyword, weight):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO learned_signatures (keyword, weight) 
        VALUES (?, ?)
        ON CONFLICT(keyword) DO UPDATE SET weight = weight + ?
    ''', (keyword, weight, weight))
    conn.commit()
    conn.close()

def get_learned_signatures():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT keyword, weight FROM learned_signatures ORDER BY weight DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()
    return rows

def get_incidents():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT s.cluster_id, COUNT(*) as tweet_count, MAX(s.max_threat) as severity_score, MAX(s.timestamp) as last_active,
               CASE WHEN t.cluster_id IS NOT NULL THEN 'Neutralized' ELSE 'Active' END as status
        FROM submissions s
        LEFT JOIN takedowns t ON s.cluster_id = t.cluster_id
        WHERE s.cluster_id IS NOT NULL 
        GROUP BY s.cluster_id 
        ORDER BY last_active DESC 
        LIMIT 10
    ''')
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def execute_takedown(cluster_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO takedowns (cluster_id) VALUES (?)', (cluster_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
