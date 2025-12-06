#!/usr/bin/env python3
"""
Convert questions.csv to quiz-config.json structure
Preserves intro/outro slides and generates all rounds with questions from CSV
"""

import csv
import json
import sys

def parse_csv_to_rounds(csv_path):
    """Parse CSV and organize questions by round"""
    rounds = {1: [], 2: [], 4: [], 5: []}
    current_round = None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if this is a round header
            if row['question'].startswith('ROUND '):
                round_text = row['question'].split()
                if 'BONUS' in round_text:
                    current_round = f"{round_text[1]}_BONUS"
                else:
                    current_round = int(round_text[1])
                continue

            # Skip empty rows
            if not row['question'] or not row['question'].strip():
                continue

            # Add question to current round
            if current_round:
                rounds.setdefault(current_round, []).append(row)

    return rounds

def create_mcq_question(row, round_num, q_num):
    """Create MCQ question slide from CSV row"""
    # Map answer letter to index
    answer_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    correct_index = answer_map.get(row['answer'].strip().upper(), 0)

    return {
        "id": f"r{round_num}-q{q_num}",
        "type": "question-mcq",
        "round": round_num,
        "questionNumber": q_num,
        "questionText": row['question'],
        "options": [
            row['A'],
            row['B'],
            row['C'],
            row['D']
        ],
        "correctOptionIndex": correct_index,
        "timerSeconds": 30
    }

def create_bonus_question(row, round_num, bonus_num):
    """Create bonus (free-text) question from CSV row"""
    question_id = f"r{round_num}-bonus{bonus_num}"

    # Extract question text and answer from the CSV format
    question_text = row['question'].strip().strip('"')
    answer_text = row['A'].strip()

    # Bonus question type is in the 'difficulty' column for bonus questions
    question_type = row.get('difficulty', '').strip()

    if 'Guess' in question_type:  # "Guess Song" or "Guess song"
        # Extract answer from column A which has format "GUEST/GUESS ARTIST/SONG: ..."
        if 'GUEST ARTIST/SONG:' in answer_text:
            answer_text = answer_text.split('GUEST ARTIST/SONG:', 1)[1].strip()
        elif 'GUESS ARTIST/SONG:' in answer_text:
            answer_text = answer_text.split('GUESS ARTIST/SONG:', 1)[1].strip()
        instructions = "Write the song name and artist\n1 point each!"
    elif 'Christmas' in question_type:  # "Christmas Q." or "Christmas Q"
        # Extract answer from column A which has format "FILL BLANK. Answer: ..."
        if 'FILL BLANK. Answer:' in answer_text:
            answer_text = answer_text.split('FILL BLANK. Answer:', 1)[1].strip()
        elif 'Answer:' in answer_text:
            answer_text = answer_text.split('Answer:', 1)[1].strip()
        instructions = "Write the answer!\n2 points!"
    else:
        instructions = "Write the answer!\n2 points!"

    return {
        "id": question_id,
        "type": "question-free-text",
        "round": round_num,
        "questionNumber": f"Bonus {bonus_num}",
        "questionText": question_text,
        "correctAnswerText": answer_text,
        "timerSeconds": 30,
        "pointsAvailable": 2,
        "instructions": instructions
    }

def create_answer_slide(question_slide):
    """Create answer slide for a question"""
    q_id = question_slide['id']
    round_num = question_slide['round']

    return {
        "id": f"{q_id}-answer",
        "type": "answer",
        "round": round_num,
        "questionRefId": q_id,
        "title": "Bonus Answer" if "bonus" in q_id else "Answer",
        "correctAnswerText": question_slide.get('correctAnswerText', '')
    }

def create_round_slides(round_num, questions, bonus_questions):
    """Create all slides for a round"""
    slides = []

    # Round intro
    slides.append({
        "id": f"round{round_num}-intro",
        "type": "round-intro",
        "round": round_num,
        "title": f"Round {round_num}",
        "subtitle": "(multiple choice round)",
        "instructions": "Remember to write the rounds & team name each time"
    })

    # Regular questions
    question_slides = []
    for i, q in enumerate(questions, 1):
        q_slide = create_mcq_question(q, round_num, i)
        question_slides.append(q_slide)
        slides.append(q_slide)

    # Bonus questions
    bonus_slides = []
    for i, b in enumerate(bonus_questions, 1):
        b_slide = create_bonus_question(b, round_num, i)
        bonus_slides.append(b_slide)
        slides.append(b_slide)

    # Answer slides for regular questions
    for q_slide in question_slides:
        slides.append(create_answer_slide(q_slide))

    # Answer slides for bonus questions
    for b_slide in bonus_slides:
        slides.append(create_answer_slide(b_slide))

    # Round end
    slides.append({
        "id": f"r{round_num}-end",
        "type": "info",
        "title": f"End of Round {round_num}",
        "subtitle": "Time to check your answers!"
    })

    # Break (except after last round)
    if round_num < 6:
        slides.append({
            "id": f"break-{round_num}",
            "type": "info",
            "title": "BREAK TIME",
            "subtitle": f"Grab a drink and get ready for Round {round_num + 1}!"
        })

    return slides

