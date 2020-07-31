# import textwrap

# print(textwrap.shorten('Curabitur at lacus ac velit ornare lobortis. Donec vitae sapien ut libero venenatis faucibus. Donec id justo. Fusce risus nisl, viverra et, tempor et, pretium in, sapien.', width='20'))

def txt2paragraph(filepath):
    lines = filepath.readlines()

    paragraph = ''
    for line in lines:
        if line.isspace():  # is it an empty line?
            if paragraph:
                yield paragraph
                paragraph = ''
            else:
                continue
        else:
            paragraph += ' ' + line.strip()
    yield paragraph

txt2paragraph('''It’s an elementary issue, but quite important to performance, to build up the result as a list of strings and combine them with ''.join at the end. Building up a large string as a string, by repeated application of += in a loop, is never the right approach—it’s slow and clumsy. Good Pythonic style demands using a list as the intermediate accumulator when building up a string.

The show_paragraphs function demonstrates all the simple features of the Paragraphs class and can be used to unit-test the latter by feeding it a known text file.

Python 2.2 makes it very easy to build iterators and generators. This, in turn, makes it very tempting to build a more lightweight version of the by-paragraph buncher as a generator function, with no classes involved:''')