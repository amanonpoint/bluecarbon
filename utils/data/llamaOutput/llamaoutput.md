
Gareth James • Daniela Witten • Trevor Hastie • Robert Tibshirani

# An Introduction to Statistical Learning

# with Applications in R

# 123




# Gareth James

# Department of Information and Operations Management

# University of Southern California

# Los Angeles, CA, USA

# Daniela Witten

# Department of Biostatistics

# University of Washington

# Seattle, WA, USA

# Trevor Hastie

# Department of Statistics

# Stanford University

# Stanford, CA, USA

# Robert Tibshirani

# Department of Statistics

# Stanford University

# Stanford, CA, USA

ISSN 1431-875X

ISBN 978-1-4614-7137-0

ISBN 978-1-4614-7138-7 (eBook)

DOI 10.1007/978-1-4614-7138-7

Springer New York Heidelberg Dordrecht London

Library of Congress Control Number: 2013936251

© Springer Science+Business Media New York 2013 (Corrected at 6th printing 2015)

This work is subject to copyright. All rights are reserved by the Publisher, whether the whole or part of the material is concerned, specifically the rights of translation, reprinting, reuse of illustrations, recitation, broadcasting, reproduction on microfilms or in any other physical way, and transmission or information storage and retrieval, electronic adaptation, computer software, or by similar or dissimilar methodology now known or hereafter developed. Exempted from this legal reservation are brief excerpts in connection with reviews or scholarly analysis or material supplied specifically for the purpose of being entered and executed on a computer system, for exclusive use by the purchaser of the work. Duplication of this publication or parts thereof is permitted only under the provisions of the Copyright Law of the Publisher’s location, in its current version, and permission for use must always be obtained from Springer. Permissions for use may be obtained through RightsLink at the Copyright Clearance Center. Violations are liable to prosecution under the respective Copyright Law.

The use of general descriptive names, registered names, trademarks, service marks, etc. in this publication does not imply, even in the absence of a specific statement, that such names are exempt from the relevant protective laws and regulations and therefore free for general use.

While the advice and information in this book are believed to be true and accurate at the date of publication, neither the authors nor the editors nor the publisher can accept any legal responsibility for any errors or omissions that may be made. The publisher makes no warranty, express or implied, with respect to the material contained herein.

Printed on acid-free paper

Springer is part of Springer Science+Business Media (www.springer.com)

To our parents:

- Alison and Michael James
- Chiara Nappi and Edward Witten
- Valerie and Patrick Hastie
- Vera and Sami Tibshirani

and to our families:

- Michael, Daniel, and Catherine
- Tessa and Ari
- Samantha, Timothy, and Lynda
- Charlie, Ryan, Julie, and Cheryl

NO_CONTENT_HERE

# Preface

Statistical learning refers to a set of tools for modeling and understanding complex datasets. It is a recently developed area in statistics and blends with parallel developments in computer science and, in particular, machine learning. The field encompasses many methods such as the lasso and sparse regression, classification and regression trees, and boosting and support vector machines.

With the explosion of “Big Data” problems, statistical learning has become a very hot field in many scientific areas as well as marketing, finance, and other business disciplines. People with statistical learning skills are in high demand.

One of the first books in this area—The Elements of Statistical Learning (ESL) (Hastie, Tibshirani, and Friedman)—was published in 2001, with a second edition in 2009. ESL has become a popular text not only in statistics but also in related fields. One of the reasons for ESL’s popularity is its relatively accessible style. But ESL is intended for individuals with advanced training in the mathematical sciences. An Introduction to Statistical Learning (ISL) arose from the perceived need for a broader and less technical treatment of these topics. In this new book, we cover many of the same topics as ESL, but we concentrate more on the applications of the methods and less on the mathematical details. We have created labs illustrating how to implement each of the statistical learning methods using the popular statistical software package R. These labs provide the reader with valuable hands-on experience.

This book is appropriate for advanced undergraduates or master’s students in statistics or related quantitative fields or for individuals in other

# Preface

disciplines who wish to use statistical learning tools to analyze their data. It can be used as a textbook for a course spanning one or two semesters.

We would like to thank several readers for valuable comments on preliminary drafts of this book: Pallavi Basu, Alexandra Chouldechova, Patrick Danaher, Will Fithian, Luella Fu, Sam Gross, Max Grazier G’Sell, Courtney Paulson, Xinghao Qiao, Elisa Sheng, Noah Simon, Kean Ming Tan, and Xin Lu Tan.

It’s tough to make predictions, especially about the future.

-Yogi Berra

Los Angeles, USA                                Gareth James

Seattle, USA                                  Daniela Witten

Palo Alto, USA      Trevor Hastie

Palo Alto, USA      Robert Tibshirani

Contents

# Preface

vii

# 1  Introduction

1

# 2  Statistical Learning

15

# 2.1     What Is Statistical Learning?

15

# 2.1.1        Why Estimate f ?

17

# 2.1.2     How Do We Estimate f ?

21

# 2.1.3     The Trade-Oﬀ Between Prediction Accuracy and Model Interpretability

24

# 2.1.4     Supervised Versus Unsupervised Learning

26

# 2.1.5            Regression Versus Classiﬁcation Problems

28

# 2.2     Assessing Model Accuracy

29

# 2.2.1     Measuring the Quality of Fit

29

# 2.2.2     The Bias-Variance Trade-Oﬀ

33

# 2.2.3     The Classiﬁcation Setting

37

# 2.3     Lab: Introduction to R

42

# 2.3.1          Basic Commands

42

# 2.3.2     Graphics

45

# 2.3.3     Indexing Data

47

# 2.3.4        Loading Data

48

# 2.3.5     Additional Graphical and Numerical Summaries

49

# 2.4     Exercises

52

ix


# Contents

# 3 Linear Regression

# 3.1 Simple Linear Regression

61

# 3.1.1 Estimating the Coeﬃcients

61

# 3.1.2 Assessing the Accuracy of the Coeﬃcient Estimates

63

# 3.1.3 Assessing the Accuracy of the Model

68

