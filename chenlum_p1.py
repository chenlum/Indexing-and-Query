import re


def main():
    # read the file and slice lines for further analysis
    file = open('grimms.txt', 'r')
    all_lines = file.readlines()
    file.close()
    # only use story lines ro build index
    lines = all_lines[124: 9209]

    # get title list and title line list
    titles = get_titles(lines, all_lines)
    title_lines = get_title_lines(titles, lines)

    # checkpoint1, build the index
    word_line = 124
    w2s = dict()
    # iterate though story lines
    for line in lines:
        word_line += 1
        # replace characters that is not a-z,A-Z,0-9,' ' with nothing
        line = re.sub(r'[^a-zA-Z0-9 ]+', '', line).lower().split()
        # get rid of stopwords
        words = [word for word in line if word not in stopword_list()]
        for word in words:
            # locate the word line in a story domain, record word, title, lines in a dictionary
            for i in range(len(title_lines)):
                if i != len(title_lines) - 1:
                    if title_lines[i] < word_line < title_lines[i + 1]:
                        w2s.setdefault(word, {}).setdefault(titles[i], []).append(word_line)
                else:
                    if title_lines[i] < word_line:
                        w2s.setdefault(word, {}).setdefault(titles[i], []).append(word_line)

    # checkpoint2, boolean search interface and advanced queries
    query = input("Please enter your query: ")
    # prompt the user to input a query until the string "qquit" is entered
    while query != 'qquit':
        query_list = query.split()
        print("query = " + query)
        # input a single word, return stories containing word1
        if len(query_list) == 1:
            if query in w2s:
                for story in w2s[query]:
                    print("     " + story)
                    search_results(query, story, w2s, all_lines)
            else:
                print("        --")
        # input keyword "or" between two words, return stories containing either word1 or word2
        elif len(query_list) == 3 and query_list[1] == 'or':
            word1 = query_list[0]
            word2 = query_list[2]
            # create a set of stories containing either word1 or word2
            stories = set(w2s.get(word1, {}).keys()).union(set(w2s.get(word2, {}).keys()))
            if stories != set():
                for story in stories:
                    print("     " + story)
                    # if word1 and word2 are both in the story
                    if w2s.get(word1).get(story, 0) != 0 and w2s.get(word2).get(story, 0) != 0:
                        print("       " + word1)
                        search_results(word1, story, w2s, all_lines)
                        print("       " + word2)
                        search_results(word2, story, w2s, all_lines)
                    # if word1 is in the story but word2 is not
                    elif w2s.get(word1).get(story, 0) != 0 and w2s.get(word2).get(story, 0) == 0:
                        print("       " + word1)
                        search_results(word1, story, w2s, all_lines)
                        print("       " + word2)
                        print("         --")
                    # if word2 is in the story but word1 is not
                    elif w2s.get(word1).get(story, 0) == 0 and w2s.get(word2).get(story, 0) != 0:
                        print("       " + word2)
                        search_results(word2, story, w2s, all_lines)
                        print("       " + word1)
                        print("         --")
            else:
                print("        --")
        # input keyword "and" between two words, return stories containing word1 and word2
        elif len(query_list) == 3 and query_list[1] == 'and':
            word1 = query_list[0]
            word2 = query_list[2]
            query_words = [word1, word2]
            # create a set of stories containing both word1 and word2
            stories = (set(w2s.get(word1, {}).keys())).intersection(set(w2s.get(word2, {}).keys()))
            if stories != set():
                for story in stories:
                    print("     " + story)
                    for word in query_words:
                        print("       " + word)
                        search_results(word, story, w2s, all_lines)
            else:
                print("        --")
        # input keyword "morethan" between two elements, return stories that let a word appear more than a specified number of times
        elif query_list[1] == 'morethan':
            story_existence = False
            query = query_list[0]
            if query in w2s:
                # if the second element is a number, compare directly
                if query_list[2].isdigit():
                    number = int(query_list[2])
                    for story in w2s[query]:
                        if len(w2s.get(query, {}).get(story, [])) > number:
                            story_existence = True
                            print("     " + story)
                            search_results(query, story, w2s, all_lines)
                # if the second element is a string, get the reference word frequency in the story, then compare
                elif query_list[2].isalpha():
                    reference = query_list[2]
                    for story in w2s[query]:
                        if len(w2s.get(query, {}).get(story, [])) > len(w2s.get(reference, {}).get(story, [])):
                            story_existence = True
                            print("     " + story)
                            print("       " + query)
                            search_results(query, story, w2s, all_lines)
                            print("       " + reference)
                            # check if the reference frequency is 0
                            if story in w2s.get(reference, {}):
                                search_results(reference, story, w2s, all_lines)
                            else:
                                print("        --")
                # if no such story exists, print '--'
                if story_existence is False:
                    print("        --")
            else:
                print("        --")
        # return stories in which two words are within plus/minus one line of each other
        elif query_list[1] == 'near':
            word1 = query_list[0]
            word2 = query_list[2]
            # create a set of stories containing both word1 and word2
            stories = (set(w2s.get(word1, {}).keys())).intersection(set(w2s.get(word2, {}).keys()))
            story_existence = False
            if stories != set():
                # iterate through each story in the intersection set
                for story in stories:
                    # iterate through each line num of the story
                    for line_num in w2s[word1][story]:
                        # iterate through lines within plus/minus one line of the target line
                        for line in all_lines[line_num-2: line_num]:
                            if word2 in line:
                                story_existence = True
                                print("     " + story)
                                print("       " + word1)
                                search_results(word1, story, w2s, all_lines)
                                print("       " + word2)
                                search_results(word2, story, w2s, all_lines)
                # if no such story exists, print '--'
                if story_existence is False:
                    print("        --")
            else:
                print("        --")
        # return stories containing word1, word2,..., wordn
        else:
            stories = set(w2s.get(query_list[0], {}).keys())
            # create a set of stories containing all words
            for word in query_list[1:]:
                stories = stories.intersection(set(w2s.get(word, {}).keys()))
            if stories != set():
                for story in stories:
                    print("     " + story)
                    for word in query_list:
                        print("       " + word)
                        search_results(word, story, w2s, all_lines)
            else:
                print("        --")
        query = input("Please enter your query: ")


def stopword_list():
    stopwords = list()
    file = open('stopwords.txt', 'r')
    for word in file:
        stopwords.append(word.strip())
    return stopwords


def get_titles(lines, all_lines):
    titles = list()
    line_num = 124
    for line in lines:
        line_num += 1
        # match lines only containing A-Z, '-', '[', ']'
        match = re.match(r'[A-Z\-,\[\] ]+', line)
        # if four lines above the matched lines is blank, it is a title
        if match and all_lines[line_num-4] in ['\n', '\r\n']:
            title = match.group().strip()
            # get rid of those single capital letters
            if len(title) > 1:
                titles.append(title)
    return titles


def get_title_lines(titles, lines):
    title_lines = list()
    line_num = 124
    for line in lines:
        line_num += 1
        for title in titles:
            if line.strip() == title:
                title_lines.append(line_num)
    return title_lines


def search_results(query, story, w2s, all_lines):
    for line_num in w2s[query][story]:
        # surround the query word with two asterisks and display the word in all capital letters
        output = all_lines[line_num-1].lower().replace(query, "**" + query.upper() + "**")
        print("       " + str(line_num) + " " + output)


main()



