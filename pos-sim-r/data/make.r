library(knitr)
library(markdown)
library(rmarkdown)
ff <- commandArgs(TRUE)[1]
params <- new.env()
## here I pass all the parameters to the report
## I assume that the report and the code R in the same location
## the result pdf also will be in the same location , otherwise you can set
## paths as you like

render("analyze.Rmd",run_pandoc=TRUE)