# 3.2 Multiple Linear Regression

71

# 3.2.1 Estimating the Regression Coeﬃcients

72

# 3.2.2 Some Important Questions

75

# 3.3 Other Considerations in the Regression Model

82

# 3.3.1 Qualitative Predictors

82

# 3.3.2 Extensions of the Linear Model

86

# 3.3.3 Potential Problems

92

# 3.4 The Marketing Plan

102

# 3.5 Comparison of Linear Regression with K-Nearest Neighbors

104

# 3.6 Lab: Linear Regression

109

# 3.6.1 Libraries

109

# 3.6.2 Simple Linear Regression

110

# 3.6.3 Multiple Linear Regression

113

# 3.6.4 Interaction Terms

115

# 3.6.5 Non-linear Transformations of the Predictors

115

# 3.6.6 Qualitative Predictors

117

# 3.6.7 Writing Functions

119

# 3.7 Exercises

120

# 4 Classification

# 4.1 An Overview of Classification

128

# 4.2 Why Not Linear Regression?

129

# 4.3 Logistic Regression

130

# 4.3.1 The Logistic Model

131

# 4.3.2 Estimating the Regression Coeﬃcients

133

# 4.3.3 Making Predictions

134

# 4.3.4 Multiple Logistic Regression

135

# 4.3.5 Logistic Regression for >2 Response Classes

137

# 4.4 Linear Discriminant Analysis

138

# 4.4.1 Using Bayes’ Theorem for Classification

138

# 4.4.2 Linear Discriminant Analysis for p = 1

139

# 4.4.3 Linear Discriminant Analysis for p >1

142

# 4.4.4 Quadratic Discriminant Analysis

149

# 4.5 A Comparison of Classification Methods

151

# 4.6 Lab: Logistic Regression, LDA, QDA, and KNN

154

# 4.6.1 The Stock Market Data

154

# 4.6.2 Logistic Regression

156

# 4.6.3 Linear Discriminant Analysis

161




# Contents

# 4.6.4

Quadratic Discriminant Analysis . . . . . . . . . . . 163

# 4.6.5

K -Nearest Neighbors . . . . . . . . . . . . . . . . . . 163

# 4.6.6

An Application to Caravan Insurance Data . . . . . 165

# 4.7

Exercises . . . . . . . . . . . . . . . . . . . . . . . . . . . . 168

# 5

Resampling Methods . . . . . . . . . . . . . . . . . . . . . . . . 175

# 5.1

Cross-Validation . . . . . . . . . . . . . . . . . . . . . . . . 176

# 5.1.1

The Validation Set Approach . . . . . . . . . . . . . . . . . 176

# 5.1.2

Leave-One-Out Cross-Validation . . . . . . . . . . . . 178

# 5.1.3

k-Fold Cross-Validation . . . . . . . . . . . . . . . . . 181

# 5.1.4

Bias-Variance Trade-Oﬀ for k-Fold Cross-Validation . . . . . . . . . . . . . . . . . . . . 183

# 5.1.5

Cross-Validation on Classiﬁcation Problems . . . . . 184

# 5.2

The Bootstrap . . . . . . . . . . . . . . . . . . . . . . . . . 187

# 5.3

Lab: Cross-Validation and the Bootstrap . . . . . . . . . . . 190

# 5.3.1

The Validation Set Approach . . . . . . . . . . . . . . . . . 191

# 5.3.2

Leave-One-Out Cross-Validation . . . . . . . . . . . . 192

# 5.3.3

k-Fold Cross-Validation . . . . . . . . . . . . . . . . . 193

# 5.3.4

The Bootstrap . . . . . . . . . . . . . . . . . . . . . . . . . 194

# 5.4

Exercises . . . . . . . . . . . . . . . . . . . . . . . . . . . . 197

# 6

Linear Model Selection and Regularization . . . . . . . . . . . . 203

# 6.1

Subset Selection . . . . . . . . . . . . . . . . . . . . . . . . 205

# 6.1.1

Best Subset Selection . . . . . . . . . . . . . . . . . . . . . 205

# 6.1.2

Stepwise Selection . . . . . . . . . . . . . . . . . . . . . . . 207

# 6.1.3

Choosing the Optimal Model . . . . . . . . . . . . . . . . . 210

# 6.2

Shrinkage Methods . . . . . . . . . . . . . . . . . . . . . . . 214

# 6.2.1

Ridge Regression . . . . . . . . . . . . . . . . . . . . . . . . 215

# 6.2.2

The Lasso . . . . . . . . . . . . . . . . . . . . . . . . . . . 219

# 6.2.3

Selecting the Tuning Parameter . . . . . . . . . . . . . . . 227

# 6.3

Dimension Reduction Methods . . . . . . . . . . . . . . . . 228

# 6.3.1

Principal Components Regression . . . . . . . . . . . . . 230

# 6.3.2

Partial Least Squares . . . . . . . . . . . . . . . . . . . . 237

# 6.4

Considerations in High Dimensions . . . . . . . . . . . . . . 238

# 6.4.1

High-Dimensional Data . . . . . . . . . . . . . . . . . . . . 238

# 6.4.2

What Goes Wrong in High Dimensions? . . . . . . . . . . . 239

# 6.4.3

Regression in High Dimensions . . . . . . . . . . . . . . . 241

# 6.4.4

Interpreting Results in High Dimensions . . . . . . . . . . 243

# 6.5

Lab 1: Subset Selection Methods . . . . . . . . . . . . . . . 244

# 6.5.1

Best Subset Selection . . . . . . . . . . . . . . . . . . . . 244

# 6.5.2

Forward and Backward Stepwise Selection . . . . . . . . . . 247

# 6.5.3

Choosing Among Models Using the Validation Set Approach and Cross-Validation . . . . . . . . . . 248




# Contents

# 6.6 Lab 2: Ridge Regression and the Lasso

# 6.6.1 Ridge Regression

# 6.6.2 The Lasso

# 6.7 Lab 3: PCR and PLS Regression

# 6.7.1 Principal Components Regression

# 6.7.2 Partial Least Squares

