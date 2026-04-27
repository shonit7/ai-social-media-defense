import random
import re
import uuid
import database

FAKE_KEYWORDS = ['breaking', 'shocking', 'unbelievable', 'secret', 'truth', 'revealed', 'conspiracy', 'scandal', 'click here', 'viral', 'mind-blowing', 'banned', 'hidden', 'hoax', 'urgent']
SPAM_KEYWORDS = ['crypto', 'giveaway', 'btc', 'eth', 'bitcoin', 'ethereum', 'buy now', 'limited time', 'invest', 'cash', 'dm me', 'whatsapp']
FACT_CHECKS = {
    'conspiracy': 'Conspiracy theories often use emotional triggers to bypass logical analysis. Verify claims through independent, peer-reviewed sources.',
    'secret': 'Claims of "hidden secrets" are common clickbait tactics to manufacture artificial urgency.',
    'crypto': 'Legitimate organizations do not guarantee returns or ask for initial cryptocurrency deposits. This is a classic hallmark of a high-yield investment scam.',
    'giveaway': 'Mass social media giveaways requiring immediate engagement or deposits are highly likely to be automated phishing attempts.',
    'hoax': 'This terminology is frequently used to discredit verified events. Cross-reference with primary sources.',
    'banned': 'Sensationalist claims about content being "banned" are designed to manipulate curiosity and bypass content moderation algorithms.',
    'truth': 'Sensationalist appeals to "the truth" often accompany unverified claims.',
    'viral': 'Content explicitly engineered to go "viral" often prioritizes engagement over factual accuracy.'
}

# Emotion Keywords
FEAR_KWS = ['banned', 'depopulate', 'scandal', 'hidden', 'secret', 'rigged', 'compromised', 'darker', 'furious']
URGENCY_KWS = ['urgent', 'breaking', 'now', 'fast', 'immediately', 'hurry', 'limited time']
JOY_KWS = ['great', 'beautiful', 'wonderful', 'happy', 'love', 'blessed', 'celebrate', 'amazing']

STOP_WORDS = set(['the', 'and', 'are', 'you', 'for', 'that', 'this', 'with', 'they', 'from', 'have'])

