# IROS_review_summarization
Given a html file that contains all reviews for a paper, aggregate all information, for example: calculate the avergage score

# Usage
## Generate `.html` file that contains all reviews
[1] First, go to the IROS workspace\
[2]`Reviews` menu under each paper \
[3]`One click reviews` to display all reviews within a window \
[4] Find a way to save the window to a `.html` file to the local folder, for example, `reviews/`

## Generate summarization files
Run
```
python summarizeReviews.py <path to the folder that contains html files, for example, reviews>
```
Summarization files will be stored in the same folder, for example, `reviews` in `.txt` format. 

## (Optional) Ask ChatGPT to summarize the comments
Copy the content in `.txt` files to ChatGPT