# 6.8 Exercises

# 7 Moving Beyond Linearity

# 7.1 Polynomial Regression

# 7.2 Step Functions

# 7.3 Basis Functions

# 7.4 Regression Splines

# 7.4.1 Piecewise Polynomials

# 7.4.2 Constraints and Splines

# 7.4.3 The Spline Basis Representation

# 7.4.4 Choosing the Number and Locations of the Knots

# 7.4.5 Comparison to Polynomial Regression

# 7.5 Smoothing Splines

# 7.5.1 An Overview of Smoothing Splines

# 7.5.2 Choosing the Smoothing Parameter λ

# 7.6 Local Regression

# 7.7 Generalized Additive Models

# 7.7.1 GAMs for Regression Problems

# 7.7.2 GAMs for Classification Problems

# 7.8 Lab: Non-linear Modeling

# 7.8.1 Polynomial Regression and Step Functions

# 7.8.2 Splines

# 7.8.3 GAMs

# 7.9 Exercises

# 8 Tree-Based Methods

# 8.1 The Basics of Decision Trees

# 8.1.1 Regression Trees

# 8.1.2 Classification Trees

# 8.1.3 Trees Versus Linear Models

# 8.1.4 Advantages and Disadvantages of Trees

# 8.2 Bagging, Random Forests, Boosting

# 8.2.1 Bagging

# 8.2.2 Random Forests

# 8.2.3 Boosting

# 8.3 Lab: Decision Trees

# 8.3.1 Fitting Classification Trees

# 8.3.2 Fitting Regression Trees




# Contents

# 8.3.3 Bagging and Random Forests

328

# 8.3.4 Boosting

330

# 8.4 Exercises

332

# 9 Support Vector Machines

# 9.1 Maximal Margin Classifier

338

# 9.1.1 What Is a Hyperplane?

338

# 9.1.2 Classification Using a Separating Hyperplane

339

# 9.1.3 The Maximal Margin Classifier

341

# 9.1.4 Construction of the Maximal Margin Classifier

342

# 9.1.5 The Non-separable Case

343

# 9.2 Support Vector Classifiers

344

# 9.2.1 Overview of the Support Vector Classifier

344

# 9.2.2 Details of the Support Vector Classifier

345

# 9.3 Support Vector Machines

349

# 9.3.1 Classification with Non-linear Decision Boundaries

349

# 9.3.2 The Support Vector Machine

350

# 9.3.3 An Application to the Heart Disease Data

354

# 9.4 SVMs with More than Two Classes

355

# 9.4.1 One-Versus-One Classification

355

# 9.4.2 One-Versus-All Classification

356

# 9.5 Relationship to Logistic Regression

356

# 9.6 Lab: Support Vector Machines

359

# 9.6.1 Support Vector Classifier

359

# 9.6.2 Support Vector Machine

363

# 9.6.3 ROC Curves

365

# 9.6.4 SVM with Multiple Classes

366

# 9.6.5 Application to Gene Expression Data

366

# 9.7 Exercises

368

# 10 Unsupervised Learning

373

# 10.1 The Challenge of Unsupervised Learning

373

# 10.2 Principal Components Analysis

374

# 10.2.1 What Are Principal Components?

375

# 10.2.2 Another Interpretation of Principal Components

379

# 10.2.3 More on PCA

380

# 10.2.4 Other Uses for Principal Components

385

# 10.3 Clustering Methods

385

# 10.3.1 K-Means Clustering

386

# 10.3.2 Hierarchical Clustering

390

# 10.3.3 Practical Issues in Clustering

399

# 10.4 Lab 1: Principal Components Analysis

401




# Contents

# 10.5 Lab 2: Clustering

404

# 10.5.1 K -Means Clustering

404

# 10.5.2 Hierarchical Clustering

406

# 10.6 Lab 3: NCI60 Data Example

407

# 10.6.1 PCA on the NCI60 Data

408

# 10.6.2 Clustering the Observations of the NCI60 Data

410

# 10.7 Exercises

413

Index 419





# 1 Introduction

# An Overview of Statistical Learning

Statistical learning refers to a vast set of tools for understanding data. These tools can be classified as supervised or unsupervised. Broadly speaking, supervised statistical learning involves building a statistical model for predicting, or estimating, an output based on one or more inputs. Problems of this nature occur in fields as diverse as business, medicine, astrophysics, and public policy. With unsupervised statistical learning, there are inputs but no supervising output; nevertheless we can learn relationships and structure from such data. To provide an illustration of some applications of statistical learning, we briefly discuss three real-world data sets that are considered in this book.

# Wage Data

In this application (which we refer to as the Wage data set throughout this book), we examine a number of factors that relate to wages for a group of males from the Atlantic region of the United States. In particular, we wish to understand the association between an employee’s age and education, as well as the calendar year, on his wage. Consider, for example, the left-hand panel of Figure 1.1, which displays wage versus age for each of the individuals in the data set. There is evidence that wage increases with age but then decreases again after approximately age 60. The blue line, which provides an estimate of the average wage for a given age, makes this trend clearer.

G. James et al., An Introduction to Statistical Learning: with Applications in R, Springer Texts in Statistics, DOI 10.1007/978-1-4614-7138-7, © Springer Science+Business Media New York 2013





2        1. Introduction

![Three plots showing Wage data: scatter plot of Wage vs Age, box plot of Wage vs Year, and box plot of Wage vs Education Level]

**FIGURE 1.1.** Wage data, which contains income survey information for males from the central Atlantic region of the United States. Left: wage as a function of age. On average, wage increases with age until about 60 years of age, at which point it begins to decline. Center: wage as a function of year. There is a slow but steady increase of approximately $10,000 in the average wage between 2003 and 2009. Right: Boxplots displaying wage as a function of education, with 1 indicating the lowest level (no high school diploma) and 5 the highest level (an advanced graduate degree). On average, wage increases with the level of education.

Given an employee's age, we can use this curve to *predict* his wage. However, it is also clear from Figure 1.1 that there is a significant amount of variability associated with this average value, and so age alone is unlikely to provide an accurate prediction of a particular man's wage.

