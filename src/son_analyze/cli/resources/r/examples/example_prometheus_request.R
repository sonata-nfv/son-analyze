library(son.analyze)

containerId <- "a778fc8383a6"
step <- 5

r <- query(rangeQuery("http://172.17.0.5:9090",
                      sprintf("container_cpu_usage_seconds_total{id=~'/docker/%s'}", containerId),
                      interval = lubridate::as.interval(lubridate::hours(-1),
                                                        lubridate::now()),
                      step = paste0(step, "s")))


total <- local({
  m <- function(x, y) {
    tmp <- list()
    tmp[[y$labels$cpu]] <- y$df$Value
    return(c(x, tmp))
  }
  filtered <- filterByLabel(r, "cpu", "^cpu")
  data.frame(Reduce(m, filtered, list(), accumulate = FALSE))
})


d <- local({
  `%>%` <- dplyr::`%>%`
  dplyr::as.tbl(total) %>%
    dplyr::mutate(Total = Reduce(`+`, .)) %>%
    dplyr::mutate(Diff = c(0, diff(Total))) %>%
    dplyr::mutate(Load = (Diff / step / length(total)))
})


with(r[[1]], {
  x <- xts::xts(d, order.by = df$Timestamp)
  plot(x$Load, t = "l", main = "")
  title(main = metricName, sub = id)
})
