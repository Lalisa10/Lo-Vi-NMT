from collections import defaultdict
import os

class VNBPE:
    def __init__(self, min_freq=2, dumpWord=None):
        self.min_freq = min_freq
        self.dumpWord = dumpWord if dumpWord is not None else set(['&quot;', '.', ',', '?', '!', ';', ':', '"', "'", '(', ')', '[', ']', '{', '}', '<', '>', '/', '\\', '@', '#', '$', '%', '^', '&', '*', '-', '+', '=', '~'])
        self.merge_rules = []

    def get_most_freq_pair(self, text):
        """
        Thu thập các cặp từ phổ biến với tần suất lớn hơn min_freq từ tập train.
        Chỉ sử dụng trong giai đoạn học từ tập train.
        """
        pair_freq = defaultdict(int)
        for line in text:
            words = line.split()
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i + 1]
                if w1 not in self.dumpWord and w2 not in self.dumpWord and not w1.isdigit():
                    pair_freq[(w1, w2)] += 1
        return [(pair, freq) for pair, freq in pair_freq.items() if freq > self.min_freq]

    def learn_merge_rules(self, train_path, codes_path):
        """
        Học các quy tắc hợp nhất từ tập train và ghi vào file codes.
        Đây là nơi duy nhất gọi get_most_freq_pair.
        """
        with open(train_path, 'r', encoding='utf-8') as train_f, \
             open(codes_path, 'w', encoding='utf-8') as codes_f:
            text = [line.strip() for line in train_f.readlines()]
            pairs = self.get_most_freq_pair(text)
            sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
            for pair, freq in sorted_pairs:
                original_word = pair[0] + ' ' + pair[1]
                replaced_word = pair[0] + '_' + pair[1]
                self.merge_rules.append((pair[0], pair[1], replaced_word))
                codes_f.write(original_word + ' -> ' + replaced_word + '\n')

    def apply_merge_rules(self, text):
        """
        Áp dụng các quy tắc hợp nhất đã học lên văn bản (train, dev, hoặc test).
        Không học thêm bất kỳ thông tin nào từ văn bản đầu vào.
        """
        for rule in self.merge_rules:
            pair = (rule[0], rule[1])
            replaced_word = rule[2]
            for i in range(len(text)):
                words = text[i].split()
                new_words = []
                j = 0
                while j < len(words):
                    if j < len(words) - 1 and words[j] == pair[0] and words[j + 1] == pair[1]:
                        new_words.append(replaced_word)
                        j += 2
                    else:
                        new_words.append(words[j])
                        j += 1
                text[i] = ' '.join(new_words)
        return text

    def process_file(self, input_path, output_path):
        """
        Áp dụng các quy tắc hợp nhất lên file đầu vào và ghi vào file đầu ra.
        """
        with open(input_path, 'r', encoding='utf-8') as input_f, \
             open(output_path, 'w', encoding='utf-8') as output_f:
            text = [line.strip() for line in input_f.readlines()]
            tokenized_text = self.apply_merge_rules(text)
            for line in tokenized_text:
                output_f.write(line + '\n')

# Sử dụng
if __name__ == '__main__':
    vnbpe = VNBPE(min_freq=2)
    
    # Học quy tắc từ tập train
    vnbpe.learn_merge_rules('train.txt', 'codes.txt')
    
    # Áp dụng quy tắc lên tập train, dev, test
    for dataset in ['train', 'dev', 'test']:
        input_path = f'{dataset}.vi'
        output_path = f'{dataset}_output.vi'
        vnbpe.process_file(input_path, output_path)