We also have information regarding each employee's education level and the year in which the wage was earned. The center and right-hand panels of Figure 1.1, which display wage as a function of both year and education, indicate that both of these factors are associated with wage. Wages increase by approximately $10,000, in a roughly linear (or straight-line) fashion, between 2003 and 2009, though this rise is very slight relative to the variability in the data. Wages are also typically greater for individuals with higher education levels: men with the lowest education level (1) tend to have substantially lower wages than those with the highest education level (5). Clearly, the most accurate prediction of a given man's wage will be obtained by combining his age, his education, and the year. In Chapter 3, we discuss linear regression, which can be used to predict wage from this data set. Ideally, we should predict wage in a way that accounts for the non-linear relationship between wage and age. In Chapter 7, we discuss a class of approaches for addressing this problem.

## *Stock Market Data*

The Wage data involves predicting a *continuous* or *quantitative* output value. This is often referred to as a *regression* problem. However, in certain cases we may instead wish to predict a non-numerical value—that is, a *categorical*



1. Introduction       3

| ![Yesterday boxplot showing percentage change in S\&P for Down and Up days](boxplot_yesterday) | ![Two Days Previous boxplot showing percentage change in S\&P for Down and Up days](boxplot_two_days) | ![Three Days Previous boxplot showing percentage change in S\&P for Down and Up days](boxplot_three_days) |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Yesterday<br/>Today's Direction: Down vs Up                                                    | Two Days Previous<br/>Today's Direction: Down vs Up                                                   | Three Days Previous<br/>Today's Direction: Down vs Up                                                     |


**FIGURE 1.2.** Left: *Boxplots of the previous day's percentage change in the S&P index for the days for which the market increased or decreased, obtained from the* Smarket *data.* Center and Right: *Same as left panel, but the percentage changes for 2 and 3 days previous are shown.*

or *qualitative* output. For example, in Chapter 4 we examine a stock market data set that contains the daily movements in the Standard & Poor's 500 (S&P) stock index over a 5-year period between 2001 and 2005. We refer to this as the Smarket data. The goal is to predict whether the index will *increase* or *decrease* on a given day using the past 5 days' percentage changes in the index. Here the statistical learning problem does not involve predicting a numerical value. Instead it involves predicting whether a given day's stock market performance will fall into the Up bucket or the Down bucket. This is known as a *classification* problem. A model that could accurately predict the direction in which the market will move would be very useful!

The left-hand panel of Figure 1.2 displays two boxplots of the previous day's percentage changes in the stock index: one for the 648 days for which the market increased on the subsequent day, and one for the 602 days for which the market decreased. The two plots look almost identical, suggesting that there is no simple strategy for using yesterday's movement in the S&P to predict today's returns. The remaining panels, which display boxplots for the percentage changes 2 and 3 days previous to today, similarly indicate little association between past and present returns. Of course, this lack of pattern is to be expected: in the presence of strong correlations between successive days' returns, one could adopt a simple trading strategy to generate profits from the market. Nevertheless, in Chapter 4, we explore these data using several different statistical learning methods. Interestingly, there are hints of some weak trends in the data that suggest that, at least for this 5-year period, it is possible to correctly predict the direction of movement in the market approximately 60% of the time (Figure 1.3).


# 1. Introduction

0.52

Predicted Probability

0.50

0.48

0.46

Down        Up

Today’s Direction

FIGURE 1.3. We fit a quadratic discriminant analysis model to the subset of the Smarket data corresponding to the 2001–2004 time period, and predicted the probability of a stock market decrease using the 2005 data. On average, the predicted probability of decrease is higher for the days in which the market does decrease. Based on these results, we are able to correctly predict the direction of movement in the market 60% of the time.

# Gene Expression Data

The previous two applications illustrate data sets with both input and output variables. However, another important class of problems involves situations in which we only observe input variables, with no corresponding output. For example, in a marketing setting, we might have demographic information for a number of current or potential customers. We may wish to understand which types of customers are similar to each other by grouping individuals according to their observed characteristics. This is known as a clustering problem. Unlike in the previous examples, here we are not trying to predict an output variable.

We devote Chapter 10 to a discussion of statistical learning methods for problems in which no natural output variable is available. We consider the NCI60 data set, which consists of 6,830 gene expression measurements for each of 64 cancer cell lines. Instead of predicting a particular output variable, we are interested in determining whether there are groups, or clusters, among the cell lines based on their gene expression measurements. This is a difficult question to address, in part because there are thousands of gene expression measurements per cell line, making it hard to visualize the data.

The left-hand panel of Figure 1.4 addresses this problem by representing each of the 64 cell lines using just two numbers, Z1 and Z2. These are the first two principal components of the data, which summarize the 6,830 expression measurements for each cell line down to two numbers or dimensions. While it is likely that this dimension reduction has resulted in





# 1. Introduction

FIGURE 1.4. Left: Representation of the NCI60 gene expression data set in a two-dimensional space, Z₁ and Z₂. Each point corresponds to one of the 64 cell lines. There appear to be four groups of cell lines, which we have represented using different colors. Right: Same as left panel except that we have represented each of the 14 different types of cancer using a different colored symbol. Cell lines corresponding to the same cancer type tend to be nearby in the two-dimensional space.

Some loss of information, it is now possible to visually examine the data for evidence of clustering. Deciding on the number of clusters is often a difficult problem. But the left-hand panel of Figure 1.4 suggests at least four groups of cell lines, which we have represented using separate colors. We can now examine the cell lines within each cluster for similarities in their types of cancer, in order to better understand the relationship between gene expression levels and cancer.

In this particular data set, it turns out that the cell lines correspond to 14 different types of cancer. (However, this information was not used to create the left-hand panel of Figure 1.4.) The right-hand panel of Figure 1.4 is identical to the left-hand panel, except that the 14 cancer types are shown using distinct colored symbols. There is clear evidence that cell lines with the same cancer type tend to be located near each other in this two-dimensional representation. In addition, even though the cancer information was not used to produce the left-hand panel, the clustering obtained does bear some resemblance to some of the actual cancer types observed in the right-hand panel. This provides some independent verification of the accuracy of our clustering analysis.

