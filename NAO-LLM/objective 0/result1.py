import json
import os

def analyze_all_emotions(folder_path):
    """
    Reads JSON files from a folder, finds all unique 'emotion' values,
    and for each unique emotion, prints the corresponding 'emotion-recognized' values.

    Args:
        folder_path: The path to the folder containing the JSON files.
    """

    all_emotions = set()  # Use a set to store unique emotions
    emotion_recognition_map = {}  # Dictionary to store emotion: [recognized_emotions]

    for filename in os.listdir(folder_path):
        if filename.startswith("feedback_") and filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    for entry in data:
                        if "emotion" in entry:
                            all_emotions.add(entry["emotion"])
                            if entry["emotion"] not in emotion_recognition_map:
                                emotion_recognition_map[entry["emotion"]] = []
                            emotion_recognition_map[entry["emotion"]].append(entry["emotion-recognized"])

                elif isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            for entry in value:
                                if isinstance(entry, dict) and "emotion" in entry:
                                    all_emotions.add(entry["emotion"])
                                    if entry["emotion"] not in emotion_recognition_map:
                                        emotion_recognition_map[entry["emotion"]] = []
                                    emotion_recognition_map[entry["emotion"]].append(entry["emotion-recognized"])
                else:
                    print(f"Warning: Unexpected file structure in {filename}. Skipping.")

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in {filename}. Skipping.")
            except FileNotFoundError:
                print(f"Error: File not found: {filename}")  # Should not happen
            except Exception as e:
                print(f"An unexpected error occurred processing {filename}: {e}")

    # Print results for each unique emotion
    for emotion in sorted(all_emotions):  # Sorted for consistent output
        print(f"Recognized emotions for '{emotion}':")
        if emotion in emotion_recognition_map:
            for recognized_emotion in emotion_recognition_map[emotion]:
                print(f"- {recognized_emotion}")
        else:
            print("- No recognized emotions found.")  # Should not normally happen
        print() # Add an empty line for better separation


def main():
    folder_path = "/Users/matteorigat/Desktop/results"  # Or get from user input

    if not os.path.isdir(folder_path):
        print("Error: The specified folder does not exist.")
        return

    analyze_all_emotions(folder_path)

if __name__ == "__main__":
    main()