def analyze_text(text):
    lower_text = text.lower()
    
    # 1. Apply Learned Signatures from DB
    learned_sigs = database.get_learned_signatures()
    learned_penalty = 0
    for sig_row in learned_sigs:
        keyword, weight = sig_row[0], sig_row[1]
        if keyword in lower_text:
            learned_penalty += weight
    
    fake_score = random.randint(5, 15)
    bot_score = random.randint(5, 15)
    spam_score = random.randint(0, 10)
    viral_score = 0
    
    found_fake = []
    found_spam = []
    fact_checks = []
    
    for kw in FAKE_KEYWORDS:
        if kw in lower_text:
            fake_score += 35
            viral_score += 30
            found_fake.append(kw)
            if kw in FACT_CHECKS:
                has_check = any(c['misleadingQuote'] == kw for c in fact_checks)
                if not has_check:
                    fact_checks.append({
                        "misleadingQuote": f'...{kw}...',
                        "counterMessage": FACT_CHECKS[kw],
                        "confidenceScore": random.randint(88, 99)
                    })
                
    for kw in SPAM_KEYWORDS:
        if kw in lower_text:
            spam_score += 40
            found_spam.append(kw)
            if kw in FACT_CHECKS:
                has_check = any(c['misleadingQuote'] == kw for c in fact_checks)
                if not has_check:
                    fact_checks.append({
                        "misleadingQuote": f'...{kw}...',
                        "counterMessage": FACT_CHECKS[kw],
                        "confidenceScore": random.randint(85, 95)
                    })
                
    hashtag_count = lower_text.count('#')
    if hashtag_count > 2:
        bot_score += (hashtag_count * 15)
        spam_score += (hashtag_count * 5)
        
    exclamation_count = lower_text.count('!')
    if exclamation_count > 2:
        viral_score += (exclamation_count * 12)
        fake_score += 15
        
    upper_chars = len(re.findall(r'[A-Z]', text))
    total_letters = len(re.findall(r'[a-zA-Z]', text))
    upper_ratio = upper_chars / total_letters if total_letters > 0 else 0
    
    if total_letters > 10 and upper_ratio > 0.4:
        fake_score += 20
        bot_score += 25
        viral_score += 20

    # Add dynamically learned penalties
    fake_score += learned_penalty
    bot_score += int(learned_penalty * 0.5)

    fake_score = min(fake_score, 99)
    bot_score = min(bot_score, 99)
    spam_score = min(spam_score, 99)
    viral_score = min(viral_score, 99)
    
    max_threat = max(fake_score, bot_score, spam_score)
    trust_score = 100 - max_threat
    
    # Emotional Vector Calculation
    emotion_scores = {"Fear": 0, "Urgency": 0, "Joy": 0, "Neutral": 10}
    for kw in FEAR_KWS:
        if kw in lower_text: emotion_scores["Fear"] += 25
    for kw in URGENCY_KWS:
        if kw in lower_text: emotion_scores["Urgency"] += 25
    for kw in JOY_KWS:
        if kw in lower_text: emotion_scores["Joy"] += 20
        
    dominant_emotion = "Neutral"
    max_e_score = 10
    for e, val in emotion_scores.items():
        if val > max_e_score:
            dominant_emotion = e
            max_e_score = val
    
    bot_confidence = min(99, bot_score + (spam_score * 0.4))
    classification = "HUMAN"
    bot_type = None
    
    if bot_confidence > 75:
        classification = "BOT ENTITY"
        if spam_score > fake_score: bot_type = "Commercial Spam Bot"
        elif fake_score > spam_score: bot_type = "Propaganda Bot"
        else: bot_type = "Engagement Farming Bot"
    elif max_threat > 45:
        classification = "SUSPICIOUS"
        
    # Deepfake Mutation Tracker / Cluster Match
    cluster_id = database.find_similar_cluster(text)
    is_cluster = cluster_id is not None
    
    if is_cluster:
        spam_score = max(spam_score, 85)
        bot_score = max(bot_score, 80)
        max_threat = max(fake_score, bot_score, spam_score)
        trust_score = 100 - max_threat
    elif max_threat > 50:
        cluster_id = "C-" + str(uuid.uuid4())[:8].upper()
        
    severity = "Critical" if max_threat > 80 else "High" if max_threat > 50 else "Medium" if max_threat > 30 else "Low"
    
    action_class = "defense-allow"
    action_text = "SAFE : ALLOW"
    
    if max_threat >= 80 or is_cluster:
        action_class = "defense-blocked"
        action_text = "HIGH RISK : BLOCKED"
    elif spam_score > 50 or bot_score > 50:
        action_class = "defense-quarantined"
        action_text = "SPAM/BOT : QUARANTINED"
    elif fake_score > 50:
        action_class = "defense-flagged"
        action_text = "FAKE NEWS : FLAGGED"
        
    # Self-Evolving Rule Extraction
    if max_threat > 80:
        words = re.findall(r'\b[a-z]{5,}\b', lower_text)
        for w in words:
            if w not in STOP_WORDS and w not in FAKE_KEYWORDS and w not in SPAM_KEYWORDS:
                # We found a new potential signature in a confirmed high-threat payload
                database.add_learned_signature(w, 2)
                
    # Generate Network Spread Data
    uncontained_nodes = []
    uncontained_edges = []
    contained_nodes = []
    contained_edges = []
    
    containment_effect = 0
    estimated_reach = 0
    spread_intensity = "Low"
    
    if viral_score > 80: spread_intensity = "Critical"
    elif viral_score > 50: spread_intensity = "High"
    elif viral_score > 20: spread_intensity = "Medium"
    
    if is_cluster or max_threat > 50:
        origin_id = 1
        node_shape = "star"
        uncontained_nodes.append({"id": origin_id, "label": "Origin", "color": "#ff0000", "shape": node_shape, "size": 30})
        contained_nodes.append({"id": origin_id, "label": "Origin", "color": "#ff0000", "shape": node_shape, "size": 30})
        
        num_spreaders = min(max(3, int(viral_score / 3)), 30)
        estimated_reach = num_spreaders * random.randint(500, 5000)
        
        neutralized_count = 0
        for i in range(2, num_spreaders + 2):
            label = f"Bot_{i}" if classification == "BOT ENTITY" else f"User_{i}"
            
            # Uncontained simulation (everything goes viral)
            unc_color = "#ff3333" if random.random() > 0.5 else "#ffb800"
            uncontained_nodes.append({"id": i, "label": label, "color": unc_color})
            
            # Contained simulation
            con_color = "#ffb800" if random.random() > 0.3 else "#00ff66" 
            if action_class == "defense-blocked" and random.random() > 0.2: 
                con_color = "#555555" # Blocked spread simulation
                neutralized_count += 1
            elif action_class == "defense-quarantined" and random.random() > 0.5:
                con_color = "#555555"
                neutralized_count += 1
                
            contained_nodes.append({"id": i, "label": label, "color": con_color})
            
            target = 1 if random.random() > 0.7 else random.randint(1, i-1)
            uncontained_edges.append({"from": target, "to": i})
            contained_edges.append({"from": target, "to": i})
            
        containment_effect = int((neutralized_count / num_spreaders) * 100) if num_spreaders > 0 else 0
    else:
        estimated_reach = random.randint(10, 100)
        uncontained_nodes.append({"id": 1, "label": "User", "color": "#00ff66", "shape": "dot", "size": 20})
        contained_nodes.append({"id": 1, "label": "User", "color": "#00ff66", "shape": "dot", "size": 20})
        
    result = {
        "text": text,
        "fakeScore": fake_score,
        "botScore": bot_score,
        "spamScore": spam_score,
        "viralScore": viral_score,
        "maxThreat": max_threat,
        "trustScore": trust_score,
        "botConfidence": bot_confidence,
        "classification": classification,
        "botType": bot_type,
        "clusterId": cluster_id,
        "isCluster": is_cluster,
        "severity": severity,
        "actionClass": action_class,
        "actionText": action_text,
        "foundFake": found_fake,
        "foundSpam": found_spam,
        "emotion": dominant_emotion,
        "factChecks": fact_checks,
        "containmentEffect": containment_effect,
        "estimatedViralReach": estimated_reach,
        "spreadIntensity": spread_intensity,
        "network": {
            "uncontained": {"nodes": uncontained_nodes, "edges": uncontained_edges},
            "contained": {"nodes": contained_nodes, "edges": contained_edges}
        }
    }
    
    database.insert_submission(result)
    return result

def get_stats():
    rows = database.get_recent_submissions(100)
    stats = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "total": len(rows), "blocked": 0}
    for r in rows:
        if r['severity'] in stats: stats[r['severity']] += 1
        if r['action'] == 'defense-blocked': stats['blocked'] += 1
    return stats
