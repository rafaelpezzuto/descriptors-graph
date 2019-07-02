y2016 = read.csv(file='Temp/rev-saude/2016.csv', header = F)
rownames(y2016) <- y2016$V1
y2016$V1 <- NULL
k2016 = kmeans(y2016, 30)
k2016$cluster