# A Brief History of Statistical Learning

Though the term statistical learning is fairly new, many of the concepts that underlie the field were developed long ago. At the beginning of the nineteenth century, Legendre and Gauss published papers on the method





# 1. Introduction

of least squares, which implemented the earliest form of what is now known as linear regression. The approach was ﬁrst successfully applied to problems in astronomy. Linear regression is used for predicting quantitative values, such as an individual’s salary. In order to predict qualitative values, such as whether a patient survives or dies, or whether the stock market increases or decreases, Fisher proposed linear discriminant analysis in 1936. In the 1940s, various authors put forth an alternative approach, logistic regression. In the early 1970s, Nelder and Wedderburn coined the term generalized linear models for an entire class of statistical learning methods that include both linear and logistic regression as special cases.

By the end of the 1970s, many more techniques for learning from data were available. However, they were almost exclusively linear methods, because ﬁtting non-linear relationships was computationally infeasible at the time. By the 1980s, computing technology had ﬁnally improved suﬃciently that non-linear methods were no longer computationally prohibitive. In mid 1980s Breiman, Friedman, Olshen and Stone introduced classiﬁcation and regression trees, and were among the ﬁrst to demonstrate the power of a detailed practical implementation of a method, including cross-validation for model selection. Hastie and Tibshirani coined the term generalized additive models in 1986 for a class of non-linear extensions to generalized linear models, and also provided a practical software implementation.

Since that time, inspired by the advent of machine learning and other disciplines, statistical learning has emerged as a new subﬁeld in statistics, focused on supervised and unsupervised modeling and prediction. In recent years, progress in statistical learning has been marked by the increasing availability of powerful and relatively user-friendly software, such as the popular and freely available R system. This has the potential to continue the transformation of the ﬁeld from a set of techniques used and developed by statisticians and computer scientists to an essential toolkit for a much broader community.

# This Book

The Elements of Statistical Learning (ESL) by Hastie, Tibshirani, and Friedman was ﬁrst published in 2001. Since that time, it has become an important reference on the fundamentals of statistical machine learning. Its success derives from its comprehensive and detailed treatment of many important topics in statistical learning, as well as the fact that (relative to many upper-level statistics textbooks) it is accessible to a wide audience. However, the greatest factor behind the success of ESL has been its topical nature. At the time of its publication, interest in the ﬁeld of statistical



# 1. Introduction

Learning was starting to explode. ESL provided one of the first accessible and comprehensive introductions to the topic.

Since ESL was first published, the field of statistical learning has continued to flourish. The field’s expansion has taken two forms. The most obvious growth has involved the development of new and improved statistical learning approaches aimed at answering a range of scientific questions across a number of fields. However, the field of statistical learning has also expanded its audience. In the 1990s, increases in computational power generated a surge of interest in the field from non-statisticians who were eager to use cutting-edge statistical tools to analyze their data. Unfortunately, the highly technical nature of these approaches meant that the user community remained primarily restricted to experts in statistics, computer science, and related fields with the training (and time) to understand and implement them.

In recent years, new and improved software packages have significantly eased the implementation burden for many statistical learning methods. At the same time, there has been growing recognition across a number of fields, from business to health care to genetics to the social sciences and beyond, that statistical learning is a powerful tool with important practical applications. As a result, the field has moved from one of primarily academic interest to a mainstream discipline, with an enormous potential audience. This trend will surely continue with the increasing availability of enormous quantities of data and the software to analyze it.

The purpose of An Introduction to Statistical Learning (ISL) is to facilitate the transition of statistical learning from an academic to a mainstream field. ISL is not intended to replace ESL, which is a far more comprehensive text both in terms of the number of approaches considered and the depth to which they are explored. We consider ESL to be an important companion for professionals (with graduate degrees in statistics, machine learning, or related fields) who need to understand the technical details behind statistical learning approaches. However, the community of users of statistical learning techniques has expanded to include individuals with a wider range of interests and backgrounds. Therefore, we believe that there is now a place for a less technical and more accessible version of ESL.

In teaching these topics over the years, we have discovered that they are of interest to master’s and PhD students in fields as disparate as business administration, biology, and computer science, as well as to quantitatively-oriented upper-division undergraduates. It is important for this diverse group to be able to understand the models, intuitions, and strengths and weaknesses of the various approaches. But for this audience, many of the technical details behind statistical learning methods, such as optimization algorithms and theoretical properties, are not of primary interest. We believe that these students do not need a deep understanding of these aspects in order to become informed users of the various methodologies.


# 1. Introduction

In order to contribute to their chosen fields through the use of statistical learning tools. ISLR is based on the following four premises.

1. Many statistical learning methods are relevant and useful in a wide range of academic and non-academic disciplines, beyond just the statistical sciences. We believe that many contemporary statistical learning procedures should, and will, become as widely available and used as is currently the case for classical methods such as linear regression. As a result, rather than attempting to consider every possible approach (an impossible task), we have concentrated on presenting the methods that we believe are most widely applicable.
2. Statistical learning should not be viewed as a series of black boxes. No single approach will perform well in all possible applications. Without understanding all of the cogs inside the box, or the interaction between those cogs, it is impossible to select the best box. Hence, we have attempted to carefully describe the model, intuition, assumptions, and trade-offs behind each of the methods that we consider.
3. While it is important to know what job is performed by each cog, it is not necessary to have the skills to construct the machine inside the box! Thus, we have minimized discussion of technical details related to fitting procedures and theoretical properties. We assume that the reader is comfortable with basic mathematical concepts, but we do not assume a graduate degree in the mathematical sciences. For instance, we have almost completely avoided the use of matrix algebra, and it is possible to understand the entire book without a detailed knowledge of matrices and vectors.
4. We presume that the reader is interested in applying statistical learning methods to real-world problems. In order to facilitate this, as well as to motivate the techniques discussed, we have devoted a section within each chapter to R computer labs. In each lab, we walk the reader through a realistic application of the methods considered in that chapter. When we have taught this material in our courses, we have allocated roughly one-third of classroom time to working through the labs, and we have found them to be extremely useful. Many of the less computationally-oriented students who were initially intimidated by R’s command level interface got the hang of things over the course of the quarter or semester. We have used R because it is freely available and is powerful enough to implement all of the methods discussed in the book. It also has optional packages that can be downloaded to implement literally thousands of additional methods. Most importantly, R is the language of choice for academic statisticians, and new approaches often become available in.




