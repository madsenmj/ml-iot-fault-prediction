# Map 1-based optional input ports to variables
dataset1 <- maml.mapInputPort(1) # class: data.frame

install.packages("src/magrittr_1.5.zip",lib="src/",repos=NULL)
install.packages("src/xgboost_0.4-3.zip",lib="src/",repos=NULL)
library(xgboost,lib.loc="src/")
library(Matrix)

inputdata <- data.matrix(dataset1[,-1])
bst_model <- xgb.load('src/0002.model')

pred <- predict(bst_model, inputdata)
dim(pred) <- c(4,nrow(dataset1))
predout <- t(pred)
data.set <- data.frame('Probability Normal'=predout[,1],check.names=F)


# Select data.frame to be sent to the output Dataset port
maml.mapOutputPort("data.set");