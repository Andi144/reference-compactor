import argparse
import os

import bibtexparser

ARGS = None


def add_numbers(words_to_compact: dict):
    unit_position = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh",
                     "Eighth", "Ninth"]
    compact_unit_position = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th",
                             "9th"]
    second_position = ["Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
                       "Eighty", "Ninety"]
    compact_second_position = ["2", "3", "4", "5", "6", "7", "8", "9"]
    
    # 10 - 19
    words_to_compact["Tenth"] = "10th"
    words_to_compact["Eleventh"] = "11th"
    words_to_compact["Twelfth"] = "12th"
    words_to_compact["Thirteenth"] = "13th"
    words_to_compact["Fourteenth"] = "14th"
    words_to_compact["Fifteenth"] = "15th"
    words_to_compact["Sixteenth"] = "16th"
    words_to_compact["Seventeenth"] = "17th"
    words_to_compact["Eighteenth"] = "18th"
    words_to_compact["Nineteenth"] = "19th"
    # 20, 30, ..., 90
    words_to_compact["Twentieth"] = "20th"
    words_to_compact["Thirtieth"] = "30th"
    words_to_compact["Fortieth"] = "40th"
    words_to_compact["Fiftieth"] = "50th"
    words_to_compact["Sixtieth"] = "60th"
    words_to_compact["Seventieth"] = "70th"
    words_to_compact["Eightieth"] = "80th"
    words_to_compact["Ninetieth"] = "90th"
    # 21, 22, ..., 29, 31, 32, ..., 39, ..., 91, 92, ..., 99
    for s_long, s_short in zip(second_position, compact_second_position):
        for u_long, u_short in zip(unit_position, compact_unit_position):
            long = s_long + "-" + u_long
            short = s_short + u_short
            words_to_compact[long] = short
    # 1 - 9 (add last so the replacing does not work as "Twenty-Third" -> "Twenty-3rd")
    for long, short in zip(unit_position, compact_unit_position):
        words_to_compact[long] = short


# TODO: "month" ---> braces "{}" are added (which the ACM format does not recognize)

def main(bib, out):
    words_to_compact = {
        "Proceedings"  : "Proc.",
        "Conference"   : "Conf.",
        "International": "Int'l.",
        }
    add_numbers(words_to_compact)
    
    with open(bib) as f:
        bib_database = bibtexparser.load(f)
    
    for entry in bib_database.entries:
        for key_to_delete in KEYS_TO_DELETE:
            if key_to_delete in entry:
                del entry[key_to_delete]
        
        if ARGS.replace_link_with_url and "link" in entry:
            value = entry["link"]
            del entry["link"]
            entry["url"] = value
        
        if "booktitle" in entry:
            booktitle = str(entry["booktitle"])
            
            for long, short in words_to_compact.items():
                booktitle = booktitle.replace(long, short)
            
            entry["booktitle"] = booktitle
        
        if ARGS.compact_first_names:
            if "author" in entry:
                author = str(entry["author"])
                authors = author.split(" and ")
                compact_authors = []
                
                for a in authors:
                    names = a.split(", ")
                    if len(names) == 2:
                        last_names = names[0]
                        first_names = names[1]
                        compact_author = last_names + ", " + compact_author_first_names(
                                first_names)
                        compact_authors.append(compact_author)
                    else:
                        compact_authors.append(author)
                
                entry["author"] = " and ".join(compact_authors)
    
    if out is None:
        out = os.path.join(os.path.dirname(bib), "compact_" + os.path.basename(bib))
    
    compact_content = bibtexparser.dumps(bib_database)
    with open(out, "w") as f:
        f.write(compact_content)


def compact_author_first_names(first_names_str: str):
    compact_first_names = []
    # Anton B C. Dora EF ---> [Anton], [C], [C.], [Dora], [EF]
    first_names = first_names_str.split(" ")
    
    for first_name in first_names:
        if len(first_name) <= 1:
            # cannot compact more than this ---> B
            compact_first_names.append(first_name)
        elif len(first_name) == 2 and "." in first_name:
            # already abbreviated ---> C.
            compact_first_names.append(first_name)
        elif first_name.isupper():
            # also already abbreviated (e.g., multiple names) ---> EF
            compact_first_names.append(first_name)
        else:
            # Anton ---> A.
            # Dora ---> D.
            compact_first_names.append(first_name[0] + ".")
    
    return " ".join(compact_first_names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="BibTex reference compactor",
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("bib", type=str, help="The BibTex bibliography file.")
    parser.add_argument("--out", type=str, default=None,
                        help="The compacted BibTex bibliography file. If not specified, "
                             "the default file will be in the same directory as 'bib' "
                             "with the same name but 'compact' prepended.")
    parser.add_argument("--replace_link_with_url", action="store_true",
                        help="Replaces 'link' keys with 'url' keys (e.g., useful for "
                             "ACM that uses 'natbib' which supports 'url' keys).")
    parser.add_argument("--compact_first_names", action="store_true",
                        help="Compacts the first names of authors, e.g., 'Anton' will be "
                             "compacted to 'A.'. If the author has multiple first "
                             "names, all first names will be compacted.")
    parser.add_argument("--keys_to_delete", type=str, nargs="*", default=[],
                        help="List of all BibTex keys that should be deleted.")
    ARGS = parser.parse_args()
    KEYS_TO_DELETE = ARGS.keys_to_delete
    print(ARGS)
    
    main(ARGS.bib, ARGS.out)