# 1. Introduction

R years before they are implemented in commercial packages. However, the labs in ISL are self-contained, and can be skipped if the reader wishes to use a different software package or does not wish to apply the methods discussed to real-world problems.

# Who Should Read This Book?

This book is intended for anyone who is interested in using modern statistical methods for modeling and prediction from data. This group includes scientists, engineers, data analysts, or quants, but also less technical individuals with degrees in non-quantitative fields such as the social sciences or business. We expect that the reader will have had at least one elementary course in statistics. Background in linear regression is also useful, though not required, since we review the key concepts behind linear regression in Chapter 3. The mathematical level of this book is modest, and a detailed knowledge of matrix operations is not required. This book provides an introduction to the statistical programming language R. Previous exposure to a programming language, such as MATLAB or Python, is useful but not required.

We have successfully taught material at this level to master’s and PhD students in business, computer science, biology, earth sciences, psychology, and many other areas of the physical and social sciences. This book could also be appropriate for advanced undergraduates who have already taken a course on linear regression. In the context of a more mathematically rigorous course in which ESL serves as the primary textbook, ISL could be used as a supplementary text for teaching computational aspects of the various approaches.

# Notation and Simple Matrix Algebra

Choosing notation for a textbook is always a difficult task. For the most part we adopt the same notational conventions as ESL.

We will use n to represent the number of distinct data points, or observations, in our sample. We will let p denote the number of variables that are available for use in making predictions. For example, the Wage data set consists of 12 variables for 3,000 people, so we have n = 3,000 observations and p = 12 variables (such as year, age, wage, and more). Note that throughout this book, we indicate variable names using colored font: Variable Name.

In some examples, p might be quite large, such as on the order of thousands or even millions; this situation arises quite often, for example, in the analysis of modern biological data or web-based advertising data.



# 1. Introduction

In general, we will let *xij represent the value of the jth variable for the ith observation, where i = 1, 2, . . . , n and j = 1, 2, . . . , p. Throughout this book, i will be used to index the samples or observations (from 1 to n) and j will be used to index the variables (from 1 to p). We let *X* denote a n × p matrix whose (i, j)th element is xij*. That is,

⌈x11            x12      . . .        x1p ⌉
⌊x21            x22      . . .        x2p ⌋
X = ⌊  .               .      . .           .     ⌋ .
⌊ .               .      . .           .     ⌋
⎜ .               .              .     .     ⎝
.           .                    .
xn1       xn2      . . .        xnp

For readers who are unfamiliar with matrices, it is useful to visualize *X as a spreadsheet of numbers with n rows and p* columns.

At times we will be interested in the rows of *X, which we write as x1, x2, . . . , xn. Here xi is a vector of length p, containing the p* variable measurements for the ith observation. That is,

⌈xi1⌉
⌊xi2⌋
xi = ⌊ . ⌋                                         (1.1)
⌊ . ⌋
⎜ . ⎝
.
xip

(Vectors are by default represented as columns.) For example, for the Wage data, *xi is a vector of length 12, consisting of year, age, wage, and other values for the ith individual. At other times we will instead be interested in the columns of X, which we write as x1, x2, . . . , xp. Each is a vector of length n*. That is,

⌈x1j ⌉
⌊x2j ⌋
xj = ⌊ . ⌋ .
⌊ . ⌋
⎜ . ⎝
.
xnj

For example, for the Wage data, *x1 contains the n = 3,000* values for year.

Using this notation, the matrix X can be written as

X = ⌈x1         x2      · · ·         xp⌉ ,

or

⌈xT ⌉
⌊ x1 ⌋
⌊xT ⌋
X = ⌊ 2 ⌋ .
.
⎜ . ⎝
.
xT
n


# 1. Introduction

The T notation denotes the transpose of a matrix or vector. So, for example,

⌈x11                     x21     . . .      xn1⌉
⌊x12                     x22     . . .      xn2⌋
XT = ⌊  x1p    x2p     . . .     xnp⌋ ,
⌊ .                       .                 .  ⌋
⎜ .                       .                 .  ⎝
.         .                 .
x1p    x2p     . . .     xnp

while

xT = ⌈xi1                 xi2    · · ·     xip⌉ .

We use yi to denote the ith observation of the variable on which we wish to make predictions, such as wage. Hence, we write the set of all n observations in vector form as

⌈y1⌉
⌊y2⌋
y = ⌊  . ⌋ .
⌊ . ⌋
⎜ . ⎝
.
yn

Then our observed data consists of {(x1, y1), (x2, y2), . . . , (xn, yn)}, where each xi is a vector of length p. (If p = 1, then xi is simply a scalar.)

In this text, a vector of length n will always be denoted in lower case bold; e.g.

⌈a1⌉
⌊a2⌋
a = ⌊  . ⌋ .
⌊ . ⌋
⎜ . ⎝
.
an

However, vectors that are not of length n (such as feature vectors of length p, as in (1.1)) will be denoted in lower case normal font, e.g. a. Scalars will also be denoted in lower case normal font, e.g. a. In the rare cases in which these two uses for lower case normal font lead to ambiguity, we will clarify which use is intended. Matrices will be denoted using bold capitals, such as A. Random variables will be denoted using capital normal font, e.g. A, regardless of their dimensions.

Occasionally we will want to indicate the dimension of a particular object. To indicate that an object is a scalar, we will use the notation a ∈ R. To indicate that it is a vector of length k, we will use a ∈ Rk (or a ∈ Rn if it is of length n). We will indicate that an object is a r × s matrix using A ∈ Rr×s.

