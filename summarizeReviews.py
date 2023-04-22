from bs4 import BeautifulSoup
import sys
import chardet
import pdb
from typing import List, Dict
import os

ENCODING = ""

MapScoreStatementToNumber = {
    "Definitely Reject": 2.0,
    "Reject": 2.5,
    "Low Borderline": 3.0,
    "Borderline": 3.5,
    "High Borderline": 4.0,
    "Accept": 4.5,
    "Definitely accept": 5.0,
}


def getAverageScore(overallAssessments: List[str]) -> float:
    scoreNums = []
    scoreStrs = ""
    for assessment in overallAssessments:
        scoreStr = assessment.split(" ")[0]
        scoreStatement = assessment.split("(")[1].split(")")[0]
        scoreStrs += f"{scoreStr},"
        try:
            scoreNum = MapScoreStatementToNumber[scoreStatement]
            scoreNums.append(scoreNum)
        except KeyError as e:
            print(f"Error {e}")
            return
        print(f"{scoreStr} - {scoreStatement} - {scoreNum}")

    averageScore = sum(scoreNums) / len(scoreNums)
    return scoreStrs, averageScore


def aggregateAllCommentsToEditor(reviews_dict: Dict) -> str:
    commentsToEditor = ""
    for review_id, review_dict in reviews_dict.items():
        comment = review_dict["Confidential comments for editorial staff"]
        commentsToEditor += f"\n--------------------\n{comment}"
    print(f"-----------------------------------")
    print(f"{commentsToEditor}")
    print(f"-----------------------------------")
    return commentsToEditor


def detectFileEncode(filePath):
    global ENCODING
    with open(filePath, "rb") as f:
        data = f.read()
    result = chardet.detect(data)
    encoding = result["encoding"]
    ENCODING = encoding
    return encoding


def extractInfor(reviewPath):
    global ENCODING
    # Check the encoding
    if ENCODING == "":
        ENCODING = "Windows-1252"
        # detectFileEncode(reviewPath)

    # File to store the summarization
    # define the reviewPath and sumPath
    summaryPath = os.path.splitext(reviewPath)[0] + ".txt"

    chatGPTPrompt = """Given reviews of a paper. Summarize all reviews to point out its problem statement, its strengths and weaknesses of the paper.
    - Use bullet points
    - Short sentences
    - No repetation
    Use the following format:
    Content: what problem the paper aims to solve
    Strengths: the paper's strengths
    Weaknesses: the paper's weaknesses
    Recommendation: the paper is ready for publication or not.
    ***
    Reviews:
    """

    # read the HTML file
    with open(reviewPath, "r", encoding=ENCODING) as f:
        html = f.read()

    # create a BeautifulSoup object
    soup = BeautifulSoup(html, "html.parser")

    # find all the review containers
    review_containers = soup.find_all("tbody", id="", style="color: ")

    # iterate through all the containers and extract the desired information for each review
    reviews_dict = {}
    for container in review_containers:
        # extract Reviewer number
        reviewer_number = (
            container.find("td", string="Reviewer number").find_next("td").text.strip()
        )

        # extract Reviewer name
        reviewer_name = (
            container.find("td", string="Reviewer name (PIN)")
            .find_next("td")
            .text.strip()
        )
        print(f"===========\nReviewer {reviewer_name}, Number {reviewer_number} ....")
        # extract overall evaluation
        overall_assessment = (
            container.find("td", string="Overall assessment")
            .find_next("td")
            .text.strip()
        )
        print(f"Overall assessment: \n {overall_assessment}")

        # extract confidential comments for editorial staff
        confidential_comments = (
            container.find("td", string="Confidential comments for editorial staff")
            .find_next("td")
            .text.strip()
        )

        # extract comments for author
        comments_for_author = (
            container.find("td", string="Comments for author")
            .find_next("td")
            .text.strip()
        )
        # extract Comment under Assessment of Video Attachment
        try:
            video_assessment = (
                soup.find("td", string="Assessment of Video Attachment")
                .find_next("td")
                .text.strip()
            )
        except:
            video_assessment = ""

        review_dict = {
            "Reviewer name": reviewer_name,
            "Overall assessment": overall_assessment,
            "Confidential comments for editorial staff": confidential_comments,
            "Comments for author": comments_for_author,
            "Video assessment": video_assessment,
        }
        reviews_dict[reviewer_number] = review_dict
    print(f"================================================")
    overall_assessments = []
    for review_id, review_dict in reviews_dict.items():
        overall_assessment = review_dict["Overall assessment"]
        overall_assessments.append(overall_assessment)
    print(overall_assessments)
    scoreStrs, averageScore = getAverageScore(overall_assessments)
    print(f"---->Avg score: {averageScore}")

    # Aggregate all comments to editor
    commentsToEditorStr = aggregateAllCommentsToEditor(reviews_dict)
    chatGPTPrompt += f"\n{commentsToEditorStr}"

    with open(summaryPath, "w") as f:
        f.write(f"======================\nAll Scores: \n {scoreStrs}\n")
        f.write(f"======================\nAvg Scores: \n {averageScore}\n")
        f.write(f"======================\nChatGPT Prompt: \n\n {chatGPTPrompt}\n")
        f.write(
            f"======================\nChatGPT Summarization based on Comments to Editor:\n"
        )


def summarizeAllReviewsInAFolder(folderPath: str):
    # loop through all files in the folder
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            # check if the file ends with ".html"
            if file.endswith(".html"):
                # get the full path to the file
                filePath = os.path.join(root, file)
                print(f"*******************************************")
                print(f"File {filePath}")
                print(f"*******************************************\n")
                extractInfor(filePath)


if __name__ == "__main__":
    # if len(sys.argv) == 2:
    #     reviewPath = sys.argv[1]
    # else:
    #     raise ValueError("Syntax: python summarizeReviews.py <path to the html file>")
    # extractInfor(reviewPath)

    if len(sys.argv) == 2:
        reviewsFolderPath = sys.argv[1]
    else:
        raise ValueError(
            "Syntax: python summarizeReviews.py <path to the folder that contains all review file>"
        )
    summarizeAllReviewsInAFolder(reviewsFolderPath)
