import re

class TextNormalizer:
    """
    A simple rule-based Inverse Text Normalization (ITN) class.
    Converts spoken-form numbers and basic punctuation into written form.
    """

    def __init__(self):
        self.number_map = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16, 
            "seventeen": 17, "eighteen": 18, "nineteen": 19,
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
        }
        
        self.multipliers = {
            "hundred": 100,
            "thousand": 1000,
            "million": 1000000,
            "billion": 1000000000
        }

    def normalize(self, text: str) -> str:
        """
        Main entry point for normalization.
        """
        if not text:
            return text
            
        text = self._convert_numbers(text)
        # Add more normalization methods here if needed (e.g., punctuation)
        return text

    def _convert_numbers(self, text: str) -> str:
        """
        Converts spoken numbers to digits.
        Example: "one hundred twenty three" -> "123"
        """
        words = text.split()
        new_words = []
        current_number_words = []

        for word in words:
            clean_word = word.lower().replace(',', '').replace('.', '')
            if clean_word in self.number_map or clean_word in self.multipliers:
                current_number_words.append(clean_word)
            else:
                if current_number_words:
                    # Process the accumulated number phrase
                    val = self._parse_number_phrase(current_number_words)
                    new_words.append(str(val))
                    current_number_words = []
                new_words.append(word)
        
        # Handle trailing numbers
        if current_number_words:
            val = self._parse_number_phrase(current_number_words)
            new_words.append(str(val))

        return " ".join(new_words)

    def _parse_number_phrase(self, words):
        """
        Parses a list of number words into a single integer.
        Simple logic: sum up values, handling multipliers.
        """
        total_value = 0
        current_chunk_value = 0
        
        for word in words:
            if word in self.number_map:
                current_chunk_value += self.number_map[word]
            elif word in self.multipliers:
                mult = self.multipliers[word]
                # If we have "one hundred", chunk is 1 * 100
                # If we have "two thousand", chunk is 2 * 1000
                # But we need to handle "one hundred twenty thousand"
                
                if current_chunk_value == 0:
                    current_chunk_value = 1
                
                if mult == 100:
                    current_chunk_value *= mult
                else:
                    total_value += current_chunk_value * mult
                    current_chunk_value = 0
        
        total_value += current_chunk_value
        return total_value