We have avoided using matrix algebra whenever possible. However, in a few instances it becomes too cumbersome to avoid it entirely. In these rare instances it is important to understand the concept of multiplying two matrices. Suppose that A ∈ Rr×d and B ∈ Rd×s. Then the product





12    1. Introduction

of **A** and **B** is denoted **AB**. The $(i, j)$th element of **AB** is computed by multiplying each element of the $i$th row of **A** by the corresponding element of the $j$th column of **B**. That is, $(\mathbf{AB})_{ij} = \sum_{k=1}^{d} a_{ik}b_{kj}$. As an example, consider

$$\mathbf{A} = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \quad \text{and} \quad \mathbf{B} = \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}.$$

Then

$$\mathbf{AB} = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix} = \begin{pmatrix} 1 \times 5 + 2 \times 7 & 1 \times 6 + 2 \times 8 \\ 3 \times 5 + 4 \times 7 & 3 \times 6 + 4 \times 8 \end{pmatrix} = \begin{pmatrix} 19 & 22 \\ 43 & 50 \end{pmatrix}.$$

Note that this operation produces an $r \times s$ matrix. It is only possible to compute **AB** if the number of columns of **A** is the same as the number of rows of **B**.

## Organization of This Book

Chapter 2 introduces the basic terminology and concepts behind statistical learning. This chapter also presents the *K-nearest neighbor* classifier, a very simple method that works surprisingly well on many problems. Chapters 3 and 4 cover classical linear methods for regression and classification. In particular, Chapter 3 reviews *linear regression*, the fundamental starting point for all regression methods. In Chapter 4 we discuss two of the most important classical classification methods, *logistic regression* and *linear discriminant analysis*.

A central problem in all statistical learning situations involves choosing the best method for a given application. Hence, in Chapter 5 we introduce *cross-validation* and the *bootstrap*, which can be used to estimate the accuracy of a number of different methods in order to choose the best one.

Much of the recent research in statistical learning has concentrated on non-linear methods. However, linear methods often have advantages over their non-linear competitors in terms of interpretability and sometimes also accuracy. Hence, in Chapter 6 we consider a host of linear methods, both classical and more modern, which offer potential improvements over standard linear regression. These include *stepwise selection*, *ridge regression*, *principal components regression*, *partial least squares*, and the *lasso*.

The remaining chapters move into the world of non-linear statistical learning. We first introduce in Chapter 7 a number of non-linear methods that work well for problems with a single input variable. We then show how these methods can be used to fit non-linear *additive* models for which there is more than one input. In Chapter 8, we investigate *tree*-based methods, including *bagging*, *boosting*, and *random forests*. *Support vector machines*, a set of approaches for performing both linear and non-linear classification,

# 1. Introduction

are discussed in Chapter 9. Finally, in Chapter 10, we consider a setting in which we have input variables but no output variable. In particular, we present principal components analysis, K-means clustering, and hierarchical clustering.

At the end of each chapter, we present one or more R lab sections in which we systematically work through applications of the various methods discussed in that chapter. These labs demonstrate the strengths and weaknesses of the various approaches, and also provide a useful reference for the syntax required to implement the various methods. The reader may choose to work through the labs at his or her own pace, or the labs may be the focus of group sessions as part of a classroom environment. Within each R lab, we present the results that we obtained when we performed the lab at the time of writing this book. However, new versions of R are continuously released, and over time, the packages called in the labs will be updated. Therefore, in the future, it is possible that the results shown in the lab sections may no longer correspond precisely to the results obtained by the reader who performs the labs. As necessary, we will post updates to the labs on the book website.

We use the symbol to denote sections or exercises that contain more challenging concepts. These can be easily skipped by readers who do not wish to delve as deeply into the material, or who lack the mathematical background.

# Data Sets Used in Labs and Exercises

In this textbook, we illustrate statistical learning methods using applications from marketing, finance, biology, and other areas. The ISLR package available on the book website contains a number of data sets that are required in order to perform the labs and exercises associated with this book. One other data set is contained in the MASS library, and yet another is part of the base R distribution. Table 1.1 contains a summary of the data sets required to perform the labs and exercises. A couple of these data sets are also available as text files on the book website, for use in Chapter 2.

# Book Website

The website for this book is located at

www.StatLearning.com



14        1. Introduction

| Name      | Description                                                       |
| --------- | ----------------------------------------------------------------- |
| Auto      | Gas mileage, horsepower, and other information for cars.          |
| Boston    | Housing values and other information about Boston suburbs.        |
| Caravan   | Information about individuals offered caravan insurance.          |
| Carseats  | Information about car seat sales in 400 stores.                   |
| College   | Demographic characteristics, tuition, and more for USA colleges.  |
| Default   | Customer default records for a credit card company.               |
| Hitters   | Records and salaries for baseball players.                        |
| Khan      | Gene expression measurements for four cancer types.               |
| NCI60     | Gene expression measurements for 64 cancer cell lines.            |
| OJ        | Sales information for Citrus Hill and Minute Maid orange juice.   |
| Portfolio | Past values of financial assets, for use in portfolio allocation. |
| Smarket   | Daily percentage returns for S\&P 500 over a 5-year period.       |
| USArrests | Crime statistics per 100,000 residents in 50 states of USA.       |
| Wage      | Income survey data for males in central Atlantic region of USA.   |
| Weekly    | 1,089 weekly stock market returns for 21 years.                   |


**TABLE 1.1.** *A list of data sets needed to perform the labs and exercises in this textbook. All data sets are available in the* ISLR *library, with the exception of* Boston *(part of* MASS*) and* USArrests *(part of the base* R *distribution).*

It contains a number of resources, including the R package associated with this book, and some additional data sets.

## Acknowledgements

A few of the plots in this book were taken from ESL: Figures 6.7, 8.3, and 10.12. All other plots are new to this book.


# Statistical Learning

# 2.1 What Is Statistical Learning?

