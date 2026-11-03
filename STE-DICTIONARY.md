# STE dictionary

This file is the project dictionary for [ASD-STE100](https://www.asd-ste100.org/) text in this repository. It records the technical names and technical verbs that we use, and the words that we do not use.

ASD-STE100 lets a project add its own technical names and technical verbs. When a word in this file has a meaning, you MUST use the word only with that meaning. When this file gives a word to use in place of a different word, you MUST use the given word.

## How to add a word

1. Add the word to the correct table, in alphabetical order.
2. Give one meaning only. Write the meaning in STE.
3. In "Do not use", write the synonyms that the word replaces.
4. Commit the change to this file before or together with the first text that uses the word.

Do not add a word that has the same meaning as a word in this file.

## Technical names

| Term | Meaning | Do not use |
|------|---------|------------|
| book | One audiobook in the library. It is one folder with audio, or one audio file in leaf mode `file`. | title (for the item), item, audiobook entry |
| claim | One identity value of a book, with a kind and a value (for example, `rel_path`). | identifier, key |
| conflict | Two or more listening states of one book after a merge, before the user selects one. | collision, clash |
| group | A folder that contains only folders, for example an author or a series folder. | grouping, container, category |
| hunk | One part of a git diff that you can stage or not stage separately. | chunk, change block |
| leaf mode | The root setting that tells which items are books: `folder` or `file`. | structure, layout, leaf type |
| listening state | The position, playback speed, last played time and finished flag of a book. | progress (for the data), bookmark |
| name pattern | The root setting that fills metadata from the path when the tags do not give it. | template, structure, preset |
| root | A folder that the user adds to the library. All books are in roots. | library folder, source, location |
| warning log | The list of warnings for one root from its last scan. | error list, issues |

## Technical verbs

| Verb | Meaning | Do not use |
|------|---------|------------|
| merge | Make one book from two known books. | combine, join, unify |
| rescan | Scan a root again when the user starts it. | refresh, reload, resync |
| scan | Read a root and find its books and warnings. | index, crawl, import |

## Words that we do not use

| Do not use | Use |
|------------|-----|
| derive | make, find |
| e.g. | for example |
| ensure | make sure that, or write the result as a requirement |
| shall | must |
| via | through, with |