def create_video_round_placeholder():
    """Create placeholder for Round 3 (videos)"""
    slides = []

    # Round intro
    slides.append({
        "id": "round3-intro",
        "type": "round-intro",
        "round": 3,
        "title": "Round 3",
        "subtitle": "(video round)",
        "instructions": "Watch carefully and identify!"
    })

    # 10 video questions
    for i in range(1, 11):
        slides.append({
            "id": f"r3-q{i}",
            "type": "question-video",
            "round": 3,
            "questionNumber": i,
            "questionText": "Watch the video!\nWhat is this from?",
            "videoSrc": f"media/video-placeholder-{i}.mp4",
            "autoplay": True,
            "timerSeconds": 30,
            "correctAnswerText": "[To be filled]"
        })

    # Answer slides
    for i in range(1, 11):
        slides.append({
            "id": f"r3-q{i}-answer",
            "type": "answer",
            "round": 3,
            "questionRefId": f"r3-q{i}",
            "title": "Answer",
            "correctAnswerText": "[To be filled]"
        })

    # Round end and break
    slides.append({
        "id": "r3-end",
        "type": "info",
        "title": "End of Round 3",
        "subtitle": "Time to check your answers!"
    })

    slides.append({
        "id": "break-3",
        "type": "info",
        "title": "BREAK TIME",
        "subtitle": "Grab a drink and get ready for Round 4!"
    })

    return slides

def create_audio_round_placeholder():
    """Create placeholder for Round 6 (audio)"""
    slides = []

    # Round intro
    slides.append({
        "id": "round6-intro",
        "type": "round-intro",
        "round": 6,
        "title": "Round 6",
        "subtitle": "(audio round)",
        "instructions": "Listen carefully and identify!"
    })

    # 10 audio questions
    for i in range(1, 11):
        slides.append({
            "id": f"r6-q{i}",
            "type": "question-audio",
            "round": 6,
            "questionNumber": i,
            "questionText": "Listen carefully!\nName the song or sound",
            "audioSrc": f"media/audio-placeholder-{i}.mp3",
            "autoplay": True,
            "timerSeconds": 30,
            "correctAnswerText": "[To be filled]"
        })

    # Answer slides
    for i in range(1, 11):
        slides.append({
            "id": f"r6-q{i}-answer",
            "type": "answer",
            "round": 6,
            "questionRefId": f"r6-q{i}",
            "title": "Answer",
            "correctAnswerText": "[To be filled]"
        })

    # Round end
    slides.append({
        "id": "r6-end",
        "type": "info",
        "title": "End of Round 6",
        "subtitle": "Time to check your answers!"
    })

    return slides

def main():
    # Parse CSV
    print("Parsing questions.csv...")
    rounds = parse_csv_to_rounds('questions.csv')

    # Load existing config to preserve settings and intro/outro slides
    print("Loading existing quiz-config.json...")
    with open('quiz-config.json', 'r', encoding='utf-8') as f:
        existing_config = json.load(f)

    # Start with settings from existing config
    new_config = {
        "settings": existing_config["settings"],
        "slides": []
    }

    # Add intro slides (welcome, prizes)
    intro_slides = [
        slide for slide in existing_config["slides"]
        if slide["id"] in ["welcome", "welcome-2", "prizes-1", "prizes-2"]
    ]
    new_config["slides"].extend(intro_slides)

    # Round 1
    print("Generating Round 1...")
    round1_questions = rounds.get(1, [])
    round1_bonus = rounds.get('1_BONUS', [])
    new_config["slides"].extend(create_round_slides(1, round1_questions, round1_bonus))

    # Round 2
    print("Generating Round 2...")
    round2_questions = rounds.get(2, [])
    round2_bonus = rounds.get('2_BONUS', [])
    new_config["slides"].extend(create_round_slides(2, round2_questions, round2_bonus))

    # Round 3 (videos - placeholder)
    print("Generating Round 3 (video placeholder)...")
    new_config["slides"].extend(create_video_round_placeholder())

    # Round 4
    print("Generating Round 4...")
    round4_questions = rounds.get(4, [])
    round4_bonus = rounds.get('4_BONUS', [])
    new_config["slides"].extend(create_round_slides(4, round4_questions, round4_bonus))

    # Round 5
    print("Generating Round 5...")
    round5_questions = rounds.get(5, [])
    round5_bonus = rounds.get('5_BONUS', [])
    new_config["slides"].extend(create_round_slides(5, round5_questions, round5_bonus))

    # Round 6 (audio - placeholder)
    print("Generating Round 6 (audio placeholder)...")
    new_config["slides"].extend(create_audio_round_placeholder())

    # Add thank you slide
    thank_you_slide = [
        slide for slide in existing_config["slides"]
        if slide.get("type") == "thank-you"
    ]
    if thank_you_slide:
        new_config["slides"].extend(thank_you_slide)

    # Write new config
    print("Writing new quiz-config.json...")
    with open('quiz-config.json', 'w', encoding='utf-8') as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*60)
    print("QUIZ GENERATION COMPLETE")
    print("="*60)
    print(f"Total slides: {len(new_config['slides'])}")
    print(f"Round 1: {len(round1_questions)} questions + {len(round1_bonus)} bonus")
    print(f"Round 2: {len(round2_questions)} questions + {len(round2_bonus)} bonus")
    print(f"Round 3: 10 video questions (placeholder)")
    print(f"Round 4: {len(round4_questions)} questions + {len(round4_bonus)} bonus")
    print(f"Round 5: {len(round5_questions)} questions + {len(round5_bonus)} bonus")
    print(f"Round 6: 10 audio questions (placeholder)")
    print("="*60)

if __name__ == "__main__":
    main()