In order to motivate our study of statistical learning, we begin with a simple example. Suppose that we are statistical consultants hired by a client to provide advice on how to improve sales of a particular product. The Advertising data set consists of the sales of that product in 200 different markets, along with advertising budgets for the product in each of those markets for three different media: TV, radio, and newspaper. The data are displayed in Figure 2.1. It is not possible for our client to directly increase sales of the product. On the other hand, they can control the advertising expenditure in each of the three media. Therefore, if we determine that there is an association between advertising and sales, then we can instruct our client to adjust advertising budgets, thereby indirectly increasing sales. In other words, our goal is to develop an accurate model that can be used to predict sales on the basis of the three media budgets.

In this setting, the advertising budgets are input variables while sales is an output variable. The input variables are typically denoted using the variable symbol X, with a subscript to distinguish them. So X1 might be the TV budget, X2 the radio budget, and X3 the newspaper budget. The inputs go by different names, such as predictors, independent variables, features, or sometimes just variables. The output variable—in this case, sales—is often called the response or dependent variable, and is typically denoted using the symbol Y. Throughout this book, we will use all of these terms interchangeably.

G. James et al., An Introduction to Statistical Learning: with Applications in R, Springer Texts in Statistics, DOI 10.1007/978-1-4614-7138-7 2, © Springer Science+Business Media New York 2013





16    2. Statistical Learning

![Three scatter plots showing Sales vs TV, Radio, and Newspaper budgets with fitted regression lines]

**FIGURE 2.1.** The **Advertising** data set. The plot displays **sales**, in thousands of units, as a function of **TV**, **radio**, and **newspaper** budgets, in thousands of dollars, for 200 different markets. In each plot we show the simple least squares fit of **sales** to that variable, as described in Chapter 3. In other words, each blue line represents a simple model that can be used to predict **sales** using **TV**, **radio**, and **newspaper**, respectively.

More generally, suppose that we observe a quantitative response $Y$ and $p$ different predictors, $X_1, X_2, \ldots, X_p$. We assume that there is some relationship between $Y$ and $X = (X_1, X_2, \ldots, X_p)$, which can be written in the very general form

$$Y = f(X) + \epsilon.$$ (2.1)

Here $f$ is some fixed but unknown function of $X_1, \ldots, X_p$, and $\epsilon$ is a random error term, which is independent of $X$ and has mean zero. In this formulation, $f$ represents the *systematic* information that $X$ provides about $Y$.

As another example, consider the left-hand panel of Figure 2.2, a plot of **income** versus **years of education** for 30 individuals in the **Income** data set. The plot suggests that one might be able to predict **income** using **years of education**. However, the function $f$ that connects the input variable to the output variable is in general unknown. In this situation one must estimate $f$ based on the observed points. Since **Income** is a simulated data set, $f$ is known and is shown by the blue curve in the right-hand panel of Figure 2.2. The vertical lines represent the error terms $\epsilon$. We note that some of the 30 observations lie above the blue curve and some lie below it; overall, the errors have approximately mean zero.

In general, the function $f$ may involve more than one input variable. In Figure 2.3 we plot **income** as a function of **years of education** and **seniority**. Here $f$ is a two-dimensional surface that must be estimated based on the observed data.



2.1 What Is Statistical Learning?              17

**FIGURE 2.2.** The Income data set. Left: The red dots are the observed values of income (in tens of thousands of dollars) and years of education for 30 individuals. Right: The blue curve represents the true underlying relationship between income and years of education, which is generally unknown (but is known in this case because the data were simulated). The black lines represent the error associated with each observation. Note that some errors are positive (if an observation lies above the blue curve) and some are negative (if an observation lies below the curve). Overall, these errors have approximately mean zero.

In essence, statistical learning refers to a set of approaches for estimating $f$. In this chapter we outline some of the key theoretical concepts that arise in estimating $f$, as well as tools for evaluating the estimates obtained.

## 2.1.1 Why Estimate $f$?

There are two main reasons that we may wish to estimate $f$: *prediction* and *inference*. We discuss each in turn.

### Prediction

In many situations, a set of inputs $X$ are readily available, but the output $Y$ cannot be easily obtained. In this setting, since the error term averages to zero, we can predict $Y$ using

$$\hat{Y} = \hat{f}(X),$$                                                    (2.2)

where $\hat{f}$ represents our estimate for $f$, and $\hat{Y}$ represents the resulting prediction for $Y$. In this setting, $\hat{f}$ is often treated as a *black box*, in the sense that one is not typically concerned with the exact form of $\hat{f}$, provided that it yields accurate predictions for $Y$.

# 2. Statistical Learning

# Income

# Seniority

# Years of Education

FIGURE 2.3. The plot displays income as a function of years of education and seniority in the Income data set. The blue surface represents the true underlying relationship between income and years of education and seniority, which is known since the data are simulated. The red dots indicate the observed values of these quantities for 30 individuals.

As an example, suppose that X1, . . . , Xp are characteristics of a patient’s blood sample that can be easily measured in a lab, and Y is a variable encoding the patient’s risk for a severe adverse reaction to a particular drug. It is natural to seek to predict Y using X, since we can then avoid giving the drug in question to patients who are at high risk of an adverse reaction—that is, patients for whom the estimate of Y is high.

The accuracy of Ȳ as a prediction for Y depends on two quantities, which we will call the reducible error and the irreducible error. In general, ȳ will not be a perfect estimate for f, and this inaccuracy will introduce some error. This error is reducible because we can potentially improve the accuracy of ȳ by using the most appropriate statistical learning technique to estimate f. However, even if it were possible to form a perfect estimate for f, so that our estimated response took the form Ȳ = f(X), our prediction would still have some error in it! This is because Y is also a function of ϵ, which, by definition, cannot be predicted using X. Therefore, variability associated with ϵ also affects the accuracy of our predictions. This is known as the irreducible error, because no matter how well we estimate f, we cannot reduce the error introduced by ϵ.

Why is the irreducible error larger than zero? The quantity ϵ may contain unmeasured variables that are useful in predicting Y: since we don’t measure them, f cannot use them for its prediction. The quantity ϵ may also contain unmeasurable variation. For example, the risk of an adverse reaction might vary for a given patient on a given day, depending on